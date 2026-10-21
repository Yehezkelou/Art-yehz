# Briefing pour Gemini — chaîne ico-vid, plan « Usine » v2.3

Tu interviens comme **deuxième avis stratégique** sur le plan d'une petite chaîne vidéo (YouTube + TikTok + Instagram) en pixel art, « ico-vid », tenue par une seule personne (6 à 12 h/semaine) assistée par Claude (Claude Code). Le plan complet v2.2 est dans `plan-2.2.txt` (même dossier). Objectif chiffré : 500 $ bruts/mois vers le mois 12, avec les seuils YouTube 2027 (1 000 abonnés + 8 000 h de visionnage en 12 mois pour la publicité, à partir du 1er février 2027).

## Ce qu'on ajoute en v2.3 : Claude « regarde » les vidéos

Claude ne lit pas un .mp4 comme un lecteur : il voit des images et lit du texte. La suite de logiciels maison (ArtCraft, pilotable par MCP) fait la traduction :
- **FilmCraft** (≈ Premiere) : décode H.264/HEVC/VP9/AV1 ; `render_frame` (image à une seconde donnée) ; détection des coupes (`clip.sceneEditDetection`) ; transcription Whisper locale datée au mot (`transcript.generate`) ; mesure du volume BS.1770/EBU R128.
- **EffectCraft** (≈ After Effects) : `render_preview` d'une comp à un temps donné (avant même le rendu) ; niveaux audio en dBFS pendant la lecture.
- Un outil à écrire, **regarder.py**, produirait pour une vidéo : planche contact (12–24 images sur une seule image), une image par plan, des rafales (images consécutives sur 1–2 s), transcription .srt, mesures du son, fiche technique → Claude lit tout ça et écrit un rapport.

Usages prévus : (1) contrôle avant publication (cases de la définition de « vidéo terminée ») ; (2) analyse de vidéos de référence (structure, rythme, accroche) — seulement des fichiers qu'on a le droit d'avoir, sinon captures d'écran ; (3) comparaison v1/v2 ; (4) au bilan J+7, regarder l'instant où les spectateurs décrochent (courbe de rétention YouTube Studio) ; (5) commandes clients (vidéo de référence → cahier des charges).
Limites : il voit des échantillons, pas le mouvement continu ; il n'entend pas la musique (mesures seulement).

## Ce qu'on te demande (réponds en français, 900 mots maximum, en Markdown)

1. **Ta critique franche de la stratégie** (§ 12 contenu, § 13 marketing, § 14 revenus, § 15 feuille de route) : les 3 plus gros risques ou angles morts, et pour chacun une correction concrète. Ne répète pas ce que le plan dit déjà ; dis où tu n'es pas d'accord.
2. **La partie « regarder les vidéos »** : est-ce utile tel quel ? Qu'est-ce qui manque ou est surestimé ? Comment s'en servir pour la **stratégie** (pas seulement le contrôle qualité) ?
3. **Ton rôle à toi (Gemini via la CLI `agy`)** dans l'usine : où un deuxième modèle apporte-t-il vraiment quelque chose (ex. avis contradictoire aux bilans, compréhension vidéo native, autre chose) ? Où ce serait du bruit ? Propose une règle simple pour savoir quand on te consulte.
4. Pour tout chiffre ou règle de plateforme que tu avances, dis si tu en es sûr ou non.

Tu es en lecture seule : ne modifie aucun fichier.
