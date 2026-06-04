# Protocole de modelisation et de transparence

## Pourquoi un modele en etages ?

Les trip reports ne peuvent pas etre correctement analyses par mots-cles seuls. Les mots-cles detectent des passages candidats, mais ils confondent souvent :

- evenement reel vs peur ;
- prise de substance vs analogie ;
- police reelle vs paranoia ;
- mort reelle vs ego death ;
- arrestation juridique vs cardiac arrest ;
- suicide tente vs ideation.

Le modele adequat doit donc etre une chaine hybride :

```text
corpus deduplique
-> dictionnaires transparents haute sensibilite
-> extraction inductive des termes du corpus
-> audit des faux positifs et calibration des dictionnaires
-> extraction de snippets
-> flags contextuels automatiques
-> annotation humaine
-> embeddings et topic modelling exploratoire
-> classification supervisee multilabel
-> validation externe/inter-codeur
```

## Niveau 0 : corpus

Le corpus brut contient des lignes source, pas des reports uniques. Le fichier local actuel contient :

- 34 848 lignes brutes ;
- 8 011 reports Erowid uniques apres deduplication par ExpID.

Toutes les analyses report-level doivent utiliser les 8 011 reports uniques.

## Niveau 1 : dictionnaires transparents

Les dictionnaires servent uniquement de filet initial. Ils doivent etre publies comme materiel supplementaire, sous forme de patrons et categories.

Commande :

```bash
python3 scripts/export_keyword_inventory.py
```

Sortie :

```text
outputs/tables/keyword_inventory_all.csv
```

Ce fichier contient :

- marqueurs phenomenologiques actuels ;
- taxonomie phenomenologique etendue ;
- regles de familles de substances ;
- regles de groupes-cibles ;
- evenements indesirables graves ;
- marqueurs medico-legaux ;
- mots-cles psychedeliques ;
- flags contextuels ;
- faux positifs connus.

## Niveau 1b : termes derives du corpus

Le dictionnaire a priori doit etre compare a une extraction inductive depuis les reports eux-memes.

Commande :

```bash
python3 scripts/extract_corpus_derived_terms.py
```

Sortie :

```text
outputs/tables/corpus_derived_terms.csv
```

Cette sortie contient les mots, bigrammes et trigrammes frequents ou specifiques :

- dans le corpus total ;
- par groupe de substance ;
- par marqueur phenomenologique ;
- par marqueur adverse event ;
- par marqueur medico-legal.

La difference methodologique est detaillee dans `docs/deductive_vs_inductive_terms.md`.

## Niveau 1c : audit inductif des faux positifs

Les termes derives du corpus ne sont pas des labels. Ils indiquent qu'un terme est frequent ou specifique d'une cohorte deja construite.

Ils doivent donc etre lus comme une couche diagnostique :

- terme coherent : renforce l'interpretation de la cohorte ;
- terme inattendu : peut reveler un theme oublie ;
- terme incoherent : peut reveler un faux positif ;
- terme de boilerplate : peut reveler un probleme de nettoyage ;
- terme ambigu : doit etre relu dans les reports sources.

Exemple :

`piercing` est apparu comme specifique de la cohorte `charges_court_probation`. La relecture a montre que cette cohorte etait contaminee par un patron trop large autour de `charge/charged/charges`, captant des usages non juridiques comme `charging cord`, `charged into my extremities` ou `take charge`. Le patron a ete durci vers des expressions juridiquement contextualisees comme `charged with`, `facing charges` et `criminal charges`, puis les tables ont ete regenerees.

Cette boucle doit etre repetee avant toute interpretation quantitative forte.

## Niveau 2 : flags contextuels

Les flags contextuels ne sont pas un modele final. Ils servent a prioriser la relecture.

Exemples :

- `auto_is_feared_or_belief` : "I thought the police were coming" ;
- `auto_is_hypothetical` : "I wanted to jump" ;
- `auto_is_negated` : "I did not go to the hospital" ;
- `auto_is_analogy` : "It felt DMT-like" ;
- `auto_is_marker_specific_false_positive` : "cardiac arrest" pour arrestation juridique.

Commande :

```bash
python3 scripts/build_human_review_files.py
```

Sorties locales :

- `data/processed/human_review/combined_human_review.csv`
- `outputs/human_review/human_review_workbook.xlsx`

## Niveau 3 : annotation humaine

Avant tout modele supervise, il faut un jeu annote.

Unite d'annotation recommandee :

- report-level pour la presence globale d'une dimension ;
- snippet-level pour valider un evenement ou un passage ambigu.

Statuts minimaux :

- `confirmed`
- `probable`
- `mentioned_not_event`
- `false_positive`
- `unclear`

Pour la phenomenologie, coder en multilabel :

- present ;
- absent ;
- unclear ;
- valence : positive, negative, mixed, neutral ;
- phase narrative : onset, escalation, peak, resolution, aftermath.

## Niveau 4 : embeddings

Les embeddings servent a rapprocher les passages similaires et a explorer les themes latents. Ils ne doivent pas etre presentes comme preuve definitive.

Approche recommandee :

1. segmenter les reports en paragraphes ou fenetres de 150-300 mots ;
2. calculer des embeddings localement si possible ;
3. indexer les passages avec `report_id`, substance, phase narrative et marqueurs ;
4. inspecter les voisins proches de passages prototypes.

Usage :

- trouver des faux negatifs ;
- enrichir le codebook ;
- verifier si des themes non anticipes emergent ;
- construire un echantillonnage actif pour annotation.

Point ethique : ne pas envoyer les textes complets ou snippets vers une API externe sans clarifier les permissions Erowid.

## Niveau 5 : clustering et topic modelling moderne

Le topic modelling utile ici doit etre interpretable et auditable.

Pipeline recommande :

```text
paragraphes/snippets
-> embeddings
-> reduction dimensionnelle type UMAP
-> clustering type HDBSCAN
-> representation des topics par c-TF-IDF / mots caracteristiques
-> inspection humaine des clusters
```

Equivalent conceptuel : approche type BERTopic.

Sorties a publier :

- nombre de clusters ;
- taille des clusters ;
- mots caracteristiques ;
- exemples paraphrases ;
- distribution par substance ;
- distribution par marqueur humain valide.

Ne pas publier de longs extraits sans permission.

## Niveau 6 : classification supervisee multilabel

Une fois un jeu annote suffisant obtenu, entrainer un modele multilabel.

Baseline robuste :

- TF-IDF n-grams ;
- regression logistique ou Linear SVM ;
- calibration des probabilites ;
- seuil par label.

Modele plus avance :

- embeddings de phrases ;
- classifieur linear/logistic sur embeddings ;
- eventuellement transformer fine-tune local si le volume annote est suffisant.

Labels prioritaires :

- `fear_of_death`
- `ego_dissolution`
- `mystical_experience`
- `paranoia`
- `entity_encounter`
- `traumatic_reexperiencing`
- `autobiographical_insight`
- `religious_feeling`
- `interoceptive_threat`
- `loss_of_control`
- `acceptance_surrender`
- `integration_positive_afterwards`
- `negative_aftermath`

Evaluation :

- precision, recall, F1 par label ;
- macro-F1 et micro-F1 ;
- matrice d'erreurs qualitative ;
- comparaison mots-cles vs modele supervise ;
- validation sur holdout non vu ;
- si possible double codage et kappa/alpha inter-codeur.

## Niveau 7 : modele final pour l'article

Le modele final ne doit pas etre decrit comme "l'IA a trouve". Il faut decrire :

1. dictionnaires transparents pour screening ;
2. annotation humaine sur echantillon ;
3. correction des faux positifs ;
4. modele supervise entraine sur annotations ;
5. estimation des labels sur le corpus complet ;
6. analyse par substances et par trajectoires narratives.

## Figures methodologiques

Figures a produire :

- flowchart du corpus et des etapes ;
- schema du pipeline NLP ;
- heatmap labels phenomenologiques x substances ;
- UMAP des embeddings colore par label humain ;
- topic map ou barplot des clusters ;
- matrice confusion/precision-recall par label ;
- comparaison mots-cles vs modele supervise.

## Transparence minimale dans le papier

Inclure :

- taille du corpus brut et deduplique ;
- regles de deduplication ;
- liste des dictionnaires en supplement ;
- strategie d'annotation ;
- nombre de documents/snippets annotes ;
- accord inter-codeur ;
- modele utilise ;
- hyperparametres principaux ;
- metriques de performance ;
- limites : auto-selection Erowid, faux positifs, absence de donnees standardisees, causalite non inferable.
