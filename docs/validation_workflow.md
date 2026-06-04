# Workflow de validation des reports

## Objectif

Les scripts de screening produisent des candidats. La validation consiste à relire les trip reports locaux pour transformer ces candidats en événements confirmés, probables, faux positifs ou mentions non événementielles.

Les textes complets restent locaux dans :

```text
data/processed/reports_for_coding.csv
```

Ils ne doivent pas être commités.

## Files à coder

Événements indésirables graves :

```text
data/processed/serious_event_validation_queue.csv
```

Médecine légale / psychédéliques :

```text
data/processed/forensic_legal_validation_queue.csv
```

Ces deux fichiers sont locaux et non versionnés car ils contiennent des snippets.

## Fichier humain enrichi

Pour préparer une relecture plus facile, lancer :

```bash
python3 scripts/build_human_review_files.py
```

Cela crée :

```text
data/processed/human_review/forensic_legal_human_review.csv
data/processed/human_review/serious_event_human_review.csv
data/processed/human_review/combined_human_review.csv
outputs/human_review/human_review_workbook.xlsx
outputs/tables/human_review_context_summary.csv
```

Le fichier combiné peut être ouvert dans Excel, Numbers, LibreOffice ou Google Sheets.

Le classeur généré reste local, car il contient des snippets.

Colonnes utiles :

- `auto_review_priority` : `high`, `medium`, `low` ;
- `auto_context_guess` : hypothèse automatique sur le statut du passage ;
- `auto_actor_guess` : sujet probable, autorité/secours, ami/tiers, unclear ;
- `auto_is_feared_or_belief` : peur, croyance, hallucination ou conviction ;
- `auto_is_hypothetical` : conditionnel, possibilité, intention ou idéation ;
- `auto_is_negated` : négation proche du mot-clé ;
- `auto_is_analogy` : comparaison ou métaphore ;
- `auto_is_marker_specific_false_positive` : faux positif lexical connu, par exemple `cardiac arrest` pour arrestation juridique ;
- `auto_local_window` : fenêtre courte autour du mot-clé.

Ces colonnes ne remplacent pas le codage humain. Elles servent à trier les lignes, repérer les faux positifs et prioriser la lecture.

## Relire un report précis

Exemple :

```bash
python3 scripts/review_validation_reports.py --report-id exp100200
```

Par défaut, le script lit la queue médico-légale. Pour la queue événements graves :

```bash
python3 scripts/review_validation_reports.py \
  --queue data/processed/serious_event_validation_queue.csv \
  --report-id exp100568
```

## Exporter un batch local de validation

Exemple pour relire 20 cas d'arrestation/détention :

```bash
python3 scripts/review_validation_reports.py \
  --marker arrest_detention_custody \
  --limit 20 \
  --out data/processed/review_batches/arrest_detention_batch.md
```

Exemple pour relire 20 cas de défenestration/chute/saut :

```bash
python3 scripts/review_validation_reports.py \
  --queue data/processed/serious_event_validation_queue.csv \
  --marker defenestration_jump_fall_height \
  --limit 20 \
  --out data/processed/review_batches/defenestration_batch.md
```

Le fichier Markdown généré contient les textes locaux. Il reste dans `data/processed/` et ne doit pas être versionné.

## Codage minimal

Pour chaque ligne, coder :

- `validation_status` : `confirmed`, `probable`, `mentioned_not_event`, `false_positive`, `unclear` ;
- `substance_contribution` : `central`, `contributory`, `contextual`, `unrelated`, `unclear` ;
- `notes` : phrase courte justifiant la décision.

Pour le pipeline médico-légal, coder aussi :

- `legal_event_confirmed` : oui/non/incertain ;
- `actor_role` : auteur, victime, témoin, tiers, unclear ;
- `third_party_harm_or_risk` : none, risk_only, injury, death, unclear ;
- `legal_outcome` : none, police_contact, arrest, charge, court, prison, unclear.

## Règle de décision

Ne pas coder un événement comme confirmé si le report mentionne seulement une peur, une hypothèse, une métaphore ou un contexte général.

Exemples :

- "I thought the police were coming" : pas forcément un contact police confirmé.
- "I felt like I was dying" : peur de mourir, pas décès ni urgence médicale confirmé.
- "I could have jumped" : risque/idée, pas tentative confirmée.
- "Police arrived and handcuffed me" : événement médico-légal confirmé.
