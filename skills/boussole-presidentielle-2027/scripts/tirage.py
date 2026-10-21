#!/usr/bin/env python3
"""Tire les questions à poser : quels enjeux, dans quel ordre, avec quelle formulation, quel pôle à gauche.

Usage (les réponses déjà données arrivent sur l'entrée standard, rien n'est écrit sur le disque) :
    python3 tirage.py --mode rapide --graine hasard                  # premières questions, graine tirée
    python3 tirage.py --mode rapide --graine 4821                    # même tirage qu'un passage précédent
    python3 tirage.py --mode adaptatif --graine 4821 <<'FIN'          # questions suivantes
    {"reponses": {"eco_retraite": 1, "sec_cannabis": null}, "importance": {"economie": 2}}
    FIN

Modes :
- rapide    : RAPIDE enjeux, au moins un par thème, tirés au hasard en favorisant ceux qui départagent le plus
              les candidats (pouvoir de départage, voir pouvoir()) ;
- adaptatif : le même socle, puis des lots de LOT enjeux choisis pour départager les candidats encore proches
              de la personne (ceux dont la marge recouvre celle du premier), jusqu'à ce que le premier se
              détache, que les enjeux restants ne départagent plus ces candidats, ou que MAX_ADAPTATIF enjeux
              aient été posés ;
- complet   : tous les enjeux.
La sortie est un objet JSON : {"mode", "graine", "posees", "fin", "raison", "questions": [...]}. Les questions
déjà posées (présentes dans "reponses", même à null) ne sont jamais reposées : on peut ainsi passer d'un mode à
l'autre sans recommencer. "fin" vaut true quand il n'y a plus rien à poser dans ce mode.

Chaque question indique l'enjeu, la formulation tirée parmi ses variantes, le pôle affiché à gauche et, pour
chacune des cinq réponses dans l'ordre d'affichage (de gauche à droite), la valeur à transmettre à score.py
(-2 = pôle A nettement, 2 = pôle B nettement). Tout dépend de la graine : avec la même graine et les mêmes
réponses, le tirage est identique (tests, reprise d'un questionnaire). Une graine différente à chaque passage
fait varier les enjeux, leur ordre, les formulations et le côté des pôles.
"""
import json
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import calculer, charger  # noqa: E402

RAPIDE = 12          # enjeux du mode rapide, et socle du mode adaptatif
LOT = 4              # enjeux ajoutés à chaque étape du mode adaptatif
MAX_ADAPTATIF = 32   # au-delà, le mode adaptatif s'arrête
GAIN_MIN = 0.4       # en dessous, un enjeu ne départage plus les candidats en tête (écart-type pondéré)
PLANCHER_POIDS = 0.1  # chaque enjeu garde une chance d'être tiré, même s'il départage peu
TIRAGES_ADAPTATIF = 300  # tirages du bootstrap pour estimer le peloton de tête (le score final en fait 1 000)
MODES = ("rapide", "adaptatif", "complet")


def pouvoir(enjeu_id, candidats):
    """Pouvoir de départage : écart-type des positions × part des candidats dont la position est connue."""
    vals = [(c.get("positions", {}).get(enjeu_id) or {}).get("valeur") for c in candidats]
    vals = [v for v in vals if v is not None]
    if len(vals) < 2 or not candidats:
        return 0.0
    return statistics.pstdev(vals) * len(vals) / len(candidats)


def variantes_utilisables(enjeu):
    """Les variantes validées par un humain si l'enjeu en a, sinon toutes."""
    validees = [v for v in enjeu["variantes"] if v.get("validee")]
    return validees or enjeu["variantes"]


def presenter(enjeu, themes, graine):
    """Formulation et côté des pôles, tirés à partir de la graine et de l'enjeu seulement (stables d'un appel à l'autre)."""
    rng = random.Random(f"{graine}/{enjeu['id']}")
    v = rng.choice(variantes_utilisables(enjeu))
    gauche = rng.choice("ab")
    droite = "b" if gauche == "a" else "a"
    signe = -1 if gauche == "a" else 1   # réponse « pôle de gauche nettement » = -2 si A est à gauche
    textes = {"a": v["a"], "b": v["b"]}
    libelles = [f"{textes[gauche]} — nettement", f"Plutôt : {textes[gauche]}", "Entre les deux",
                f"Plutôt : {textes[droite]}", f"{textes[droite]} — nettement"]
    return {
        "enjeu": enjeu["id"],
        "theme": enjeu["theme"],
        "theme_libelle": themes[enjeu["theme"]],
        "variante": v["id"],
        "question": v["question"],
        "contexte": enjeu.get("contexte"),
        "gauche": {"pole": gauche, "texte": textes[gauche]},
        "droite": {"pole": droite, "texte": textes[droite]},
        "options": [{"libelle": lib, "valeur": signe * s} for lib, s in zip(libelles, (2, 1, 0, -1, -2))],
    }


def tirage_pondere(rng, ids, poids, k):
    """k éléments distincts, tirés sans remise avec une probabilité proportionnelle à leur poids."""
    ids, choisis = list(ids), []
    while ids and len(choisis) < k:
        total = sum(poids[i] for i in ids)
        x, cumul = rng.random() * total, 0.0
        for i in ids:
            cumul += poids[i]
            if x <= cumul:
                break
        choisis.append(i)
        ids.remove(i)
    return choisis


def ordonner(rng, enjeux, theme_de):
    """Ordre aléatoire, en évitant deux enjeux du même thème à la suite quand c'est possible."""
    reste = list(enjeux)
    rng.shuffle(reste)
    ordre = []
    while reste:
        precedent = theme_de[ordre[-1]] if ordre else None
        restant = {}
        for e in reste:
            restant[theme_de[e]] = restant.get(theme_de[e], 0) + 1
        # Parmi les thèmes différents du précédent, celui qui a le plus d'enjeux restants (sinon on
        # risquerait de devoir les enchaîner à la fin) ; à égalité, l'ordre tiré au hasard.
        possibles = [k for k, e in enumerate(reste) if theme_de[e] != precedent] or [0]
        i = max(possibles, key=lambda k: (restant[theme_de[reste[k]]], -k))
        ordre.append(reste.pop(i))
    return ordre


def socle(questions, candidats, graine):
    """Les RAPIDE enjeux du mode rapide (et du socle adaptatif), dans leur ordre de passage."""
    rng = random.Random(f"{graine}/socle")
    enjeux = questions["enjeux"]
    theme_de = {e["id"]: e["theme"] for e in enjeux}
    poids = {e["id"]: pouvoir(e["id"], candidats) + PLANCHER_POIDS for e in enjeux}
    choisis = []
    for theme in questions["themes"]:
        du_theme = [e["id"] for e in enjeux if e["theme"] == theme]
        choisis += tirage_pondere(rng, du_theme, poids, 1)
    # Compléments : au plus deux enjeux par thème, pour que le mode rapide reste varié.
    while len(choisis) < min(RAPIDE, len(enjeux)):
        pris = {t: sum(theme_de[c] == t for c in choisis) for t in questions["themes"]}
        dispo = [e["id"] for e in enjeux if e["id"] not in choisis and pris[e["theme"]] < 2]
        dispo = dispo or [e["id"] for e in enjeux if e["id"] not in choisis]
        choisis += tirage_pondere(rng, dispo, poids, 1)
    return ordonner(rng, choisis, theme_de)


def departage(enjeu_id, peloton, importance, theme):
    """Gain d'un enjeu pour départager les candidats du peloton : écart-type de leurs positions connues,
    pondéré par la part de positions connues et par l'importance du thème."""
    vals = [(c.get("positions", {}).get(enjeu_id) or {}).get("valeur") for c in peloton]
    vals = [v for v in vals if v is not None]
    if len(vals) < 2:
        return 0.0
    return statistics.pstdev(vals) * len(vals) / len(peloton) * float(importance.get(theme, 1)) ** 0.5


def suivantes(questions, candidats, user, graine, tirages=TIRAGES_ADAPTATIF):
    """Prochain lot du mode adaptatif : (enjeux, raison d'arrêt ou None)."""
    posees = set(user.get("reponses", {}))
    reste_socle = [e for e in socle(questions, candidats, graine) if e not in posees]
    if reste_socle:
        return reste_socle, None
    if len(posees) >= MAX_ADAPTATIF:
        return [], f"{MAX_ADAPTATIF} enjeux posés, le maximum du mode adaptatif"
    res = calculer(user, questions, candidats, tirages=tirages, graine=graine)
    noms = set(res["peloton_de_tete"])
    peloton = [c for c in candidats if c["nom"] in noms]
    if len(peloton) < 2:
        return [], "le premier candidat se détache : sa marge ne recouvre plus celle d'aucun autre"
    theme_de = {e["id"]: e["theme"] for e in questions["enjeux"]}
    importance = user.get("importance", {})
    rng = random.Random(f"{graine}/adaptatif/{len(posees)}")
    gains = {e["id"]: departage(e["id"], peloton, importance, e["theme"]) + rng.random() * 1e-6
             for e in questions["enjeux"] if e["id"] not in posees}
    utiles = sorted((i for i in gains if gains[i] >= GAIN_MIN), key=lambda i: -gains[i])
    if not utiles:
        return [], "les enjeux restants ne départagent plus les candidats en tête"
    # Au plus un enjeu par thème dans un lot, pour garder l'alternance des thèmes.
    lot, themes_pris = [], set()
    for i in utiles:
        if theme_de[i] not in themes_pris:
            lot.append(i)
            themes_pris.add(theme_de[i])
        if len(lot) == min(LOT, MAX_ADAPTATIF - len(posees)):
            break
    return ordonner(rng, lot, theme_de), None


def tirer(mode, graine, user=None, questions=None, candidats=None):
    if mode not in MODES:
        raise SystemExit(f"Mode inconnu : {mode} (attendu : {', '.join(MODES)})")
    if questions is None:
        questions, candidats = charger()
    user = user or {}
    par_id = {e["id"]: e for e in questions["enjeux"]}
    inconnus = sorted(set(user.get("reponses", {})) - set(par_id))
    if inconnus:
        raise SystemExit(f"Identifiants d'enjeu inconnus : {', '.join(inconnus)}")
    posees = set(user.get("reponses", {}))
    raison = None
    if mode == "rapide":
        ids = [e for e in socle(questions, candidats, graine) if e not in posees]
    elif mode == "complet":
        rng = random.Random(f"{graine}/complet")
        theme_de = {e["id"]: e["theme"] for e in questions["enjeux"]}
        ids = ordonner(rng, [e for e in par_id if e not in posees], theme_de)
    else:
        ids, raison = suivantes(questions, candidats, user, graine)
    if not ids and raison is None:
        raison = f"tous les enjeux du mode {mode} ont été posés"
    return {
        "mode": mode,
        "graine": graine,
        "posees": len(posees),
        "fin": not ids,
        "raison": raison,
        "questions": [presenter(par_id[i], questions["themes"], graine) for i in ids],
    }


def main():
    mode = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else None
    if mode is None or "--graine" not in sys.argv:
        raise SystemExit(__doc__)
    graine = sys.argv[sys.argv.index("--graine") + 1]
    # « hasard » : une nouvelle graine, renvoyée dans la sortie pour être réutilisée aux appels suivants.
    graine = random.SystemRandom().randrange(1, 10 ** 6) if graine == "hasard" else int(graine)
    user = {}
    if not sys.stdin.isatty():
        brut = sys.stdin.read()
        if brut.strip():
            user = json.loads(brut)
    print(json.dumps(tirer(mode, graine, user), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
