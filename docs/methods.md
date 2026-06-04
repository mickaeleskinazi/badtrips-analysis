# Méthodes

## Corpus

Le corpus de travail rassemble des reports classés comme expériences difficiles sur Erowid, toutes substances confondues. Chaque ligne du fichier source correspond à un report ou à une entrée scrappée, avec au minimum une URL, un titre, une catégorie de substance, une catégorie Erowid, une URL de catégorie source et le texte extrait.

## Étape 1 : audit descriptif

Objectifs :

- compter les reports ;
- décrire les catégories de substances ;
- vérifier les catégories Erowid ;
- mesurer la longueur des textes ;
- estimer la disponibilité des métadonnées internes : année d'expérience, âge, genre, dose, poids, date de publication, ExpID.

Cette étape ne produit que des sorties agrégées.

## Étape 2 : nettoyage

Le nettoyage devra identifier et retirer :

- menus et éléments de navigation ;
- publicités et appels aux dons ;
- blocs de copyright et conditions d'utilisation ;
- marqueurs techniques comme les liens PDF/LaTeX ;
- duplications internes dues au scraping.

Les règles de nettoyage doivent être versionnées et testées sur des échantillons locaux, sans publier les textes.

## Étape 3 : analyse exploratoire

Analyses prévues :

- distribution des récits par substance et catégorie ;
- distribution des longueurs ;
- disponibilité des métadonnées par catégorie ;
- années d'expérience et dates de publication lorsque disponibles ;
- vocabulaire descriptif agrégé, après nettoyage ;
- cooccurrences de termes liés aux dimensions somatiques, affectives, perceptives, sociales et existentielles.

## Étape 4 : analyse phénoménologique

L'analyse phénoménologique doit partir d'un codebook explicite. Les codes initiaux peuvent inclure :

- montée de l'angoisse ;
- perte de contrôle ;
- peur de mourir ;
- déréalisation ou dépersonnalisation ;
- menace corporelle ;
- surcharge perceptive ;
- paranoïa ou menace sociale ;
- confusion cognitive ;
- rupture temporelle ;
- boucle de pensée ;
- crise existentielle ou morale ;
- demande d'aide ou recours à autrui ;
- hospitalisation ou intervention médicale ;
- aftermath positif, neutre ou négatif.

Le codebook doit rester révisable après annotation d'un premier échantillon.

## Utilisation directe des reports

L'analyse phénoménologique requiert une lecture directe des textes. Le projet distingue donc trois niveaux :

1. Corpus brut local : le fichier scrappé original, non versionné.
2. Corpus de codage local : un fichier dédupliqué contenant les textes complets et des identifiants stables, non versionné.
3. Résultats partageables : tables agrégées, figures, codebook, méthodes et statistiques qui ne republient pas les récits.

Le fichier de codage local peut être généré avec :

```bash
python3 scripts/prepare_coding_corpus.py
```

Ce fichier est destiné à l'annotation qualitative, par exemple dans un tableur, un outil CAQDAS, ou des scripts locaux. Les citations courtes destinées à l'article devront être sélectionnées plus tard, en tenant compte des permissions et des limites de citation.
