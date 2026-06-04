# Prochaines etapes pour publication

## Pipeline evenements indesirables graves

### Etape 1 : validation

Coder en priorite :

- `defenestration_jump_fall_height`
- `traffic_driving_accident`
- `ambulance_paramedics_fire_rescue`
- `er_hospital_icu`
- `suicidality_self_harm`
- `seizure_coma_unconscious`
- `death_fatality_reported`
- `psychosis_delirium_dangerous`

Objectif minimal : 50 a 75 reports par marqueur prioritaire, puis 100 a 200 controles negatifs.

### Etape 2 : indicateurs

Produire deux niveaux de resultats :

- taux de screening lexical ;
- taux valide ou valeur predictive positive par marqueur.

Les taux valides doivent toujours etre presentes comme proportions dans un corpus auto-selectionne, pas comme incidence populationnelle.

### Figures prioritaires

1. Flowchart du corpus : reports bruts, reports uniques, reports screen-positifs, reports valides.
2. Heatmap substance group x evenement grave.
3. Bar plot des evenements graves valides.
4. UpSet plot ou matrice de cooccurrence entre evenements graves.
5. Heatmap phenomenologie x evenement grave : peur de mourir, perte de controle, interoception, paranoia, medical intervention.
6. Forest plot exploratoire : odds ratios par substance/groupe pour les evenements graves, avec prudence sur les covariables.
7. Figure qualitative : typologie des trajectoires de crise, sans citer de longs extraits.

## Pipeline medecine legale / psychedeliques

### Etape 1 : population principale

Utiliser `psychedelic_target_group_only` comme population principale. Garder `psychedelic_related` comme analyse de sensibilite.

### Etape 2 : validation medico-legale

Coder en priorite :

- `arrest_detention_custody`
- `charges_court_probation`
- `impaired_driving_traffic_endangerment`
- `assault_violence_weapon`
- `endangerment_of_others`
- `suicide_self_harm_forensic`
- `homicide_death_investigation`
- `sexual_assault_exploitation`

Variables essentielles :

- evenement confirme ;
- role du narrateur : auteur, victime, temoin, tiers ;
- issue legale : police contact, arrest, charge, court, prison ;
- dommage ou risque pour autrui ;
- contribution de la substance : central, contributory, contextual, unrelated, unclear.

### Figures prioritaires

1. Flowchart medico-legal : corpus, noyau psychedelique, screen-positifs, valides.
2. Heatmap groupe psychedelique x marqueur medico-legal.
3. Bar plot des types d'evenements valides.
4. Stacked bar legal outcome par groupe psychedelique.
5. Alluvial plot : phenomenologie dominante -> comportement -> issue legale.
6. UpSet plot : police, arrestation, violence, mise en danger, hospitalisation psychiatrique.
7. Forest plot exploratoire des associations entre groupes psychedeliques et marqueurs medico-legaux.

## Analyses transversales

Croisements prioritaires :

- substance group x serious AE ;
- substance group x medico-legal marker ;
- dose extraite x marqueur grave, seulement pour les groupes avec assez de doses comparables ;
- peur de mourir x acceptation/let go x resolution ;
- interoceptive threat x medical rescue ;
- paranoia/loss of control/fear of madness x police/arrest/violence.

## Regles de publication

- Ne pas publier les textes complets.
- Eviter les longs verbatims sans permission explicite.
- Utiliser des paraphrases ou des micro-extraits si necessaire.
- Separarer clairement screening, validation et interpretation causale.
- Ne pas conclure que la molecule cause l'evenement medico-legal sans codage d'imputabilite.
