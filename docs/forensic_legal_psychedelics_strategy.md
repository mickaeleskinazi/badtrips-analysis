# Pipeline medecine legale et psychedeliques

## Objectif

Ce pipeline explore les co-mentions medico-legales dans les trip reports lies aux psychedeliques :

- police, 911, sheriff, security ;
- arrestation, detention, prison, jail ;
- charges, tribunal, probation, avocat ;
- possession, trafic, paraphernalia, customs ;
- assault, violence, armes, menaces ;
- homicide, mort violente, coroner/autopsy ;
- suicide, tentative de suicide, self-harm ;
- violence sexuelle ou exploitation ;
- vol, cambriolage, intrusion, trespass ;
- vandalisme, degats materiels, incendie ;
- nudite publique, disorderly conduct, perturbation de l'ordre public ;
- conduite sous influence, accident, mise en danger routiere ;
- fuite, resistance a l'arrestation, poursuite ;
- mise en danger d'autrui ;
- hospitalisation psychiatrique sous contrainte, 5150, psych hold ;
- search and rescue, personne disparue.

## Populations

Le script distingue trois niveaux :

1. `all_reports` : tous les reports Erowid du corpus local.
2. `psychedelic_related` : reports ayant soit un groupe-cible psychedelique, soit un mot-cle molecule dans le texte.
3. `psychedelic_target_group_only` : reports classes dans un groupe-cible psychedelique par la taxonomie du projet.

Les groupes-cibles psychedeliques initiaux sont :

- `psilocybin_mushrooms`
- `lsd_lysergamides`
- `dmt_ayahuasca_5meo`
- `other_tryptamines`
- `mescaline_cacti`
- `phenethylamines_2c_nbome_dox`
- `mdma_entactogens`
- `salvia`

## Mots-cles psychedeliques

Le dictionnaire inclut notamment :

- LSD, acid, blotter, tabs, gel tabs, 1P-LSD, AL-LAD, ETH-LAD, ALD-52 ;
- psilocybin, psilocin, magic mushrooms, shrooms, cubensis, liberty caps ;
- DMT, 5-MeO-DMT, ayahuasca, changa, pharmahuasca, bufo ;
- 4-AcO-DMT, 4-HO-MET, 4-HO-MiPT, DPT, DiPT, MiPT ;
- mescaline, peyote, San Pedro, Peruvian torch ;
- 2C-B, 2C-E, 2C-I, 2C-T-7, NBOMe, 25I/25C/25B, DOB, DOC, DOI, DOM ;
- MDMA, MDA, MDEA, ecstasy, molly, methylone, 6-APB ;
- salvia, salvinorin.

## Prudence interpretative

Le pipeline ne demontre pas que le psychedelique a cause l'evenement medico-legal. Il detecte une co-presence narrative :

> episode psychotrope + marqueur medico-legal.

La causalite, l'imputabilite et la contribution de la substance doivent etre codees manuellement.

## Commande

```bash
python3 scripts/extract_forensic_legal_events.py
```

Sorties agregees :

- `outputs/tables/forensic_legal_prevalence.csv`
- `outputs/tables/forensic_legal_by_psychedelic_group.csv`
- `outputs/tables/forensic_psychedelic_keyword_prevalence.csv`
- `outputs/tables/forensic_legal_keyword_inventory.csv`

Sorties locales non versionnees :

- `data/processed/forensic_legal_rows.csv`
- `data/processed/forensic_legal_validation_queue.csv`

## Validation manuelle

La validation doit coder au minimum :

- `validation_status` : `confirmed`, `probable`, `mentioned_not_event`, `false_positive`, `unclear` ;
- `legal_event_confirmed` : oui/non/incertain ;
- `event_type` : arrestation, violence, vol, accident, mise en danger, etc. ;
- `actor_role` : auteur, victime, temoin, tiers, unclear ;
- `third_party_harm_or_risk` : none, risk_only, injury, death, unclear ;
- `legal_outcome` : none, police_contact, arrest, charge, court, prison, unclear ;
- `substance_contribution` : central, contributory, contextual, unrelated, unclear.

## Analyses possibles

1. Comparer les groupes psychedeliques : LSD vs psilocybine vs phenethylamines/NBOMe vs MDMA.
2. Identifier les evenements a forte valeur medico-legale : arrestation, violence, conduite, mise en danger d'autrui.
3. Croiser avec les marqueurs phenomenologiques : paranoia, perte de controle, peur de mourir, delire, derealisation.
4. Construire une typologie qualitative : crise panique avec appel police, comportement public dangereux, violence defensive/paranoide, accident, judiciarisation.
5. Comparer les co-mentions brutes aux evenements confirmes apres validation.

## Limites

- Les mots police, jail, assault ou court peuvent etre mentionnes sans evenement reel.
- Certaines categories sont asymetriques : un report peut decrire un auteur, une victime, un temoin ou une peur imaginaire.
- Les taux bruts sont des signaux de screening, pas des taux medico-legaux valides.
- Le corpus Erowid est auto-selectionne et oriente vers les experiences saillantes.
