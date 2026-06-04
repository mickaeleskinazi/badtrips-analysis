# Erowid Bad Trips Analysis

Projet de recherche exploratoire sur les récits d'expériences difficiles ("bad trips") issus d'Erowid, toutes substances confondues.

## Objectif

Construire une analyse exploratoire puis phénoménologique des récits d'expériences difficiles afin d'identifier les structures récurrentes de l'expérience vécue : peur, perte de contrôle, désorientation, détresse corporelle, paranoïa, crise existentielle, temporalité altérée, aftermath, recours à autrui, etc.

Question de départ :

> Quelles structures phénoménologiques récurrentes caractérisent les expériences difficiles rapportées sur Erowid, et comment varient-elles selon les substances ou classes de substances ?

## Données

Le corpus brut n'est pas versionné dans Git. Les récits Erowid sont des textes publics mais protégés par copyright et soumis à des conditions d'utilisation. Le fichier local actuel attendu est :

```text
data/badtrip_reports_by_substance.csv
```

Avant toute diffusion publique, publication d'article, dépôt de données, entraînement de modèle ou redistribution d'extraits substantiels, il faut clarifier les permissions avec Erowid.

## Structure

```text
data/                 corpus local non versionné
docs/                 notes éthiques, méthodes, codebook
notebooks/            analyses interactives
outputs/              figures et tables générées
paper/                plan et brouillons de l'article
scripts/              commandes reproductibles
src/trip_reports/     code réutilisable
```

## Démarrage

Générer un premier audit agrégé du corpus :

```bash
python3 scripts/audit_corpus.py
```

Les sorties sont écrites dans `outputs/tables/` :

- `corpus_audit_summary.csv`
- `substance_category_counts.csv`
- `erowid_category_counts.csv`
- `metadata_presence.csv`

Ces fichiers ne contiennent pas le texte brut des reports.

## Axes d'analyse

1. Audit du corpus : nombre de récits, catégories, substances, longueurs, métadonnées disponibles.
2. Nettoyage : retrait du boilerplate, publicités, mentions de navigation, copyright et doublons.
3. Extraction structurée : âge, genre, année d'expérience, date de publication, dose, voie, substances.
4. Analyse exploratoire : distributions, cooccurrences, familles lexicales, variations par substance.
5. Codebook phénoménologique : dimensions vécues transversales et sous-codes.
6. Codage qualitatif assisté : annotation d'un échantillon, contrôle inter-codeur si possible.
7. Article : méthodes, résultats descriptifs, typologie phénoménologique, limites.

