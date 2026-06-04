# Codebook phénoménologique provisoire

Ce codebook est une première grille de travail. Il doit être testé sur un échantillon de reports, puis révisé.

Une version opérationnelle étendue, destinée à l'annotation humaine et aux futurs modèles supervisés, est disponible dans `docs/expanded_phenomenological_taxonomy.md`.

Les mots-clés transparents associés à la taxonomie sont exportables avec :

```bash
python3 scripts/export_keyword_inventory.py
```

## Affects et tonalité

- `anxiety_panic` : anxiété aiguë, panique, terreur.
- `fear_of_death` : conviction ou peur explicite de mourir.
- `dysphoria` : malaise affectif, tristesse, désespoir, honte.
- `guilt_moral_distress` : culpabilité, faute, jugement moral de soi.

## Corps

- `somatic_threat` : impression que le corps est menacé ou dysfonctionne.
- `nausea_vomiting` : nausée, vomissements, malaise digestif.
- `pain_or_injury` : douleur, blessure, chute, dommage corporel.
- `autonomic_overload` : tachycardie, sueurs, tremblements, chaleur, froid.

## Perception et cognition

- `perceptual_overload` : surcharge sensorielle ou perceptive.
- `confusion_disorientation` : confusion, incapacité à comprendre la situation.
- `thought_loop` : boucle de pensée, rumination, répétition.
- `memory_gap` : amnésie ou trous mnésiques.
- `time_distortion` : temps ralenti, accéléré, fragmenté ou infini.

## Soi et monde

- `depersonalization` : distance au corps ou au soi.
- `derealization` : monde irréel, étrange ou artificiel.
- `loss_of_control` : incapacité à contrôler pensées, corps ou situation.
- `existential_crisis` : crise ontologique, sens de la vie, réalité, mort, identité.

## Social et contexte

- `paranoia_social_threat` : menace sociale, suspicion, peur d'autrui.
- `isolation` : solitude, absence d'aide, retrait.
- `seeking_help` : appel à un ami, famille, urgence, médecin.
- `medical_or_police_intervention` : intervention médicale, hospitalisation, police.

## Temporalité de l'expérience

- `onset` : montée initiale de l'expérience.
- `peak_crisis` : moment de crise maximale.
- `resolution` : descente ou résolution.
- `aftermath_negative` : effets négatifs durables.
- `aftermath_integrative` : apprentissage, intégration, relecture positive.
