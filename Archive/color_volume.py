import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from shapely.geometry import Polygon


root = tk.Tk()
root.title("Color Gamut Coverage Calculator")
root.geometry("1000x800")

tk.Label(root, text="Enter measured RGB primaries (x, y) for Red, Green, Blue:").grid(row=0, column=0, columnspan=4)
tk.Label(root, text="Red X:").grid(row=1, column=0)
tk.Label(root, text="Red Y:").grid(row=1, column=2)
tk.Label(root, text="Green X:").grid(row=2, column=0)
tk.Label(root, text="Green Y:").grid(row=2, column=2)
tk.Label(root, text="Blue X:").grid(row=3, column=0)
tk.Label(root, text="Blue Y:").grid(row=3, column=2)

rx = tk.Entry(root)
ry = tk.Entry(root)
gx = tk.Entry(root)
gy = tk.Entry(root)
bx = tk.Entry(root)
by = tk.Entry(root)

rx.grid(row=1, column=1)
ry.grid(row=1, column=3)
gx.grid(row=2, column=1)
gy.grid(row=2, column=3)
bx.grid(row=3, column=1)
by.grid(row=3, column=3)

calculate_button = tk.Button(master=root, text="Calculate",
                              command=lambda: calculate_gamut_coverage([(float(rx.get()), float(ry.get())),
                                                                            (float(gx.get()), float(gy.get())),
                                                                                (float(bx.get()), float(by.get()))],
                                                                                    "User Input"))

plot_button = tk.Button(master=root, text="Plot Gamut",
                        command=lambda: plot_gamut([(float(rx.get()), float(ry.get())),
                                                  (float(gx.get()), float(gy.get())),
                                                  (float(bx.get()), float(by.get()))],
                                                  "User Input"))

calculate_button.grid(row=4, column=0, columnspan=4)
plot_button.grid(row=5, column=0, columnspan=4)

# screen_measured_primaries = [(float(rx.get()), float(ry.get())), (float(gx.get()), float(gy.get())), (float(bx.get()), float(by.get()))]

# sRGB Primaries (CIE 1931 xy)
# Red (0.640, 0.330), Green (0.300, 0.600), Blue (0.150, 0.060)
srgb_primaries = [(0.640, 0.330), (0.300, 0.600), (0.150, 0.060)]

# DCI-P3 Primaries (CIE 1931 xy)
# Red (0.680, 0.320), Green (0.265, 0.690), Blue (0.150, 0.060)
dci_p3_primaries = [(0.680, 0.320), (0.265, 0.690), (0.150, 0.060)]

# adobe RGB Primaries (CIE 1931 xy)
# Red (0.640, 0.330), Green (0.210, 0.710), Blue (0.150, 0.060)
adobe_rgb_primaries = [(0.640, 0.330), (0.210, 0.710), (0.150, 0.060)]

# Rec. 2020 Primaries (CIE 1931 xy)
# Red (0.708, 0.292), Green (0.170, 0.797), Blue (0.131, 0.046)
rec2020_primaries = [(0.708, 0.292), (0.170, 0.797), (0.131, 0.046)]

def calculate_gamut_coverage(measured_rgb, display_name="Display"):
    """
    Calculates the percentage coverage of a target gamut by a measured gamut.
    
    :param measured_rgb: List of (x, y) tuples for Red, Green, Blue
    :param target_rgb: List of (x, y) tuples for Red, Green, Blue
    :return: Coverage percentage, Area Ratio percentage
    """

    # Create Polygons
    poly_measured = Polygon(measured_rgb)
    poly_srgb = Polygon(srgb_primaries)
    poly_dci_p3 = Polygon(dci_p3_primaries)
    poly_rec2020 = Polygon(rec2020_primaries)
    
    
    # Calculate areas
    area_measured = poly_measured.area
    area_srgb = poly_srgb.area
    area_dci_p3 = poly_dci_p3.area
    area_rec2020 = poly_rec2020.area

    
    # Calculate intersection (The part of measured that is actually inside target)
    intersection_area_srgb = poly_measured.intersection(poly_srgb).area
    intersection_area_dci_p3 = poly_measured.intersection(poly_dci_p3).area
    intersection_area_rec2020 = poly_measured.intersection(poly_rec2020).area

    
    # Coverage: How much of the target is "covered" by the display
    coverage_srgb = (intersection_area_srgb / area_srgb) * 100
    coverage_dci_p3 = (intersection_area_dci_p3 / area_dci_p3) * 100
    coverage_rec2020 = (intersection_area_rec2020 / area_rec2020) * 100

    # Ratio: Total size of the measured gamut vs the target (can exceed 100%)
    ratio_srgb = (area_measured / area_srgb) * 100
    ratio_dci_p3 = (area_measured / area_dci_p3) * 100
    ratio_rec2020 = (area_measured / area_rec2020) * 100
    
    print(f"--- Display Analysis {display_name} ---")
    print(f"{display_name} sRGB Coverage:          {coverage_srgb:.2f}%")
    print(f"{display_name} DCI-P3 Coverage:        {coverage_dci_p3:.2f}%")
    print(f"{display_name} Rec. 2020 Coverage:     {coverage_rec2020:.2f}%")
    print(f"{display_name} sRGB Area Ratio:        {ratio_srgb:.2f}%")
    print(f"{display_name} DCI-P3 Area Ratio:      {ratio_dci_p3:.2f}%")
    print(f"{display_name} Rec. 2020 Area Ratio:   {ratio_rec2020:.2f}%")

    return

def plot_gamut(measured_rgb, display_name="Display"):
    fig = Figure(figsize=(6, 6))
    
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 0.8)
    ax.set_ylim(0, 0.9)
    ax.set_xlabel('x')
    ax.set_ylabel('y', rotation=0)

    poly = Polygon(measured_rgb)
    x, y = poly.exterior.xy

    ax.fill(x, y, alpha=0.5, label=f'{display_name} Gamut', fc="#ff00ff17", ec='#ff00ff')

    # Plot target gamuts
    # ax.plot(*zip(*srgb_primaries), label='sRGB', color='red')
    # ax.plot(*zip(*dci_p3_primaries), label='DCI-P3', color='green')
    # ax.plot(*zip(*adobe_rgb_primaries), label='Adobe RGB', color='cyan')
    # ax.plot(*zip(*rec2020_primaries), label='Rec. 2020', color='blue')

    
    
    # Plot measured gamut
    # ax.plot(*zip(*measured_rgb), label=display_name, color='magenta')
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(f'Color Gamut Comparison - {display_name}')
    ax.legend()
    ax.grid()
    
    
    canvas = tk.Canvas(root, width=400, height=400)
    canvas.grid(row=6, column=0, columnspan=4)
    

    figure_canvas = FigureCanvasTkAgg(fig, master=root)
    figure_canvas.draw()
    figure_canvas.get_tk_widget().grid(row=6, column=0, columnspan=4)




# # LG LM238WR2-SPE1
# LG_measured_primaries = [
#     (0.675740243, 0.310889965), # Measured Red
#     (0.258883167, 0.682012479), # Measured Green
#     (0.145142905, 0.053797002)  # Measured Blue
# ]

# # JFC 238UHB10E01.V0
# JFC1000_measured_primaries = [
#     (0.649283352, 0.337008056), # Measured Red
#     (0.291831883, 0.659303766), # Measured Green
#     (0.148324881, 0.046066538)  # Measured Blue
# ]


# calculate_gamut_coverage(LG_measured_primaries, "LG LM238WR2-SPE1")
# calculate_gamut_coverage(JFC1000_measured_primaries, "JFC 238UHB10E01.V0")



root.mainloop()