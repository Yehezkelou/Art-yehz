# Presets ico-vid (étape 4)

Installés dans `~/Documents/EffectCraft/Presets/` → panneau **Effets et paramètres prédéfinis ▸
\* Animation Presets**. Double-clic (ou glisser sur un calque) pour appliquer.

**Règle de fabrication :** aucun preset ne touche aux propriétés du calque. Tout passe par ses
propres effets (*Transform*, *Linear Wipe*, *Iris Wipe* + curseurs nommés). Appliquer un preset
ne déplace et ne redimensionne donc jamais le calque, et plusieurs presets se cumulent.

## À lire avant : presets ou mouvements rapides ?

Les presets passent par l'effet *Transform* : réglables avec des curseurs, mais **~1 s de plus par
image au rendu** sur cette machine, et un effet posé sur un calque parent ne fait **pas** bouger
ses enfants (sur un perso rigé, seule la tête bougerait, sans les yeux).
Pour l'usage courant, préférer les **mouvements rapides** (`rapides/ico rapide - … .jsonl`,
*Fichier ▸ Scripts ▸ Exécuter un fichier de script…* sur le calque sélectionné). Ce sont des
expressions sur la transformation du calque : gratuites au rendu, enfants compris. Les réglages
sont les nombres en tête de l'expression.

## « Au marqueur » = tu choisis l'instant

Les presets marqués *(marqueur)* se déclenchent à **chaque marqueur du calque** (sélectionne le
calque, place la tête de lecture, touche `*` du pavé numérique ou *Calque ▸ Marqueurs ▸ Ajouter*).
Sans marqueur, ils ne font rien.

| Preset | Sur quoi | Réglages (curseurs ajoutés) |
|---|---|---|
| ico - Pop apparition | tout calque — à son point d'entrée | — (0 → 110 → 100 % + fondu de 0,08 s) |
| ico - Rebond squash et stretch | objet, perso — depuis son point d'entrée | Hauteur rebond (px), Rebonds par seconde, Amortissement, Pivot vers le bas (px) = ½ hauteur de l'objet pour écraser au sol |
| ico - Secousse comique (marqueur) | perso, tête, texte | Force secousse, Durée secousse (s) |
| ico - Zoom de reaction (marqueur) | perso / tête | Zoom réaction % (monte, redescend à 30 % et reste) |
| ico - Clignement auto | calque d'un œil | Intervalle clignement (s) |
| ico - Respiration | perso | Amplitude respiration % |
| ico - Transition fondu au noir | tout calque (sur fond noir) | Fondu entrée (s), Fondu sortie (s) — 0 = pas de fondu |
| ico - Transition volet | tout calque | Volet entrée (s), Volet sortie (s) |
| ico - Transition iris cartoon (sur solide noir) | **un solide noir plein cadre, tout en haut, sur toute la durée** | Iris ouverture (s), Iris fermeture (s), Iris décalage X / Y (pour fermer sur un visage) |
| ico pixel - Clignotement degats (marqueur) | sprite | — (0,6 s de clignotement à 12 i/s) |
| ico pixel - Saut avec arc (marqueur) | sprite | Hauteur saut (px), Durée saut (s) — positions entières |
| ico pixel - Scintillement piece | pièce, objet à ramasser | — |

## Sous-titres mot par mot

- **Apparition mot par mot** : preset texte intégré **Bounce In Words** (même panneau).
- **Mot en cours surligné (karaoké)** : `ico - Sous-titre mot par mot surligne.jsonl` (ce dossier).
  Sélectionne le calque texte, puis *Fichier ▸ Scripts ▸ Exécuter un fichier de script…*.
  Réglage : effet *Slider Control* = mots par seconde (0 = 2,5) ; couleur : *Animateur ▸ Fill Color*
  (jaune `#FFD24A` par défaut). Un seul animateur de texte par calque.
  C'est un script et pas un preset : un `.ecpreset` ne sait pas transporter un animateur de texte.

## Refaire / modifier

`build/make_presets.py` génère tous les `.ecpreset` à partir de `build/catalog-effets.ecpreset`
(une instance de chaque effet, enregistrée par EffectCraft lui-même) :
`python3 build/make_presets.py ~/Documents/EffectCraft/Presets`.
`build/test_presets.py` produit le script de test (valeurs attendues vérifiées le 20/10/2026).
