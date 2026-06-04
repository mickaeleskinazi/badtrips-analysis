# Premiers résultats exploratoires

Ces résultats sont une première analyse automatique du corpus dédupliqué `reports_for_coding.csv` : 8 011 reports uniques après normalisation des URLs Erowid et déduplication par ExpID. Les marqueurs sont lexicaux et doivent être interprétés comme des indicateurs de tri, pas comme des mesures définitives. Ils servent à orienter le codage phénoménologique manuel.

## Familles de substances

Les reports peuvent appartenir à plusieurs familles si plusieurs catégories de substances sont associées au même report.

| Famille | Reports | % des reports |
| --- | ---: | ---: |
| Psychédéliques classiques | 2 383 | 29.75 |
| Pharmaceuticals | 1 283 | 16.02 |
| Stimulants | 996 | 12.43 |
| Psychédéliques phenethylamines | 915 | 11.42 |
| Cannabis / cannabinoïdes | 622 | 7.76 |
| Dissociatifs | 617 | 7.70 |
| Délirogènes | 561 | 7.00 |
| Dépresseurs / sédatifs | 546 | 6.82 |
| Entactogènes | 528 | 6.59 |
| Opioïdes | 527 | 6.58 |

## Marqueurs phénoménologiques globaux

| Marqueur | Reports | % |
| --- | ---: | ---: |
| Menace interoceptive | 5 574 | 69.58 |
| Soutien social | 4 126 | 51.50 |
| Peur de mourir | 3 491 | 43.58 |
| Déréalisation / dépersonnalisation | 3 378 | 42.17 |
| Paranoïa / menace sociale | 3 066 | 38.27 |
| Intégration positive après coup | 2 983 | 37.24 |
| Perte de contrôle | 2 612 | 32.61 |
| Intervention médicale | 2 562 | 31.98 |
| Distorsion temporelle | 1 851 | 23.11 |
| Acceptation / surrender | 1 101 | 13.74 |
| Peur de devenir fou | 946 | 11.81 |

## Résultats par groupes ciblés

Une seconde agrégation plus proche des molécules permet de réduire les redondances et d'obtenir des profils plus interprétables.

| Groupe ciblé | Reports | Menace interoceptive | Peur de mourir | Acceptation / surrender | Intégration positive |
| --- | ---: | ---: | ---: | ---: | ---: |
| Psilocybine / champignons | 515 | 73.79 | 57.28 | 24.47 | 57.48 |
| LSD / lysergamides | 391 | 67.26 | 61.13 | 29.67 | 55.24 |
| MDMA / entactogènes | 542 | 66.24 | 44.28 | 16.79 | 43.36 |
| Amphétamine-like stimulants | 434 | 60.14 | 41.01 | 11.06 | 32.72 |
| Cannabis naturel | 379 | 79.95 | 55.15 | 21.37 | 42.22 |
| Cannabinoïdes synthétiques | 216 | 88.89 | 65.74 | 11.57 | 37.50 |
| Ketamine/PCP/arylcyclohexylamines | 293 | 65.19 | 50.85 | 17.75 | 39.25 |
| DXM | 230 | 74.35 | 49.13 | 8.70 | 37.83 |
| Salvia | 244 | 60.25 | 42.21 | 22.95 | 43.44 |

Cette table suggère que l'axe substance reste utile. Les cannabinoïdes synthétiques et le cannabis naturel sont très marqués par l'interoception et la peur de mourir. Les groupes psilocybine/champignons et LSD/lysergamides montrent aussi une peur de mourir élevée, mais avec davantage de marqueurs d'acceptation et d'intégration. Les amphétamine-like stimulants ont un profil moins intégratif et plus proche d'une menace corporelle ou médicale.

## Résultats par grandes familles

### Cannabis et cannabinoïdes

Le profil cannabis/cannabinoïdes est particulièrement marqué par l'interoception et la peur de mourir :

- menace interoceptive : 83.12 % ;
- peur de mourir : 58.52 % ;
- intervention médicale : 34.86 % ;
- acceptation / surrender : 17.36 % ;
- intégration positive après coup : 40.68 %.

Ce résultat soutient l'idée que de nombreux bad trips au cannabis ou aux cannabinoïdes prennent la forme d'une crise corporelle : coeur, respiration, impression d'overdose, peur que le corps lâche.

### Psychédéliques classiques

Les psychédéliques classiques combinent fortement peur de mourir, interoception et intégration :

- menace interoceptive : 74.61 % ;
- peur de mourir : 51.78 % ;
- intervention médicale : 28.70 % ;
- acceptation / surrender : 21.36 % ;
- intégration positive après coup : 47.29 %.

Ce profil correspond bien à l'hypothèse d'une crise qui peut parfois devenir transformatrice : forte menace existentielle, mais aussi plus grande présence de récits d'acceptation et d'intégration.

### Dépresseurs, sédatifs et pharmaceuticals

Les dépresseurs/sédatifs et pharmaceuticals montrent davantage de marqueurs médicaux :

- pharmaceuticals : intervention médicale 41.62 % ;
- dépresseurs/sédatifs : intervention médicale 43.04 % ;
- dépresseurs/sédatifs : acceptation / surrender 5.49 % ;
- pharmaceuticals : acceptation / surrender 8.65 %.

Ce profil suggère un pôle plus toxicologique ou médical : intoxication, perte de conscience, urgence, sevrage, interaction médicamenteuse.

### Salvia

Salvia ressort avec un profil intéressant :

- peur de mourir : 42.21 % ;
- acceptation / surrender : 22.95 % ;
- intégration positive après coup : 43.44 % ;
- intervention médicale : 15.57 %.

Ce profil pourrait correspondre à des expériences très intenses, parfois de type disparition du soi ou bascule de réalité, mais moins médicalisées que d'autres familles.

## Cooccurrences principales

Les cooccurrences les plus fréquentes soutiennent le modèle proposé :

- menace interoceptive + peur de mourir : 35.68 % ;
- menace interoceptive + déréalisation/dépersonnalisation : 30.23 % ;
- menace interoceptive + perte de contrôle : 25.09 % ;
- peur de mourir + déréalisation/dépersonnalisation : 21.88 % ;
- soutien social + intégration positive après coup : 19.42 %.

## Lecture provisoire

La première analyse soutient trois intuitions fortes :

1. La menace interoceptive est probablement une dimension centrale des bad trips.
2. La peur de mourir est un point de convergence entre crises corporelles, psychédéliques, dissociatives et médicales.
3. L'acceptation et l'intégration ne sont pas distribuées uniformément : elles semblent plus présentes dans les récits psychédéliques classiques et Salvia que dans les récits sédatifs/pharmaceuticals.

## Limites immédiates

- Les marqueurs lexicaux produisent des faux positifs et des faux négatifs.
- Les familles de substances sont encore approximatives.
- Les reports multi-substances compliquent l'attribution causale.
- Les pourcentages ne doivent pas être interprétés comme des taux épidémiologiques.
- Le prochain niveau doit être un codage manuel stratifié par familles de substances.
