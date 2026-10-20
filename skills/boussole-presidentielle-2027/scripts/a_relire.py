#!/usr/bin/env python3
"""Liste, en Markdown, les positions qui n'ont pas encore été relues par un humain (relu: false).

Usage :
    python3 a_relire.py                          # toutes les positions à relire
    python3 a_relire.py --candidat marine-le-pen # un seul candidat (slug)
    python3 a_relire.py --limite 50              # les 50 plus prioritaires
    python3 a_relire.py > a-relire.md

Les positions sont classées par priorité :
  1. valeur extrême (2 ou -2) ET confiance « deduite » ;
  2. valeur extrême (2 ou -2) ;
  3. confiance « deduite » ;
  4. les autres.
Dans chaque groupe, les positions sans citation passent en premier.

Pour relire une position : ouvrir la source, vérifier que la citation y figure mot pour mot,
qu'elle justifie la valeur au regard du texte exact de l'affirmation, et que le résumé est
neutre. Si tout est juste, passer "relu" à true dans la fiche ; sinon corriger (relu reste false).
Les positions nulles ne sont pas listées.
"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
GROUPES = {
    1: "Valeur extrême et position déduite",
    2: "Valeur extrême (2 ou -2)",
    3: "Position déduite",
    4: "Autres positions",
}


def priorite(p):
    extreme = abs(p["valeur"]) == 2
    deduite = p.get("confiance") == "deduite"
    if extreme and deduite:
        return 1
    if extreme:
        return 2
    if deduite:
        return 3
    return 4


def main():
    candidat = sys.argv[sys.argv.index("--candidat") + 1] if "--candidat" in sys.argv else None
    limite = int(sys.argv[sys.argv.index("--limite") + 1]) if "--limite" in sys.argv else None
    questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    textes = {q["id"]: q["texte"] for q in questions["questions"]}
    ordre = {qid: i for i, qid in enumerate(textes)}

    items, total, relues = [], 0, 0
    for f in sorted((DATA / "candidats").glob("*.json")):
        if candidat and f.stem != candidat:
            continue
        c = json.loads(f.read_text(encoding="utf-8"))
        for qid, p in c.get("positions", {}).items():
            if p.get("valeur") is None:
                continue
            total += 1
            if p.get("relu") is True:
                relues += 1
                continue
            sans_cit = not (p.get("citation") or "").strip()
            items.append((priorite(p), not sans_cit, f.stem, ordre.get(qid, 99), c.get("nom", f.stem), qid, p))
    if candidat and not total:
        sys.exit(f"Aucune position renseignée pour « {candidat} » (vérifier le slug).")

    items.sort(key=lambda x: x[:4])
    reste = len(items)
    if limite is not None:
        items = items[:limite]

    print("# Positions à relire\n")
    print(f"{reste} positions sur {total} restent à relire ({relues} déjà relues)"
          + (f" ; {len(items)} affichées." if limite is not None else "."))
    print("\nPour chaque position : ouvrir la source, vérifier que la citation y figure mot pour mot "
          "et qu'elle justifie la valeur au regard du texte exact de l'affirmation, puis passer "
          "`relu` à `true` dans la fiche.")
    groupe = None
    for prio, _, slug, _, nom, qid, p in items:
        if prio != groupe:
            groupe = prio
            n = sum(1 for it in items if it[0] == prio)
            print(f"\n## {prio}. {GROUPES[prio]} ({n})\n")
        v = p["valeur"]
        citation = (p.get("citation") or "").strip()
        print(f"- [ ] **{nom}** — `{qid}` : valeur **{v:+d}**, confiance *{p.get('confiance')}* "
              f"(`data/candidats/{slug}.json`)")
        print(f"  - Affirmation : {textes.get(qid, '?')}")
        print(f"  - Résumé : {p.get('resume', '')}")
        print(f"  - Citation : {'« ' + citation + ' »' if citation else '**aucune citation**'}")
        print(f"  - Source : <{p.get('source')}> ({p.get('date_source', '?')})")


if __name__ == "__main__":
    main()
