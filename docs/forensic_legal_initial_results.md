# Resultats initiaux medico-legaux

## Corpus

Le pipeline a rescanné 8 011 reports uniques.

Populations :

| Population | N |
| --- | ---: |
| Tous les reports | 8 011 |
| Psychédélique-related large | 5 126 |
| Groupe-cible psychédélique uniquement | 3 462 |

Pour un article, la population `psychedelic_target_group_only` est la plus robuste. La population `psychedelic_related` est utile pour ne pas manquer les récits multi-substances, mais elle est plus exposée aux faux positifs.

## Screening medico-legal

Dans les 3 462 reports du noyau psychédélique :

| Marqueur | N | % |
| --- | ---: | ---: |
| any forensic/legal marker | 2 124 | 61.35 |
| justice system composite | 1 171 | 33.82 |
| interpersonal violence composite | 1 191 | 34.40 |
| forensic psychiatry interface | 1 062 | 30.68 |
| criminalized behavior composite | 1 005 | 29.03 |
| public safety endangerment composite | 661 | 19.09 |
| law enforcement contact | 586 | 16.93 |
| arrest/detention/custody | 460 | 13.29 |
| drug crime/possession/supply | 448 | 12.94 |
| suicide/self-harm forensic | 346 | 9.99 |
| property damage/vandalism/arson | 327 | 9.45 |
| charges/court/probation | 205 | 5.92 |
| impaired driving/traffic endangerment | 171 | 4.94 |
| theft/burglary/robbery | 171 | 4.94 |
| trespass/intrusion | 147 | 4.25 |
| homicide/death investigation | 87 | 2.51 |
| sexual assault/exploitation | 65 | 1.88 |
| involuntary psychiatric/legal hold | 46 | 1.33 |

Ces chiffres sont des taux de screening lexical, pas des taux validés.

## Priorités de validation

Priorité 1 :

- `arrest_detention_custody`
- `charges_court_probation`
- `impaired_driving_traffic_endangerment`
- `assault_violence_weapon`
- `endangerment_of_others`
- `suicide_self_harm_forensic`
- `homicide_death_investigation`
- `sexual_assault_exploitation`

Priorité 2 :

- `law_enforcement_contact`
- `drug_crime_possession_supply`
- `theft_burglary_robbery`
- `trespass_intrusion`
- `property_damage_vandalism_arson`
- `involuntary_psychiatric_legal_hold`

## Fichiers de validation

Le fichier local principal pour le codage est :

```text
data/processed/forensic_legal_validation_queue.csv
```

Il contient 1 086 lignes de validation plus l'en-tête, avec snippet, patron détecté, groupe psychédélique, et colonnes vides pour coder :

- confirmation de l'événement ;
- rôle du narrateur ;
- risque ou dommage à autrui ;
- issue légale ;
- contribution de la substance ;
- notes.

## Hypothèse de papier possible

Hypothèse prudente :

> Dans les bad trip reports associés aux psychédéliques, les co-mentions médico-légales semblent se concentrer autour de quatre configurations narratives : contact police/justice, désorganisation comportementale publique, violence ou risque interpersonnel, et interface psychiatrie/urgence. Ces configurations pourraient dépendre davantage de la perte de contrôle, de la paranoïa, de la confusion/délire et du contexte social que de la seule molécule.

Analyse suivante :

1. valider manuellement 50 à 75 reports par marqueur prioritaire ;
2. comparer les taux validés par groupe psychédélique ;
3. croiser avec `paranoia_social_threat`, `loss_of_control`, `fear_of_madness`, `fear_of_death`, `medical_intervention` ;
4. isoler les cas où la contribution de la substance est `central` ou `contributory`.
