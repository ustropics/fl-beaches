import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from shapely.geometry import LineString, MultiLineString, box
from shapely.ops import unary_union
import matplotlib.patches as mpatches

# ---------------------------------------------------------
# 1. Setup Florida bounding box and projection
# ---------------------------------------------------------
proj = ccrs.PlateCarree()
fig, ax = plt.subplots(figsize=(15, 15), subplot_kw={"projection": proj})
ax.set_extent([-88, -79.5, 24, 31], crs=proj)

# ---------------------------------------------------------
# 2. Add base layers
# ---------------------------------------------------------
ax.add_feature(cfeature.LAND, facecolor="#1B1B1B", zorder=0)
ax.add_feature(cfeature.OCEAN, facecolor="lightblue", zorder=0)
ax.add_feature(cfeature.LAKES.with_scale("10m"),
               facecolor="lightblue", edgecolor='lightgrey', alpha=1)
ax.add_feature(cfeature.BORDERS.with_scale(
    "10m"), edgecolor='black', linewidth=0.6)
ax.add_feature(cfeature.STATES.with_scale("10m"),
               edgecolor='lightgrey', linewidth=1.2)

# ---------------------------------------------------------
# 2.5. Add Florida counties using shapefile
# ---------------------------------------------------------
reader = shpreader.Reader('ne_10m_admin_2_counties.shp')

fl_box = box(-88, 24, -79.5, 31)
fl_counties = [record.geometry for record in reader.records()
               if record.attributes.get('REGION') == 'FL' and record.geometry.intersects(fl_box)]

if not fl_counties:
    fl_counties = [record.geometry for record in reader.records()
                   if record.attributes.get('ISO_3166_2') == 'US-FL' and record.geometry.intersects(fl_box)]

COUNTIES = cfeature.ShapelyFeature(
    fl_counties, ccrs.PlateCarree(), facecolor='none', edgecolor='gray', linewidth=0.5)
ax.add_feature(COUNTIES, zorder=1)

# ---------------------------------------------------------
# 3. Load the coastline geometry
# ---------------------------------------------------------
shpfilename = shpreader.natural_earth(
    resolution='10m', category='physical', name='coastline')
reader = shpreader.Reader(shpfilename)
coast_shapes = list(reader.geometries())

fl_geoms = [geom.intersection(fl_box)
            for geom in coast_shapes if geom.intersects(fl_box)]
coast_geom = unary_union(fl_geoms)

# ---------------------------------------------------------
# 4. Define coastal regions by longitude (distinct colors)
# ---------------------------------------------------------
regions = [
    {"name": "Panhandle (pure white quartz)",
     "color": "#FFF5CC", "lon_range": [-87.7, -84.5]},

    {"name": "Central Gulf (quartz + shell mix)",
     "color": "#FFD966", "lon_range": [-84.5, -82.2]},

    {"name": "SW Florida (shell & carbonate rich)",
     "color": "#E4A672", "lon_range": [-82.2, -81.0]},

    {"name": "Central East (quartz-dominant)",
     "color": "#F8CBA6", "lon_range": [-81.0, -80.5]},

    {"name": "NE Florida (coquina & shell sand)",
     "color": "#C68642", "lon_range": [-82.0, -81.0]},

    {"name": "Southeast (coral/organic carbonate)",
     "color": "#D95B43", "lon_range": [-80.5, -79.7]},
]

# ---------------------------------------------------------
# 5. Function to plot colored coastline segments
# ---------------------------------------------------------


def plot_segment(geom, lon_min, lon_max, color, label):
    clip_box = box(lon_min, 23, lon_max, 31.5)
    clipped = geom.intersection(clip_box)

    if clipped.is_empty:
        return

    if isinstance(clipped, (LineString, MultiLineString)):
        if isinstance(clipped, LineString):
            clipped = MultiLineString([clipped])
        for line in clipped.geoms:
            xs, ys = line.xy
            plt.plot(xs, ys, transform=proj, color=color,
                     linewidth=4, solid_capstyle='round', label=label)
    elif hasattr(clipped, 'geoms'):
        for subgeom in clipped.geoms:
            if isinstance(subgeom, (LineString, MultiLineString)):
                plot_segment(subgeom, lon_min, lon_max, color, label)


# ---------------------------------------------------------
# 6. Plot each region
# ---------------------------------------------------------
for r in regions:
    plot_segment(coast_geom, r["lon_range"][0],
                 r["lon_range"][1], r["color"], r["name"])

# ---------------------------------------------------------
# 6.5. Legend (region + description)
# ---------------------------------------------------------
legend_patches = [
    mpatches.Patch(color=r["color"], label=r["name"])
    for r in regions
]

leg = ax.legend(
    handles=legend_patches,
    loc="lower left",
    bbox_to_anchor=(0.02, 0.05),
    fontsize=12,
    title="Florida Coastal Sand Composition by Region",
    title_fontsize=16,
    frameon=True,
    facecolor="#2E2E2E",
    edgecolor="lightgray",
    labelspacing=0.7,
    handlelength=1.8,
)

for text in leg.get_texts():
    text.set_color("white")
leg.get_title().set_color("white")
leg.get_frame().set_alpha(0.9)

# ---------------------------------------------------------
# 7. Title and subtitle (white text)
# ---------------------------------------------------------
ax.set_title(
    "Regional Variations in Florida Beach Sand Composition",
    fontsize=16,
    color="black",
    pad=10
)

# Remove ticks
ax.set_xticks([])
ax.set_yticks([])

# ---------------------------------------------------------
# 8. Save at high resolution (no display)
# ---------------------------------------------------------
output_path = "florida_sand_regions_map.png"
plt.savefig(
    output_path,
    dpi=600,
    bbox_inches="tight",
    facecolor=fig.get_facecolor(),
    edgecolor="none"
)

print(f"Map saved at high resolution: {output_path}")
