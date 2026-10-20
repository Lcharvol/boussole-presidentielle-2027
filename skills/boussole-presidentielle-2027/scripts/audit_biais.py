#!/usr/bin/env python3
"""Audit de neutralité : le calcul ou les formulations favorisent-ils mécaniquement un camp ?

Usage : python3 audit_biais.py [--profils 2000] [--graine 2027]
Sortie : un rapport Markdown sur la sortie standard (repris dans le résumé de la CI).

1. Profils aléatoires. On tire des profils sans opinion (réponses uniformes de -2 à 2, 10 % de
   « je passe »), on les passe dans le calcul de score.py et on compte combien de fois chaque
   candidat sort premier ou dans les trois premiers, en mode long et en mode rapide. Si le calcul
   était neutre, chaque candidat classé aurait la même chance : 1 / (nombre de candidats classés).
   L'attendu est calculé profil par profil, seulement quand le candidat est classé (couverture
   suffisante), pour séparer l'effet de la couverture de celui du calcul.
2. Axe principal. On calcule, à partir des seules positions des candidats, l'axe qui les
   sépare le plus (première composante principale). Aucune question ni aucun candidat n'est
   étiqueté à la main ; le signe de l'axe est orienté pour l'affichage avec un seul repère
   (REPERE_GAUCHE), ce qui ne change ni les corrélations ni l'équilibre.
3. Formulations. Pour chaque question, on mesure la corrélation entre la position des candidats
   et leur place sur l'axe, calculé sans cette question (pour ne pas la comparer à elle-même) :
   « d'accord » correspond-il plutôt à un pôle ou à l'autre ? Si la plupart des affirmations
   penchent du même côté, une personne qui répond souvent « d'accord » est poussée vers ce pôle.
"""
import math
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from score import calculer, charger  # noqa: E402  (même formule que le skill, sans la dupliquer)

PART_PASSE = 0.1
REPERE_GAUCHE = "jean-luc-melenchon"   # sert seulement à orienter le signe de l'axe
MIN_POSITIONS_AXE = 10                 # en dessous, un candidat n'est pas placé sur l'axe
SEUIL_CORRELATION = 0.4                # |r| en dessous : question transversale
MIN_CANDIDATS_QUESTION = 6             # en dessous, le sens d'une question n'est pas mesurable
RATIO_FORT, Z_FORT = 2.0, 3.0          # écart « net » : 2 fois l'attendu (ou moitié) et z ≥ 3
MODES = {"long": {"rapide", "moyen", "long"}, "moyen": {"rapide", "moyen"}, "rapide": {"rapide"}}


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
    """Renvoie (coordonnée par slug, part de variance expliquée) sur les questions qids."""
    base = [c for c in candidats if sum(valeur(c, q) is not None for q in qids) >= MIN_POSITIONS_AXE]
    moy = {}
    for q in qids:
        vals = [valeur(c, q) for c in base if valeur(c, q) is not None]
        moy[q] = statistics.fmean(vals) if vals else 0.0
    # Positions centrées par question ; une position inconnue vaut la moyenne (0 une fois centrée).
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
        # Coordonnée par moindres carrés sur les seules questions connues du candidat.
        coords[c["slug"]] = sum(x * w[i] for i, x in connues) / sum(w[i] ** 2 for i, _ in connues)
    if coords.get(REPERE_GAUCHE, 0) > 0:
        coords = {k: -v for k, v in coords.items()}
    return coords, propre / trace


# --- Profils aléatoires ------------------------------------------------------------------

def simuler(questions, candidats, qids, n, rng, tirage):
    stats = {c["slug"]: {"classe": 0, "premier": 0, "top3": 0, "att1": 0.0, "att3": 0.0, "var1": 0.0}
             for c in candidats}
    for _ in range(n):
        rep = {q: (None if rng.random() < PART_PASSE else rng.choice(tirage)) for q in qids}
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
    return stats


def ratio(obs, att):
    return obs / att if att else None


def fmt_ratio(x):
    return "—" if x is None else f"{x:.2f}"


# --- Rapport -----------------------------------------------------------------------------

def main():
    n = option("--profils", 2000)
    graine = option("--graine", 2027)
    questions, candidats = charger()
    qs = questions["questions"]
    nom = {c["slug"]: c["nom"] for c in candidats}
    qids_mode = {m: [q["id"] for q in qs if q["niveau"] in niv] for m, niv in MODES.items()}
    tous = qids_mode["long"]

    coords, variance = axe(candidats, tous)
    ordre = sorted(coords, key=coords.get)
    tiers = len(ordre) / 3
    camp = {s: ("gauche" if i < tiers else "centre" if i < 2 * tiers else "droite") for i, s in enumerate(ordre)}

    L = ["# Audit de neutralité", "",
         f"{len(candidats)} candidats actifs, {len(qs)} questions, {n} profils aléatoires par mode "
         f"(graine {graine}). Script : `scripts/audit_biais.py`.", ""]

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

    # 2. Formulations
    L += ["## 2. Sens des formulations", "",
          f"Pour chaque affirmation, corrélation entre la position des candidats et leur place sur l'axe "
          f"(recalculé sans cette question). r < -{SEUIL_CORRELATION} : « d'accord » rapproche du pôle "
          f"gauche ; r > {SEUIL_CORRELATION} : du pôle droit ; entre les deux : question transversale.", "",
          "| Question | Mode | r | « D'accord » rapproche de | Candidats |", "|---|---|---|---|---|"]
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
            cote = "gauche" if r <= -SEUIL_CORRELATION else "droite" if r >= SEUIL_CORRELATION else "transversale"
        sens[q["id"]] = (r, cote)
        rs = "—" if r is None else f"{r:+.2f}"
        L.append(f"| `{q['id']}` {q['texte']} | {q['niveau']} | {rs} | {cote} | {len(paires)} |")

    L += ["", "**Équilibre global**", "", "| Mode | Questions | Pôle gauche | Pôle droit | Transversales | Indéterminées | Somme des r |",
          "|---|---|---|---|---|---|---|"]
    desequilibre = {}
    for m, ids in qids_mode.items():
        g = sum(sens[i][1] == "gauche" for i in ids)
        d = sum(sens[i][1] == "droite" for i in ids)
        t = sum(sens[i][1] == "transversale" for i in ids)
        somme = sum(sens[i][0] or 0 for i in ids if not sens[i][1].startswith("indéterminé"))
        desequilibre[m] = (g, d)
        L.append(f"| {m} | {len(ids)} | {g} | {d} | {t} | {len(ids) - g - d - t} | {somme:+.2f} |")
    L.append("")

    # Profils de réponse constants : test direct de l'effet d'acquiescement.
    L += ["Profils constants (même réponse à toutes les questions) — premier du classement :", "",
          "| Mode | Toujours « tout à fait d'accord » | Toujours « plutôt d'accord » | Toujours « plutôt pas d'accord » | Toujours « pas du tout d'accord » |",
          "|---|---|---|---|---|"]
    for m, ids in qids_mode.items():
        cells = []
        for v in (2, 1, -1, -2):
            cl = calculer({"reponses": {q: v for q in ids}}, questions, candidats, tirages=0)["classement"]
            if cl:
                s = cl[0]["slug"]
                cells.append(f"{cl[0]['nom']} ({camp.get(s, 'non placé')}, {cl[0]['score']} %)")
            else:
                cells.append("—")
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("")

    # 3. Profils aléatoires
    L += ["## 3. Profils aléatoires", "",
          f"Chaque profil répond au hasard (de -2 à 2, uniforme) et passe {round(100 * PART_PASSE)} % des questions, "
          "sans pondération des thèmes. Un tel profil n'a pas d'opinion : un calcul neutre devrait mettre chaque "
          "candidat classé premier avec la même probabilité. **Attendu** = somme, sur les profils où le candidat "
          "est classé, de 1 / (nombre de candidats classés) ; il tient donc compte de la couverture. "
          "**Ratio** = observé / attendu (1 = neutre).", ""]
    rng = random.Random(graine)
    extremite = {c["slug"]: statistics.fmean([abs(valeur(c, q)) for q in tous if valeur(c, q) is not None] or [0])
                 for c in candidats}
    signalements = {}
    camps_mode = {}
    for m in ("long", "rapide"):
        ids = qids_mode[m]
        st = simuler(questions, candidats, ids, n, rng, (-2, -1, 0, 1, 2))
        L += [f"### Mode {m} ({len(ids)} questions)", "",
              "| Candidat | Classé | 1er | Attendu | Ratio 1er | Top 3 | Ratio top 3 | Positions connues (mode) | Écart moyen à 0 |",
              "|---|---|---|---|---|---|---|---|---|"]
        lignes = []
        for c in candidats:
            s = st[c["slug"]]
            r1, r3 = ratio(s["premier"], s["att1"]), ratio(s["top3"], s["att3"])
            z = (s["premier"] - s["att1"]) / math.sqrt(s["var1"]) if s["var1"] else 0
            connues = sum(valeur(c, q) is not None for q in ids)
            lignes.append((c, s, r1, r3, z, connues))
        lignes.sort(key=lambda x: -(x[2] if x[2] is not None else -1))
        for c, s, r1, r3, z, connues in lignes:
            classe = f"{round(100 * s['classe'] / n)} %" if s["classe"] >= n / 200 or not s["classe"] else "< 1 %"
            L.append(f"| {c['nom']} | {classe} | {s['premier']} | {s['att1']:.0f} | "
                     f"{fmt_ratio(r1)} | {s['top3']} | {fmt_ratio(r3)} | {connues}/{len(ids)} | {extremite[c['slug']]:.2f} |")
            if s["classe"] == 0:
                signalements.setdefault(c["slug"], []).append(f"jamais classé en mode {m} (couverture insuffisante)")
            elif r1 is not None and abs(z) >= Z_FORT and (r1 >= RATIO_FORT or r1 <= 1 / RATIO_FORT):
                signalements.setdefault(c["slug"], []).append(
                    f"{'sur' if r1 > 1 else 'sous'}-représenté en mode {m} (ratio {r1:.2f}, z = {z:+.1f})")

        # Facteurs explicatifs, sur les candidats classés au moins 20 % du temps.
        actifs = [x for x in lignes if x[1]["classe"] >= 0.2 * n and x[2] is not None]
        rr = [math.log(max(x[2], 0.01)) for x in actifs]
        r_ext = pearson([extremite[x[0]["slug"]] for x in actifs], rr)
        r_nb = pearson([x[5] for x in actifs], rr)
        L += ["", f"Corrélation entre le ratio (log) et : l'écart moyen à 0 des positions r = "
                  f"{'—' if r_ext is None else f'{r_ext:+.2f}'} ; le nombre de positions connues r = "
                  f"{'—' if r_nb is None else f'{r_nb:+.2f}'} ({len(actifs)} candidats classés au moins 20 % du temps).", ""]

        # Agrégat par tiers de l'axe.
        par_camp = {}
        for c, s, *_ in lignes:
            k = camp.get(c["slug"], "non placé")
            a = par_camp.setdefault(k, [0, 0.0])
            a[0] += s["premier"]
            a[1] += s["att1"]
        camps_mode[m] = par_camp
        L += ["| Tiers de l'axe | 1er observé | Attendu | Ratio |", "|---|---|---|---|"]
        for k in ("gauche", "centre", "droite", "non placé"):
            if k in par_camp:
                o, a = par_camp[k]
                L.append(f"| {k} | {o} | {a:.0f} | {fmt_ratio(ratio(o, a))} |")
        L.append("")

    # Effet d'une tendance à acquiescer, à opinions égales par ailleurs.
    L += ["### Tendance à acquiescer", "",
          "Mêmes profils aléatoires, mais tirés de -1 à 2 (penchant pour « d'accord ») ou de -2 à 1 "
          "(penchant pour « pas d'accord »). Part des premières places par tiers de l'axe :", "",
          "| Mode | Profil | gauche | centre | droite |", "|---|---|---|---|---|"]
    parts = {}
    for m in ("long", "rapide"):
        for libelle, tirage in (("neutre (-2 à 2)", None), ("acquiesçant (-1 à 2)", (-1, 0, 1, 2)),
                                ("contestataire (-2 à 1)", (-2, -1, 0, 1))):
            if tirage is None:
                pc = {k: v[0] for k, v in camps_mode[m].items()}
            else:
                st = simuler(questions, candidats, qids_mode[m], n, rng, tirage)
                pc = {}
                for c in candidats:
                    k = camp.get(c["slug"], "non placé")
                    pc[k] = pc.get(k, 0) + st[c["slug"]]["premier"]
            total = sum(pc.values()) or 1
            parts[(m, libelle.split()[0])] = {k: 100 * pc.get(k, 0) / total for k in ("gauche", "centre", "droite")}
            L.append(f"| {m} | {libelle} | " + " | ".join(
                f"{round(v)} %" for v in parts[(m, libelle.split()[0])].values()) + " |")
    L.append("")

    # 4. Synthèse
    L += ["## 4. Synthèse", ""]
    if signalements:
        L += ["Candidats nettement sur- ou sous-représentés (ratio ≥ 2 ou ≤ 0,5 et z ≥ 3), ou jamais classés :", ""]
        for s, msgs in signalements.items():
            L.append(f"- {nom[s]} : " + " ; ".join(msgs))
        L.append("")
    else:
        L += ["Aucun candidat nettement sur- ou sous-représenté.", ""]

    def formulations(m):
        g, d = desequilibre[m]
        pa, pn = parts[(m, "acquiesçant")], parts[(m, "neutre")]
        effet = (pa["droite"] - pa["gauche"]) - (pn["droite"] - pn["gauche"])
        return (f"en mode {m}, {g} affirmation(s) orientent « d'accord » vers le pôle gauche et {d} vers le pôle "
                f"droit ; répondre « d'accord » plus souvent déplace l'écart droite - gauche des premières places de "
                f"{effet:+.0f} points")

    L += ["Causes probables :", "",
          "- **Couverture inégale des fiches.** Un candidat dont on connaît peu de positions est exclu du "
          "classement principal (moins de 50 % des questions répondues) : il ne peut jamais sortir premier. "
          "Quand il est classé, son score repose sur peu de questions, donc varie davantage d'un profil à "
          "l'autre, ce qui le place plus souvent tout en haut comme tout en bas. En mode rapide, avec 8 "
          "questions, une ou deux positions manquantes suffisent à faire basculer un candidat.",
          "- **Positions nuancées.** Avec un accord égal à 1 - |écart| / 4, une position à 0 est en moyenne "
          "plus proche d'une réponse quelconque qu'une position à ±2 : face à des réponses au hasard, les "
          "candidats aux positions modérées sont avantagés, quel que soit leur camp. Cet effet pèse surtout "
          "sur les personnes qui répondent souvent « neutre » ou sans opinion tranchée.",
          f"- **Sens des formulations.** {formulations('long').capitalize()} ; {formulations('rapide')}. "
          "Une série d'affirmations orientées dans le même sens favorise le pôle correspondant chez les "
          "personnes qui répondent souvent « d'accord ».", ""]

    # 5. Priorités de complétion
    rapides = qids_mode["rapide"]
    L += ["## 5. Fiches à compléter en priorité", "",
          "Candidats sous 50 % de positions connues, du moins couvert au plus couvert, avec les questions du "
          "mode rapide qui leur manquent (ce sont elles qui les excluent ou les font basculer en mode rapide) :", ""]
    for c in sorted(candidats, key=lambda c: sum(valeur(c, q) is not None for q in tous)):
        connues = sum(valeur(c, q) is not None for q in tous)
        if connues >= len(tous) / 2:
            continue
        manque = [f"`{q}`" for q in rapides if valeur(c, q) is None]
        L.append(f"- {c['nom']} : {connues}/{len(tous)}" + (" ; mode rapide : " + ", ".join(manque) if manque else ""))
    peu = sorted(qs, key=lambda q: sum(valeur(c, q["id"]) is not None for c in candidats))[:8]
    L += ["", "Questions dont on connaît le moins de positions : " + ", ".join(
        f"`{q['id']}` ({sum(valeur(c, q['id']) is not None for c in candidats)})" for q in peu) + ".", ""]
    print("\n".join(L))


if __name__ == "__main__":
    main()
