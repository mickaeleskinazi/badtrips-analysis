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

Préparer ensuite un corpus local dédupliqué pour le codage phénoménologique :

```bash
python3 scripts/prepare_coding_corpus.py
```

Cette commande écrit un fichier de travail dans `data/processed/reports_for_coding.csv`. Ce fichier contient les textes complets et reste donc non versionné. Il sert à lire, annoter et coder les reports localement.

Lancer une première analyse automatique des marqueurs phénoménologiques :

```bash
python3 scripts/analyze_phenomenology.py
```

Cette commande écrit `data/processed/report_codes.csv` localement et des tables agrégées dans `outputs/tables/`. Une synthèse interprétative est disponible dans `docs/first_analysis_results.md`.

La stratégie d'agrégation des substances est décrite dans `docs/substance_grouping_strategy.md`.

Extraire les co-paramètres disponibles pour les analyses :

```bash
python3 scripts/extract_covariates.py
```

Le plan analytique autour de la peur de mourir, du `let go` et des covariables est décrit dans `docs/covariates_and_action_plan.md`.

Extraire les doses numériques préliminaires et lancer les modèles exploratoires :

```bash
python3 scripts/extract_doses.py
python3 scripts/run_exploratory_models.py
```

Les résultats régressifs sont synthétisés dans `docs/regression_results.md`.

Générer une carte exploratoire substances x AE-like markers :

```bash
python3 scripts/generate_ae_maps.py
```

La synthèse est disponible dans `docs/ae_map_results.md`.

Générer les graphes dose-réponse exploratoires :

```bash
python3 scripts/plot_dose_response.py
```

La partie phénoménologique est cadrée dans `docs/phenomenological_framework.md`.

Extraire les événements indésirables graves en screening haute sensibilité :

```bash
python3 scripts/extract_serious_events.py
```

La stratégie d'exhaustivité et de validation est décrite dans `docs/serious_ae_strategy.md`. Cette commande produit aussi une file de validation locale dans `data/processed/serious_event_validation_queue.csv`.

Lancer le pipeline médico-légal centré sur les psychédéliques :

```bash
python3 scripts/extract_forensic_legal_events.py
```

La stratégie dédiée au papier médecine légale / psychédéliques est décrite dans `docs/forensic_legal_psychedelics_strategy.md`.
Les premiers résultats de screening sont synthétisés dans `docs/forensic_legal_initial_results.md`.

Relire localement les reports candidats pour validation :

```bash
python3 scripts/review_validation_reports.py --report-id exp100200
```

Le workflow de validation est décrit dans `docs/validation_workflow.md`.
Les prochaines analyses et figures pour publication sont listées dans `docs/publication_next_steps.md`.

## Axes d'analyse

1. Audit du corpus : nombre de récits, catégories, substances, longueurs, métadonnées disponibles.
2. Nettoyage : retrait du boilerplate, publicités, mentions de navigation, copyright et doublons.
3. Extraction structurée : âge, genre, année d'expérience, date de publication, dose, voie, substances.
4. Analyse exploratoire : distributions, cooccurrences, familles lexicales, variations par substance.
5. Codebook phénoménologique : dimensions vécues transversales et sous-codes.
6. Codage qualitatif assisté : annotation d'un échantillon, contrôle inter-codeur si possible.
7. Article : méthodes, résultats descriptifs, typologie phénoménologique, limites.

## Principe de publication

Le dépôt GitHub doit pouvoir rendre le travail reproductible sans redistribuer les textes. En pratique, le code, les règles de nettoyage, les schémas de codage, les figures agrégées et les tables non reconstructibles peuvent être versionnés ; les reports complets et les fichiers d'annotation contenant des extraits doivent rester locaux sauf permission explicite.
