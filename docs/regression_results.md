# Résultats régressifs exploratoires

Ces modèles sont exploratoires. Ils utilisent les marqueurs lexicaux automatiques et les covariables extraites des textes. Ils ne doivent pas être interprétés causalement. L'unité d'analyse est le report unique après déduplication canonique : 8 011 reports.

## Déduplication corrigée

La première déduplication par URL conservait séparément certaines variantes `erowid.org` et `www.erowid.org`. La déduplication est maintenant faite par ExpID quand il est disponible.

Résumé :

- lignes source : 34 848 ;
- reports uniques : 8 011 ;
- lignes redondantes retirées : 26 837 ;
- maximum de lignes source associées à un même report : 53.

## Modèles logistiques

Les modèles contrôlent notamment :

- groupe de substance ciblé ;
- longueur du report ;
- multi-groupe ;
- année d'expérience ;
- âge disponible/âge filtré ;
- genre ;
- contexte seul ou avec autrui ;
- première fois ;
- usager expérimenté.

### Peur de mourir

Outcome : `fear_of_death`.

Principaux résultats ajustés :

| Terme | OR | IC 95 % | p |
| --- | ---: | ---: | ---: |
| menace interoceptive | 3.12 | 2.78-3.50 | <0.001 |
| cannabinoïdes synthétiques | 2.34 | 1.71-3.20 | <0.001 |
| LSD/lysergamides | 1.45 | 1.11-1.88 | 0.006 |
| benzodiazépines/Z-drugs/sédatifs | 1.41 | 1.14-1.74 | 0.001 |
| DXM | 1.34 | 1.00-1.80 | 0.049 |
| DMT/ayahuasca/5-MeO-DMT | 1.32 | 1.06-1.63 | 0.011 |
| psilocybine/champignons | 1.31 | 1.05-1.62 | 0.015 |
| déréalisation/dépersonnalisation | 1.21 | 1.09-1.35 | <0.001 |
| perte de contrôle | 1.19 | 1.06-1.32 | 0.002 |

Lecture : la menace interoceptive est le prédicteur le plus robuste de la peur de mourir. Les cannabinoïdes synthétiques ressortent fortement même après contrôle des autres marqueurs et covariables.

### Let go / surrender

Outcome : `acceptance_surrender`.

Principaux résultats ajustés :

| Terme | OR | IC 95 % | p |
| --- | ---: | ---: | ---: |
| DMT/ayahuasca/5-MeO-DMT | 1.85 | 1.42-2.40 | <0.001 |
| déréalisation/dépersonnalisation | 1.54 | 1.31-1.80 | <0.001 |
| peur de mourir | 1.15 | 0.99-1.33 | 0.075 |
| intervention médicale | 0.85 | 0.73-1.00 | 0.048 |
| délirogènes/anticholinergiques | 0.46 | 0.31-0.68 | <0.001 |

Lecture : le `let go` semble moins directement lié à la peur de mourir qu'à la transformation du rapport au soi/réel. La déréalisation/dépersonnalisation et le groupe DMT/ayahuasca/5-MeO-DMT ressortent plus nettement. L'intervention médicale est associée à moins de `let go`, ce qui va dans le sens d'une distinction entre résolution expérientielle et résolution externe/médicale.

### Intégration positive après coup

Outcome : `integration_positive_afterwards`.

Principaux résultats ajustés :

| Terme | OR | IC 95 % | p |
| --- | ---: | ---: | ---: |
| psilocybine/champignons | 1.50 | 1.22-1.85 | <0.001 |
| DMT/ayahuasca/5-MeO-DMT | 1.30 | 1.06-1.61 | 0.014 |
| acceptation/surrender | 1.26 | 1.09-1.46 | 0.002 |
| délirogènes/anticholinergiques | 0.69 | 0.56-0.86 | <0.001 |

Lecture : le `let go` est associé à davantage d'intégration positive, même en contrôlant les groupes de substance et plusieurs covariables. Les champignons/psilocybine ressortent fortement sur l'intégration.

### Intervention médicale

Outcome : `medical_intervention`.

Principaux résultats ajustés :

| Terme | OR | IC 95 % | p |
| --- | ---: | ---: | ---: |
| peur de mourir | 1.98 | 1.78-2.19 | <0.001 |
| benzodiazépines/Z-drugs/sédatifs | 1.80 | 1.46-2.20 | <0.001 |
| DXM | 1.75 | 1.32-2.33 | <0.001 |
| menace interoceptive | 1.41 | 1.25-1.59 | <0.001 |
| délirogènes/anticholinergiques | 1.36 | 1.11-1.66 | 0.003 |
| psilocybine/champignons | 0.61 | 0.49-0.77 | <0.001 |
| DMT/ayahuasca/5-MeO-DMT | 0.42 | 0.33-0.54 | <0.001 |
| Salvia | 0.34 | 0.23-0.49 | <0.001 |

Lecture : l'intervention médicale dessine un pôle toxicologique/médical distinct du pôle psychédélique-intégratif.

## Chemin peur de mourir -> let go -> intégration

Comparaisons descriptives :

| Groupe | n | Let go % | Intégration % | Peur de mourir % |
| --- | ---: | ---: | ---: | ---: |
| peur de mourir présente | 3 491 | 18.45 | 42.97 | 100.00 |
| peur de mourir absente | 4 520 | 10.11 | 32.81 | 0.00 |
| déréalisation/dépersonnalisation présente | 3 378 | 22.62 | 46.65 | 52.96 |
| perte de contrôle présente | 2 612 | 19.56 | 42.04 | 53.02 |
| psilocybine/champignons | 515 | 24.47 | 57.48 | 57.28 |
| LSD/lysergamides | 391 | 29.67 | 55.24 | 61.13 |
| DMT/ayahuasca/5-MeO-DMT | 528 | 27.46 | 49.81 | 53.60 |
| cannabinoïdes synthétiques | 216 | 11.57 | 37.50 | 65.74 |
| DXM | 230 | 8.70 | 37.83 | 49.13 |
| délirogènes/anticholinergiques | 561 | 5.88 | 26.56 | 36.36 |

Lecture : la peur de mourir augmente la fréquence de `let go`, mais le profil le plus net semble être psychédélique/déréalisation plutôt que purement somatique. Les cannabinoïdes synthétiques ont une peur de mourir très élevée mais peu de `let go`, ce qui est théoriquement important.

## Dose-réponse

Une extraction préliminaire des doses numériques a été ajoutée. Elle détecte des valeurs dans le bloc `DOSE:` et les classe par unité.

Disponibilité :

- dose numérique détectée : 5 417 reports, 67.62 % ;
- mg : 3 101 reports, 38.71 % ;
- g : 1 121 reports, 13.99 % ;
- buvard/blotter/tab/hit : 986 reports, 12.31 % ;
- pill/tablet : 578 reports, 7.22 % ;
- ug : 132 reports, 1.65 % ;
- ml : 106 reports, 1.32 % ;
- capsule : 62 reports, 0.77 % ;
- goutte/drop : 33 reports, 0.41 %.

Les modèles dose-réponse actuels sont des screens par groupe/unité et doivent être considérés comme très préliminaires. Après correction de la déduplication, peu de groupes ont assez de doses parsées pour des conclusions robustes.

Signaux exploratoires :

- LSD/lysergamides, dose en buvards/blotters : dose associée à plus d'acceptation/surrender, OR 1.89, p=0.035 ; à valider car l'unité "buvard" ne mesure pas la quantité réelle de LSD.
- DXM, dose en mg : dose associée à plus d'intervention médicale, OR 1.81, p=0.008.
- Ketamine/PCP/arylcyclohexylamines, dose en mg : dose associée à plus de peur de mourir, OR 1.61, p=0.008.
- Psilocybine/champignons, dose en g : signal non significatif pour peur de mourir après contrôle minimal, OR 1.19, p=0.295.
- MDMA/entactogènes, dose en mg : pas de signal clair dans ce screen.

Un script produit aussi des graphes dose-réponse locaux :

```bash
python3 scripts/plot_dose_response.py
```

Sortie :

- `outputs/figures/dose_response_panels.png`

## Prochaine étape

Avant de faire de la dose-réponse une analyse centrale, il faut :

1. valider manuellement un échantillon de blocs `DOSE:` ;
2. créer des parseurs par substance/unité ;
3. distinguer dose initiale, dose totale, redosing et dosage approximatif ;
4. exclure ou recoder les reports multi-substances ;
5. modéliser séparément les substances où la dose est comparable.
