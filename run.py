import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from shapely.geometry import LineString, MultiLineString, box
from shapely.ops import unary_union
import geopandas as gpd

# ---------------------------------------------------------
# 1. Setup Florida bounding box and projection
# ---------------------------------------------------------
proj = ccrs.PlateCarree()
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": proj})
ax.set_extent([-88, -79.5, 24, 31], crs=proj)

# ---------------------------------------------------------
# 2. Add base layers
# ---------------------------------------------------------
ax.add_feature(cfeature.LAND, facecolor="white", zorder=0)
ax.add_feature(cfeature.OCEAN, facecolor="lightblue", zorder=0)
ax.add_feature(cfeature.LAKES.with_scale("10m"),
               facecolor="lightblue", edgecolor='none', alpha=0.6)
ax.add_feature(cfeature.BORDERS.with_scale(
    "10m"), edgecolor='black', linewidth=0.6)
ax.add_feature(cfeature.STATES.with_scale("10m"),
               edgecolor='black', linewidth=1.2)

# ---------------------------------------------------------
# 3. Load the actual coastline geometry from Cartopy's data
# ---------------------------------------------------------
shpfilename = shpreader.natural_earth(
    resolution='10m', category='physical', name='coastline')
reader = shpreader.Reader(shpfilename)
coast_shapes = list(reader.geometries())

# Clip to Florida bounding box
fl_box = box(-88, 24, -79.5, 31)
fl_geoms = [geom.intersection(fl_box)
            for geom in coast_shapes if geom.intersects(fl_box)]
coast_geom = unary_union(fl_geoms)

# ---------------------------------------------------------
# 4. Define coastal regions by longitude
# ---------------------------------------------------------
regions = [
    {"name": "Panhandle", "color": "saddlebrown", "lon_range": [-87.7, -83.5]},
    {"name": "Central", "color": "gold", "lon_range": [-83.5, -80.5]},
    {"name": "South", "color": "darkorange", "lon_range": [-80.5, -79.7]},
]

# ---------------------------------------------------------
# 5. Function to plot colored segments of coastline
# ---------------------------------------------------------


def plot_segment(geom, lon_min, lon_max, color, label):
    if isinstance(geom, (LineString, MultiLineString)):
        for line in getattr(geom, "geoms", [geom]):
            xs, ys = line.xy
            mask = [(lon_min <= x <= lon_max) for x in xs]
            if any(mask):
                plt.plot(
                    [x for x, m in zip(xs, mask) if m],
                    [y for y, m in zip(ys, mask) if m],
                    transform=proj,
                    color=color,
                    linewidth=3,
                    label=label
                )


# ---------------------------------------------------------
# 6. Plot each regional coastline
# ---------------------------------------------------------
for r in regions:
    plot_segment(coast_geom, r["lon_range"][0],
                 r["lon_range"][1], r["color"], r["name"])

# ---------------------------------------------------------
# 7. Final map styling
# ---------------------------------------------------------
ax.legend(loc="lower left", frameon=True)
ax.set_title("Florida Map with True Colored Coastline Regions", fontsize=16)
ax.set_xticks([])
ax.set_yticks([])
plt.tight_layout()
plt.show()
