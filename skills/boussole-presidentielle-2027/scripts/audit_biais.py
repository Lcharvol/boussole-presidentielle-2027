#!/usr/bin/env python3
"""Audit de neutralité : le calcul, le tirage ou les formulations favorisent-ils mécaniquement un camp ?

Usage : python3 audit_biais.py [--profils 2000] [--profils-adaptatif 200] [--graine 2027] [--graines 1]
Sortie : un rapport Markdown sur la sortie standard (repris dans le résumé de la CI).

1. Axe principal. On calcule, à partir des seules positions des candidats, l'axe qui les sépare le plus
   (première composante principale). Aucun enjeu ni aucun candidat n'est étiqueté à la main ; le signe de
   l'axe est orienté pour l'affichage avec un seul repère (REPERE_GAUCHE), ce qui ne change ni les
   corrélations ni l'équilibre.
2. Pôles. Pour chaque enjeu, la corrélation entre la position des candidats (-2 = pôle A, +2 = pôle B) et
   leur place sur l'axe, calculé sans cet enjeu, dit quel pôle rapproche de quel côté. Le côté où chaque pôle
   est affiché étant tiré au hasard à chaque passage (tirage.py), une personne qui choisit plus souvent
   l'option de gauche (ou de droite) à l'écran n'est poussée vers aucun camp ; l'audit le vérifie.
3. Profils aléatoires. On tire des profils sans opinion (réponses uniformes, 10 % de « je passe ») et on
   les fait passer par le vrai déroulé : tirage.py choisit les enjeux (une graine par profil), score.py
   calcule. On compte combien de fois chaque candidat sort premier, dans chaque mode. Si le calcul et le
   tirage étaient neutres, chaque candidat classé aurait la même chance : 1 / (nombre de candidats
   classés). L'attendu est calculé profil par profil, seulement quand le candidat est classé (couverture
   suffisante), pour séparer l'effet de la couverture de celui du calcul.

Avec --graines N, la simulation est refaite avec N graines (graine, graine + 1, …), en parallèle sur les
processeurs disponibles. Les tableaux par candidat cumulent toutes les graines ; les ratios des tiers sont
donnés en moyenne et écart-type entre graines. À 2 000 profils, un ratio de tiers varie d'environ ±0,03
d'une graine à l'autre : un seul tirage ne permet pas de comparer deux versions des données.

Deux pentes résument l'équilibre sans dépendre du découpage en tiers : la régression pondérée (poids =
attendu) du log du ratio de chaque candidat classé sur sa coordonnée normalisée (« gauche → droite »), et sur
la valeur absolue de cette coordonnée (« extrêmes / milieu »). Une pente nulle = neutre ; l'incertitude est
l'erreur type due au nombre de profils (le log d'un ratio a une variance d'environ 1 / attendu).
"""
import math
import os
import random
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import calculer, charger  # noqa: E402  (même formule que le skill, sans la dupliquer)
from tirage import presenter, tirer  # noqa: E402  (même tirage que le skill)

PART_PASSE = 0.1
REPERE_GAUCHE = "jean-luc-melenchon"   # sert seulement à orienter le signe de l'axe
MIN_POSITIONS_AXE = 10                 # en dessous, un candidat n'est pas placé sur l'axe
SEUIL_CORRELATION = 0.4                # |r| en dessous : enjeu transversal
MIN_CANDIDATS_QUESTION = 6             # en dessous, le sens d'un enjeu n'est pas mesurable
RATIO_FORT, Z_FORT = 2.0, 3.0          # écart « net » : 2 fois l'attendu (ou moitié) et z ≥ 3
PART_CLASSE_MIN = 0.2                  # pentes et corrélations : candidats classés au moins 20 % du temps
TIRAGES_ECRAN = {"uniforme": (-2, -1, 0, 1, 2), "penche à gauche": (-2, -1, 0, 1), "penche à droite": (-1, 0, 1, 2)}


def option(nom, defaut):
    if nom in sys.argv:
        return int(sys.argv[sys.argv.index(nom) + 1])
    return defaut


def valeur(c, qid):
    return (c.get("positions", {}).get(qid) or {}).get("valeur")


def pearson(xs, ys):
    if len(xs) < 3:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else None


# --- Axe principal (composante principale, bibliothèque standard) ---------------------------

def axe(candidats, qids):
    """Renvoie (coordonnée par slug, part de variance expliquée) sur les enjeux qids."""
    base = [c for c in candidats if sum(valeur(c, q) is not None for q in qids) >= MIN_POSITIONS_AXE]
    moy = {}
    for q in qids:
        vals = [valeur(c, q) for c in base if valeur(c, q) is not None]
        moy[q] = statistics.fmean(vals) if vals else 0.0
    # Positions centrées par enjeu ; une position inconnue vaut la moyenne (0 une fois centrée).
    X = [[(valeur(c, q) - moy[q]) if valeur(c, q) is not None else 0.0 for q in qids] for c in base]
    n = len(qids)
    cov = [[sum(r[i] * r[j] for r in X) for j in range(n)] for i in range(n)]
    w = [1.0] * n
    for _ in range(500):  # itération de la puissance
        nw = [sum(cov[i][j] * w[j] for j in range(n)) for i in range(n)]
        norme = math.sqrt(sum(x * x for x in nw)) or 1.0
        nw = [x / norme for x in nw]
        if max(abs(a - b) for a, b in zip(nw, w)) < 1e-10:
            w = nw
            break
        w = nw
    propre = sum(w[i] * sum(cov[i][j] * w[j] for j in range(n)) for i in range(n))
    trace = sum(cov[i][i] for i in range(n)) or 1.0
    coords = {}
    for c in candidats:
        connues = [(i, valeur(c, q) - moy[q]) for i, q in enumerate(qids) if valeur(c, q) is not None]
        if len(connues) < MIN_POSITIONS_AXE:
            continue
        # Coordonnée par moindres carrés sur les seuls enjeux connus du candidat.
        coords[c["slug"]] = sum(x * w[i] for i, x in connues) / sum(w[i] ** 2 for i, _ in connues)
    if coords.get(REPERE_GAUCHE, 0) > 0:
        coords = {k: -v for k, v in coords.items()}
    return coords, propre / trace


# --- Profils aléatoires, passés par le vrai tirage ----------------------------------------

def repondre(q, rng, ecran):
    """Réponse d'un profil à une question tirée : choisie sur l'échelle affichée (-2 = option de gauche
    nettement), puis convertie en valeur pour score.py selon le côté où chaque pôle est affiché."""
    if rng.random() < PART_PASSE:
        return None
    s = rng.choice(ecran)
    return q["options"][s + 2]["valeur"]


def derouler(mode, graine, rng, ecran, questions, candidats):
    """Fait passer un profil sans opinion par le déroulé complet d'un mode ; renvoie ses réponses."""
    rep = {}
    while True:
        t = tirer(mode, graine, {"reponses": rep}, questions, candidats)
        if t["fin"]:
            return rep
        for q in t["questions"]:
            rep[q["enjeu"]] = repondre(q, rng, ecran)
        if mode != "adaptatif":
            return rep


def simuler(mode, n, graine, ecran, questions, candidats):
    stats = {c["slug"]: {"classe": 0, "premier": 0, "top3": 0, "att1": 0.0, "att3": 0.0, "var1": 0.0}
             for c in candidats}
    longueurs = []
    rng = random.Random(f"{graine}/{mode}/{ecran}")
    for i in range(n):
        rep = derouler(mode, graine * 100003 + i, rng, ecran, questions, candidats)
        longueurs.append(len(rep))
        classement = calculer({"reponses": rep}, questions, candidats, tirages=0)["classement"]
        k = len(classement)
        if not k:
            continue
        for rang, r in enumerate(classement):
            s = stats[r["slug"]]
            s["classe"] += 1
            s["att1"] += 1 / k
            s["var1"] += (1 / k) * (1 - 1 / k)
            s["att3"] += min(3, k) / k
            s["premier"] += rang == 0
            s["top3"] += rang < 3
    return stats, longueurs


def simuler_tache(tache):
    """Une simulation (mode, graine, écran) dans un processus séparé : les données sont relues sur place."""
    mode, n, graine, ecran = tache
    questions, candidats = charger()
    return simuler(mode, n, graine, ecran, questions, candidats)


def simuler_graines(taches, paralleles):
    """Lance les simulations, en parallèle si possible ; renvoie les résultats dans l'ordre des tâches."""
    if paralleles <= 1 or len(taches) == 1:
        return [simuler_tache(t) for t in taches]
    with ProcessPoolExecutor(max_workers=min(paralleles, len(taches))) as ex:
        return list(ex.map(simuler_tache, taches))


def cumuler(stats):
    """Additionne les compteurs par candidat de plusieurs graines."""
    total = {}
    for st in stats:
        for slug, s in st.items():
            t = total.setdefault(slug, dict.fromkeys(s, 0))
            for k, v in s.items():
                t[k] += v
    return total


def pente(stats, coords, f, part_min, n):
    """Pente pondérée (poids = attendu) du log du ratio des candidats classés sur f(coordonnée normalisée).

    Renvoie (pente, erreur type) ou None. La variance du log d'un ratio vaut environ 1 / attendu : le poids
    est donc aussi l'inverse de la variance, et l'erreur type vaut 1 / √(Σ poids × (x - x̄)²).
    """
    pts = [(coords[s], st["premier"], st["att1"]) for s, st in stats.items()
           if s in coords and st["classe"] >= part_min * n and st["premier"] > 0]
    if len(pts) < 3:
        return None
    et = statistics.pstdev([p[0] for p in pts]) or 1.0
    xs = [f(p[0] / et) for p in pts]
    ys = [math.log(p[1] / p[2]) for p in pts]
    ws = [p[2] for p in pts]
    W = sum(ws)
    mx = sum(w * x for w, x in zip(ws, xs)) / W
    my = sum(w * y for w, y in zip(ws, ys)) / W
    sxx = sum(w * (x - mx) ** 2 for w, x in zip(ws, xs))
    if not sxx:
        return None
    return sum(w * (x - mx) * (y - my) for w, x, y in zip(ws, xs, ys)) / sxx, 1 / math.sqrt(sxx)


def fmt_pente(p):
    return "—" if p is None else f"{p[0]:+.3f} ± {p[1]:.3f}"


def moyenne_et(valeurs):
    """« moyenne ± écart-type entre graines », ou la valeur seule avec une graine."""
    valeurs = [v for v in valeurs if v is not None]
    if not valeurs:
        return "—"
    if len(valeurs) == 1:
        return f"{valeurs[0]:.2f}"
    return f"{statistics.fmean(valeurs):.2f} ± {statistics.stdev(valeurs):.2f}"


def ratio(obs, att):
    return obs / att if att else None


def fmt_ratio(x):
    return "—" if x is None else f"{x:.2f}"


def par_camp(stats, camp):
    res = {}
    for slug, s in stats.items():
        a = res.setdefault(camp.get(slug, "non placé"), [0, 0.0])
        a[0] += s["premier"]
        a[1] += s["att1"]
    return res


# --- Rapport -----------------------------------------------------------------------------

def main():
    n = option("--profils", 2000)
    n_adapt = option("--profils-adaptatif", 200)
    graine = option("--graine", 2027)
    nb_graines = max(1, option("--graines", 1))
    graines = [graine + k for k in range(nb_graines)]
    questions, candidats = charger()
    qs = questions["enjeux"]
    nom = {c["slug"]: c["nom"] for c in candidats}
    tous = [q["id"] for q in qs]
    profils = {"complet": n, "rapide": n, "adaptatif": n_adapt}

    coords, variance = axe(candidats, tous)
    ordre = sorted(coords, key=coords.get)
    tiers = len(ordre) / 3
    camp = {s: ("gauche" if i < tiers else "centre" if i < 2 * tiers else "droite") for i, s in enumerate(ordre)}

    texte_graines = (f"graine {graine}" if nb_graines == 1 else
                     f"{nb_graines} graines, de {graines[0]} à {graines[-1]}, soit {n * nb_graines} et "
                     f"{n_adapt * nb_graines} profils au total")
    L = ["# Audit de neutralité", "",
         f"{len(candidats)} candidats actifs, {len(qs)} enjeux ; profils aléatoires : {n} en modes complet et "
         f"rapide, {n_adapt} en mode adaptatif par graine ({texte_graines}). Script : `scripts/audit_biais.py`.", ""]

    # 1. Axe
    L += ["## 1. Axe principal calculé à partir des données", "",
          f"L'axe qui sépare le plus les candidats explique {round(100 * variance)} % de la variance de leurs "
          f"positions. Il est calculé sans aucune étiquette ; seul son sens est orienté pour l'affichage "
          f"(repère : {nom.get(REPERE_GAUCHE, REPERE_GAUCHE)} du côté négatif). Les candidats ayant moins de "
          f"{MIN_POSITIONS_AXE} positions connues ne sont pas placés.", "",
          "| Candidat | Coordonnée | Tiers de l'axe | Positions connues |", "|---|---|---|---|"]
    for s in ordre:
        connues = sum(valeur(c, q) is not None for c in candidats if c["slug"] == s for q in tous)
        L.append(f"| {nom[s]} | {coords[s]:+.2f} | {camp[s]} | {connues}/{len(tous)} |")
    non_places = [c["nom"] for c in candidats if c["slug"] not in coords]
    if non_places:
        L += ["", "Non placés (trop peu de positions) : " + ", ".join(non_places) + "."]
    L += ["", "Les tiers « gauche », « centre » et « droite » désignent seulement la position sur cet axe "
              "calculé, découpé en trois parts égales.", ""]

    # 2. Pôles
    L += ["## 2. Pôles des enjeux", "",
          f"Pour chaque enjeu, corrélation entre la position des candidats (-2 = pôle A, +2 = pôle B) et leur "
          f"place sur l'axe (recalculé sans cet enjeu). r > {SEUIL_CORRELATION} : le pôle A rapproche du côté "
          f"gauche de l'axe ; r < -{SEUIL_CORRELATION} : le pôle B ; entre les deux : enjeu transversal. "
          "À l'écran, le côté de chaque pôle est tiré au hasard à chaque passage.", "",
          "| Enjeu | Pôle A | Pôle B | r | Pôle proche de la gauche de l'axe | Candidats |", "|---|---|---|---|---|---|"]
    sens = {}
    for q in qs:
        autres = [x for x in tous if x != q["id"]]
        co, _ = axe(candidats, autres)
        paires = [(valeur(c, q["id"]), co[c["slug"]]) for c in candidats
                  if c["slug"] in co and valeur(c, q["id"]) is not None]
        r = pearson([p[0] for p in paires], [p[1] for p in paires])
        if r is None or len(paires) < MIN_CANDIDATS_QUESTION:
            cote = "indéterminé (trop peu de positions)"
        else:
            cote = "A" if r >= SEUIL_CORRELATION else "B" if r <= -SEUIL_CORRELATION else "transversal"
        sens[q["id"]] = (r, cote)
        rs = "—" if r is None else f"{r:+.2f}"
        L.append(f"| `{q['id']}` | {q['pole_a']} | {q['pole_b']} | {rs} | {cote} | {len(paires)} |")
    nb = {k: sum(v[1] == k for v in sens.values()) for k in ("A", "B", "transversal")}
    L += ["", f"Pôle proche de la gauche de l'axe : A pour {nb['A']} enjeux, B pour {nb['B']}, "
              f"{nb['transversal']} transversaux, {len(qs) - sum(nb.values())} indéterminés. Ce décompte ne "
              "joue pas sur le résultat (le côté d'affichage est tiré au hasard) ; il garde les données lisibles.", ""]

    # Profils constants : toujours le pôle A, toujours le pôle B (information sur les données).
    L += ["Profils constants en mode complet (même réponse à tous les enjeux) — premier du classement :", "",
          "| Toujours « pôle A nettement » | Toujours « pôle B nettement » |", "|---|---|"]
    cells = []
    for v in (-2, 2):
        cl = calculer({"reponses": {q: v for q in tous}}, questions, candidats, tirages=0)["classement"]
        cells.append(f"{cl[0]['nom']} ({camp.get(cl[0]['slug'], 'non placé')}, {cl[0]['score']} %)" if cl else "—")
    L += ["| " + " | ".join(cells) + " |", ""]

    # 3. Profils aléatoires
    L += ["## 3. Profils aléatoires", "",
          f"Chaque profil répond au hasard (uniforme sur les cinq crans) et passe {round(100 * PART_PASSE)} % des "
          "questions, sans pondération des thèmes, en suivant le vrai tirage (une graine par profil : enjeux, "
          "formulations et côtés des pôles changent d'un profil à l'autre). Un tel profil n'a pas d'opinion : un "
          "calcul neutre devrait mettre chaque candidat classé premier avec la même probabilité. **Attendu** = "
          "somme, sur les profils où le candidat est classé, de 1 / (nombre de candidats classés) ; il tient donc "
          "compte de la couverture. **Ratio** = observé / attendu (1 = neutre).", ""]
    extremite = {c["slug"]: statistics.fmean([abs(valeur(c, q)) for q in tous if valeur(c, q) is not None] or [0])
                 for c in candidats}
    # Toutes les simulations d'un coup (modes × penchants × graines), en parallèle.
    cles, taches = [], []
    for m in ("complet", "rapide", "adaptatif"):
        for libelle, ecran in TIRAGES_ECRAN.items():
            if profils[m] and (libelle == "uniforme" or m == "complet"):
                for g in graines:
                    cles.append((m, libelle, g))
                    taches.append((m, profils[m], g, ecran))
    sim = dict(zip(cles, simuler_graines(taches, os.cpu_count() or 1)))

    membres = {k: [s for s in ordre if camp[s] == k] for k in ("gauche", "centre", "droite")}
    signalements, camps_mode, pentes_mode = {}, {}, {}
    for m in ("complet", "rapide", "adaptatif"):
        if not profils[m]:
            continue
        nm = profils[m] * nb_graines
        par_graine = [sim[(m, "uniforme", g)][0] for g in graines]
        st = cumuler(par_graine)
        longueurs = [x for g in graines for x in sim[(m, "uniforme", g)][1]]
        L += [f"### Mode {m} ({nm} profils, {statistics.fmean(longueurs):.1f} enjeux posés en moyenne, "
              f"de {min(longueurs)} à {max(longueurs)})", "",
              "| Candidat | Classé | 1er | Attendu | Ratio 1er | Top 3 | Ratio top 3 | Positions connues | Écart moyen à 0 |",
              "|---|---|---|---|---|---|---|---|---|"]
        lignes = []
        for c in candidats:
            s = st[c["slug"]]
            r1, r3 = ratio(s["premier"], s["att1"]), ratio(s["top3"], s["att3"])
            z = (s["premier"] - s["att1"]) / math.sqrt(s["var1"]) if s["var1"] else 0
            connues = sum(valeur(c, q) is not None for q in tous)
            lignes.append((c, s, r1, r3, z, connues))
        lignes.sort(key=lambda x: -(x[2] if x[2] is not None else -1))
        for c, s, r1, r3, z, connues in lignes:
            classe = f"{round(100 * s['classe'] / nm)} %" if s["classe"] >= nm / 200 or not s["classe"] else "< 1 %"
            L.append(f"| {c['nom']} | {classe} | {s['premier']} | {s['att1']:.0f} | "
                     f"{fmt_ratio(r1)} | {s['top3']} | {fmt_ratio(r3)} | {connues}/{len(tous)} | {extremite[c['slug']]:.2f} |")
            if s["classe"] == 0:
                signalements.setdefault(c["slug"], []).append(f"jamais classé en mode {m} (couverture insuffisante)")
            elif r1 is not None and abs(z) >= Z_FORT and (r1 >= RATIO_FORT or r1 <= 1 / RATIO_FORT):
                signalements.setdefault(c["slug"], []).append(
                    f"{'sur' if r1 > 1 else 'sous'}-représenté en mode {m} (ratio {r1:.2f}, z = {z:+.1f})")

        actifs = [x for x in lignes if x[1]["classe"] >= PART_CLASSE_MIN * nm and x[2] is not None]
        rr = [math.log(max(x[2], 0.01)) for x in actifs]
        r_ext = pearson([extremite[x[0]["slug"]] for x in actifs], rr)
        r_nb = pearson([x[5] for x in actifs], rr)
        L += ["", f"Corrélation entre le ratio (log) et : l'écart moyen à 0 des positions r = "
                  f"{'—' if r_ext is None else f'{r_ext:+.2f}'} ; le nombre de positions connues r = "
                  f"{'—' if r_nb is None else f'{r_nb:+.2f}'} ({len(actifs)} candidats classés au moins "
                  f"{round(100 * PART_CLASSE_MIN)} % du temps).", ""]

        pentes = {}
        for cle, f in (("gd", lambda x: x), ("ext", abs)):
            pentes[cle] = pente(st, coords, f, PART_CLASSE_MIN, nm)
            if nb_graines > 1:
                une = [pente(x, coords, f, PART_CLASSE_MIN, profils[m]) for x in par_graine]
                pentes[cle + "_graines"] = [p[0] for p in une if p]
        pentes_mode[m] = pentes
        dispersion = (lambda cle: f" (écart-type entre graines {statistics.stdev(pentes[cle + '_graines']):.3f})"
                      if nb_graines > 1 and len(pentes[cle + "_graines"]) > 1 else "")
        L += [f"Pente gauche → droite : {fmt_pente(pentes['gd'])}{dispersion('gd')} ; pente extrêmes / milieu : "
              f"{fmt_pente(pentes['ext'])}{dispersion('ext')}. Régression pondérée par l'attendu du log du ratio "
              "des mêmes candidats sur leur coordonnée normalisée (écart-type 1), ou sur sa valeur absolue. Une "
              "pente positive avantage la droite de l'axe, ou ses extrémités ; 0 = neutre ; ± = erreur type.", ""]

        pc = par_camp(st, camp)
        camps_mode[m] = [par_camp(x, camp) for x in par_graine]
        entete = "| Tiers de l'axe | 1er observé | Attendu | Ratio |"
        if nb_graines > 1:
            entete += " Ratio par graine (moyenne ± écart-type) |"
        L += [entete + " Classés / candidats du tiers | Jamais classés (moins de 1 % des profils) |",
              "|---" * (entete.count("|") + 1) + "|"]
        for k in ("gauche", "centre", "droite", "non placé"):
            if k not in pc:
                continue
            o, a = pc[k]
            ligne = f"| {k} | {o} | {a:.0f} | {fmt_ratio(ratio(o, a))} |"
            if nb_graines > 1:
                ligne += f" {moyenne_et([ratio(*x[k]) for x in camps_mode[m] if k in x])} |"
            liste = membres.get(k, [s for s in nom if s not in coords])
            jamais = [nom[s] for s in liste if st[s]["classe"] < nm / 100]
            ligne += f" {len(liste) - len(jamais)} / {len(liste)} | {', '.join(jamais) or '—'} |"
            L.append(ligne)
        L.append("")

    # Effet d'un penchant pour un côté de l'écran, à opinions égales par ailleurs.
    L += ["### Penchant pour un côté de l'écran", "",
          "Mêmes profils, mais qui choisissent plus souvent l'option affichée à gauche (crans tirés de -2 à 1) ou "
          "à droite (de -1 à 2). C'est l'équivalent, pour les dilemmes, de la tendance à répondre « d'accord » : "
          "comme le côté de chaque pôle est tiré au hasard, ce penchant ne devrait favoriser aucun camp. Part des "
          "premières places par tiers de l'axe, en mode complet :", "",
          "| Profil | gauche | centre | droite |", "|---|---|---|---|"]
    parts = {}
    for libelle in TIRAGES_ECRAN:
        st = cumuler([sim[("complet", libelle, g)][0] for g in graines])
        pc = {k: v[0] for k, v in par_camp(st, camp).items()}
        total = sum(pc.values()) or 1
        parts[libelle] = {k: 100 * pc.get(k, 0) / total for k in ("gauche", "centre", "droite")}
        L.append(f"| {libelle} | " + " | ".join(f"{round(v)} %" for v in parts[libelle].values()) + " |")
    ecart = {p: (parts[p]["droite"] - parts[p]["gauche"]) - (parts["uniforme"]["droite"] - parts["uniforme"]["gauche"])
             for p in ("penche à gauche", "penche à droite")}
    L += ["", "Écart droite - gauche des premières places, comparé au profil uniforme : "
              + " ; ".join(f"{p} {v:+.0f} points" for p, v in ecart.items())
              + ". (Un penchant resserre aussi les réponses autour du milieu, ce qui profite un peu au centre "
                "dans les deux cas : cet effet ne dépend pas du côté.)", ""]

    # 4. Synthèse
    L += ["## 4. Synthèse", ""]
    if signalements:
        L += ["Candidats nettement sur- ou sous-représentés (ratio ≥ 2 ou ≤ 0,5 et z ≥ 3), ou jamais classés :", ""]
        for s, msgs in signalements.items():
            L.append(f"- {nom[s]} : " + " ; ".join(msgs))
        L.append("")
    else:
        L += ["Aucun candidat nettement sur- ou sous-représenté.", ""]
    L += ["Ratios des tiers de l'axe (premières places observées / attendues"
          + (", moyenne ± écart-type entre graines" if nb_graines > 1 else "") + ") et pentes (± erreur type) :", "",
          "| Mode | gauche | centre | droite | Pente gauche → droite | Pente extrêmes / milieu |",
          "|---|---|---|---|---|---|"]
    for m, pcs in camps_mode.items():
        L.append(f"| {m} | " + " | ".join(moyenne_et([ratio(*pc[k]) for pc in pcs if k in pc])
                                         for k in ("gauche", "centre", "droite"))
                 + f" | {fmt_pente(pentes_mode[m]['gd'])} | {fmt_pente(pentes_mode[m]['ext'])} |")
    L += ["", "Les tiers comptent aussi les candidats jamais classés (voir les tableaux par mode) : le ratio d'un "
              "tiers repose parfois sur peu de candidats en compétition. Les pentes ne dépendent pas de ce découpage.", ""]

    # 5. Priorités de complétion
    L += ["## 5. Fiches à compléter en priorité", "",
          "Candidats sous 50 % de positions connues, du moins couvert au plus couvert :", ""]
    for c in sorted(candidats, key=lambda c: sum(valeur(c, q) is not None for q in tous)):
        connues = sum(valeur(c, q) is not None for q in tous)
        if connues < len(tous) / 2:
            L.append(f"- {c['nom']} : {connues}/{len(tous)}")
    peu = sorted(qs, key=lambda q: sum(valeur(c, q["id"]) is not None for c in candidats))[:8]
    L += ["", "Enjeux dont on connaît le moins de positions : " + ", ".join(
        f"`{q['id']}` ({sum(valeur(c, q['id']) is not None for c in candidats)})" for q in peu) + ".", ""]
    print("\n".join(L))


if __name__ == "__main__":
    main()
