import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from clip_aux_functions import *

# plot two side by side





path_og = r"F:\CARTO_MAT_FILES\2021894\FA\FA_05_14_2025_17-08-30_1-AE_vtk_mesh_clipped.vtk"
mesh_flat = pv.read(path_og)

path_filled = r"F:\CARTO_MAT_FILES\2021894\FA\FA_05_14_2025_17-08-30_1-AE_vtk_mesh_clipped_filled_flat.vtk"
mesh_filled = pv.read(path_filled)

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

boring_cmap = plt.get_cmap('hsv', 200)

# Truncate the colormap
truncated_cmap = truncate_colormap(boring_cmap, 0, 0.8)

# plot one mesh

# plot side by side
plotter = pv.Plotter(shape=(1, 2))
plotter.set_background('black')
plotter.subplot(0, 0)
plotter.add_mesh(mesh_filled, scalars='scalars', cmap=truncated_cmap, clim=[0.2, 0.55])
plotter.add_text("Original Mesh", position='upper_left', font_size=12, color='white')
plotter.subplot(0, 1)
plotter.add_mesh(mesh_flat, scalars='scalars', cmap=truncated_cmap, clim=[0.2, 0.45])
plotter.add_text("Flattened Mesh", position='upper_left', font_size=12, color='white')
plotter.view_xy()  # Force XY view
plotter.show()

