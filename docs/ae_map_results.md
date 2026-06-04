# Carte substances x AE-like markers

## Objectif

Cette analyse crée une carte exploratoire entre groupes de substances et événements/symptômes rapportés dans les trip reports. Le terme `AE-like marker` désigne ici un marqueur lexical d'événement ou symptôme, pas un adverse event médicalement validé.

Sorties générées localement :

- `outputs/tables/ae_marker_prevalence.csv`
- `outputs/tables/ae_marker_by_target_group.csv`
- `outputs/tables/ae_marker_heatmap_matrix.csv`
- `outputs/figures/ae_marker_heatmap.png`

Les fichiers report-level restent dans `data/processed/` et ne sont pas versionnés.

## Marqueurs AE-like globaux

Sur 8 011 reports uniques :

| Marqueur | Reports | % |
| --- | ---: | ---: |
| panique/anxiété | 4 403 | 54.96 |
| injury/accident | 4 083 | 50.97 |
| gastro-intestinal | 2 895 | 36.14 |
| neurologique/moteur | 2 676 | 33.40 |
| urgence médicale | 2 481 | 30.97 |
| déréalisation/dépersonnalisation | 2 452 | 30.61 |
| confusion/delirium | 2 108 | 26.31 |
| psychose/paranoïa | 2 093 | 26.13 |
| perte de conscience/blackout | 1 997 | 24.93 |
| respiratoire | 1 550 | 19.35 |
| cardiovasculaire | 1 339 | 16.71 |
| self-harm/suicidality | 622 | 7.76 |

## Profils par substances

### Psychédéliques classiques

Psilocybine/champignons et LSD/lysergamides ressortent surtout sur :

- panique/anxiété ;
- déréalisation/dépersonnalisation ;
- confusion/delirium ;
- psychose/paranoïa pour LSD/lysergamides ;
- intégration positive dans les analyses précédentes.

Cela soutient un profil plus phénoménologique/existentiel que strictement toxicologique.

### Cannabis naturel et cannabinoïdes synthétiques

Cannabis naturel :

- panique/anxiété : 73.61 % ;
- neurologique/moteur : 44.85 % ;
- psychose/paranoïa : 44.06 % ;
- déréalisation/dépersonnalisation : 42.74 %.

Cannabinoïdes synthétiques :

- panique/anxiété : 70.83 % ;
- neurologique/moteur : 39.35 % ;
- gastro-intestinal : 36.57 % ;
- urgence médicale : 36.11 % ;
- psychose/paranoïa : 32.41 %.

Les cannabinoïdes synthétiques gardent donc un profil plus médicalisé et plus somatique que le cannabis naturel.

### DXM et sédatifs

DXM :

- urgence médicale : 46.52 % ;
- gastro-intestinal : 44.35 % ;
- neurologique/moteur : 38.26 % ;
- perte de conscience/blackout : 29.57 %.

Benzodiazépines/Z-drugs/sédatifs :

- urgence médicale : 41.28 % ;
- perte de conscience/blackout : 35.96 %.

Ces profils appartiennent davantage au pôle toxicologique/médical.

### Salvia

Salvia est très marquée par :

- panique/anxiété : 75.00 % ;
- déréalisation/dépersonnalisation : 74.59 % ;
- confusion/delirium : 41.80 % ;
- faible urgence médicale : 15.57 % dans l'analyse phénoménologique.

Elle ressemble donc à un cas limite : très forte rupture de réalité/soi, mais moins médicalisée.

## Limites

- Les marqueurs sont lexicaux et doivent être validés manuellement.
- `injury_accident` est probablement trop large et devra être audité.
- Certains marqueurs captent des descriptions rétrospectives ou des avertissements, pas seulement des événements vécus.
- Les reports longs ont plus de chances de contenir plusieurs marqueurs.

## Prochaine étape

1. Auditer manuellement 20 reports positifs par marqueur AE central.
2. Affiner `injury_accident`, `cardiovascular` et `respiratory`.
3. Combiner la map AE avec les modèles `fear_of_death`, `let_go` et `medical_intervention`.
4. Produire une figure finale substance x AE pour l'article après validation.

