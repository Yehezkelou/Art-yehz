# Test J2 : voix VoiceStudio + transcription FilmCraft (22/10/2026)

**Résultat : réussi sur la phrase courte.** Transcription identique pour les 3 voix ; seul écart : « 5 » écrit en chiffre au lieu de « cinq » (0 % d'erreur réelle, 7 % en comparaison brute).

## Voix (VoiceStudio, moteur omnivoice.cpp 886fc07, modèle OmniVoice-GGUF Q4_K_M, Apache-2.0)
- Moteur compilé dans ~/.local/src/omnivoice.cpp (les binaires de VoiceStudio/bin sont des fichiers vides) ; modèles dans ~/.local/share/omnivoice/models.
- Phrase : « Ton GPS te trouve à cinq mètres près. Et il doit ça à Einstein. » (3,84 s), seed 7, --lang French.
- voix-1 « male, middle-aged, low pitch » · voix-2 « female, middle-aged, moderate pitch » · voix-3 « male, young adult, high pitch ».
- Mesures : crête −6,0 dBFS pour les trois ; RMS −22,5 / −21,6 / −19,7 dBFS ; parole sur toute la durée.
- Vitesse sur le processeur (pas de carte graphique, 7 Go de RAM) : 432 s pour la 1re (compilation FilmCraft en parallèle), ~5 min pour les suivantes ; ~930 Mo de mémoire.
- Réglages de voix possibles : genre, âge, hauteur, chuchotement, accent (pas de réglage « énergique »).

## Transcription (FilmCraft 0.10.0, feature whisper, modèle whisper-base, MIT)
- `filmcraft-cli run` : file.import → transcript.generate (language fr) → file.saveAs ; mots lus dans project.transcripts du .fcproj.
- 3 fichiers en 31 s (y compris le chargement du modèle).
- Fiche technique : `filmcraft-cli probe` donne audio_streams = [] pour sketch-01 et vulga-01 (vidéos muettes) ; pilote_agy.py l'utilise désormais quand ffprobe est absent.

## Limites
- Voix de synthèse propre : plus facile à transcrire qu'une vraie voix au micro. Le critère « < 10 % d'erreurs » reste à confirmer sur les 30 s complètes (texte-test.txt).
