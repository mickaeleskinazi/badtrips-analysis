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
