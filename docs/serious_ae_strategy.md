# Événements indésirables graves

## Objectif

Cette étape vise à détecter de façon aussi exhaustive que possible les événements graves rapportés ou mentionnés dans les trip reports :

- défenestration, saut ou chute depuis une hauteur ;
- accident routier ou conduite dangereuse ;
- police, arrestation, prison, conséquences légales ;
- ambulance, pompiers, paramedics, secours ;
- urgences, hospitalisation, ICU, intubation, réanimation ;
- pensées suicidaires, tentative de suicide, self-harm ;
- psychose, délire dangereux, perte de contact avec la réalité ;
- convulsions, coma, perte de conscience, blackout ;
- blessures graves ;
- violence, agression, contention ;
- comportements publics dangereux ;
- noyade, suffocation, exposition ;
- décès/fatalité rapportée.

## Pourquoi une approche en deux temps ?

L'exhaustivité exige un filet large, mais un filet large produit des faux positifs. La stratégie sépare donc :

1. **Screening haute sensibilité** : repérer tous les reports susceptibles de contenir un événement grave.
2. **Validation qualitative** : lire les reports marqués pour confirmer, infirmer ou recoder l'événement.

Le fichier `data/processed/report_serious_events.csv` est local et non versionné. Il contient les codes report-level. Le fichier `data/processed/serious_event_validation_index.csv` donne les IDs/URLs à auditer, sans copier le texte.

## Commande

```bash
python3 scripts/extract_serious_events.py
```

Sorties agrégées :

- `outputs/tables/serious_event_prevalence.csv`
- `outputs/tables/serious_event_by_target_group.csv`
- `outputs/tables/serious_event_keyword_inventory.csv`

Sorties locales non versionnées :

- `data/processed/report_serious_events.csv`
- `data/processed/serious_event_validation_index.csv`

## Résultats de screening

Sur 8 011 reports uniques :

| Marqueur | Reports | % |
| --- | ---: | ---: |
| any serious-event-like marker, large | 5 532 | 69.06 |
| high-confidence serious-event screen | 4 716 | 58.87 |
| medical rescue | 2 256 | 28.16 |
| ER/hospital/ICU | 1 895 | 23.65 |
| life-threatening medical | 1 864 | 23.27 |
| seizure/coma/unconscious/blackout | 1 762 | 21.99 |
| accident/trauma composite | 1 697 | 21.18 |
| psychosis/delirium dangerous | 1 418 | 17.70 |
| police/arrest/legal | 1 344 | 16.78 |
| ambulance/paramedics/fire rescue | 1 036 | 12.93 |
| suicidality/self-harm | 756 | 9.44 |
| serious injury/trauma | 724 | 9.04 |
| near drowning/suffocation/exposure | 705 | 8.80 |
| traffic/driving accident | 403 | 5.03 |
| death/fatality reported | 166 | 2.07 |
| defenestration/jump/fall from height | 49 | 0.61 |

Ces chiffres sont des prévalences de **screening lexical**, pas des taux validés.

## Profils à vérifier en priorité

### LSD/lysergamides

Le screening retrouve beaucoup de marqueurs behavioral/legal :

- high-confidence serious-event screen : 72.89 % ;
- behavioral danger : 64.45 % ;
- psychosis/delirium dangerous : 39.13 % ;
- police/arrest/legal : 37.85 %.

À valider : faux positifs liés à mentions de police ou délire non dangereux.

### Cannabis naturel et cannabinoïdes synthétiques

Cannabis naturel :

- high-confidence serious-event screen : 73.09 % ;
- life-threatening medical : 29.82 % ;
- seizure/coma/unconscious/blackout : 29.29 % ;
- police/arrest/legal : 25.86 %.

Cannabinoïdes synthétiques :

- high-confidence serious-event screen : 62.96 % ;
- medical rescue : 36.11 % ;
- life-threatening medical : 31.94 % ;
- seizure/coma/unconscious/blackout : 30.56 % ;
- ambulance/paramedics/fire rescue : 20.83 %.

À valider : distinguer anxiété extrême, syncope/blackout, vrai coma, secours réels.

### DXM, délirogènes, sédatifs

Ces groupes ont un pôle médical/toxicologique fort :

- DXM : medical rescue 43.48 % ;
- délirogènes : psychosis/delirium dangerous 27.99 %, medical rescue 36.36 % ;
- benzodiazépines/Z-drugs/sédatifs : life-threatening medical 41.10 %, seizure/coma/unconscious/blackout 40.18 %.

## Comment viser l'exhaustivité ?

### 1. Construire une ontologie ouverte

Partir des catégories graves évidentes, puis ajouter les termes rencontrés :

- rescue/legal/medical ;
- trauma/accident ;
- self-harm/suicide ;
- delirium/psychosis/dangerous behavior ;
- coma/seizure/blackout ;
- death/fatality.

### 2. Utiliser un filet lexical large

Le script doit favoriser le rappel initial. Il vaut mieux récupérer trop de candidats que manquer des défenestrations ou tentatives suicidaires.

### 3. Valider manuellement

Pour chaque marqueur grave :

1. ouvrir `data/processed/serious_event_validation_index.csv` ;
2. lire les reports locaux correspondants dans `reports_for_coding.csv` ;
3. confirmer ou infirmer l'événement ;
4. coder un niveau de certitude :
   - `confirmed`;
   - `probable`;
   - `mentioned_not_event`;
   - `false_positive`;
   - `unclear`.

### 4. Chercher les faux négatifs

Après validation des positifs, échantillonner des reports négatifs, surtout :

- reports avec `medical_intervention`;
- reports avec `fear_of_death`;
- reports avec `interoceptive_threat`;
- reports longs ;
- reports Train Wrecks / Health Problems.

Lire ces négatifs permet d'ajouter des synonymes manqués.

### 5. Geler une version du codebook

Une fois les règles stabilisées, versionner :

- la taxonomie ;
- les patrons regex ;
- les règles d'exclusion ;
- les résultats de validation ;
- les taux validés.

## Limites

- Les reports peuvent mentionner police/hôpital sans événement réel.
- `blackout` ou `passed out` peut être grave ou non selon le contexte.
- Certaines catégories sont trop sensibles et doivent être durcies après lecture.
- Les taux ne sont pas épidémiologiques : Erowid surreprésente des récits difficiles et auto-sélectionnés.
- Les événements graves confirmés nécessitent une lecture humaine.

