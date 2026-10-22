#!/usr/bin/env python3
"""Rend une scène three.js en séquence PNG pixel art (palette ico-pixel-32) : enveloppe de outils/rendu3d/rendu3d.mjs.

    python3 -I ~/videos/outils/rendu3d.py <scene.mjs> <dossier> --debut 0 --fin 2            # f_0000.png … f_0047.png
    python3 -I ~/videos/outils/rendu3d.py <scene.mjs> <dossier> --debut 3 --fin 5 --fond 1d1b2e --params '{"texte": "0,1"}'
    python3 -I ~/videos/outils/rendu3d.py <scene.mjs> <dossier> --debut 0 --fin 1 --images 0,12   # aperçus

Depuis un compositeur d'épisode :
    import rendu3d
    info = rendu3d.rendre("scenes/bits.mjs", ".montage/3d/bits", 0, 4.5, params={"graine": 3})
    # info : résumé JSON de l'outil (images, ms_par_image, gpu…) ; fichiers <sortie>/f_0000.png …

L'image i est l'instant debut + i/ips (fin exclue, round((fin - debut) × ips) images), RGBA 8 bits, couleurs de la
palette seulement, alpha 0 ou 255. Contrat des scènes et de `outils` : outils/README.md (section rendu3d).
Node : ICO_NODE, sinon `node` du PATH, sinon C:\\Program Files\\nodejs\\node.exe ; navigateur : ICO_CHROME, sinon
Chrome puis Edge. Dépendances : `npm ci` dans outils/rendu3d/ (une fois par clone). Code 0 réussi, 1 échec.
"""
import argparse, json, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chemins  # noqa: E402

OUTIL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rendu3d", "rendu3d.mjs")


class ErreurRendu(RuntimeError):
    pass


def trouver_node(env=None):
    """Chemin de node, ou None."""
    env = os.environ if env is None else env
    if env.get("ICO_NODE"):
        return env["ICO_NODE"] if os.path.exists(env["ICO_NODE"]) else None
    n = shutil.which("node")
    if n:
        return n
    for p in [os.path.join(env.get("PROGRAMFILES", r"C:\Program Files"), "nodejs", "node.exe"),
              r"C:\Program Files\nodejs\node.exe", "/usr/local/bin/node", "/usr/bin/node"]:
        if os.path.exists(p):
            return p
    return None


def dependances_presentes():
    base = os.path.join(os.path.dirname(OUTIL), "node_modules")
    return all(os.path.exists(os.path.join(base, *p)) for p in
               [("three", "build", "three.module.js"), ("puppeteer-core", "package.json")])


def commande(scene, sortie, debut, fin, ips=24, fond="transparent", params=None,
             largeur=270, hauteur=480, images=None, node=None):
    """Liste d'arguments de la commande node (sans la lancer)."""
    cmd = [node or trouver_node() or "node", OUTIL, "--scene", os.path.abspath(scene), "--out", os.path.abspath(sortie),
           "--debut", repr(float(debut)), "--fin", repr(float(fin)), "--ips", str(int(ips)),
           "--largeur", str(int(largeur)), "--hauteur", str(int(hauteur)), "--fond", str(fond).lstrip("#"),
           "--params", json.dumps(params or {}, ensure_ascii=False)]
    if images is not None:
        cmd += ["--images", ",".join(str(int(i)) for i in images)]
    return cmd


def rendre(scene, sortie, debut, fin, ips=24, fond="transparent", params=None,
           largeur=270, hauteur=480, images=None, delai=None):
    """Rend la scène dans `sortie` ; renvoie le résumé (dict). ErreurRendu si node, les dépendances ou le rendu échouent."""
    node = trouver_node()
    if not node:
        raise ErreurRendu("node introuvable (installer Node.js ≥ 22 ou définir ICO_NODE)")
    if not dependances_presentes():
        raise ErreurRendu(f"dépendances absentes : lancer « npm ci » dans {os.path.dirname(OUTIL)}")
    env = dict(os.environ)
    env.setdefault("ICO_VIDEOS", chemins.racine())
    r = subprocess.run(commande(scene, sortie, debut, fin, ips, fond, params, largeur, hauteur, images, node),
                       capture_output=True, text=True, encoding="utf-8", env=env, timeout=delai)
    try:
        info = json.loads(r.stdout)
    except ValueError:
        info = None
    if r.returncode != 0 or not info or not info.get("ok"):
        msg = (info or {}).get("erreur") or r.stderr.strip() or f"code {r.returncode}"
        raise ErreurRendu(f"rendu3d : {msg}")
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rend une scène three.js en PNG pixel art (palette ico-pixel-32).")
    ap.add_argument("scene")
    ap.add_argument("sortie")
    ap.add_argument("--debut", type=float, required=True)
    ap.add_argument("--fin", type=float, required=True)
    ap.add_argument("--ips", type=int, default=24)
    ap.add_argument("--largeur", type=int, default=270)
    ap.add_argument("--hauteur", type=int, default=480)
    ap.add_argument("--fond", default="transparent", help="transparent ou RRGGBB")
    ap.add_argument("--params", default="{}", help="JSON passé à creer()")
    ap.add_argument("--images", default=None, help="numéros d'images à rendre seulement, ex. 0,5,9")
    a = ap.parse_args(argv)
    try:
        params = json.loads(a.params)
        images = [int(x) for x in a.images.split(",") if x.strip()] if a.images else None
    except ValueError as e:
        ap.error(f"--params ou --images invalide : {e}")
    try:
        info = rendre(a.scene, a.sortie, a.debut, a.fin, a.ips, a.fond, params, a.largeur, a.hauteur, images)
    except (ErreurRendu, OSError) as e:
        print(e, file=sys.stderr)
        return 1
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
