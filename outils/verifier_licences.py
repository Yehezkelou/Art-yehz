#!/usr/bin/env python3
"""Vérifie le manifeste des licences de ~/videos/assets (plan 2.3, § 5.2–5.3).

    python3 -I ~/videos/outils/verifier_licences.py                        # assets/ ↔ manifeste.toml
    python3 -I ~/videos/outils/verifier_licences.py --projet x.ecproj      # + médias d'un projet EffectCraft
    python3 -I ~/videos/outils/verifier_licences.py --credits              # crédits CC-BY pour la description

Rouge (code 1) si : un fichier d'assets/ n'a pas d'entrée, une entrée pointe vers un fichier absent,
la licence est vide, inconnue, NC ou ND, une CC-BY n'a pas de crédit, vendable = true hors
« propriétaire », ou un média d'assets/ utilisé par le projet n'a pas d'entrée valide.
Proposé par l'agent architecte (Gemini), relu et resserré par Claude.
"""
import argparse, json, os, sys, tomllib

HOME = os.path.expanduser("~")
RACINE = os.path.join(HOME, "videos/assets")
LICENCES = {"propriétaire", "CC0", "CC-BY-4.0", "CC-BY-3.0", "itch-commercial", "OFL-1.1"}


def erreurs_licence(fichier, e):
    lic = str(e.get("licence") or "").strip()
    parts = lic.upper().split("-")
    if not lic:
        return [f"{fichier} : licence vide"]
    err = []
    if "NC" in parts:
        err.append(f"{fichier} : licence non commerciale « {lic} » (chaîne monétisée = commercial)")
    elif "ND" in parts:
        err.append(f"{fichier} : licence sans modification « {lic} » (on recadre et on anime)")
    elif lic not in LICENCES:
        err.append(f"{fichier} : licence inconnue « {lic} » (autorisées : {', '.join(sorted(LICENCES))})")
    if lic.startswith("CC-BY") and not str(e.get("credit") or "").strip():
        err.append(f"{fichier} : crédit obligatoire manquant pour « {lic} »")
    if e.get("vendable") is True and lic != "propriétaire":
        err.append(f"{fichier} : vendable = true interdit pour « {lic} » (seul « propriétaire » se vend)")
    return err


def medias_projet(chemin):
    """Chemins des médias d'un .ecproj : items[*].kind.path (et .sequence) des éléments Footage."""
    with open(chemin, encoding="utf-8") as f:
        items = json.load(f).get("items", {})
    out = []
    for it in items.values() if isinstance(items, dict) else items:
        kind = it.get("kind") or {}
        if kind.get("type") == "Footage":
            out += [p for p in [kind.get("path"), *(kind.get("sequence") or [])] if isinstance(p, str) and p]
    return out


def verifier(racine=RACINE, manifeste=None, projets=()):
    racine = os.path.realpath(racine)
    manifeste = os.path.realpath(manifeste or os.path.join(racine, "manifeste.toml"))
    if not os.path.isfile(manifeste):
        return [f"manifeste introuvable : {manifeste}"], []
    with open(manifeste, "rb") as f:
        entrees = tomllib.load(f).get("asset", [])

    err, credits, connus, valides = [], [], set(), set()
    for e in entrees:
        fichier = os.path.normpath(str(e.get("fichier") or "")).replace(os.sep, "/")
        if fichier in (".", "") or fichier.startswith("../") or os.path.isabs(fichier):
            err.append(f"entrée avec un chemin invalide : « {e.get('fichier')} »")
            continue
        if fichier in connus:
            err.append(f"{fichier} : entrée en double")
            continue
        connus.add(fichier)
        e_err = erreurs_licence(fichier, e)
        if not os.path.isfile(os.path.join(racine, fichier)):
            e_err.insert(0, f"{fichier} : fichier absent du disque")
        err += e_err
        if not e_err:
            valides.add(fichier)
            if str(e["licence"]).startswith("CC-BY"):
                credits.append(str(e["credit"]).strip())

    for dossier, sous, noms in os.walk(racine):
        sous[:] = sorted(d for d in sous if not d.startswith("."))
        for nom in sorted(noms):
            chemin = os.path.realpath(os.path.join(dossier, nom))
            rel = os.path.relpath(chemin, racine).replace(os.sep, "/")
            if not nom.startswith(".") and chemin != manifeste and rel not in connus:
                err.append(f"{rel} : fichier sans entrée dans le manifeste")

    for projet in projets:
        base = os.path.dirname(os.path.realpath(projet))
        for m in medias_projet(projet):
            # EffectCraft résout un chemin relatif depuis le dossier du projet
            abs_m = os.path.realpath(os.path.join(base, os.path.expanduser(m)))
            if os.path.commonpath([abs_m, racine]) != racine:
                continue
            rel = os.path.relpath(abs_m, racine).replace(os.sep, "/")
            if rel not in valides:
                err.append(f"{os.path.basename(projet)} utilise {rel} sans entrée valide au manifeste")
    return err, credits


def main(argv=None):
    ap = argparse.ArgumentParser(description="Contrôle des licences des assets ico-vid.")
    ap.add_argument("--racine", default=RACINE)
    ap.add_argument("--manifeste")
    ap.add_argument("--projet", action="append", default=[])
    ap.add_argument("--credits", action="store_true")
    a = ap.parse_args(argv)
    err, credits = verifier(a.racine, a.manifeste, a.projet)
    if err:
        print(f"ROUGE — {len(err)} problème(s) :")
        for e in err:
            print("  - " + e)
        return 1
    print("VERT — manifeste conforme.")
    if a.credits and credits:
        print("Crédits : " + " · ".join(credits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
