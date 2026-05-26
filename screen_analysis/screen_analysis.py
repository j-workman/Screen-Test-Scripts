import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import pandas as pd
import os
import colour
from colour.plotting import plot_RGB_colourspaces_in_chromaticity_diagram_CIE1931
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon

class ScreenColorAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Color Analysis App")
        self.root.geometry("700x500")
        self.root.configure(bg="#f5f5f7")
        self.gamma_file_path = None
        self.uniformity_file_path = None

        # --- Dual-Purpose Button (Click OR Drag & Drop) ---
        self.drop_gamma_button = tk.Button(
            root, 
            text="📥 Click to Browse or Drag & Drop GammaMeasData.CSV here", 
            bg="#ffffff", 
            fg="#333333",
            font=("Helvetica", 12, "bold"),
            relief="groove", 
            bd=2,
            cursor="hand2",
            command=self.open_gamma_file_dialog  # Triggers when clicked
        )
        self.drop_gamma_button.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Register the button as a drag-and-drop target
        self.drop_gamma_button.drop_target_register(DND_FILES)
        self.drop_gamma_button.dnd_bind('<<Drop>>', self.handle_drop)

        self.plot_color_space_button = tk.Button(
            root, 
            text="Calculate and Plot Color Space", 
            bg="#4caf50", 
            fg="#ffffff",
            font=("Helvetica", 12, "bold"),
            relief="groove", 
            bd=2,
            cursor="hand2",
            command=self.plot_color_space,
            state='disabled'  # Initially disabled until a file is loaded
        )
        self.plot_color_space_button.pack(padx=20, pady=10)

        self.drop_uniformity_button = tk.Button(
            root, 
            text="📥 Click to Browse or Drag & Drop Uniformity ColorMeasurement.CSV here", 
            bg="#ffffff", 
            fg="#333333",
            font=("Helvetica", 12, "bold"),
            relief="groove", 
            bd=2,
            cursor="hand2",
            command=self.open_uniformity_file_dialog  # Triggers when clicked
        )
        self.drop_uniformity_button.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Register the button as a drag-and-drop target
        self.drop_uniformity_button.drop_target_register(DND_FILES)
        self.drop_uniformity_button.dnd_bind('<<Drop>>', self.handle_drop)

        self.uniformity_calculate_button = tk.Button(
            root, 
            text="Calculate and Map Uniformity", 
            bg="#4caf50", 
            fg="#ffffff",
            font=("Helvetica", 12, "bold"),
            relief="groove", 
            bd=2,
            cursor="hand2",
            command=self.calculate_uniformity,
            state='disabled'  # Initially disabled until a file is loaded
        )
        self.uniformity_calculate_button.pack(padx=20, pady=10)

    def open_gamma_file_dialog(self):
        """Open file dialog for GammaMeasData CSV."""
        file_path = filedialog.askopenfilename(
            title="Select a GammaMeasData CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.validate_and_load_gamma(file_path)

    def open_uniformity_file_dialog(self):
        """Open file dialog for UniformityData CSV."""
        file_path = filedialog.askopenfilename(
            title="Select a UniformityData CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.validate_and_load_uniformity(file_path)

    def handle_drop(self, event):
        """Handles the event when a file is dragged and dropped onto a button."""
        files = self.root.tk.splitlist(event.data)
        if not files:
            return
        widget = getattr(event, 'widget', None)
        file_path = files[0]
        if widget is self.drop_gamma_button:
            self.validate_and_load_gamma(file_path)
        elif widget is self.drop_uniformity_button:
            self.validate_and_load_uniformity(file_path)

    def validate_and_load_gamma(self, file_path):
        """Validates that the file is a CSV and updates the UI."""
        if file_path.lower().endswith('.csv'):
            file_name = file_path.split('/')[-1]
            # Visual feedback on successful load
            self.drop_gamma_button.config(
                text=f"✅ Loaded: {file_name}\n(Click or drop another to replace)", 
                bg="#e8f5e9", 
                fg="#2e7d32"
            )
            self.gamma_file_path = file_path
            self.process_csv(file_path)
        else:
            messagebox.showerror("Invalid File Type", "Please select or drop a valid .csv file.")

    def process_csv(self, file_path):
        """Reads the CSV file and displays it in the preview text area."""
        try:
            df = pd.read_csv(file_path)
            self.plot_color_space_button.config(state='normal')  # Enable the calculate button after loading a file
            # self.text_area.config(state='normal')
            # self.text_area.delete(1.0, tk.END)
            # self.text_area.insert(tk.END, df.head(5).to_string(index=False))
            # self.text_area.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error Reading File", f"Could not read the CSV file.\n\nDetails: {e}")

    def validate_and_load_uniformity(self, file_path):
        """Validates uniformity CSV and updates the uniformity UI."""
        if file_path.lower().endswith('.csv'):
            file_name = file_path.split('/')[-1]
            self.drop_uniformity_button.config(
                text=f"✅ Loaded: {file_name}\n(Click or drop another to replace)",
                bg="#e8f5e9",
                fg="#2e7d32"
            )
            self.uniformity_file_path = file_path
            self.process_uniformity_csv(file_path)
        else:
            messagebox.showerror("Invalid File Type", "Please select or drop a valid .csv file.")

    def process_uniformity_csv(self, file_path):
        """Reads the Uniformity CSV and enables uniformity calculation UI."""
        try:
            df = pd.read_csv(file_path)
            self.uniformity_calculate_button.config(state='normal')
        except Exception as e:
            messagebox.showerror("Error Reading File", f"Could not read the CSV file.\n\nDetails: {e}")

    def plot_color_space(self):
        try:
            if not self.gamma_file_path:
                messagebox.showerror("No File Loaded", "Please load a GammaMeasData CSV before calculating and plotting.")
                return
            file_path = self.gamma_file_path
            base_name = os.path.basename(file_path)
            model_name = base_name.split(" GammaMeasData")[0]

            if file_path:
                red_df = pd.read_csv(file_path, skiprows=21, nrows=17, index_col=False)
                rx = red_df.loc[red_df['Tone'] == 255, 'x'].values[0]
                ry = red_df.loc[red_df['Tone'] == 255, 'y'].values[0]

                green_df = pd.read_csv(file_path, skiprows=41, nrows=17, index_col=False)
                gx = green_df.loc[green_df['Tone'] == 255, 'x'].values[0]
                gy = green_df.loc[green_df['Tone'] == 255, 'y'].values[0]

                blue_df = pd.read_csv(file_path, skiprows=61, nrows=17, index_col=False)
                bx = blue_df.loc[blue_df['Tone'] == 255, 'x'].values[0]
                by = blue_df.loc[blue_df['Tone'] == 255, 'y'].values[0]

                measured_primaries = [(rx, ry), (gx, gy), (bx, by)]
            else:
                print("File selection cancelled.")
                exit()
            footer_row = blue_df.iloc[-1]
            date_value = footer_row.iloc[-2]
            time_value = footer_row.iloc[-1]
            timestamp_text = f"{date_value} {time_value}"

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
                                                                                title=f'{model_name} | CIE 1931\n{timestamp_text}',
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
            plt.rcParams['savefig.dpi'] = 200
            plt.show()


        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during calculation and plotting.\n\nDetails: {e}")

    def calculate_uniformity(self):
        try:
            if not self.uniformity_file_path:
                messagebox.showerror("No File Loaded", "Please load a 'Uniformity ColorMeasurement.CSV' before calculating uniformity.")
                return
            file_path = self.uniformity_file_path
            base_name = os.path.basename(file_path)
            model_name = base_name.split(" Uniformity ColorMeasurement")[0]

            # Read the CSV. The file contains 16 rows including the header row
            # and 22 columns including the index column. We'll take the first
            # 15 data rows (skip the header) and attempt to extract the
            # Always use the 7th column by position.
            df = pd.read_csv(file_path)
            num_data_rows = max(0, 16 - 1)

            if df.shape[1] < 7:
                messagebox.showerror("Missing Column", "The loaded CSV does not have enough columns to locate column Lv (7th column).")
                return

            lv_col_name = df.columns[6]
            lv_series = df[lv_col_name]
            lv_values = lv_series.iloc[:num_data_rows].values if num_data_rows > 0 else lv_series.values

            # Read date and time from the final row's two last columns
            footer_row = df.iloc[-1]
            date_value = footer_row.iloc[-3]
            time_value = footer_row.iloc[-2]
            timestamp_text = f"{date_value} {time_value}"

            # Ensure we have exactly 15 values for the 5x3 grid
            if len(lv_values) < 15:
                messagebox.showerror("Insufficient Data", "Uniformity CSV does not contain 15 data values in column 7.")
                return

            grid_vals = np.array(lv_values[:15], dtype=float).reshape((3, 5))

            fig, ax = plt.subplots(figsize=(6, 4))
            fig.canvas.manager.set_window_title(f'{model_name} Uniformity Plot')
            fig.patch.set_alpha(1.0)

            im = ax.imshow(grid_vals, cmap='cividis', aspect='equal', origin='upper')
            ax.set_title(f"{model_name} Luminance Uniformity\n{timestamp_text}", fontsize=12)

            # Label cells with index (1-15), value, and percent difference from average
            avg_val = float(grid_vals.mean())
            luminance_variation = grid_vals.min() / grid_vals.max() * 100 if grid_vals.max() > 0 else 0
            for r in range(3):
                for c in range(5):
                    idx = r * 5 + c + 1
                    val = float(grid_vals[r, c])
                    if avg_val == 0:
                        delta_pct = 0.0
                    else:
                        delta_pct = (val - avg_val) / avg_val * 100.0
                    if val < avg_val:
                        ax.text(c, r, f"{idx}\n{val:.2f}\n{delta_pct:+.1f}%", ha='center', va='center', color='white', fontsize=10)
                    else:
                        ax.text(c, r, f"{idx}\n{val:.2f}\n{delta_pct:+.1f}%", ha='center', va='center', color='black', fontsize=10)

            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='Luminance cd/m²')
            plt.tight_layout()
            plt.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
            plt.xlabel(f"Avg. Luminance: {avg_val:.2f} cd/m²    Luminance Variation: {luminance_variation:.2f}%", fontsize=10)
            plt.rcParams['savefig.dpi'] = 200
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while calculating uniformity.\n\nDetails: {e}")
        

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ScreenColorAnalysisApp(root)
    root.mainloop()