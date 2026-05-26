import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import colour
from colour.plotting import plot_RGB_colourspaces_in_chromaticity_diagram_CIE1931
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

def get_csv_file_path():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.lift()
    root.attributes('-topmost', True)  # Bring the file dialog to the front
    file_path = filedialog.askopenfilename(title="Select Screen Measurement CSV file", filetypes=[("CSV files", "*.csv")])
    root.destroy()
    return file_path


def get_save_directory():
    root = tk.Tk()
    root.withdraw()
    root.lift()
    root.attributes('-topmost', True)
    save_dir = filedialog.askdirectory(title="Select folder to save the color space plot")
    root.destroy()
    return save_dir

selected_file = get_csv_file_path()

base_name = os.path.basename(selected_file)
model_name = base_name.split(" GammaMeasData")[0]

if selected_file:
    red_df = pd.read_csv(selected_file, skiprows=21, nrows=17, index_col=False)
    rx = red_df.loc[red_df['Tone'] == 255, 'x'].values[0]
    ry = red_df.loc[red_df['Tone'] == 255, 'y'].values[0]

    green_df = pd.read_csv(selected_file, skiprows=41, nrows=17, index_col=False)
    gx = green_df.loc[green_df['Tone'] == 255, 'x'].values[0]
    gy = green_df.loc[green_df['Tone'] == 255, 'y'].values[0]

    blue_df = pd.read_csv(selected_file, skiprows=61, nrows=17, index_col=False)
    bx = blue_df.loc[blue_df['Tone'] == 255, 'x'].values[0]
    by = blue_df.loc[blue_df['Tone'] == 255, 'y'].values[0]

    measured_primaries = [(rx, ry), (gx, gy), (bx, by)]
else:
    print("File selection cancelled.")
    exit()

colourspaces=['sRGB', 'DCI-P3', 'Adobe RGB (1998)', 'Linear Rec.2020']

measured_gamut_poly = Polygon(measured_primaries)
x, y = measured_gamut_poly.exterior.xy

stats_labels = {}
for name in colourspaces:
    cs = colour.RGB_COLOURSPACES[name]
    ref_poly = Polygon(cs.primaries)
    intersection_area = measured_gamut_poly.intersection(ref_poly).area
    coverage = (intersection_area / ref_poly.area) * 100
    area_ratio = (measured_gamut_poly.area / ref_poly.area) * 100
    stats_labels[name] = f"{name}\n  (Cov: {coverage:.2f}%, Ratio: {area_ratio:.2f}%)"

figure, axes = plot_RGB_colourspaces_in_chromaticity_diagram_CIE1931(colourspaces=['sRGB', 'DCI-P3', 'Adobe RGB (1998)', 'Linear Rec.2020'], 
                                                                     show = False, 
                                                                     plot_kwargs={'marker': 'None'},
                                                                     title=f'{model_name} | CIE 1931',
                                                                     show_whitepoints=False
                                                                     )

figure.canvas.manager.set_window_title(f'{model_name} Color Space Plot')
figure.patch.set_alpha(1.0)


axes.fill(x, y, label=f'{model_name}', fc="#000000B4", ec="#000000")

handles, labels = axes.get_legend_handles_labels()
new_labels = []

for label in labels:
    if label in stats_labels:
        new_labels.append(stats_labels[label])
    else:
        new_labels.append(label)

axes.legend(handles, new_labels, loc='upper right', fontsize=8, labelspacing=1.0)

save_dir = get_save_directory()
if save_dir:
    save_path = os.path.join(save_dir, f'{model_name}_color_space_plot.png')
    plt.savefig(save_path, dpi=250, bbox_inches='tight')
    print(f'Saved plot to: {save_path}')
else:
    print('Save cancelled. Plot will not be saved.')

plt.show()

