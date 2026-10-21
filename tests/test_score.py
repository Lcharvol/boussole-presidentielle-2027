"""Tests du calcul de proximité (scripts/score.py).

Lancement depuis la racine du dépôt : python3 -m unittest discover -s tests -v
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "skills" / "boussole-presidentielle-2027" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import score  # noqa: E402

QUESTIONS = {
    "themes": {"economie": "Économie", "ecologie": "Écologie"},
    "enjeux": [
        {"id": "eco_1", "theme": "economie"},
        {"id": "eco_2", "theme": "economie"},
        {"id": "eco_3", "theme": "economie"},
        {"id": "ecl_1", "theme": "ecologie"},
        {"id": "ecl_2", "theme": "ecologie"},
    ],
}


def candidat(slug, positions):
    """positions : {qid: (valeur, confiance)}"""
    return {
        "slug": slug,
        "nom": slug.capitalize(),
        "parti": "Parti " + slug,
        "statut": "déclaré",
        "positions": {q: {"valeur": v, "confiance": c} for q, (v, c) in positions.items()},
    }


def par_slug(res):
    return {r["slug"]: r for r in res["classement"] + res["donnees_insuffisantes"]}


class AucuneReponse(unittest.TestCase):
    def test_rien_ne_compte(self):
        c = candidat("alice", {"eco_1": (2, "programme")})
        res = score.calculer({"reponses": {"eco_1": None}}, QUESTIONS, [c])
        self.assertEqual(res["nb_reponses"], 0)
        self.assertEqual(res["classement"], [])
        self.assertEqual(res["peloton_de_tete"], [])
        r = par_slug(res)["alice"]
        self.assertIsNone(r["score"])
        self.assertIsNone(r["marge"])
        self.assertEqual(r["couverture"], 0)
        score.markdown(res, QUESTIONS)  # ne doit pas planter

    def test_question_inconnue(self):
        with self.assertRaises(SystemExit):
            score.calculer({"reponses": {"xyz": 1}}, QUESTIONS, [])

    def test_reponse_hors_echelle(self):
        with self.assertRaises(SystemExit):
            score.calculer({"reponses": {"eco_1": 3}}, QUESTIONS, [])


class UnSeulTheme(unittest.TestCase):
    def test_score_marge_et_themes(self):
        alice = candidat("alice", {"eco_1": (2, "programme"), "eco_2": (-2, "programme"),
                                   "eco_3": (2, "programme"), "ecl_1": (2, "programme")})
        res = score.calculer({"reponses": {"eco_1": 2, "eco_2": 2, "eco_3": 2}}, QUESTIONS, [alice])
        r = par_slug(res)["alice"]
        # accords 1, 0, 1 → 67 %
        self.assertEqual(r["score"], 67)
        self.assertEqual(list(r["par_theme"]), ["economie"])
        self.assertGreater(r["marge"], 0)
        self.assertLessEqual(r["marge"], 50)

    def test_accord_parfait_sans_marge(self):
        alice = candidat("alice", {"eco_1": (1, "programme"), "eco_2": (-1, "deduite")})
        res = score.calculer({"reponses": {"eco_1": 1, "eco_2": -1}}, QUESTIONS, [alice])
        r = par_slug(res)["alice"]
        self.assertEqual((r["score"], r["marge"]), (100, 0))


class CandidatSansDonnees(unittest.TestCase):
    def test_classe_a_part(self):
        alice = candidat("alice", {"eco_1": (2, "programme"), "eco_2": (1, "programme")})
        vide = candidat("vide", {"eco_1": (None, "programme")})
        res = score.calculer({"reponses": {"eco_1": 2, "eco_2": 1}}, QUESTIONS, [alice, vide])
        self.assertEqual([r["slug"] for r in res["classement"]], ["alice"])
        r = par_slug(res)["vide"]
        self.assertIsNone(r["score"])
        self.assertIsNone(r["marge"])
        self.assertEqual(r["couverture"], 0)
        self.assertIn("vide", score.markdown(res, QUESTIONS).lower())

    def test_retire_ignore_par_charger(self):
        _, candidats = score.charger()
        self.assertTrue(all(c.get("statut") != "retiré" for c in candidats))


class ExAequo(unittest.TestCase):
    def test_score_exact_avant_couverture(self):
        # Même score affiché (7 %) : le moins couvert passe devant parce que son score exact est plus haut.
        plein = candidat("plein", {"eco_1": (-2, "programme"), "eco_2": (-1, "programme"),
                                   "eco_3": (0, "programme"), "ecl_1": (0, "programme")})
        partiel = candidat("partiel", {"eco_1": (-1, "programme"), "eco_2": (-1, "programme"),
                                       "eco_3": (0, "programme")})
        user = {"reponses": {"eco_1": 2, "eco_2": 2, "eco_3": 2, "ecl_1": 2}}
        cl = score.calculer(user, QUESTIONS, [plein, partiel], tirages=0)["classement"]
        self.assertEqual([r["score"] for r in cl], [7, 7])
        self.assertEqual([r["slug"] for r in cl], ["partiel", "plein"])
        self.assertLess(cl[0]["couverture"], cl[1]["couverture"])

class Ponderation(unittest.TestCase):
    REPONSES = {"reponses": {"eco_1": 2, "eco_2": 2}}

    def score_de(self, conf_accord, conf_desaccord, importance=None):
        c = candidat("alice", {"eco_1": (2, conf_accord), "eco_2": (-2, conf_desaccord)})
        user = dict(self.REPONSES, importance=importance or {})
        return par_slug(score.calculer(user, QUESTIONS, [c]))["alice"]["score"]

    def test_constantes(self):
        self.assertEqual(score.POIDS_CONFIANCE, {"programme": 1.0, "declaration": 0.85, "deduite": 0.6})

    def test_meme_confiance_neutre(self):
        self.assertEqual(self.score_de("programme", "programme"), 50)
        self.assertEqual(self.score_de("deduite", "deduite"), 50)

    def test_position_deduite_pese_moins(self):
        # accord (1) en programme, désaccord (0) déduit : 1 / (1 + 0,6) = 62,5 %
        self.assertEqual(self.score_de("programme", "deduite"), round(100 / 1.6))
        # l'inverse : 0,6 / 1,6 = 37,5 %
        self.assertEqual(self.score_de("deduite", "programme"), round(60 / 1.6))
        # déclaration : 0,85 / 1,85
        self.assertEqual(self.score_de("declaration", "programme"), round(85 / 1.85))

    def test_confiance_inconnue_comme_deduite(self):
        self.assertEqual(self.score_de("programme", "rumeur"), self.score_de("programme", "deduite"))

    def test_multiplie_importance(self):
        # eco_1 en économie (importance 3, programme), ecl_1 en écologie (1, déduite)
        c = candidat("alice", {"eco_1": (2, "programme"), "ecl_1": (-2, "deduite")})
        user = {"reponses": {"eco_1": 2, "ecl_1": 2}, "importance": {"economie": 3}}
        r = par_slug(score.calculer(user, QUESTIONS, [c]))["alice"]
        self.assertEqual(r["score"], round(100 * 3 / (3 + 0.6)))
        self.assertEqual(r["par_confiance"], {"programme": 1, "declaration": 0, "deduite": 1})


class CorrectionDuHasard(unittest.TestCase):
    def test_accord_hasard(self):
        self.assertAlmostEqual(score.accord_hasard(0), 0.7)
        self.assertAlmostEqual(score.accord_hasard(1), 0.65)
        self.assertAlmostEqual(score.accord_hasard(-2), 0.5)

    def test_neutre_face_au_hasard(self):
        # Face à une réponse uniforme, l'accord corrigé moyen est nul quelle que soit la position :
        # une position nuancée n'est plus avantagée.
        for v in range(-2, 3):
            self.assertAlmostEqual(sum(score.accord_corrige(u, v) for u in range(-2, 3)), 0)
            self.assertAlmostEqual(score.accord_corrige(v, v), 1)

    def test_nuance_et_tranche(self):
        # Réponse « tout à fait d'accord » : le candidat à 2 l'emporte sur celui à 0, qui fait moins
        # bien que le hasard.
        user = {"reponses": {"eco_1": 2, "eco_2": 2}}
        tranche = candidat("tranche", {"eco_1": (2, "programme"), "eco_2": (2, "programme")})
        nuance = candidat("nuance", {"eco_1": (0, "programme"), "eco_2": (0, "programme")})
        r = par_slug(score.calculer(user, QUESTIONS, [tranche, nuance]))
        self.assertEqual(r["tranche"]["score"], 100)
        self.assertEqual(r["nuance"]["score"], round(50 + 50 * (0.5 - 0.7) / 0.3))

    def test_position_inconnue_rapproche_de_50(self):
        # Accord parfait sur 2 questions, position inconnue sur la 3e : score tiré vers 50 %.
        alice = candidat("alice", {"eco_1": (2, "programme"), "eco_2": (-2, "programme")})
        user = {"reponses": {"eco_1": 2, "eco_2": -2, "eco_3": 1}}
        r = par_slug(score.calculer(user, QUESTIONS, [alice]))["alice"]
        self.assertEqual(r["score"], round(50 + 50 * 2 / (2 + score.POIDS_INCONNUE)))
        self.assertEqual(r["couverture"], 0.67)

    def test_poids_inconnue_egalise_la_dispersion(self):
        # Écart-type relatif du score face au hasard : identique à 50 % et 100 % de couverture.
        def dispersion(f):
            return f ** 0.5 / (f + score.POIDS_INCONNUE * (1 - f))
        self.assertAlmostEqual(dispersion(0.5), dispersion(1.0))
        for f in (0.6, 0.7, 0.8, 0.9):
            self.assertLess(abs(dispersion(f) - 1), 0.02)


class Reproductibilite(unittest.TestCase):
    USER = {"reponses": {"eco_1": 2, "eco_2": -1, "eco_3": 0, "ecl_1": 1, "ecl_2": -2},
            "importance": {"ecologie": 2}}

    def candidats(self):
        return [
            candidat("alice", {"eco_1": (2, "programme"), "eco_2": (1, "declaration"),
                               "eco_3": (-2, "deduite"), "ecl_1": (1, "programme"), "ecl_2": (0, "programme")}),
            candidat("bob", {"eco_1": (-1, "programme"), "eco_2": (-1, "programme"),
                             "eco_3": (1, "declaration"), "ecl_1": (2, "deduite"), "ecl_2": (-2, "programme")}),
            candidat("chloe", {"eco_1": (-2, "programme"), "eco_2": (2, "programme"),
                               "eco_3": (2, "programme"), "ecl_1": (-2, "programme"), "ecl_2": (2, "programme")}),
        ]

    def test_meme_resultat(self):
        a = score.calculer(self.USER, QUESTIONS, self.candidats())
        b = score.calculer(self.USER, QUESTIONS, self.candidats())
        self.assertEqual(a, b)

    def test_ordre_des_reponses_sans_effet(self):
        inverse = {"reponses": dict(reversed(list(self.USER["reponses"].items()))),
                   "importance": self.USER["importance"]}
        self.assertEqual(score.calculer(self.USER, QUESTIONS, self.candidats()),
                         score.calculer(inverse, QUESTIONS, self.candidats()))

    def test_peloton_par_recouvrement(self):
        res = score.calculer(self.USER, QUESTIONS, self.candidats())
        premier = res["classement"][0]
        for r in res["classement"]:
            recouvre = r["score"] + r["marge"] >= premier["score"] - premier["marge"]
            self.assertEqual(r["nom"] in res["peloton_de_tete"], recouvre)
        self.assertIn(premier["nom"], res["peloton_de_tete"])

    def test_sans_tirages(self):
        # Utilisé par l'audit, qui n'a besoin que du classement : pas de marge, même classement.
        avec = score.calculer(self.USER, QUESTIONS, self.candidats())
        sans = score.calculer(self.USER, QUESTIONS, self.candidats(), tirages=0)
        self.assertEqual([r["nom"] for r in sans["classement"]], [r["nom"] for r in avec["classement"]])
        self.assertTrue(all(r["marge"] is None for r in sans["classement"]))
        self.assertEqual(sans["peloton_de_tete"], [sans["classement"][0]["nom"]])

    def test_entree_standard(self):
        """Le script lit les réponses sur l'entrée standard et donne deux fois la même sortie."""
        entree = json.dumps({"reponses": {"eco_retraite": 2, "imm_baisse": -2, "eur_ukraine": 1}})
        sorties = [
            subprocess.run([sys.executable, str(SCRIPTS / "score.py"), "--json"], input=entree,
                           capture_output=True, text=True, check=True).stdout
            for _ in range(2)
        ]
        self.assertEqual(sorties[0], sorties[1])
        res = json.loads(sorties[0])
        self.assertEqual(res["nb_reponses"], 3)
        self.assertIn("peloton_de_tete", res)
        self.assertTrue(all("marge" in r for r in res["classement"]))


if __name__ == "__main__":
    unittest.main()
