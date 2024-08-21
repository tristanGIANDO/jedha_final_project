# Jedha Final Project

[![project](https://img.shields.io/badge/Planning-%230077B5.svg?logo=github&logoColor=white)](https://github.com/users/tristanGIANDO/projects/6)
[![julie](https://img.shields.io/badge/Julie-%230077B5.svg?&logoColor=white)](https://app.jedha.co/course/projects-prep-ft/project-overview-ft)

# Pitch du projet

Les Etats membres de l'Union européenne ont pour ambition de réduire leurs émissions de 55% en 2030 par rapport à 1990.
La France pour sa part s'est fixée un objectif de réduction de 40% de ses émissions d'ici 2030 et de neutralité carbone d'ici 2050, dont 33 % d’énergies renouvelables dans la consommation totale
En 2022 elle était de 20,7%, dont 11% d'eolien.

Selon l'ADEM, L’électricité produite :
-par l’éolien en mer émet 15,6 g CO2e/kWh,
-par l’éolien terrestre émet 14,1 g CO2e/kWh,
-par photovoltaïque émet 43,9 g CO2e/kWh… et cela descend à 25 g CO2e/kWh pour des panneaux fabriqués en France !

### sources

-https://librairie.ademe.fr/energies-renouvelables-reseaux-et-stockage/2459-energie-eolienne.html
-https://www.connaissancedesenergies.org/fiche-pedagogique/parc-eolien-francais
-https://www.connaissancedesenergies.org/fiche-pedagogique/eoliennes-en-france-quels-debats

### Cartes

-carte vents + eoliennes : https://fabwoj.fr/WINDY/
-carte éoliennes  : https://fabwoj.fr/eol/
-https://macarte.ign.fr/carte/1X3jxe/Carte-EnR-Grand-public

### Data

-https://www.thewindpower.net/index_fr.php > complet mais payant
-https://www.georisques.gouv.fr/donnees/bases-de-donnees/eolien-terrestre > ensemble des eoliennes terrestre / Puissance max / Coordonnée...
-https://www.data.gouv.fr/fr/datasets/5a82655db595081fb6b66415/ > production annuelle par commune (possible comparaison nb eolienne sur commune et production max possible)
-https://openweathermap.org/ > API pour vent

### Data à voir

-https://opendata.reseaux-energies.fr/
-https://www.energiesdelamer.eu/carte-des-emr/
-https://api.gouv.fr/les-api/api-donnees-ouvertes-enedis
-Voir site des DREAL

## Organisation / Schéma de réfléxion

### DATA ANALYSE

Q1 :
- est ce que le réchauffement climatique influe sur la force du vent ? Idem ? Vent à la hausse ? Vent à la baisse ? (il semble que oui : https://www.lesechos.fr/industrie-services/energie-environnement/rechauffement-climatique-le-monde-devient-plus-venteux-1149128#:~:text=Selon%20une%20%C3%A9tude%2C%20la%20vitesse,37%20%25%20d'ici%202024)
Q2 :
- Y a-t-il des zones venteuses différentes :
  - Nouvelles zones venteuse (nous intéresse pour la suite) ? 
  - Les anciennes zones venteuse devenues non venteuses ne nous intéressent pas pour la suite mais si il est possible d'affirmer un changement tant mieux.
- récupérer les données des stations météo concernant la force du vent (sur 50 ans ?) ET l'orientation du vent
- faire des moyennes sur la force du vent et l'orientation (par mois ou par saison ?)
- produire une carte évolutive montrant les moyennes du vent et l'orientation du vent

### DATA SCIENCE :
Q3 : 
- quelles zones pour le futur : 
- rajouter les spots d'implantation d'éolienne (terre / mer ?) pour vérifier les zones non exploités de nos jours et les zones à exploiter dans les 5 ans
  
Q4 :
- si il y a une modification des zones, peut-on éventuellement créer un modèle évolutif des zones futurement venteuses à 10/15/20 ans ?
- voir éventuellement pour un modèle de ML supervisé

Q5 : 
- Une fois que nous avons identifié des zones est-il possible de créer un modèle pour placer nos éoliennes ? Du deep Learning pour placer nos futurs éoliennes sur des images satellites ?
- problématique de récupérer des images satellites en nombre

### PROD :
Q6 : 
- présentation des cartes sur un streamlit. Voir API / MSFLOW selon les donnees produites
- voir déjà si des modèles adaptés existent	

Cette organisation à l'avantage de ne pas avoir à travailler avec la production réellement produite par ville. Mais il est possible de mettre en corrélation nos zones identifiés et la production par ville pour voir si nos hypothèses fonctionnent ( sur la viz ? voir le ML ?)

# Install

1. Dans `Anaconda Prompt`, `cd` jusqu'au repository en local.

2. Executer la commande :

```bash
conda env create -f environment.yml
```

3. Activer l'environnement :

```bash
conda activate jedha_project
```

4. Dans VSCode, sélectionner l'environnement `jedha_project`.

---

Pour mettre à jour l'environnement :

1. Modifier `jedha_final_project/environment.yml`
2. Executer la commande:

```bash
conda env update --file environment.yml
```

# Usage

Les datasets sont stockés sur AWS S3 -> https://us-east-1.console.aws.amazon.com/s3/buckets/jedha-final-project-jrat?region=us-east-1&bucketType=general&tab=objects

**Pour en ajouter :** (peut être privé par défaut)

Executer le fichier `jedha_final_project\data_collection\manage_files_s3.py` avec les chemins des fichiers à ajouter.

**Pour les lire :**

Utiliser le root `https://jedha-final-project-jrat.s3.amazonaws.com` + le nom du fichier.

Exemple :

```py
import pandas as pd

df = pd.read_csv("https://jedha-final-project-jrat.s3.amazonaws.com/parc_national.csv")
df.head()
```
