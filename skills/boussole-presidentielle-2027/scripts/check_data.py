#!/usr/bin/env python3
"""Vérifie les fiches candidats et signale ce qui est incomplet ou ancien.

Usage : python3 check_data.py [--jours 30]

Vérifie d'abord data/enjeux.json (identifiants uniques, thèmes connus, deux pôles, deux ou trois variantes complètes
par enjeu) : une erreur y fait échouer le script. Les variantes que Lcharvol n'a pas encore validées (`validee`)
sont signalées en alerte.

Affiche, pour chaque candidat : statut, date de mise à jour, positions renseignées,
positions seulement déduites, positions avec citation et positions relues par un humain.
Les positions sans citation, les citations trop longues et les sources d'agrégateurs sont
signalées en alerte. Code de sortie 1 si une fiche est invalide.
"""
import json
import sys
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
VALEURS = {-2, -1, 0, 1, 2, None}
CONFIANCES = {"programme", "declaration", "deduite"}
CITATION_MAX = 300
AGREGATEURS = ("votons-2027", "elyseescope", "monvote2027")
VARIANTES_MIN, VARIANTES_MAX = 2, 3


def verifier_enjeux(enjeux):
    """Renvoie (erreurs, alertes) sur la structure de data/enjeux.json."""
    erreurs, alertes = [], []
    ids = [e.get("id") for e in enjeux["enjeux"]]
    doublons = sorted({i for i in ids if ids.count(i) > 1})
    if doublons:
        erreurs.append(f"identifiants d'enjeu en double : {doublons}")
    non_validees = 0
    for e in enjeux["enjeux"]:
        eid = e.get("id")
        if e.get("theme") not in enjeux["themes"]:
            erreurs.append(f"{eid}: thème inconnu {e.get('theme')!r}")
        for k in ("pole_a", "pole_b"):
            if not (e.get(k) or "").strip():
                erreurs.append(f"{eid}: {k} manquant")
        vs = e.get("variantes") or []
        if not VARIANTES_MIN <= len(vs) <= VARIANTES_MAX:
            erreurs.append(f"{eid}: {len(vs)} variantes (attendu {VARIANTES_MIN} à {VARIANTES_MAX})")
        vids = [v.get("id") for v in vs]
        for i, v in enumerate(vs):
            if not str(v.get("id", "")).startswith(f"{eid}.") or vids.count(v.get("id")) > 1:
                erreurs.append(f"{eid}: identifiant de variante {v.get('id')!r} (attendu {eid}.N, unique)")
            for k in ("question", "a", "b"):
                if not (v.get(k) or "").strip():
                    erreurs.append(f"{v.get('id')}: champ {k} vide")
            if not isinstance(v.get("validee", False), bool):
                erreurs.append(f"{v.get('id')}: validee {v.get('validee')!r} (booléen attendu)")
            non_validees += not v.get("validee")
    if non_validees:
        alertes.append(f"{non_validees} variantes pas encore validées par un humain (champ validee)")
    return erreurs, alertes


def main():
    jours = int(sys.argv[sys.argv.index("--jours") + 1]) if "--jours" in sys.argv else 30
    questions = json.loads((DATA / "enjeux.json").read_text(encoding="utf-8"))
    err_enjeux, alertes_enjeux = verifier_enjeux(questions)
    ids = [q["id"] for q in questions["enjeux"]]
    print(f"Enjeux : {len(ids)} ; variantes : {sum(len(e['variantes']) for e in questions['enjeux'])}")
    for m in err_enjeux:
        print(f"ERREUR enjeux.json : {m}")
    for m in alertes_enjeux:
        print(f"Alerte enjeux.json : {m}")
    print()
    erreurs = len(err_enjeux)
    print(f"{'Candidat':28} {'Statut':22} {'MAJ':11} {'Pos.':>5} {'Prog.':>5} {'Déd.':>5} "
          f"{'Cit.':>5} {'Relues':>7}  Alertes")
    total_relues = total_renseignees = 0
    for f in sorted((DATA / "candidats").glob("*.json")):
        alertes = []
        try:
            c = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"{f.name}: JSON invalide ({e})")
            erreurs += 1
            continue
        if c.get("format") != 2:
            alertes.append(f"format {c.get('format')!r} (2 attendu)")
            erreurs += 1
        pos = c.get("positions", {})
        inconnus = set(pos) - set(ids)
        if inconnus:
            alertes.append(f"ids inconnus {sorted(inconnus)}")
            erreurs += 1
        renseignees = prog = ded = cit = relues = 0
        sans_citation = []
        for qid in ids:
            p = pos.get(qid) or {}
            v = p.get("valeur")
            if "relu" in p and not isinstance(p["relu"], bool):
                alertes.append(f"{qid}: relu {p['relu']!r} (booléen attendu)")
                erreurs += 1
            citation = p.get("citation")
            if citation is not None and not isinstance(citation, str):
                alertes.append(f"{qid}: citation {citation!r} (texte attendu)")
                erreurs += 1
                citation = None
            if v not in VALEURS:
                alertes.append(f"{qid}: valeur {v!r} invalide")
                erreurs += 1
                continue
            if v is None:
                continue
            renseignees += 1
            if not p.get("source"):
                alertes.append(f"{qid}: sans source")
                erreurs += 1
            conf = p.get("confiance")
            if conf not in CONFIANCES:
                alertes.append(f"{qid}: confiance {conf!r}")
            prog += conf == "programme"
            ded += conf == "deduite"
            relues += p.get("relu") is True
            if any(a in (p.get("source") or "") for a in AGREGATEURS):
                alertes.append(f"{qid}: source d'agrégateur")
            if citation and citation.strip():
                cit += 1
                if len(citation) > CITATION_MAX:
                    alertes.append(f"{qid}: citation de {len(citation)} caractères (> {CITATION_MAX})")
            else:
                sans_citation.append(qid)
        if sans_citation:
            alertes.append(f"{len(sans_citation)} sans citation ({', '.join(sans_citation)})")
        total_relues += relues
        total_renseignees += renseignees
        maj = c.get("mis_a_jour", "?")
        try:
            age = (date.today() - date.fromisoformat(maj)).days
            if age > jours:
                alertes.append(f"MAJ il y a {age} j")
        except ValueError:
            alertes.append("date MAJ invalide")
        print(f"{c.get('nom', f.stem)[:28]:28} {str(c.get('statut'))[:22]:22} {maj:11} "
              f"{renseignees:>2}/{len(ids)} {prog:>5} {ded:>5} {cit:>5} {relues:>3}/{renseignees:<3}  "
              f"{'; '.join(alertes)}")
    print(f"\nPositions renseignées relues par un humain : {total_relues}/{total_renseignees} "
          f"({total_renseignees - total_relues} à relire : python3 scripts/a_relire.py)")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
