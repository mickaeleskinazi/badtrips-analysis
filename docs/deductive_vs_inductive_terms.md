# Dictionnaire a priori vs termes derives du corpus

## Deux sources differentes

Le projet distingue maintenant deux fichiers.

### 1. Dictionnaire a priori

```text
outputs/tables/keyword_inventory_all.csv
```

Ce fichier vient de nos categories theoriques et methodologiques :

- hypothese de recherche ;
- phenomenologie des bad trips ;
- CEQ, ego dissolution, experience mystique, interoception ;
- categories medico-legales ;
- evenements indesirables graves ;
- faux positifs deja identifies.

Il est exporte avec :

```bash
python3 scripts/export_keyword_inventory.py
```

Ce dictionnaire est deductif : on part de concepts, puis on regarde comment ils apparaissent dans les reports.

### 2. Termes derives du corpus

```text
outputs/tables/corpus_derived_terms.csv
```

Ce fichier vient directement des 8 011 trip reports dedupliques.

Il est exporte avec :

```bash
python3 scripts/extract_corpus_derived_terms.py
```

Il contient :

- termes frequents dans tout le corpus ;
- termes specifiques par groupe de substances ;
- termes specifiques aux marqueurs phenomenologiques ;
- termes specifiques aux evenements indesirables ;
- termes specifiques au pipeline medico-legal.

Ce fichier est inductif : on part du langage des reports, puis on regarde ce qui emerge.

## Colonnes principales

- `comparison_type` : type de comparaison, par exemple `overall`, `target_group`, `phenomenology_marker`, `serious_event_marker`, `forensic_legal_marker`.
- `cohort` : groupe analyse, par exemple `lsd_lysergamides`, `fear_of_death`, `arrest_detention_custody`.
- `term` : mot, bigramme ou trigramme extrait du corpus.
- `cohort_doc_pct` : pourcentage de reports de la cohorte contenant le terme.
- `background_doc_pct` : pourcentage hors cohorte contenant le terme.
- `specificity_log_odds` : score de specificite du terme pour la cohorte.

Important : `all_reports` n'est pas une cohorte phenomenologique ou clinique a interpreter. C'est le vocabulaire de fond de tous les reports dedupliques. Il sert a identifier les mots banals du corpus, a calculer la specificite des autres cohortes, et a reperer les artefacts d'extraction ou de boilerplate. Les interpretations doivent donc porter sur les cohortes specifiques, pas sur `all_reports`.

## Comment utiliser ces fichiers ensemble ?

La logique methodologique est :

```text
keyword_inventory_all.csv
= ce que notre theorie cherche

corpus_derived_terms.csv
= ce que le corpus fait emerger
```

On compare ensuite :

1. categories prevues par la theorie ;
2. termes vraiment frequents dans les reports ;
3. termes specifiques d'une substance ;
4. termes revelant des faux positifs.

Exemple :

- si `cardiac arrest` ressort dans la cohorte `arrest_detention_custody`, cela indique un faux positif du mot `arrest` ;
- si `ego death` ressort dans `fear_of_death`, cela montre qu'il faut distinguer peur de mourir corporelle et mort de l'ego ;
- si des termes religieux emergent dans les clusters ou dans `fear_of_death`, ils peuvent justifier un label `religious_feeling`.

## Role dans le futur modele

Les termes derives du corpus servent a :

- enrichir le codebook ;
- decouvrir des themes oublies ;
- identifier des faux positifs ;
- auditer les cohortes construites par mots-cles ;
- choisir des exemples pour annotation humaine ;
- nommer les clusters/topic models ;
- comparer les resultats deductifs et inductifs.

Ils ne remplacent pas l'annotation humaine.

## Boucle de calibration des dictionnaires

Les termes inductifs doivent etre utilises comme outil de controle qualite.

Le principe :

```text
1. appliquer le dictionnaire a priori
2. construire les cohortes screen-positive
3. extraire les termes specifiques de chaque cohorte
4. reperer les termes incoherents ou inattendus
5. relire quelques reports sources
6. corriger le dictionnaire ou ajouter un faux positif connu
7. regenerer les tables
```

Un terme inattendu ne signifie pas automatiquement que la categorie est fausse. Il peut indiquer :

- un theme reel non anticipe ;
- une cooccurrence contextuelle ;
- une sous-population particuliere ;
- un faux positif lexical ;
- un probleme de nettoyage du texte ;
- un terme ambigu.

## Exemple : `piercing` dans `charges_court_probation`

Lors d'un audit, le terme `piercing` est apparu comme specifique de la cohorte medico-legale `charges_court_probation`.

Interpretation initiale possible mais incorrecte :

> `piercing` serait un terme medico-legal.

Interpretation methodologique correcte :

> `piercing` est surrepresente dans une cohorte construite par screening ; cela peut signaler que la cohorte est contaminee.

La relecture de quelques reports a montre que le probleme venait du patron trop large :

```text
charg(ed|es|ing)?
```

Ce patron captait des usages non juridiques :

- `cardiac arrest` pour arrestation ;
- `charging cord` ;
- `charged into my extremities` ;
- `take charge`.

Le dictionnaire a donc ete durci pour chercher un contexte juridique :

```text
charged with
charged for possession/assault/dui/etc.
charges filed/dropped/pending/against
facing charges
pressed charges
criminal charges
```

Apres correction, `piercing` ne ressortait plus dans cette cohorte, et les termes specifiques etaient plus coherents : `court`, `trial`, `probation`, `conviction`, `lawyer`, `felony`, `dui`, `jail`.

Cet exemple illustre que l'inductif ne sert pas seulement a decouvrir des themes ; il sert aussi a detecter les erreurs du deductif.

## Reporting dans la methode

Dans un article, cette etape peut etre decrite comme :

> We used corpus-derived n-grams as a diagnostic layer to audit the lexical screening dictionaries. Terms overrepresented in each screen-positive cohort were inspected to identify unexpected themes, ambiguous language, boilerplate artifacts, and false-positive lexical rules. When clear false positives were detected, the corresponding dictionary rule was tightened and the pipeline was rerun.

En francais :

> Les n-grams derives du corpus ont ete utilises comme couche diagnostique pour auditer les dictionnaires de screening. Les termes surrepresentes dans chaque cohorte screen-positive ont ete inspectes afin d'identifier themes inattendus, ambiguite lexicale, artefacts de nettoyage et faux positifs. Lorsque des faux positifs nets etaient identifies, la regle correspondante etait durcie, puis le pipeline regenere.

## Parametres actuels

Par defaut :

- corpus : `data/processed/reports_for_coding.csv` ;
- n-grams : 1 a 3 mots ;
- frequence documentaire minimale : 10 reports ;
- vocabulaire retenu : 25 000 termes ;
- top termes par cohorte : 75 ;
- top termes globaux : 300.

Commande configurable :

```bash
python3 scripts/extract_corpus_derived_terms.py \
  --min-df 10 \
  --max-vocab 25000 \
  --top-n 75
```

## Limites

- Les termes derives dependent encore des cohortes construites par screening ; si une cohorte contient des faux positifs, les termes emergents peuvent les reveler.
- Les n-grams ne comprennent pas le sens.
- Les termes tres frequents peuvent etre narratifs plutot que phenomenologiques.
- Les resultats doivent etre relus et utilises pour reviser le codebook.
