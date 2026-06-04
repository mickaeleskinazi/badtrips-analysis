# Taxonomie phenomenologique etendue

Cette taxonomie sert a construire le codebook humain et les futurs labels supervises. Les categories sont multilabel : un meme report peut contenir plusieurs dimensions.

## Categories centrales

| Label | Nom FR | Definition courte |
| --- | --- | --- |
| `mystical_experience` | experience mystique | Unite, sacralite, noese, ineffabilite, transcendance du temps/espace. |
| `ego_dissolution` | dissolution de l'ego | Perte des frontieres du soi ou disparition du sujet separe. |
| `paranoia` | paranoia | Menace sociale, surveillance, persecution, peur des autorites. |
| `fear_of_death` | angoisse de mort | Conviction ou peur de mourir, somatique ou existentielle. |
| `entity_encounter` | rencontre avec des entites | Entites, presences, aliens, esprits, dieux, voix personnifiees. |
| `traumatic_reexperiencing` | reviviscence traumatique | Retour de trauma, flashbacks, abus, violence, honte traumatique. |
| `autobiographical_insight` | insight autobiographique | Compréhension personnelle sur histoire, relations, habitudes, conflits. |
| `religious_feeling` | sentiment religieux | Dieu, priere, enfer, paradis, peche, salut, revelation. |

## Categories transversales utiles

| Label | Nom FR | Definition courte |
| --- | --- | --- |
| `interoceptive_threat` | menace interoceptive | Corps ressenti comme dangereux, illisible ou non controlable. |
| `loss_of_control` | perte de controle | Incapacite percue a controler pensees, corps, emotions ou comportement. |
| `fear_of_madness` | peur de devenir fou | Peur de rester psychotique, schizophrene, ou de ne jamais revenir. |
| `derealization_depersonalization` | derealisation/depersonnalisation | Monde ou soi irreel, etranger, artificiel, dissocie. |
| `time_distortion` | distorsion temporelle | Temps infini, arrete, ralenti, cyclique ou impossible a evaluer. |
| `thought_loop` | boucle de pensee | Repetition intrusive ou circulaire de pensees/scenes/phrases. |
| `perceptual_overload` | surcharge perceptive | Intensite sensorielle excessive, hallucinations envahissantes. |
| `acceptance_surrender` | acceptation/surrender | Bascule par let go, abandon du controle, consentement a traverser. |
| `integration_positive_afterwards` | integration positive | Apprentissage, gratitude, prudence, transformation apres coup. |
| `negative_aftermath` | sequelles negatives | Anxiete persistante, flashbacks, derealisation durable, traumatisation. |

## Regles d'annotation

### 1. Ne pas confondre intensite et valence

Une dissolution de l'ego peut etre :

- positive ;
- terrifiante ;
- mixte ;
- neutre.

Coder la categorie et la valence separement.

### 2. Distinguer evenement, peur et metaphore

Exemples :

- "I died" peut etre ego dissolution, pas mort reelle.
- "I thought I was dying" = angoisse de mort, pas deces.
- "I met entities" = rencontre avec entites si le narrateur decrit une presence/personnalite.
- "It was DMT-like" = analogie, pas prise de DMT.

### 3. Coder la phase narrative

Pour chaque label important :

- `onset`
- `escalation`
- `peak`
- `resolution`
- `aftermath`

Cela permet de modeliser les trajectoires, pas seulement les themes.

### 4. Coder la fonction dans le recit

Pour les dimensions centrales, ajouter :

- `threatening`
- `transformative`
- `neutral_descriptive`
- `ambivalent`

Exemple : une experience mystique peut etre vecue comme revelation liberatrice ou comme terreur cosmique.

## Labels minimaux pour premier modele supervise

Pour un premier modele viable, commencer par :

1. `fear_of_death`
2. `interoceptive_threat`
3. `loss_of_control`
4. `paranoia`
5. `ego_dissolution`
6. `entity_encounter`
7. `mystical_experience`
8. `acceptance_surrender`
9. `integration_positive_afterwards`
10. `negative_aftermath`

Ces labels sont suffisamment frequents et centraux pour entrainer un modele multilabel initial.

## Labels secondaires a ajouter apres calibration

- `traumatic_reexperiencing`
- `autobiographical_insight`
- `religious_feeling`
- `fear_of_madness`
- `derealization_depersonalization`
- `time_distortion`
- `thought_loop`
- `perceptual_overload`

## Source des mots-cles

Les mots-cles operationnels sont stockes dans :

```text
src/trip_reports/phenomenological_taxonomy.py
```

Ils peuvent etre exportes avec :

```bash
python3 scripts/export_keyword_inventory.py
```

Le CSV exporte se trouve dans :

```text
outputs/tables/keyword_inventory_all.csv
```
