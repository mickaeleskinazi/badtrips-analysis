Objet : Plan de travail méthodologique pour l'analyse des bad trip reports Erowid

Cher Michel,

Je t'envoie un point d'étape sur le projet d'analyse des trip reports Erowid portant sur les expériences difficiles, avec un focus progressif sur la phénoménologie des bad trips, les événements indésirables graves, et les dimensions médico-légales associées aux psychédéliques.

À ce stade, le corpus brut contient 34 848 lignes issues du scraping, mais après déduplication par identifiant Erowid ExpID, nous travaillons sur 8 011 trip reports uniques. Les analyses automatiques actuelles sont donc réalisées au niveau report, et non au niveau ligne brute.

Le point méthodologique important est que les dictionnaires de mots-clés ne sont pas considérés comme des résultats définitifs. Ils servent uniquement de couche de screening à haute sensibilité. Nous avons séparé deux approches :

1. Une approche déductive, fondée sur des catégories théoriques définies a priori : peur de mourir, dissolution de l'ego, expérience mystique, paranoïa, rencontre avec des entités, reviviscence traumatique, insight autobiographique, sentiment religieux, menace intéroceptive, perte de contrôle, acceptation/surrender, intégration positive, etc.

2. Une approche inductive, fondée sur les termes qui émergent réellement du corpus : mots, bigrammes et trigrammes spécifiques aux sous-groupes de substances, aux marqueurs phénoménologiques, aux événements indésirables graves et aux marqueurs médico-légaux.

L'objectif est de comparer ce que notre théorie cherche à ce que le corpus fait émerger, puis d'utiliser les termes inductifs comme couche d'audit. Lorsqu'un terme inattendu apparaît dans une cohorte, il ne doit pas être interprété immédiatement comme un résultat : il peut révéler un thème réel, mais aussi un faux positif, une ambiguïté sémantique ou un artefact de nettoyage. Cette boucle permet de durcir progressivement les dictionnaires avant toute analyse quantitative forte.

Le plan de travail proposé est le suivant :

1. Stabiliser les dictionnaires de screening

Nous devons d'abord réduire les faux positifs les plus évidents dans les dictionnaires adverse events, médico-légal et phénoménologique. Pour cela, nous utiliserons les termes dérivés du corpus afin d'auditer les cohortes screen-positive.

Les cohortes prioritaires à relire sont notamment :

- arrestation/détention/custody ;
- charges/court/probation ;
- homicide/death investigation ;
- suicide/self-harm ;
- death/fatality reported ;
- fear of death ;
- ego dissolution ;
- paranoia.

2. Effectuer un premier tri humain léger

Il n'est pas nécessaire de trier tout le corpus immédiatement. La prochaine étape utile est de coder un premier échantillon limité mais informatif :

- environ 50 lignes médico-légales ;
- environ 50 lignes adverse events ;
- puis un premier échantillon phénoménologique dédié.

Pour chaque ligne, l'idée est de coder :

- confirmed ;
- probable ;
- false_positive ;
- mentioned_not_event ;
- unclear.

Cette première validation permettra d'identifier les erreurs récurrentes du screening automatique.

3. Corriger les patterns

Après les 100 à 150 premières lignes codées, nous pourrons repérer les faux positifs systématiques : termes trop larges, métaphores, peurs non réalisées, analogies de substance, événements passés hors trip, ou mentions concernant un tiers. Les dictionnaires seront ensuite corrigés, puis les tables régénérées.

4. Construire un vrai jeu d'annotation

Une fois les règles stabilisées, il faudrait constituer un jeu d'annotation plus structuré :

- environ 300 lignes médico-légales ;
- environ 300 lignes adverse events ;
- environ 300 lignes phénoménologiques ;
- environ 100 contrôles négatifs.

Un total d'environ 1 000 lignes annotées devrait permettre de calibrer les catégories et d'entraîner un premier modèle supervisé simple.

5. Ajouter une queue de validation phénoménologique

Pour l'instant, les fichiers de relecture humaine concernent surtout les adverse events et le pipeline médico-légal. La prochaine brique importante sera de créer une file dédiée aux dimensions phénoménologiques :

- fear_of_death ;
- ego_dissolution ;
- mystical_experience ;
- paranoia ;
- entity_encounter ;
- traumatic_reexperiencing ;
- autobiographical_insight ;
- religious_feeling ;
- acceptance_surrender ;
- integration_positive_afterwards ;
- negative_aftermath.

C'est probablement cette partie qui sera centrale pour l'article principal sur la phénoménologie des bad trips.

6. Produire les premières figures publiables

Une fois une validation minimale obtenue, nous pourrons produire :

- un flowchart du corpus ;
- une heatmap substances x marqueurs validés ;
- un barplot des faux positifs vs événements confirmés ;
- une carte adverse events x substances ;
- une carte médico-légal x psychédéliques ;
- une analyse de cooccurrence des dimensions phénoménologiques ;
- une typologie qualitative des trajectoires de crise : peur de mourir, résistance, surrender, intégration.

7. Entraîner un premier modèle automatique

Le modèle ne doit venir qu'après annotation humaine. Le modèle de départ le plus robuste serait une baseline supervisée multilabel :

- TF-IDF n-grams ;
- régression logistique ou Linear SVM ;
- évaluation par label : precision, recall, F1.

Les embeddings, le clustering et le topic modelling pourront ensuite servir à explorer les thèmes latents, identifier des faux négatifs, nommer les clusters et enrichir le codebook.

En résumé, la priorité actuelle n'est pas d'ajouter davantage de modèles, mais de stabiliser les catégories par une validation humaine ciblée. Le pipeline actuel permet déjà de distinguer :

- ce qui vient d'un dictionnaire théorique a priori ;
- ce qui émerge inductivement du corpus ;
- ce qui doit être validé humainement avant interprétation.

Je pense que la prochaine réunion pourrait être consacrée à valider ensemble le codebook, choisir les cohortes prioritaires à relire, et définir le volume minimal d'annotation nécessaire avant de passer aux analyses quantitatives et aux modèles supervisés.

Bien à toi,

Mickaël
