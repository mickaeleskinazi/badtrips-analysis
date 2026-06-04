# Co-paramètres et plan d'action

## Positionnement général

Le projet doit garder deux axes en parallèle :

```text
substances / groupes de substances -> profils phénoménologiques
dimensions phénoménologiques -> mécanismes de crise et de résolution
```

L'analyse par substances répond à la question : quelles molécules ou familles ouvrent vers quels types de crises ?

L'analyse par symptômes/dimensions répond à la question : quelle est la structure vécue du bad trip, indépendamment de la substance ?

## Variable centrale : let go / surrender

`let go` ne doit pas être traité comme un simple symptôme. C'est plutôt une variable de transition ou de résolution.

Hypothèse :

> Le passage de la panique à l'acceptation dépend de la capacité à abandonner le contrôle face à la peur de mourir, à la dissolution du soi ou à une interoception menaçante. Ce processus serait plus fréquent dans les récits psychédéliques que dans les récits toxicologiques ou sédatifs.

Questions à tester :

- Le `let go` apparaît-il plus souvent quand la peur de mourir est présente ?
- Est-il plus fréquent dans les reports psilocybine, LSD, DMT/ayahuasca, Salvia ?
- Est-il associé à davantage d'intégration positive après coup ?
- Est-il moins fréquent dans les récits avec intervention médicale ?
- Est-il facilité par le soutien social ou un changement de setting ?

## Co-paramètres disponibles

### Co-paramètres explicites

Disponibilité dans le corpus dédupliqué de 8 011 reports :

| Champ | Reports | % |
| --- | ---: | ---: |
| genre | 8 000 | 99.86 |
| année d'expérience | 7 964 | 99.41 |
| année de publication | 8 000 | 99.86 |
| dose présente | 7 931 | 99.00 |
| poids corporel présent | 7 586 | 94.69 |
| âge | 2 826 | 35.28 |

Utilisation :

- genre : descriptif et covariable exploratoire, avec prudence ;
- âge : utiliser seulement après filtrage des valeurs aberrantes, par exemple 12-80 ans ;
- dose : présence oui/non dans un premier temps ; extraction quantitative plus tard ;
- année d'expérience/publication : utile pour tendances temporelles et contrôle historique ;
- poids corporel : surtout indicateur de complétude du report.

### Co-paramètres structuraux

Disponibles pour tous les reports :

- longueur du texte ;
- nombre de mots ;
- nombre de catégories de substances ;
- nombre de groupes ciblés ;
- multi-substance ou multi-groupe ;
- catégorie Erowid source.

Utilisation :

- contrôler le fait que les reports longs contiennent plus facilement des mots-clés ;
- distinguer single-substance et polyconsommation ;
- éviter d'interpréter des taux lexicaux sans tenir compte de la longueur.

### Co-paramètres de contexte dérivés du texte

Première extraction lexicale :

| Feature | Reports | % |
| --- | ---: | ---: |
| voie orale | 6 154 | 76.82 |
| fumé/vaporisé/inhalé | 4 118 | 51.40 |
| seul | 3 585 | 44.75 |
| usager expérimenté | 3 205 | 40.01 |
| dehors/nature | 3 145 | 39.26 |
| domicile | 2 799 | 34.94 |
| première fois | 2 278 | 28.44 |
| fête/festival/club | 1 362 | 17.00 |
| insufflation | 1 186 | 14.80 |
| avec autrui | 1 089 | 13.59 |
| état préalable négatif | 808 | 10.09 |
| injection | 770 | 9.61 |
| intention thérapeutique | 513 | 6.40 |

Ces variables sont utiles pour tri et hypothèses, mais demandent validation manuelle car elles peuvent contenir des faux positifs.

## Variables phénoménologiques déjà disponibles

Marqueurs automatiques :

- menace interoceptive ;
- peur de mourir ;
- peur de devenir fou ;
- perte de contrôle ;
- déréalisation / dépersonnalisation ;
- paranoïa / menace sociale ;
- distorsion temporelle ;
- intervention médicale ;
- soutien social ;
- acceptation / surrender ;
- intégration positive après coup.

## Analyses prioritaires

### Analyse 1 : matrice substances x dimensions

Objectif : produire une carte descriptive.

Lignes :

- psilocybine/champignons ;
- LSD/lysergamides ;
- DMT/ayahuasca/5-MeO-DMT ;
- autres tryptamines ;
- phenethylamines/2C/NBOMe/DOx ;
- MDMA/entactogènes ;
- cannabis naturel ;
- cannabinoïdes synthétiques ;
- dissociatifs ;
- Salvia ;
- délirogènes.

Colonnes :

- menace interoceptive ;
- peur de mourir ;
- perte de contrôle ;
- déréalisation/dépersonnalisation ;
- intervention médicale ;
- acceptation/surrender ;
- intégration positive.

### Analyse 2 : peur de mourir comme nœud central

Comparer les reports avec et sans peur de mourir :

- substances surreprésentées ;
- cooccurrence avec interoception ;
- cooccurrence avec déréalisation ;
- cooccurrence avec perte de contrôle ;
- probabilité d'acceptation/surrender ;
- probabilité d'intégration positive.

### Analyse 3 : let go / surrender

Comparer les reports avec et sans `acceptance_surrender`.

Variables explicatives candidates :

- groupe de substance ;
- peur de mourir ;
- perte de contrôle ;
- déréalisation/dépersonnalisation ;
- interoception menaçante ;
- soutien social ;
- contexte seul vs avec autrui ;
- première fois vs expérimenté ;
- longueur du report.

Issue secondaire :

- intégration positive après coup.

### Analyse 4 : cannabis naturel vs cannabinoïdes synthétiques

Hypothèse :

> Les cannabinoïdes synthétiques présentent un profil plus fortement interoceptif et mortifère que le cannabis naturel, avec moins de let go et moins d'intégration.

Comparer :

- menace interoceptive ;
- peur de mourir ;
- intervention médicale ;
- perte de contrôle ;
- acceptation/surrender ;
- intégration positive.

### Analyse 5 : psychédéliques classiques

Focalisation :

- psilocybine/champignons ;
- LSD/lysergamides ;
- DMT/ayahuasca/5-MeO-DMT ;
- Salvia comme cas limite.

Question :

> Les récits psychédéliques difficiles ont-ils davantage de chance de contenir un passage de la peur de mourir vers l'acceptation ou l'intégration ?

## Modèles statistiques possibles

Les stats doivent rester exploratoires, pas causales.

### Descriptif

- pourcentages par groupe ;
- ratios de prévalence ;
- intervalles de confiance bootstrap ;
- heatmaps.

### Modèles simples

Régressions logistiques exploratoires :

- outcome 1 : peur de mourir ;
- outcome 2 : acceptation/surrender ;
- outcome 3 : intégration positive ;
- outcome 4 : intervention médicale.

Covariables :

- groupe de substance ;
- longueur du report ;
- multi-substance ;
- année d'expérience ;
- genre ;
- âge filtré ;
- contexte seul ;
- soutien social ;
- première fois ;
- expérimenté.

### Modèles à éviter pour l'instant

- modèles causaux forts ;
- interprétation clinique individuelle ;
- dose-réponse tant que les doses ne sont pas extraites proprement ;
- comparaisons fines par espèce de champignon ou taux de THC.

## Codage qualitatif

Le prochain passage doit être qualitatif.

Échantillon proposé :

- 20 reports psilocybine/champignons avec peur de mourir ;
- 20 reports LSD/lysergamides avec peur de mourir ;
- 20 reports cannabis naturel avec menace interoceptive ;
- 20 reports cannabinoïdes synthétiques avec menace interoceptive ;
- 20 reports DMT/ayahuasca/5-MeO-DMT ;
- 20 reports Salvia ;
- 20 reports avec `acceptance_surrender` ;
- 20 reports sans `acceptance_surrender` mais avec peur de mourir.

But :

- vérifier les marqueurs automatiques ;
- décrire la séquence narrative ;
- repérer le moment de bascule ;
- distinguer acceptation réelle, résignation, épuisement, dissociation et intervention externe.

## Plan d'action immédiat

1. Nettoyer/valider les marqueurs lexicaux sur un échantillon.
2. Créer une table d'analyse combinant codes, covariables et groupes ciblés.
3. Produire les premières heatmaps substances x dimensions.
4. Faire l'analyse spécifique `fear_of_death -> let_go -> integration`.
5. Tirer un échantillon stratifié pour codage manuel.
6. Réviser le codebook avec les exemples lus.
7. Rédiger une première section résultats exploratoires.
