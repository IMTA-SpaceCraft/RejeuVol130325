import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import contextily as ctx
import geopandas as gpd
import xyzservices.providers as xyz
import os
import rasterio
import rasterio.plot
from shapely.geometry import Point
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from matplotlib.collections import LineCollection
from datetime import datetime, timedelta  # Ajout pour la conversion horaire

# Dossier de cache
cache_folder = "./tile_cache/"
os.makedirs(cache_folder, exist_ok=True)

# Fonction pour pré-télécharger les tuiles
def download_tiles(s, w, n, e, zoom=10, cache_folder=cache_folder):
    raster_path = os.path.join(cache_folder, "tiles.tif")
    ctx.bounds2raster(w, s, e, n, zoom=zoom, source=xyz.CartoDB.Voyager, path=raster_path)
    return raster_path

# Conversion DDM -> Degrés décimaux
def convert_to_decimal(coord, direction):
    try:
        deg = int(coord[:2 if direction in ['N', 'S'] else 3])
        min_ = float(coord[2 if direction in ['N', 'S'] else 3:])
        decimal = deg + min_ / 60
        return decimal if direction in ['N', 'E'] else -decimal
    except:
        return None

# Lecture du fichier avec gestion des valeurs manquantes
def read_log(filename):
    coords = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split(";")
            if len(parts) < 5 or '-' in parts:
                continue
            date, time_, lat, lon, alt = parts[:5]
            if not all([lat, lon, alt]) or '-' in (lat+lon+alt):
                continue
            try:
                lat_dd = convert_to_decimal(lat[:-1], lat[-1])
                lon_dd = convert_to_decimal(lon[:-1], lon[-1])
                alt_m = int(alt)
                timestamp = f"{date} {time_}"
                if lat_dd is not None and lon_dd is not None:
                    coords.append((lon_dd, lat_dd, alt_m, timestamp))
            except:
                continue
    return coords

# Charger les positions
current_folder = os.path.dirname(os.path.abspath(__file__))
positions = read_log(current_folder + "\\SpacecraftIMT_Maps067_cropped.txt")
if not positions:
    raise ValueError("Aucune donnée valide trouvée.")

lons = [p[0] for p in positions]
lats = [p[1] for p in positions]
alts = [p[2] for p in positions]
times = [p[3] for p in positions]

# Transformation en projection Web Mercator
gdf = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in zip(lons, lats)], crs="EPSG:4326")
gdf = gdf.to_crs(epsg=3857)
xs = gdf.geometry.x.values
ys = gdf.geometry.y.values
zs = alts

# Création du colormap basé sur l'altitude
norm = mcolors.Normalize(vmin=min(zs), vmax=max(zs))
cmap = plt.get_cmap("plasma")

# Setup de la figure
fig, ax = plt.subplots(figsize=(10, 8))
satellite_dot, = ax.plot([], [], 'ro', markersize=6)
text_time = ax.text(0.02, 0.95, '', transform=ax.transAxes)

# Définition des limites pour le cache et téléchargement des tuiles
s, w, n, e = min(ys)-3500, min(xs)-3500, max(ys)+3500, max(xs)+3500
raster_file = download_tiles(s, w, n, e)

# Charger les tuiles pré-téléchargées avec rasterio
with rasterio.open(raster_file) as raster:
    rasterio.plot.show(raster, ax=ax)

ax.set_xlim(w, e)
ax.set_ylim(s, n)
ax.set_title("Trajectoire satellite sur carte OpenStreetMap (x30)")

plt.draw()
plt.xlabel("Longitude (proj.)")
plt.ylabel("Latitude (proj.)")

# Ajout d'une barre de couleur indiquant l'altitude
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbar_ax)
cb.set_label("Altitude (m)")

# Création de la collection de lignes colorées
segments = [((xs[i], ys[i]), (xs[i+1], ys[i+1])) for i in range(len(xs)-1)]
colors = [cmap(norm(zs[i])) for i in range(len(xs)-1)]
line_collection = LineCollection(segments, cmap=cmap, norm=norm, linewidth=2)
line_collection.set_array(np.array(zs[:-1]))
ax.add_collection(line_collection)

# Animation
def animate(i):
    satellite_dot.set_data(xs[i], ys[i])

    # Conversion et affichage formaté de l'heure
    dt = datetime.strptime(times[i], "%d%m%y %H%M%S") + timedelta(hours=1)
    formatted_time = f"{dt.hour:02d} H {dt.minute:02d} M {dt.second:02d} S"

    text_time.set_text(f"Time: {formatted_time}\nAlt: {zs[i]} m")
    line_collection.set_segments(segments[:i+1])
    return satellite_dot, text_time, line_collection

ani = FuncAnimation(fig, animate, frames=len(xs), interval=250, repeat=True)

plt.tight_layout()
plt.show()
