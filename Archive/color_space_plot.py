import colour
from colour.plotting import plot_RGB_colourspaces_in_chromaticity_diagram_CIE1931
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

colourspaces=['sRGB', 'DCI-P3', 'Adobe RGB (1998)', 'Linear Rec.2020']

display_name = "Custom Gamut"

custom_points_xy = [
    (0.675740243, 0.310889965), # Measured Red
    (0.258883167, 0.682012479), # Measured Green
    (0.145142905, 0.053797002)  # Measured Blue
]

custom_gamut_poly = Polygon(custom_points_xy)
x, y = custom_gamut_poly.exterior.xy

stats_labels = {}
for name in colourspaces:
    cs = colour.RGB_COLOURSPACES[name]
    ref_poly = Polygon(cs.primaries)
    intersection_area = custom_gamut_poly.intersection(ref_poly).area
    coverage = (intersection_area / ref_poly.area) * 100
    area_ratio = (custom_gamut_poly.area / ref_poly.area) * 100
    stats_labels[name] = f"{name}\n  (Cov: {coverage:.2f}%, Ratio: {area_ratio:.2f}%)"

figure, axes = plot_RGB_colourspaces_in_chromaticity_diagram_CIE1931(colourspaces=['sRGB', 'DCI-P3', 'Adobe RGB (1998)', 'Linear Rec.2020'], 
                                                                     show = False, 
                                                                     plot_kwargs={'marker': 'None'},
                                                                     title=f'{display_name} | CIE 1931',
                                                                     show_whitepoints=False
                                                                     )

axes.fill(x, y, label=f'{display_name}', fc="#000000B4", ec="#000000")

handles, labels = axes.get_legend_handles_labels()
new_labels = []

for label in labels:
    if label in stats_labels:
        new_labels.append(stats_labels[label])
    else:
        new_labels.append(label)

axes.legend(handles, new_labels, loc='upper right', fontsize=8, labelspacing=1.0)

plt.show()

