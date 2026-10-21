#!/usr/bin/env python3
"""Test « devine le camp » : la formulation d'un dilemme trahit-elle un camp ?

Des agents jouent des électeurs de bords différents. Pour chaque formulation, présentée avec ses deux options
dans un ordre tiré au hasard, chacun répond à trois questions :
  - redacteur : d'après la seule formulation, la personne qui l'a rédigée est-elle plutôt de gauche (G), de
    droite (D), ou est-ce impossible à dire (?) ;
  - gauche    : laquelle des deux options est celle que choisirait plutôt un électeur de gauche (1, 2 ou ?) ;
  - favorisee : laquelle des deux options la formulation présente-t-elle sous le jour le plus favorable
    (1, 2, ou = si elles sont présentées à égalité).

Trois taux par formulation, de 0 à 100 % (« ? » et « = » comptent pour moitié, comme une réponse au hasard) :
  - **rédacteur** : part des agents qui attribuent la formulation au camp de l'ancienne affirmation (le camp du
    pôle qu'elle défendait). 50 % = hasard. C'est le critère de sélection : une formulation est retenue si ce
    taux reste entre SEUIL_BAS et SEUIL_HAUT. Les anciennes affirmations, passées au même test, servent de témoin ;
  - **favorisée** : part des agents qui jugent la formulation favorable au pôle de l'ancienne affirmation.
    50 % = équilibré ; c'est le second critère (même fourchette) ;
  - **orientation** : part des agents qui reconnaissent l'option de gauche. Ce taux mesure le fond de l'enjeu
    plus que la formulation : un dilemme sur l'impôt sur la fortune reste reconnaissable, quelle que soit sa
    rédaction, et une boussole dont les pôles ne correspondraient à aucun camp ne départagerait personne. Il est
    rapporté pour information et sert à choisir, à sens égal, la formulation la moins marquée.

Le camp de chaque pôle vient des données, sans étiquette posée à la main : c'est le signe de la corrélation entre
les positions des candidats sur l'enjeu et leur place sur l'axe principal calculé par audit_biais.py. Pour les
enjeux transversaux (|r| < 0,4), ce camp est peu marqué et les taux sont donnés à titre indicatif.

Usage, depuis la racine du dépôt :
    python3 outils/devine_le_camp.py preparer DOSSIER [--graine 2027] [--lots 2] [--enjeux id1,id2] [--variantes id.1,id.2] [--temoins]
    python3 outils/devine_le_camp.py noter DOSSIER [DOSSIER…] [--markdown] [--json FICHIER]
`preparer` écrit dans DOSSIER un fichier de consignes par agent (persona × lot) et une clé (cle.json) qui reste
hors de portée des agents. Chaque agent écrit ses réponses dans reponses-<persona>-<lot>.json :
    {"<code>": {"redacteur": "G|D|?", "gauche": "1|2|?", "favorisee": "1|2|="}, ...}
`noter` lit la clé et les réponses et produit le rapport. Avec plusieurs dossiers (tours successifs), les réponses
s'additionnent pour les formulations dont le texte n'a pas changé ; celles qui ont été réécrites ne gardent que
les tours passés sur leur texte actuel.
"""
import json
import random
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SKILL = RACINE / "skills" / "boussole-presidentielle-2027"
sys.path.insert(0, str(SKILL / "scripts"))

from audit_biais import axe, pearson, valeur  # noqa: E402
from score import charger  # noqa: E402

PERSONAS = {
    "gauche-radicale": "Vous votez pour la gauche radicale (type LFI, extrême gauche).",
    "gauche-moderee": "Vous votez pour la gauche modérée (type PS, écologistes).",
    "centre": "Vous votez pour le centre (type Renaissance, MoDem, Horizons).",
    "droite": "Vous votez pour la droite (type LR).",
    "droite-nationale": "Vous votez pour la droite nationale (type RN, Reconquête).",
    "sans-camp": "Vous ne vous situez dans aucun camp et votez rarement.",
}
SEUIL_BAS, SEUIL_HAUT = 0.35, 0.65
MIN_PAR_LOT = 8

CONSIGNE = """Vous participez à un test de neutralité d'un questionnaire politique (présidentielle française 2027).
{persona} Gardez ce point de vue, mais répondez avec lucidité : on vous demande de deviner, pas de donner votre avis.

Pour chaque question ci-dessous (deux options numérotées 1 et 2), répondez à trois questions, en vous fondant
sur la FORMULATION autant que sur le fond :
- "redacteur" : d'après la seule formulation (choix des mots, cadrage, ordre d'idées, ce qui est présenté comme
  allant de soi), la personne qui l'a rédigée est-elle plutôt de gauche ("G"), plutôt de droite ("D"), ou est-ce
  impossible à dire ("?") ? Ne répondez "G" ou "D" que si un indice précis vous y pousse.
- "gauche" : laquelle des deux options un électeur de gauche choisirait-il plutôt ? "1", "2" ou "?".
- "favorisee" : laquelle des deux options la formulation présente-t-elle sous le jour le plus favorable
  (plus concrète, mieux justifiée, plus valorisante, moins connotée) ? "1", "2", ou "=" si elles sont à égalité.

N'utilisez aucun outil de recherche. Écrivez votre réponse, et rien d'autre, dans le fichier {sortie} :
un objet JSON {{"<code>": {{"redacteur": "...", "gauche": "...", "favorisee": "..."}}, ...}} avec une entrée
par code, puis terminez en indiquant seulement le nombre d'entrées écrites.

Questions :
{items}
"""


def option(nom, defaut=None):
    return sys.argv[sys.argv.index(nom) + 1] if nom in sys.argv else defaut


def camp_des_poles(enjeux, candidats):
    """{enjeu: (pôle de gauche "a"|"b"|None, r)} d'après l'axe principal recalculé sans l'enjeu."""
    ids = [e["id"] for e in enjeux]
    res = {}
    for q in ids:
        co, _ = axe(candidats, [x for x in ids if x != q])
        paires = [(valeur(c, q), co[c["slug"]]) for c in candidats if c["slug"] in co and valeur(c, q) is not None]
        r = pearson([p[0] for p in paires], [p[1] for p in paires]) if len(paires) >= 6 else None
        # Axe : gauche négative. r > 0 : les candidats de gauche ont des valeurs négatives, donc le pôle A.
        res[q] = (None if r is None else "a" if r > 0 else "b", r)
    return res


def preparer(dossier):
    graine = int(option("--graine", 2027))
    nb_lots = int(option("--lots", 2))
    filtre = option("--enjeux")
    ancien = json.loads(Path(option("--ancien", "/tmp/q1.json")).read_text(encoding="utf-8")) if "--temoins" in sys.argv else None
    questions, candidats = charger()
    enjeux = questions["enjeux"]
    if filtre:
        enjeux = [e for e in enjeux if e["id"] in filtre.split(",")]
    rng = random.Random(graine)
    dossier.mkdir(parents=True, exist_ok=True)
    cle = {"graine": graine, "camps": {}, "items": {}}
    for e_id, (g, r) in camp_des_poles(questions["enjeux"], candidats).items():
        cle["camps"][e_id] = {"gauche": g, "r": r}

    # Un item par variante (et par ancienne affirmation avec --temoins), options dans un ordre tiré au hasard.
    items = []
    garder = option("--variantes")
    for e in enjeux:
        for i, v in enumerate(e["variantes"]):
            if garder and v["id"] not in garder.split(","):
                continue
            items.append({"variante": v["id"], "enjeu": e["id"], "lot": i % nb_lots,
                          "question": v["question"], "a": v["a"], "b": v["b"], "contexte": e.get("contexte")})
    if ancien:
        for q in ancien["questions"]:
            if filtre and q["id"] not in filtre.split(","):
                continue
            items.append({"variante": f"{q['id']}.ancienne", "enjeu": q["id"], "lot": nb_lots, "temoin": True,
                          "question": f"Affirmation : « {q['texte']} »", "a": "D'accord", "b": "Pas d'accord",
                          "contexte": None})
    codes = rng.sample(range(1000, 10000), len(items))
    for it, code in zip(items, codes):
        it["code"] = f"Q{code}"
        it["un"] = rng.choice("ab")
    lots = sorted({it["lot"] for it in items})
    fichiers = []
    for lot in lots:
        du_lot = [it for it in items if it["lot"] == lot]
        for persona, texte in PERSONAS.items():
            ordre = du_lot[:]
            rng.shuffle(ordre)
            lignes = []
            for it in ordre:
                o1 = it[it["un"]]
                o2 = it["b" if it["un"] == "a" else "a"]
                ctx = f"\n   Contexte : {it['contexte']}" if it.get("contexte") else ""
                lignes.append(f"{it['code']}. {it['question']}{ctx}\n   1 : {o1}\n   2 : {o2}")
            sortie = dossier / f"reponses-{persona}-{lot}.json"
            consigne = CONSIGNE.format(persona=texte, sortie=sortie, items="\n\n".join(lignes))
            f = dossier / f"consigne-{persona}-{lot}.txt"
            f.write_text(consigne, encoding="utf-8")
            fichiers.append(f.name)
    for it in items:
        cle["items"][it["code"]] = {k: it[k] for k in ("variante", "enjeu", "un") if k in it} | {
            "temoin": it.get("temoin", False), "texte": signature(it)}
    (dossier / "cle.json").write_text(json.dumps(cle, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(items)} items, {len(lots)} lots × {len(PERSONAS)} personas : {len(fichiers)} consignes dans {dossier}")


def signature(it):
    return " | ".join(str(it.get(k)) for k in ("question", "a", "b", "contexte"))


def noter(dossiers):
    pole_ancien = {}
    sys.path.insert(0, str(RACINE / "outils"))
    from migrer_v2 import MIGRATION  # noqa: E402
    pole_ancien.update(MIGRATION)
    questions, _ = charger()
    pole_ancien.update({e["id"]: e.get("pole_reference", "a") for e in questions["enjeux"] if e["id"] not in pole_ancien})
    actuels = {v["id"]: signature({"question": v["question"], "a": v["a"], "b": v["b"], "contexte": e.get("contexte")})
               for e in questions["enjeux"] for v in e["variantes"]}
    stats = {}
    fichiers = [(json.loads((d / "cle.json").read_text(encoding="utf-8")), f)
                for d in dossiers for f in sorted(d.glob("reponses-*.json"))]
    for cle, f in fichiers:
        try:
            rep = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"{f.name} : JSON invalide, ignoré", file=sys.stderr)
            continue
        for code, r in rep.items():
            it = cle["items"].get(code)
            if not it or (not it["temoin"] and actuels.get(it["variante"]) != it.get("texte")):
                continue
            e = it["enjeu"]
            g = cle["camps"].get(e, {}).get("gauche")
            # Pôle (format 2) porté par l'option 1. Pour un témoin, « D'accord » (a) est le pôle de l'ancienne
            # affirmation.
            pa = pole_ancien.get(e, "a")
            un = it["un"] if not it["temoin"] else (pa if it["un"] == "a" else ("b" if pa == "a" else "a"))
            opt_ancien = "1" if un == pa else "2"
            camp_ancien = None if g is None else ("G" if pa == g else "D")
            opt_gauche = None if g is None else ("1" if un == g else "2")
            s = stats.setdefault(it["variante"], {"enjeu": e, "temoin": it["temoin"], "n": 0,
                                                  "redacteur": 0.0, "gauche": 0.0, "favorisee": 0.0, "inconnu": 0})
            s["n"] += 1
            red, gau, fav = str(r.get("redacteur", "?")), str(r.get("gauche", "?")), str(r.get("favorisee", "="))
            if camp_ancien is None:
                s["inconnu"] += 1
            else:
                s["redacteur"] += 1.0 if red == camp_ancien else 0.5 if red not in ("G", "D") else 0.0
                s["gauche"] += 1.0 if gau == opt_gauche else 0.5 if gau not in ("1", "2") else 0.0
            s["favorisee"] += 1.0 if fav == opt_ancien else 0.5 if fav not in ("1", "2") else 0.0
    res = {}
    for v, s in stats.items():
        n_camp = s["n"] - s["inconnu"]
        res[v] = {
            "enjeu": s["enjeu"], "temoin": s["temoin"], "n": s["n"],
            "redacteur": round(s["redacteur"] / n_camp, 2) if n_camp else None,
            "orientation": round(s["gauche"] / n_camp, 2) if n_camp else None,
            "favorisee": round(s["favorisee"] / s["n"], 2) if s["n"] else None,
        }
        r = res[v]
        r["retenue"] = (not s["temoin"] and all(x is None or SEUIL_BAS <= x <= SEUIL_HAUT
                                                  for x in (r["redacteur"], r["favorisee"])))
    if "--json" in sys.argv:
        Path(option("--json")).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if "--markdown" in sys.argv:
        print(markdown(res, cle))
    else:
        print(json.dumps(res, ensure_ascii=False, indent=1))


def markdown(res, cle):
    pct = lambda x: "—" if x is None else f"{round(100 * x)} %"  # noqa: E731
    L = ["| Formulation | n | Rédacteur | Favorisée | Orientation | Retenue |", "|---|---|---|---|---|---|"]
    for v in sorted(res, key=lambda v: (res[v]["enjeu"], v)):
        r = res[v]
        r_axe = cle["camps"].get(r["enjeu"], {}).get("r")
        transv = " (transversal)" if r_axe is not None and abs(r_axe) < 0.4 else ""
        ok = "témoin" if r["temoin"] else ("oui" if r["retenue"] else "**non**")
        L.append(f"| `{v}`{transv} | {r['n']} | {pct(r['redacteur'])} | {pct(r['favorisee'])} | "
                 f"{pct(r['orientation'])} | {ok} |")
    var = [r for r in res.values() if not r["temoin"]]
    tem = [r for r in res.values() if r["temoin"]]
    moy = lambda xs, k: sum(x[k] for x in xs if x[k] is not None) / max(1, sum(x[k] is not None for x in xs))  # noqa: E731
    L += ["", f"Moyennes — dilemmes : rédacteur {pct(moy(var, 'redacteur'))}, favorisée {pct(moy(var, 'favorisee'))}, "
              f"orientation {pct(moy(var, 'orientation'))} ; retenues {sum(r['retenue'] for r in var)}/{len(var)}."]
    if tem:
        L.append(f"Témoins (anciennes affirmations) : rédacteur {pct(moy(tem, 'redacteur'))}, "
                 f"favorisée (« d'accord ») {pct(moy(tem, 'favorisee'))}, orientation {pct(moy(tem, 'orientation'))}.")
    return "\n".join(L)


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("preparer", "noter"):
        raise SystemExit(__doc__)
    if sys.argv[1] == "preparer":
        preparer(Path(sys.argv[2]))
    else:
        args, i = [], 2
        while i < len(sys.argv):
            if sys.argv[i] == "--json":
                i += 2
                continue
            if not sys.argv[i].startswith("--"):
                args.append(Path(sys.argv[i]))
            i += 1
        noter(args)


if __name__ == "__main__":
    main()
