import tkinter as tk
from tkinter import messagebox
from shapely.geometry import Polygon

# sRGB Primaries (CIE 1931 xy)
# Red (0.640, 0.330), Green (0.300, 0.600), Blue (0.150, 0.060)
srgb_primaries = [(0.640, 0.330), (0.300, 0.600), (0.150, 0.060)]

# DCI-P3 Primaries (CIE 1931 xy)
# Red (0.680, 0.320), Green (0.265, 0.690), Blue (0.150, 0.060)
dci_p3_primaries = [(0.680, 0.320), (0.265, 0.690), (0.150, 0.060)]

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




# LG LM238WR2-SPE1
LG_measured_primaries = [
    (0.675740243, 0.310889965), # Measured Red
    (0.258883167, 0.682012479), # Measured Green
    (0.145142905, 0.053797002)  # Measured Blue
]

# JFC 238UHB10E01.V0
JFC1000_measured_primaries = [
    (0.649283352, 0.337008056), # Measured Red
    (0.291831883, 0.659303766), # Measured Green
    (0.148324881, 0.046066538)  # Measured Blue
]


calculate_gamut_coverage(LG_measured_primaries, "LG LM238WR2-SPE1")
calculate_gamut_coverage(JFC1000_measured_primaries, "JFC 238UHB10E01.V0")