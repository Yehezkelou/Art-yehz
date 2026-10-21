**Comment un `.ecproj` stocke les chemins des médias (en une ligne) :**  
Un fichier `.ecproj` est un document JSON dont le dictionnaire racine `"items"` associe chaque identifiant d'élément à un objet `{"id": …, "name": …, "kind": {"type": "Folder" | "Comp" | "Solid" | "Footage", …}}` : les modèles de [`~/videos/modeles/`](file:///home/Yehezou/videos/modeles/pixel-art.ecproj#L24-L43) ne contiennent que des éléments `Folder`, `Comp` et `Solid`, et tout média importé (`file.import`, sérialisé par [`ItemKind::Footage(Footage)`](file:///home/Yehezou/videos/logiciel/effectcraft/crates/project/src/lib.rs#L1113-L1296)) stocke son chemin dans `"items"[id]["kind"]["path"]` (ainsi que dans `"items"[id]["kind"]["sequence"]` pour une séquence d'images et `"items"[id]["proxy"]["footage"]["path"]` pour une doublure/proxy).

*Preuve — extrait de [`~/videos/modeles/pixel-art.ecproj`](file:///home/Yehezou/videos/modeles/pixel-art.ecproj#L24-L43) et structure `Footage` de [`crates/project/src/lib.rs`](file:///home/Yehezou/videos/logiciel/effectcraft/crates/project/src/lib.rs#L1113-L1296) :*
```json
  "items": {
    "1": { "id": 1, "name": "bible.ecproj", "label": "Yellow", "comment": "", "parent": null, "kind": { "type": "Folder" } },
    "2": { "id": 2, "name": "Planche bible", "label": "Sandstone", "comment": "", "parent": 1, "kind": { "type": "Comp", "width": 1080, "height": 1920, "...": "..." } },
    "42": { "id": 42, "name": "saut.wav", "label": "None", "comment": "", "parent": null, "kind": { "type": "Footage", "path": "assets/sons/saut.wav", "kind": "Audio", "sequence": [] } }
  }
```

---

### `~/videos/outils/verifier_licences.py`

```python
#!/usr/bin/env python3
"""Vérifie le manifeste des licences de la bibliothèque d'assets ico-vid (§ 5.2–5.3 du plan 2.3).

Usage :
    python3 -I ~/videos/outils/verifier_licences.py
    python3 -I ~/videos/outils/verifier_licences.py --manifeste ~/videos/assets/manifeste.toml --racine ~/videos/assets
    python3 -I ~/videos/outils/verifier_licences.py --projet ~/videos/modeles/pixel-art.ecproj

Règles vérifiées :
1. Chaque fichier présent sous `assets/` (--racine) possède une entrée `[[asset]]` dans le manifeste (sauf le manifeste lui-même).
2. Chaque entrée du manifeste pointe vers un fichier réellement existant sous `assets/`.
3. Licences autorisées : `propriétaire`, `CC0`, `CC-BY-4.0`, `CC-BY-3.0`, `itch-commercial`, `OFL-1.1`.
4. Toute licence vide, inconnue, non commerciale (`NC`) ou sans modification (`ND`) est refusée.
5. Si la licence est `CC-BY` (`CC-BY-4.0` / `CC-BY-3.0`), le champ `credit` doit être non vide.
6. `vendable = true` n'est autorisé que si `licence = "propriétaire"`.
7. Avec `--projet x.ecproj`, extrait les chemins des médias (`items[*].kind.path`, `sequence`, `proxy`)
   du projet EffectCraft et refuse tout média situé sous `assets/` qui n'a pas d'entrée valide dans le manifeste.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
from typing import Any, Sequence

HOME = os.path.expanduser("~")
RACINE_DEFAUT = os.path.join(HOME, "videos", "assets")
NOMS_MANIFESTE = ("manifeste.toml", "manifest.toml")

LICENCES_AUTORISEES = frozenset({
    "propriétaire",
    "CC0",
    "CC-BY-4.0",
    "CC-BY-3.0",
    "itch-commercial",
    "OFL-1.1",
})


def normaliser_relpath(chemin: str) -> str:
    """Normalise un chemin relatif en séparateurs POSIX sans `./` initial."""
    remplace = chemin.strip().replace("\\", "/")
    norm = os.path.normpath(remplace).replace("\\", "/")
    if norm == ".":
        return ""
    return norm.lstrip("/") if not remplace.startswith("/") else norm


def _est_dans_racine(chemin_abs: str, racine_abs: str) -> bool:
    """Indique si `chemin_abs` se trouve strictement à l'intérieur de `racine_abs`."""
    try:
        commun = os.path.commonpath([chemin_abs, racine_abs])
    except ValueError:
        return False
    return commun == racine_abs and chemin_abs != racine_abs


def lister_fichiers_assets(racine_abs: str, manifeste_abs: str) -> list[str]:
    """Liste tous les fichiers sous `racine_abs` (chemins relatifs POSIX), hors manifeste et fichiers cachés."""
    fichiers: list[str] = []
    for dossier, sous_dossiers, noms in os.walk(racine_abs):
        sous_dossiers[:] = sorted(d for d in sous_dossiers if not d.startswith("."))
        for nom in sorted(noms):
            if nom.startswith("."):
                continue
            complet = os.path.realpath(os.path.join(dossier, nom))
            if complet == manifeste_abs:
                continue
            if os.path.samefile(dossier, racine_abs) and nom in NOMS_MANIFESTE:
                continue
            rel = os.path.relpath(complet, racine_abs).replace(os.sep, "/")
            fichiers.append(rel)
    return sorted(fichiers)


def valider_licence(fichier: str, licence: Any, credit: Any, vendable: Any) -> list[str]:
    """Vérifie la licence, le crédit obligatoire CC-BY et le drapeau `vendable` d'une entrée."""
    erreurs: list[str] = []

    if not isinstance(licence, str) or not licence.strip():
        erreurs.append(f"[{fichier}] licence vide ou manquante.")
        lic = ""
    else:
        lic = licence.strip()
        upper = lic.upper()
        if lic not in LICENCES_AUTORISEES:
            if "NC" in upper.split("-") or "NON COMMERCIAL" in upper or "-NC" in upper:
                erreurs.append(
                    f"[{fichier}] licence non commerciale (NC) refusée : « {lic} » "
                    "(interdite sur une chaîne monétisée)."
                )
            elif "ND" in upper.split("-") or "-ND" in upper:
                erreurs.append(
                    f"[{fichier}] licence sans modification (ND) refusée : « {lic} » "
                    "(interdite car les assets sont recadrés/animés)."
                )
            else:
                autorisees = ", ".join(sorted(LICENCES_AUTORISEES))
                erreurs.append(
                    f"[{fichier}] licence inconnue ou non autorisée : « {lic} » "
                    f"(licences autorisées : {autorisees})."
                )

    # Règle CC-BY -> credit non vide
    if lic.startswith("CC-BY"):
        if not isinstance(credit, str) or not credit.strip():
            erreurs.append(
                f"[{fichier}] crédit obligatoire manquant ou vide pour la licence « {lic} » "
                "(renseigner le champ `credit`)."
            )

    # Règle vendable = true seulement si propriétaire
    if vendable is not None:
        if not isinstance(vendable, bool):
            erreurs.append(f"[{fichier}] le champ `vendable` doit être un booléen (true/false).")
        elif vendable and lic != "propriétaire":
            erreurs.append(
                f"[{fichier}] `vendable = true` refusé pour la licence « {lic or 'vide'} » : "
                "seuls les assets sous licence « propriétaire » peuvent être vendus en boutique."
            )

    return erreurs


def extraire_medias_ecproj(projet_path: str) -> list[str]:
    """Extrait tous les chemins de médias stockés dans un fichier `.ecproj` d'EffectCraft.

    Dans le schéma EffectCraft (`crates/project/src/lib.rs`), la clé racine `"items"` associe chaque
    identifiant à un `Item` dont `"kind"` porte `"type": "Footage"` avec `"path": "..."` et
    optionnellement `"sequence": ["...", ...]`, ainsi qu'un éventuel `"proxy": {"footage": {"path": "..."}}`.
    """
    with open(projet_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("le fichier .ecproj ne contient pas un objet JSON à la racine")

    items_raw = data.get("items", {})
    if isinstance(items_raw, dict):
        items_iter = items_raw.values()
    elif isinstance(items_raw, list):
        items_iter = items_raw
    else:
        items_iter = []

    chemins: list[str] = []

    def _ajouter_footage(bloc: dict[str, Any]) -> None:
        p = bloc.get("path")
        if isinstance(p, str) and p.strip():
            chemins.append(p.strip())
        seq = bloc.get("sequence")
        if isinstance(seq, list):
            for elem in seq:
                if isinstance(elem, str) and elem.strip():
                    chemins.append(elem.strip())

    for item in items_iter:
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        if isinstance(kind, dict):
            if kind.get("type") == "Footage" or "path" in kind or "sequence" in kind:
                _ajouter_footage(kind)
            # Au cas où un calque embarquerait une source directe avec chemin
            layers = kind.get("layers")
            if isinstance(layers, list):
                for layer in layers:
                    if isinstance(layer, dict) and isinstance(layer.get("source"), dict):
                        _ajouter_footage(layer["source"])
        elif "path" in item:
            _ajouter_footage(item)

        proxy = item.get("proxy")
        if isinstance(proxy, dict):
             proxy_footage = proxy.get("footage")
            if isinstance(proxy_footage, dict):
                _ajouter_footage(proxy_footage)

    return chemins


def resoudre_media_sous_racine(media_path: str, projet_path: str, racine_abs: str) -> str | None:
    """Si `media_path` (issu de `projet_path`) pointe dans `racine_abs`, renvoie son chemin relatif POSIX."""
    brut = os.path.expanduser(media_path.strip()).replace("\\", "/")
    if not brut:
        return None

    dossier_projet = os.path.dirname(os.path.realpath(os.path.abspath(projet_path)))
    parent_racine = os.path.dirname(racine_abs)

    candidats: list[str] = []
    if os.path.isabs(brut):
        candidats.append(os.path.realpath(os.path.abspath(brut)))
    else:
        # 1. Résolution native EffectCraft (doc_path::resolve) : relatif au dossier du .ecproj
        candidats.append(os.path.realpath(os.path.abspath(os.path.join(dossier_projet, brut))))
        # 2. Relatif au dossier parent de `assets/` (ex. chemin "assets/sons/bip.wav")
        candidats.append(os.path.realpath(os.path.abspath(os.path.join(parent_racine, brut))))
        # 3. Si le chemin commence déjà par le nom du dossier racine (ex. "assets/...")
        nom_racine = os.path.basename(racine_abs)
        if brut.startswith(nom_racine + "/"):
             sous_chemin = brut[len(nom_racine) + 1 :]
            candidats.append(os.path.realpath(os.path.abspath(os.path.join(racine_abs, sous_chemin))))
        # 4. Relatif au répertoire courant
        candidats.append(os.path.realpath(os.path.abspath(brut)))

    for cand in candidats:
        if _est_dans_racine(cand, racine_abs):
            return os.path.relpath(cand, racine_abs).replace(os.sep, "/")
    return None


def verifier_licences(
    racine: str = RACINE_DEFAUT,
    manifeste: str | None = None,
    projets: Sequence[str] | None = None,
) -> tuple[bool, list[str], list[str]]:
    """Exécute tous les contrôles de licences et retourne `(succes, erreurs, credits_cc_by)`."""
    erreurs: list[str] = []
    credits: list[str] = []

    racine_exp = os.path.expanduser(racine)
    if not os.path.isdir(racine_exp):
        return False, [f"Le dossier racine des assets est introuvable : {racine_exp}"], []
    racine_abs = os.path.realpath(os.path.abspath(racine_exp))

    if manifeste:
        manifeste_exp = os.path.expanduser(manifeste)
    else:
        candidat_fr = os.path.join(racine_abs, "manifeste.toml")
        candidat_en = os.path.join(racine_abs, "manifest.toml")
        if os.path.isfile(candidat_fr) or not os.path.isfile(candidat_en):
            manifeste_exp = candidat_fr
        else:
            manifeste_exp = candidat_en

    if not os.path.isfile(manifeste_exp):
        return False, [f"Le fichier manifeste est introuvable : {manifeste_exp}"], []
    manifeste_abs = os.path.realpath(os.path.abspath(manifeste_exp))

    try:
        with open(manifeste_abs, "rb") as f:
            doc = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        return False, [f"Erreur de syntaxe TOML dans le manifeste ({manifeste_exp}) : {exc}"], []
    except OSError as exc:
        return False, [f"Impossible de lire le manifeste ({manifeste_exp}) : {exc}"], []

    entrees_brutes = doc.get("asset", doc.get("assets", []))
    if not isinstance(entrees_brutes, list):
        return False, ["Le manifeste doit contenir une liste de tables `[[asset]]`."], []

    entrees_par_fichier: dict[str, dict[str, Any]] = {}
    entrees_valides: set[str] = set()

    for idx, entree in enumerate(entrees_brutes, start=1):
        if not isinstance(entree, dict):
            erreurs.append(f"[entrée #{idx}] format invalide (table TOML attendue).")
            continue

         brut_fichier = entree.get("fichier")
        if not isinstance(brut_fichier, str) or not brut_fichier.strip():
            erreurs.append(f"[entrée #{idx}] champ `fichier` manquant ou vide.")
            continue

        rel = normaliser_relpath(brut_fichier)
        if not rel or rel.startswith("../") or rel == ".." or os.path.isabs(brut_fichier.strip()):
            erreurs.append(
                f"[{brut_fichier}] chemin invalide (doit être un chemin relatif à l'intérieur de assets/)."
            )
            continue

        if rel in entrees_par_fichier:
            erreurs.append(f"[{rel}] entrée en doublon dans le manifeste.")
            continue
        entrees_par_fichier[rel] = entree

        cible_abs = os.path.realpath(os.path.abspath(os.path.join(racine_abs, rel)))
        err_entree: list[str] = []
        if not _est_dans_racine(cible_abs, racine_abs) or not os.path.isfile(cible_abs):
            err_entree.append(
                f"[{rel}] fichier introuvable sur le disque (attendu : {os.path.join(racine_abs, rel)})."
            )

        err_entree.extend(
            valider_licence(
                rel,
                entree.get("licence"),
                entree.get("credit"),
                entree.get("vendable"),
            )
        )

        if err_entree:
            erreurs.extend(err_entree)
        else:
            entrees_valides.add(rel)
            lic = str(entree.get("licence", "")).strip()
            if lic.startswith("CC-BY"):
                credits.append(str(entree["credit"]).strip())

    # Chaque fichier sous assets/ (hors manifeste) doit avoir une entrée dans le manifeste
    fichiers_disque = lister_fichiers_assets(racine_abs, manifeste_abs)
    for rel_disque in fichiers_disque:
        if rel_disque not in entrees_par_fichier:
            erreurs.append(f"[{rel_disque}] fichier présent sous assets/ sans entrée dans le manifeste.")

    # Contrôle optionnel d'un ou plusieurs projets .ecproj
    for proj in projets or ():
        proj_exp = os.path.expanduser(proj)
        if not os.path.isfile(proj_exp):
            erreurs.append(f"[projet {proj}] fichier .ecproj introuvable : {proj_exp}")
            continue
        try:
            medias = extraire_medias_ecproj(proj_exp)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            erreurs.append(f"[projet {proj}] lecture impossible du projet .ecproj : {exc}")
            continue

        for m in medias:
            rel_media = resoudre_media_sous_racine(m, proj_exp, racine_abs)
            if rel_media is None:
                continue
            if rel_media not in entrees_par_fichier:
                erreurs.append(
                    f"[projet { os.path.basename(proj_exp) }] média « {rel_media} » "
                    f"(extrait de « {m} ») utilisé sous assets/ sans entrée dans le manifeste."
                )
            elif rel_media not in entrees_valides:
                erreurs.append(
                    f"[projet { os.path.basename(proj_exp) }] média « {rel_media} » "
                    "utilisé sous assets/ avec une entrée de manifeste invalide."
                )

    return len(erreurs) == 0, erreurs, credits


def construire_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Vérifie les licences des assets ico-vid (manifeste.toml, dossier assets/ et projets .ecproj)."
    )
    parser.add_argument(
        "--racine",
        default=RACINE_DEFAUT,
        help=f"Dossier racine des assets (défaut : {RACINE_DEFAUT})",
    )
    parser.add_argument(
        "--manifeste",
        default=None,
        help="Chemin du fichier manifeste TOML (défaut : <racine>/manifeste.toml)",
    )
    parser.add_argument(
        "--projet",
        action="append",
        default=[],
        metavar="X.ECPROJ",
        help="Projet EffectCraft (.ecproj) dont les médias sous assets/ doivent figurer au manifeste",
    )
    parser.add_argument(
        "--credits",
        action="store_true",
        help="Affiche les lignes de crédits obligatoires (CC-BY) pour la description YouTube",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = construire_parser()
    args = parser.parse_args(argv)

    ok, erreurs, credits = verifier_licences(
        racine=args.racine,
        manifeste=args.manifeste,
        projets=args.projet,
    )

    if not ok:
        print(f"ROUGE — Échec du contrôle des licences ({len(erreurs)} erreur(s)) :", file=sys.stderr)
        for err in erreurs:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("VERT — Toutes les licences et entrées du manifeste sont conformes.")
    if args.credits and credits:
        print("Crédits : " + " · ".join(credits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

### `~/videos/outils/test_verifier_licences.py`

```python
#!/usr/bin/env python3
"""Tests unitaires pour ~/videos/outils/verifier_licences.py."""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verifier_licences as vl  # noqa: E402


class TestVerifierLicences(unittest.TestCase):
    """Vérifie l'ensemble des règles des § 5.2–5.3 du plan 2.3."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.racine = os.path.join(self.tmp.name, "assets")
        os.makedirs(self.racine, exist_ok=True)
        self.manifeste = os.path.join(self.racine, "manifeste.toml")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _creer_fichier(self, relpath: str, contenu: bytes = b"PNG") -> str:
        complet = os.path.join(self.racine, relpath)
        os.makedirs(os.path.dirname(complet), exist_ok=True)
        with open(complet, "wb") as f:
            f.write(contenu)
        return complet

    def _ecrire_manifeste(self, toml_texte: str) -> None:
        with open(self.manifeste, "w", encoding="utf-8") as f:
            f.write(toml_texte)

    def _creer_ecproj(self, nom: str, items: dict) -> str:
        chemin = os.path.join(self.tmp.name, nom)
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        doc = {
            "savedBy": "0.13.0",
            "schema": 2,
            "settings": {"bit_depth": "Bpc8", "audio_sample_rate": 48000},
            "items": items,
            "next_id": 100,
        }
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        return chemin

    def test_manifeste_valide_toutes_licences_autorisees(self) -> None:
        """Un manifeste couvrant tous les fichiers avec les 6 licences autorisées retourne 0 (vert)."""
        fichiers = [
            "decors/village-jour/3-milieu.png",
            "objets/kenney-coffre.png",
            "sons/ambiance.wav",
            "sons/fanfare.wav",
            "decors/tuiles-itch.png",
            "polices/PressStart2P.ttf",
        ]
        for f in fichiers:
            self._creer_fichier(f)

        self._ecrire_manifeste(
            """
[[asset]]
fichier  = "decors/village-jour/3-milieu.png"
source   = "dessin maison"
auteur   = "@yehz"
licence  = "propriétaire"
date     = 2026-10-24
vendable = true
credit   = ""

[[asset]]
fichier  = "objets/kenney-coffre.png"
source   = "Kenney"
auteur   = "Kenney"
licence  = "CC0"
date     = 2026-10-24
vendable = false
credit   = ""

[[asset]]
fichier  = "sons/ambiance.wav"
source   = "Freesound"
auteur   = "Alice"
licence  = "CC-BY-4.0"
date     = 2026-10-24
vendable = false
credit   = "Ambiance par Alice (CC-BY 4.0)"

[[asset]]
fichier  = "sons/fanfare.wav"
source   = "OpenGameArt"
auteur   = "Bob"
licence  = "CC-BY-3.0"
date     = 2026-10-24
vendable = false
credit   = "Fanfare par Bob (CC-BY 3.0)"

[[asset]]
fichier  = "decors/tuiles-itch.png"
source   = "itch.io"
auteur   = "PixelArtist"
licence  = "itch-commercial"
date     = 2026-10-24
vendable = false
credit   = ""

[[asset]]
fichier  = "polices/PressStart2P.ttf"
source   = "Google Fonts"
auteur   = "CodeMan38"
licence  = "OFL-1.1"
date     = 2026-10-24
vendable = false
credit   = ""
"""
        )

        ok, erreurs, credits = vl.verifier_licences(racine=self.racine, manifeste=self.manifeste)
        self.assertTrue(ok, f"Erreurs inattendues : {erreurs}")
        self.assertEqual(erreurs, [])
        self.assertEqual(len(credits), 2)

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = vl.main(["--racine", self.racine, "--manifeste", self.manifeste, "--credits"])
        self.assertEqual(code, 0)
        self.assertIn("VERT", out.getvalue())
        self.assertIn("Alice", out.getvalue())

    def test_refuse_fichier_sous_assets_sans_entree(self) -> None:
        """Un fichier présent dans assets/ mais absent du manifeste est refusé."""
        self._creer_fichier("persos/tim/tim-planche.png")
        self._creer_fichier("objets/intrus.png")
        self._ecrire_manifeste(
            """
[[asset]]
fichier  = "persos/tim/tim-planche.png"
licence  = "propriétaire"
vendable = true
"""
        )
        ok, erreurs, _ = vl.verifier_licences(racine=self.racine, manifeste=self.manifeste)
        self.assertFalse(ok)
        self.assertTrue(any("objets/intrus.png" in e and "sans entrée" in e for e in erreurs), erreurs)

    def test_refuse_entree_pointant_vers_fichier_inexistant(self) -> None:
        """Une entrée du manifeste dont le fichier n'existe pas sur le disque est refusée."""
        self._ecrire_manifeste(
            """
[[asset]]
fichier  = "sons/fantome.wav"
licence  = "CC0"
vendable = false
"""
        )
        ok, erreurs, _ = vl.verifier_licences(racine=self.racine, manifeste=self.manifeste)
        self.assertFalse(ok)
        self.assertTrue(any("sons/fantome.wav" in e and "introuvable" in e for e in erreurs), erreurs)

    def test_refuse_licences_nc_nd_vide_inconnue(self) -> None:
        """Refuse les licences NC, ND, vides et inconnues (dont CC-BY-SA)."""
        cas = [
            ("sons/nc.wav", "CC-BY-NC-4.0", "non commerciale"),
            ("sons/nd.wav", "CC-BY-ND-4.0", "sans modification"),
            ("sons/vide.wav", "", "vide"),
            ("sons/inconnue.wav", "MIT", "inconnue ou non autorisée"),
            ("sons/sa.wav", "CC-BY-SA-4.0", "inconnue ou non autorisée"),
        ]
        blocs = []
        for fich, lic, _ in cas:
            self._creer_fichier(fich)
            blocs.append(
                f'[[asset]]\nfichier = "{fich}"\nlicence = "{lic}"\nvendable = false\ncredit = " Auteur "\n'
            )
        self._ecrire_manifeste("\n".join(blocs))

        ok, erreurs, _ = vl.verifier_licences(racine=self.racine, manifeste=self.manifeste)
        self.assertFalse(ok)
        texte_erreurs = "\n".join(erreurs)
        for fich, _, attendu in cas:
            self.assertIn(fich, texte_erreurs)
            self.assertIn(attendu, texte_erreurs)

    def test_refuse_cc_by_sans_credit(self) -> None:
        """Une licence CC-BY-4.0 ou CC-BY-3.0 avec `credit` vide ou manquant est refusée."""
        self._creer_fichier("icones/satellite.png")
        self._creer_fichier("icones/horloge.png")
        self._ecrire_manifeste(
            """
[[asset]]
fichier  = "icones/satellite.png"
licence  = "CC-BY-4.0"
vendable = false
credit   = "   "

[[asset]]
fichier  = "icones/horloge.png"
licence  = "CC-BY-3.0"
vendable = false
"""
        )
        ok, erreurs, _ = vl.verifier_licences(racine=self.racine, manifeste=self.manifeste)
        self.assertFalse(ok)
        self.assertEqual(len(erreurs), 2, erreurs)
        self.assertTrue(all("crédit obligatoire" in e for e in erreurs), erreurs)

    def test_refuse_vendable_si_non_proprietaire(self) -> None:
        """`vendable = true` est refusé pour CC0, CC-BY, itch-commercial et OFL-1.1."""
        for fich, lic in [
            ("objets/coffre.png", "CC0"),
            ("objets/epée.png", "CC-BY-4.0"),
            ("objets/tuile.png", "itch-commercial"),
            ("polices/font.ttf", "OFL-1.1"),
        ]:
            self._creer_fichier(fich)

        self._ecrire_manifeste(
            """
[[asset]]
fichier  = "objets/coffre.png"
licence  = "CC0"
vendable = true

[[asset]]
fichier  = "objets/epée.png"
licence  = "CC-BY-4.0"
credit   = "Auteur"
vendable = true

[[asset]]
fichier  = "objets/tuile.png"
licence  = "itch-commercial"
vendable = true

[[asset]]
fichier  = "polices/font.ttf"
licence  = "OFL-1.1"
vendable = true
"""
        )
        ok, erreurs, _ = vl.verifier_licences(racine=self.racine, manifeste=self.manifeste)
        self.assertFalse(ok)
        self.assertEqual(len(erreurs), 4, erreurs)
        self.assertTrue(all("vendable = true" in e for e in erreurs), erreurs)

    def test_option_projet_ecproj_accepte_et_refuse_medias_non_declares(self) -> None:
        """L'option --projet lit le format réel .ecproj (`items[*].kind.path`, `sequence`, `proxy`)."""
        f_declare = self._creer_fichier("sons/saut.wav")
        self._ecrire_manifeste(
            """
[[asset]]
fichier  = "sons/saut.wav"
licence  = "propriétaire"
vendable = true
"""
        )

        # 1. Projet .ecproj utilisant uniquement le média déclaré (+ un Solid et une Comp comme dans modeles/)
        proj_ok = self._creer_ecproj(
            "ep-ok/ep.ecproj",
            {
                "1": {"id": 1, "name": "bible.ecproj", "label": "Yellow", "parent": None, "kind": {"type": "Folder"}},
                "2": {
                    "id": 2,
                    "name": "Fond",
                    "label": "Red",
                    "parent": None,
                    "kind": {"type": "Solid", "color": [0.1, 0.1, 0.2], "width": 1080, "height": 1920, "pixel_aspect": 1.0},
                },
                "3": {
                    "id": 3,
                    "name": "saut.wav",
                    "label": "None",
                    "parent": None,
                    "kind": {"type": "Footage", "path": f_declare, "kind": "Audio", "width": 0, "height": 0},
                },
            },
        )
        ok, erreurs, _ = vl.verifier_licences(
            racine=self.racine,
            manifeste=self.manifeste,
            projets=[proj_ok],
        )
        self.assertTrue(ok, f"Erreurs inattendues : {erreurs}")

        # 2. Projet .ecproj référençant un média sous assets/ (relatif ou séquence) non déclaré au manifeste
        proj_ko = self._creer_ecproj(
            "ep-ko/ep.ecproj",
            {
                "10": {
                    "id": 10,
                    "name": "musique-pirate.wav",
                    "label": "None",
                    "parent": None,
                    "kind": {
                        "type": "Footage",
                        "path": "../assets/musiques/pirate.wav",
                        "kind": "Audio",
                    },
                },
                "11": {
                    "id": 11,
                    "name": "marche_seq",
                    "label": "None",
                    "parent": None,
                    "kind": {
                        "type": "Footage",
                        "path": f_declare,
                        "kind": "Sequence",
                        "sequence": [os.path.join(self.racine, "persos/tim/marche_01.png")],
                    },
                },
            },
        )
        err_stream = io.StringIO()
        with contextlib.redirect_stderr(err_stream):
            code = vl.main(["--racine", self.racine, "--manifeste", self.manifeste, "--projet", proj_ko])
        self.assertEqual(code, 1)
        sortie_err = err_stream.getvalue()
        self.assertIn("ROUGE", sortie_err)
        self.assertIn("musiques/pirate.wav", sortie_err)
        self.assertIn("persos/tim/marche_01.png", sortie_err)

    def test_modele_reel_sans_media_passe_au_vert(self) -> None:
        """Un modèle réel de ~/videos/modeles/ (sans média externe sous assets/) est accepté."""
        self._creer_fichier("palettes/ico-pixel-32.hex")
        self._ecrire_manifeste(
            """
[[asset]]
fichier  = "palettes/ico-pixel-32.hex"
licence  = "propriétaire"
vendable = true
"""
        )
        modele_reel = os.path.expanduser("~/videos/modeles/pixel-art.ecproj")
        if os.path.isfile(modele_reel):
            ok, erreurs, _ = vl.verifier_licences(
                racine=self.racine,
                manifeste=self.manifeste,
                projets=[modele_reel],
            )
            self.assertTrue(ok, f"Erreurs inattendues sur pixel-art.ecproj : {erreurs}")


if __name__ == "__main__":
    unittest.main()
```


---
**Vérification Claude (21/10/2026)** : brouillon non utilisable tel quel (3 lignes mal indentées → IndentationError ; extrait « saut.wav » de pixel-art.ecproj inventé, aucun Footage dans les modèles). Structure reprise ; version finale réécrite dans outils/verifier_licences.py (7 tests verts).
