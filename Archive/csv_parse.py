import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog

def get_csv_file_path():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.lift()
    root.attributes('-topmost', True)  # Bring the file dialog to the front
    file_path = filedialog.askopenfilename(title="Select Screen Measurement CSV file", filetypes=[("CSV files", "*.csv")])
    return file_path

selected_file = get_csv_file_path()

base_name = os.path.basename(selected_file)
model_name = base_name.split(" GammaMeasData")[0]
print(f"Model Name: {model_name}")

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

    # print(f"Successfully loaded {selected_file}")
else:
    print("File selection cancelled.")
    exit()


print(f"Red: ({rx}, {ry})")
print(f"Green: ({gx}, {gy})")
print(f"Blue: ({bx}, {by})")