# REJEU MISSION COMPLET 13/03/25

## Dépendances : 
Pour que le script Python fonctionne bien, vérifier que les bibliothèques suivantes sont bien installées (disponibles via pip pour Python 3.x): 

    import matplotlib.pyplot
    from matplotlib.animation
    import numpy 
    import contextily
    import geopandas
    import xyzservices.providers
    import os
    import rasterio
    import rasterio.plot
    from shapely.geometry import Point
    import matplotlib.colors
    import matplotlib.cm
    from matplotlib.collections import LineCollection
    from datetime import datetime, timedelta 

Vérifier également que la connection à internet fonctionne, pour télécharger les cartes de fond (attention aux problèmes de pare feu).

## Description
Ce code, qui utilise une application Matlab App et un script python en simultané, permet de rejouer la mission ballon du 13/03/2025 à partir des logs de l'arduino principale et des logs de la kikiwi embarquée. Vérifiez bien que les deux fichiers de logs (respectivement *log_test_interpolated_cropped* et *SpacecraftIMT_Maps067_cropped* sont dans le même dossier que les exécutables).

## Synchronisation Python / Matlab
Il n'y a pas de synchronisation propre entre python et matlab, les ticks respectifs sont ajustés "à la mano" et doivent être fixés plus précisément, ou alors une architecture de synchronisation doit être implémetée.

## Gestion des délais
* Dans le script Python, le tick se règle à partir de la variable d'input *interval* lors de l'appel de FuncAnimation (fixée à 250ms par défaut). Elle corresponds à la période de rafraichissement.
* Dans Matlab, la période de rafraichissement se modifie dans la variable *Periode*, fixée à 0.01s par défaut.

Attention à être vigilant aux périodes d'échantillonage des logs (différentes entre elles !)

## Mise en marche
Ouvrir le fichier .mlapp dans Matlab, puis l'exécuter.