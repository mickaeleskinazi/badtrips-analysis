# Workflow d'analyse phénoménologique

## Principe

L'analyse phénoménologique porte sur les reports complets. Les textes doivent donc être lus, annotés et comparés. La contrainte n'est pas d'éviter les reports, mais d'éviter de les redistribuer ou de les exposer inutilement.

## Fichiers locaux

Le script suivant crée un corpus de codage dédupliqué :

```bash
python3 scripts/prepare_coding_corpus.py
```

Sorties :

- `data/processed/reports_for_coding.csv` : fichier local avec textes complets, non versionné.
- `outputs/tables/deduplication_summary.csv` : résumé agrégé, sans texte brut.

## Unité d'analyse

L'unité principale recommandée est le report unique, identifié par `report_id` et `url`. Comme un même report peut apparaître dans plusieurs catégories de substances, les catégories sont regroupées dans un champ multi-valeurs.

## Cycle de codage

1. Lire un premier échantillon diversifié de reports.
2. Annoter librement les moments de crise, bascule, menace, résolution et aftermath.
3. Stabiliser les codes dans `docs/codebook.md`.
4. Coder un échantillon plus large avec les codes stabilisés.
5. Revenir aux reports complets pour vérifier que les catégories phénoménologiques ne découpent pas artificiellement la dynamique narrative.
6. Produire des tables agrégées par code, substance et type d'expérience.

## Colonnes utiles pour l'annotation

Le fichier de codage contient :

- `report_id` : identifiant stable dérivé de l'ExpID ou de l'URL.
- `url` : lien vers la page source.
- `title` : titre du report.
- `substance_categories` : catégories de substances associées au report.
- `erowid_categories` : catégories Erowid associées.
- `text` : texte complet local pour lecture et codage.

Pour l'annotation, on peut ajouter localement des colonnes comme :

- `primary_code`
- `secondary_codes`
- `phase`
- `intensity`
- `phenomenological_memo`
- `include_in_article`

Ces fichiers annotés doivent rester hors Git s'ils contiennent du texte ou des extraits.

