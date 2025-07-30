import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

import os
from os.path import join, dirname, abspath

# Get the current directory
current_dir = '8023656'

# Find the file path that ends with "_mesh.vtk"
def find_vtk_mesh_file(directory, string="_mesh.vtk"):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(string):
                return join(root, file)
    return None

path_og = find_vtk_mesh_file(current_dir)
path_clipped = find_vtk_mesh_file(current_dir, string= '_clipped_mitral.vtk')

path_flat = find_vtk_mesh_file(current_dir , string= '_filled_flat.vtk')

path_laa = find_vtk_mesh_file(current_dir, string= '_filled_cont_laa.vtk')
path_ripv = find_vtk_mesh_file(current_dir, string= '_filled_cont_ripv.vtk')
path_rspv = find_vtk_mesh_file(current_dir, string= '_filled_cont_rspv.vtk')
path_lspv = find_vtk_mesh_file(current_dir, string= '_filled_cont_lspv.vtk')
path_lipv = find_vtk_mesh_file(current_dir, string= '_filled_cont_lipv.vtk')
path_mv = find_vtk_mesh_file(current_dir, string= '_filled_cont_mv.vtk')
path_edges_1 = find_vtk_mesh_file(current_dir, string= '_filledpath1.vtk')
path_edges_2 = find_vtk_mesh_file(current_dir, string= '_filledpath2.vtk')
path_edges_3 = find_vtk_mesh_file(current_dir, string= '_filledpath3.vtk')
path_edges_4 = find_vtk_mesh_file(current_dir, string= '_filledpath4.vtk')
path_edges_5 = find_vtk_mesh_file(current_dir, string= '_filledpath5.vtk') 
path_edges_6 = find_vtk_mesh_file(current_dir, string= '_filledpath6.vtk')
path_edges_7 = find_vtk_mesh_file(current_dir, string= '_filledpath7.vtk')
path_edges_laa1 = find_vtk_mesh_file(current_dir, string= '_filledpath_laa1.vtk')
path_edges_laa2 = find_vtk_mesh_file(current_dir, string= '_filledpath_laa2.vtk')
path_edges_laa3 = find_vtk_mesh_file(current_dir, string= '_filledpath_laa3.vtk')

# Read the meshes
mesh_flat = pv.read(path_flat)

mesh_og = pv.read(path_og)
mesh_clipped = pv.read(path_clipped)
mesh_laa = pv.read(path_laa)
mesh_ripv = pv.read(path_ripv)
mesh_rspv = pv.read(path_rspv)
mesh_lspv = pv.read(path_lspv)
mesh_lipv = pv.read(path_lipv)
mesh_mv = pv.read(path_mv)

edges1 = pv.read(path_edges_1)
edges2 = pv.read(path_edges_2)
edges3 = pv.read(path_edges_3)
edges4 = pv.read(path_edges_4)
edges5 = pv.read(path_edges_5)
edges6 = pv.read(path_edges_6)
edges7 = pv.read(path_edges_7)
laa1 = pv.read(path_edges_laa1)
laa2 = pv.read(path_edges_laa2)
laa3 = pv.read(path_edges_laa3)

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

boring_cmap = plt.get_cmap('hsv', 200)

# Truncate the colormap
truncated_cmap = truncate_colormap(boring_cmap, 0, 0.8)

# plot side by side with shared camera for the first three meshes
plotter = pv.Plotter(shape=(2, 2))
plotter.set_background('black')
plotter.link_views(views = [0,1,2])  # Link views of all subplots
plotter.subplot(0, 0)
plotter.add_mesh(mesh_og, scalars='scalars', cmap=truncated_cmap, clim=[0.2, 0.55])
plotter.add_text("Original Mesh", position='upper_left', font_size=12, color='white')
plotter.subplot(0, 1)
plotter.add_mesh(mesh_clipped, scalars='scalars', cmap=truncated_cmap, clim=[0.2, 0.55])
plotter.add_text("Clipped Mesh", position='upper_left', font_size=12, color='white')
plotter.subplot(1, 0)
plotter.add_mesh(mesh_laa, line_width=2)
plotter.add_mesh(mesh_ripv, line_width=2)
plotter.add_mesh(mesh_rspv, line_width=2)
plotter.add_mesh(mesh_lspv, line_width=2)
plotter.add_mesh(mesh_lipv, line_width=2)
plotter.add_mesh(mesh_mv, line_width=2)
plotter.add_mesh(edges1, color='red', line_width=.5)
plotter.add_mesh(edges2, color='red', line_width=.5)
plotter.add_mesh(edges3, color='red', line_width=.5)
plotter.add_mesh(edges4, color='red', line_width=.5)
plotter.add_mesh(edges5, color='red', line_width=.5)
plotter.add_mesh(edges6, color='red', line_width=.5)
plotter.add_mesh(edges7, color='red', line_width=.5)
plotter.add_mesh(laa1, color='red', line_width=.5)
plotter.add_mesh(laa2, color='red', line_width=.5)
plotter.add_mesh(laa3, color='red', line_width=.5)
plotter.add_text("Boundaries", position='upper_left', font_size=12, color='white')
plotter.subplot(1, 1)
plotter.add_mesh(mesh_flat, scalars='scalars', cmap=truncated_cmap, clim=[0.2, 0.55])
plotter.add_text("Flattened Mesh", position='upper_left', font_size=12, color='white')
plotter.view_xy()  # Force XY view
plotter.show()

