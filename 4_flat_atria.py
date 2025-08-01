"""
    Copyright (c) - Marta Nunez Garcia
    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
    Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
    any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
    without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
    Public License for more details. You should have received a copy of the GNU General Public License along with this
    program. If not, see <http://www.gnu.org/licenses/>.
"""

"""
    Implementation of left atrial (LA) flattening in "Fast quasi-conformal regional flattening of the left atrium", Nunez-Garcia, Marta, et al., 2018, arXiv preprint arXiv:1811.06896

    Input: LA mesh with clipped & filled holes (PVs, LAA) and only 1 hole corresponding to MV.
    Output: Flat (2D) version of input mesh.
    Usage: python 4_flat_atria.py --meshfile data/mesh_clipped_c.vtk

    Conformal flattening considering 6 boundaries (4 PVs + LAA + MV) and additional regional constraints
    Regional constraints fitted using segments: s1,s2,s3,s4,s5,s6,s7, s8a and s8b
    Boundaries fitted using segments: s9, s10, s11, s12, rspv_s{1,2,3}, ripv_s{1,2,3}, lipv_s{1,2,3}, lspv_s{1,2,3}, laa_s{1,2}
    Constraints (division lines) are modified to enforce proportional distribution of points in the holes.
"""

from aux_functions import *
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--meshfile', type=str, metavar='PATH', help='path to input mesh with filled holes', required=True)
parser.add_argument('--meshfile_o', type=str, metavar='PATH', help='path to open input mesh', required=True)
parser.add_argument('--save_conts', type=bool, default=True, help='set to true to save mesh contours/contraints')
parser.add_argument('--save_final_paths', type=bool, default=True, help='set to true to save modified dividing paths')
parser.add_argument('--countors', action='store_false')
parser.add_argument('--cut_laa', type=int, default=0, help='Set to 1 for anatomies with LAA and MV clipped')
args = parser.parse_args()

if os.path.isfile(args.meshfile)==False:
    sys.exit('ERROR: input file does not exist')
else:
    mesh = readvtk(args.meshfile)
    m_open = readvtk(args.meshfile_o)

seeds_filename = args.meshfile[0:len(args.meshfile)-4] + '_seeds_for_flat.vtk'
if os.path.isfile(seeds_filename)==False:
    sys.exit('ERROR: input file containing seeds for flat does not exist. Create it using: 3_divide_LA.py')
else:
    m_seeds = readvtk(seeds_filename)
to_be_flat_filename = args.meshfile[0:len(args.meshfile)-4] + '_to_be_flat.vtk'
m_out = args.meshfile[0:len(args.meshfile) - 4] + '_flat.vtk'

countors = args.countors

##################   Template creation. Define position and radius of PV holes, and radius disk. Adapt to input mesh.    ##################
rdisk = 0.5
pv_centers = np.zeros([2, 4])
r_min = 0.03
rhole_lipv = r_min
rhole_lspv = 1.1*r_min
rhole_ripv = 1.1*r_min
rhole_rspv = 1.35*r_min
rhole_laa = 1.35*r_min
laa_disp_x = 0.03  # displacement of LAA wrt LSPV (in x direction, to the left)

px_ref = -0.25
py_ref = -0.10
left_carina_length = 0.175
right_carina_length = 1.5 * left_carina_length   # real proportions, do not separate more, it induces distortion close to the holes
pwall_width = 2.6 * left_carina_length
sep_lspv_laa = 1.2
t_v5 = np.pi / 8
t_v6 = 2*np.pi - np.pi/6
t_v7 = np.pi + np.pi / 6
t_v8 = 3 * np.pi / 4 - np.pi/40

# rspv
pv_centers[0, 0] = px_ref + pwall_width
pv_centers[1, 0] = py_ref + left_carina_length + (right_carina_length - left_carina_length) / 2
# ripv
pv_centers[0, 1] = px_ref + pwall_width
pv_centers[1, 1] = py_ref - (right_carina_length - left_carina_length) / 2
# lipv
pv_centers[0, 2] = px_ref
pv_centers[1, 2] = py_ref
# lspv
pv_centers[0, 3] = px_ref
pv_centers[1, 3] = py_ref + left_carina_length
# LAA
laa_hole_center_x = px_ref - laa_disp_x
laa_hole_center_y = py_ref + left_carina_length + left_carina_length * sep_lspv_laa  # si lipv esta en (-.25, -.10)

xhole_center = pv_centers[0, :]
yhole_center = pv_centers[1, :]

# define the proportion of points in each of the PV segments
alpha = np.arctan(np.divide(laa_disp_x, laa_hole_center_y - pv_centers[1, 3]))  # angle of the line connecting LSPV and LAA
proportions = define_pv_segments_proportions(t_v5, t_v6, t_v7, alpha)
propn_rspv_s1, propn_rspv_s2, propn_rspv_s3 = proportions[0, :]
propn_ripv_s1, propn_ripv_s2, propn_ripv_s3 = proportions[1, :]
propn_lipv_s1, propn_lipv_s2, propn_lipv_s3 = proportions[2, :]
propn_lspv_s1, propn_lspv_s2, propn_lspv_s3 = proportions[3, :]

v5 = m_seeds.GetPoint(5)   # Seeds in the MV
v6 = m_seeds.GetPoint(6)
v7 = m_seeds.GetPoint(7)
v8 = m_seeds.GetPoint(8)

# define target coordinates in the disk and get them separated
coordinates = define_disk_template(rdisk, rhole_rspv, rhole_ripv, rhole_lipv, rhole_lspv, rhole_laa, xhole_center, yhole_center,laa_hole_center_x, laa_hole_center_y, t_v5, t_v6, t_v7, t_v8)
v1r_x, v1r_y, v1d_x, v1d_y, v1l_x, v1l_y, v2u_x, v2u_y, v2r_x, v2r_y, v2l_x, v2l_y, v3u_x, v3u_y, v3r_x, v3r_y, v3l_x, v3l_y, v4r_x, v4r_y, v4u_x, v4u_y, v4d_x, v4d_y, vlaad_x, vlaad_y, vlaau_x, vlaau_y, p5_x, p5_y, p6_x, p6_y, p7_x, p7_y, p8_x, p8_y = get_coords(coordinates)

##################    Open PVs and LAA holes (get 'to_be_flat_mesh'), identify contours and dividing paths in the to_be_flat mesh   ##################
# m_open = cleanpolydata(pointthreshold(mesh, 'hole', 0, 0))
m_open = DeleteNonTriangularFaces(m_open)  # Delete non-triangular faces, otherwise flat_w_constraints will not work

writevtk(m_open, to_be_flat_filename)
# contours


if countors:
    if args.cut_laa == 0:
        cont_rspv, cont_ripv, cont_lipv, cont_lspv, cont_mv, cont_laa = extract_LA_contours(m_open, args.meshfile, args.save_conts, args.cut_laa)
    else:
        cont_rspv, cont_ripv, cont_lipv, cont_lspv, cont_mv = extract_LA_contours(m_open, args.meshfile, args.save_conts, args.cut_laa)
        cont_laa = None
else:
    
    #load files
    cont_rspv = readvtk(args.meshfile[0:len(args.meshfile)-4] + '_cont_rspv.vtk')
    cont_ripv = readvtk(args.meshfile[0:len(args.meshfile)-4] + '_cont_ripv.vtk')
    cont_lipv = readvtk(args.meshfile[0:len(args.meshfile)-4] + '_cont_lipv.vtk')
    cont_lspv = readvtk(args.meshfile[0:len(args.meshfile)-4] + '_cont_lspv.vtk')
    cont_mv = readvtk(args.meshfile[0:len(args.meshfile)-4] + '_cont_mv.vtk')
    if args.cut_laa == 0:
        cont_laa = readvtk(args.meshfile[0:len(args.meshfile)-4] + '_cont_laa.vtk')
    else:
        cont_laa = None
    
mesh = DeleteNonTriangularFaces(mesh)  # Ensure only triangular faces are present

locator, locator_open, locator_rspv, locator_ripv, locator_lipv, locator_lspv, locator_laa = build_locators(mesh, m_open, cont_rspv, cont_ripv, cont_lipv, cont_lspv, cont_laa, args.cut_laa)
mv_cont_ids = get_mv_contour_ids(cont_mv, locator_open)

# paths (created with 3_divide_LA.py)
npaths = 7
path1, path2, path3, path4, path5, path6, path7, path_laa1, path_laa2, path_laa3, path8 = read_paths(args.meshfile, npaths, args.cut_laa)

# Obtain ids corresponding to the extremes of the segments
v1r, v1d, v1l, v2u, v2r, v2l, v3u, v3r, v3l, v4r, v4u, v4d, vlaad, vlaau, vlaar, id_v5, id_v6, id_v7, id_v8 = identify_segments_extremes(path1, path2, path3, path4, path5, path6, path7, path8, path_laa1, path_laa2, path_laa3,
                               locator_open, locator_rspv, locator_ripv, locator_lipv, locator_lspv, locator_laa,
                               cont_rspv, cont_ripv, cont_lipv, cont_lspv, cont_laa,
                               v5, v6, v7, v8, args.cut_laa)

# Get ids of the segments. Start with PV holes. Start with angle = 0 or pi (anticlock-wise, positive angle direction)
rspv_ids, rspv_s1_prop, rspv_s2_prop, rspv_s3_prop, v1l_prop, v1d_prop, v1r_prop = get_rspv_segments_ids(cont_rspv, locator_open, v1l, v1d, v1r, propn_rspv_s1, propn_rspv_s2, propn_rspv_s3, m_open)
ripv_ids, ripv_s1_prop, ripv_s2_prop, ripv_s3_prop, v2l_prop, v2r_prop, v2u_prop = get_ripv_segments_ids(cont_ripv, locator_open, v2l, v2r, v2u, propn_ripv_s1, propn_ripv_s2, propn_ripv_s3)
lipv_ids, lipv_s1_prop, lipv_s2_prop, lipv_s3_prop, v3r_prop, v3u_prop, v3l_prop = get_lipv_segments_ids(cont_lipv, locator_open, v3r, v3u, v3l, propn_lipv_s1, propn_lipv_s2, propn_lipv_s3)
lspv_ids, lspv_s1_prop, lspv_s2_prop, lspv_s3_prop, v4r_prop, v4u_prop, v4d_prop = get_lspv_segments_ids(cont_lspv, locator_open, v4r, v4u, v4d, propn_lspv_s1, propn_lspv_s2, propn_lspv_s3)
if args.cut_laa == 0:
    laa_ids, laa_s1, laa_s2 = get_laa_segments_ids(cont_laa, locator_open, vlaau, vlaad, vlaar)
else:
    laa_ids = None
    laa_s1 = None
    laa_s2 = None

# write updated paths after displacing segment extremes to have proportional PV segments lengths
path1_clipped_prop = find_create_path(m_open, int(v2u_prop), int(v1d_prop))  # Always second to first to get order ids order from first to second
path2_clipped_prop = find_create_path(m_open, int(v3r_prop), int(v2l_prop))
path3_clipped_prop = find_create_path(m_open, int(v4d_prop), int(v3u_prop))
path4_clipped_prop = find_create_path(m_open, int(v1l_prop), int(v4r_prop))
path5_clipped_prop = find_create_path(m_open, int(id_v5), int(v1r_prop))
path6_clipped_prop = find_create_path(m_open, int(id_v6), int(v2r_prop))
path7_clipped_prop = find_create_path(m_open, int(id_v7), int(v3l_prop))
if args.cut_laa == 0:
    path_laa1_clipped_prop = find_create_path(m_open, int(vlaad), int(v4u_prop))
    path_laa2_clipped_prop = find_create_path(m_open, int(id_v8), int(vlaau))
else:
    path8_clipped_prop = find_create_path(m_open, int(id_v8), int(v4u_prop))

if args.save_final_paths == True:
    writevtk(path1_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path1_prop.vtk')
    writevtk(path2_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path2_prop.vtk')
    writevtk(path3_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path3_prop.vtk')
    writevtk(path4_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path4_prop.vtk')
    writevtk(path5_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path5_prop.vtk')
    writevtk(path6_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path6_prop.vtk')
    writevtk(path7_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path7_prop.vtk')
    if args.cut_laa == 0:
        writevtk(path_laa1_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path_laa1_prop.vtk')
        writevtk(path_laa2_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path_laa2_prop.vtk')
    else:
        writevtk(path8_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path8_prop.vtk')
    # writevtk(path_laa1_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path_laa1_prop.vtk')
    # writevtk(path_laa2_clipped_prop, args.meshfile[0:len(args.meshfile)-4] + 'path_laa2_prop.vtk')

##################    Define segment constraint points (s1, s2, s3,..., s12)    ##################
s1 = get_segment_ids_in_to_be_flat_mesh(path1_clipped_prop, locator_open, np.concatenate([ripv_s2_prop, ripv_s3_prop]), np.concatenate([rspv_s1_prop, rspv_s2_prop]))
s2 = get_segment_ids_in_to_be_flat_mesh(path2_clipped_prop, locator_open, np.concatenate([lipv_s1_prop, lipv_s3_prop]), np.concatenate([ripv_s1_prop, ripv_s3_prop]))
s3 = get_segment_ids_in_to_be_flat_mesh(path3_clipped_prop, locator_open, np.concatenate([lspv_s2_prop, lspv_s3_prop]), np.concatenate([lipv_s1_prop, lipv_s2_prop]))
s4 = get_segment_ids_in_to_be_flat_mesh(path4_clipped_prop, locator_open, np.concatenate([rspv_s1_prop, rspv_s3_prop]), np.concatenate([lspv_s1_prop, lspv_s3_prop]))
s5 = get_segment_ids_in_to_be_flat_mesh(path5_clipped_prop, locator_open, mv_cont_ids, np.concatenate([rspv_s2_prop, rspv_s3_prop]))
s6 = get_segment_ids_in_to_be_flat_mesh(path6_clipped_prop, locator_open, mv_cont_ids, np.concatenate([ripv_s1_prop, ripv_s2_prop]))
s7 = get_segment_ids_in_to_be_flat_mesh(path7_clipped_prop, locator_open, mv_cont_ids, np.concatenate([lipv_s2_prop, lipv_s3_prop]))
if args.cut_laa == 0:
    s8a = get_segment_ids_in_to_be_flat_mesh(path_laa1_clipped_prop, locator_open, np.concatenate([laa_s1, laa_s2]), np.concatenate([lspv_s1_prop, lspv_s2_prop]))
    s8b = get_segment_ids_in_to_be_flat_mesh(path_laa2_clipped_prop, locator_open, mv_cont_ids, np.concatenate([laa_s1, laa_s2]))
    s8 = None
else:
    # s8a = get_segment_ids_in_to_be_flat_mesh(path_8_clipped_prop, locator_open, np.concatenate([lspv_s1_prop, lspv_s2_prop]), np.concatenate([mv_cont_ids, lspv_s3_prop]))
    s8 = get_segment_ids_in_to_be_flat_mesh(path8_clipped_prop, locator_open, mv_cont_ids, np.concatenate([lspv_s1_prop, lspv_s2_prop]))
    s8a = None
    s8b = None
# Last 5 segments, parts of the MV that will go to the contour of the disk. Is the MV contour ids list clockwise or anticlockwise? reorder to start in v5

try:
    pos_mv_v5 = int(np.where(mv_cont_ids.astype(int) == id_v5)[0])
except:
    # find closest point in countor to vlaad
        # locator for contour
    locator_countor = vtk.vtkPointLocator()
    locator_countor.SetDataSet(cont_mv)
    locator_countor.BuildLocator()
    id_v5 = locator_open.FindClosestPoint(locator_countor.GetDataSet().GetPoint(locator_countor.FindClosestPoint(locator_open.GetDataSet().GetPoint(id_v5))))
    pos_mv_v5 = int(np.where(mv_cont_ids.astype(int) == id_v5)[0])

mv_ids = np.append(mv_cont_ids[pos_mv_v5:mv_cont_ids.size], mv_cont_ids[0:pos_mv_v5])
try:
    pos_mv_v6 = int(np.where(mv_ids.astype(int) == id_v6)[0])
except:
    # find closest point in countor to vlaau
        # locator for contour
    locator_countor = vtk.vtkPointLocator()
    locator_countor.SetDataSet(cont_mv)
    locator_countor.BuildLocator()
    id_v6 = locator_open.FindClosestPoint(locator_countor.GetDataSet().GetPoint(locator_countor.FindClosestPoint(locator_open.GetDataSet().GetPoint(id_v6))))
    pos_mv_v6 = int(np.where(mv_ids.astype(int) == id_v6)[0])
try:
    pos_mv_v7 = int(np.where(mv_ids.astype(int) == id_v7)[0])
except:
    # find closest point in countor to vlaar
        # locator for contour
    locator_countor = vtk.vtkPointLocator()
    locator_countor.SetDataSet(cont_mv)
    locator_countor.BuildLocator()
    id_v7 = locator_open.FindClosestPoint(locator_countor.GetDataSet().GetPoint(locator_countor.FindClosestPoint(locator_open.GetDataSet().GetPoint(id_v7))))
    pos_mv_v7 = int(np.where(mv_ids.astype(int) == id_v7)[0])
try:
    pos_mv_v8 = int(np.where(mv_ids.astype(int) == id_v8)[0])
except:
    # find closest point in countor to vlaau
        # locator for contour
    locator_countor = vtk.vtkPointLocator()
    locator_countor.SetDataSet(cont_mv)
    locator_countor.BuildLocator()
    id_v8 = locator_open.FindClosestPoint(locator_countor.GetDataSet().GetPoint(locator_countor.FindClosestPoint(locator_open.GetDataSet().GetPoint(id_v8))))
    pos_mv_v8 = int(np.where(mv_ids.astype(int) == id_v8)[0])
# which one comes first?
if pos_mv_v6 < pos_mv_v8:
    # print('MV contour - clockwise direction')
    mv_ids = mv_ids.astype(int)
else:
    # print('MV contour - anti-clockwise direction, flipped required')
    # manual flip because numpy flip is not working
    aux = np.zeros(mv_ids.size)
    for i in range(mv_ids.size):
        aux[mv_ids.size-1-i] = mv_ids[i]
    # mantain the id_v5 as the first one (after the flip is the last one)
    flipped = np.append(aux[aux.size-1], aux[0:aux.size-1])
    mv_ids = flipped.astype(int)
s9 = mv_ids[0:int(np.where(mv_ids == id_v6)[0])]   # from v5 to v6 (points in the MV contour) skipping last one
s10 = mv_ids[int(np.where(mv_ids == id_v6)[0]):int(np.where(mv_ids == id_v7)[0])]
if len(s10) == 0:
    s10 = mv_ids[int(np.where(mv_ids == id_v7)[0]):int(np.where(mv_ids == id_v6)[0])]  # if no points between v6 and v7, take all points from v7 to v6
s11 = mv_ids[int(np.where(mv_ids == id_v7)[0]):int(np.where(mv_ids == id_v8)[0])]
if len(s11) == 0:
    s11 = mv_ids[int(np.where(mv_ids == id_v8)[0]):int(np.where(mv_ids == id_v7)[0])]  # if no points between v7 and v8, take all points from v8 to v5
s12 = mv_ids[int(np.where(mv_ids == id_v8)[0]):mv_ids.size]

# Concatenate all constraint segments: s1,s2,s3,s4,s5,s6,s7, s8a and s8b
auxx = np.append(s1, s2)
auxx = np.append(auxx, s3)
auxx = np.append(auxx, s4)
auxx = np.append(auxx, s5)
auxx = np.append(auxx, s6)
auxx = np.append(auxx, s7)
if args.cut_laa == 0:
    auxx = np.append(auxx, s8a)
    seq_constraints_ids = np.append(auxx, s8b).astype(int)
else:
    auxx = np.append(auxx, s8)
    seq_constraints_ids = auxx.astype(int)
##################    Define contour constraint points    ##################
# Concatenate ids of the contour segments: 3 in each veins (PV hole) + 4 external disk + 2 for LAA
auxx2 = np.append(s9, s10)
auxx2 = np.append(auxx2, s11)
auxx2 = np.append(auxx2, s12)
auxx2 = np.append(auxx2, rspv_s1_prop)
auxx2 = np.append(auxx2, rspv_s2_prop)
auxx2 = np.append(auxx2, rspv_s3_prop)
auxx2 = np.append(auxx2, ripv_s1_prop)
auxx2 = np.append(auxx2, ripv_s2_prop)
auxx2 = np.append(auxx2, ripv_s3_prop)
auxx2 = np.append(auxx2, lipv_s1_prop)
auxx2 = np.append(auxx2, lipv_s2_prop)
auxx2 = np.append(auxx2, lipv_s3_prop)
auxx2 = np.append(auxx2, lspv_s1_prop)
auxx2 = np.append(auxx2, lspv_s2_prop)
auxx2 = np.append(auxx2, lspv_s3_prop)
if args.cut_laa == 0:
    auxx2 = np.append(auxx2, laa_s1)
    seq_contour_ids = np.append(auxx2, laa_s2).astype(int)
else:
    seq_contour_ids = auxx2.astype(int)
# # check repeated points -> singular matrix and no solution
# counts1 = np.bincount(seq_constraints_ids)
# counts2 = np.bincount(seq_contour_ids)
# counts3 = np.bincount(np.concatenate([seq_constraints_ids, seq_contour_ids]))
# print('Number of repeated constraints', np.where(counts1 > 1)[0])
# print('Number of repeated contour conditions', np.where(counts2 > 1)[0])
# print('Number of repeated constraints and conditions', np.where(counts3 > 1)[0])

# put together all PV and LAA segment sizes
if args.cut_laa == 0:
    pv_laa_segment_lengths = np.zeros([5, 3])
else:
    pv_laa_segment_lengths = np.zeros([4, 3])
pv_laa_segment_lengths[0, 0] = rspv_s1_prop.size
pv_laa_segment_lengths[0, 1] = rspv_s2_prop.size
pv_laa_segment_lengths[0, 2] = rspv_s3_prop.size
pv_laa_segment_lengths[1, 0] = ripv_s1_prop.size
pv_laa_segment_lengths[1, 1] = ripv_s2_prop.size
pv_laa_segment_lengths[1, 2] = ripv_s3_prop.size
pv_laa_segment_lengths[2, 0] = lipv_s1_prop.size
pv_laa_segment_lengths[2, 1] = lipv_s2_prop.size
pv_laa_segment_lengths[2, 2] = lipv_s3_prop.size
pv_laa_segment_lengths[3, 0] = lspv_s1_prop.size
pv_laa_segment_lengths[3, 1] = lspv_s2_prop.size
pv_laa_segment_lengths[3, 2] = lspv_s3_prop.size
if args.cut_laa == 0:
    pv_laa_segment_lengths[4, 0] = laa_s1.size
    pv_laa_segment_lengths[4, 1] = laa_s2.size
s9size = s9.size
s10size = s10.size
s11size = s11.size
s12size = s12.size

##################    Create target (x0, y0) positions  according to the lengths of each segment    ##################
# Separately constraints and contours

x0_const, y0_const = define_constraints_positions(s1, s2, s3, s4, s5, s6, s7, s8, s8a, s8b, v1l_x, v1l_y, v1d_x, v1d_y, v1r_x, v1r_y, v2l_x,
                                 v2l_y, v2r_x, v2r_y, v2u_x, v2u_y, v3r_x, v3r_y, v3u_x, v3u_y, v3l_x, v3l_y,
                                 v4r_x, v4r_y, v4u_x, v4u_y, v4d_x, v4d_y, vlaad_x, vlaad_y, vlaau_x, vlaau_y, p5_x,
                                 p5_y, p6_x, p6_y, p7_x, p7_y, p8_x, p8_y, args.cut_laa)

x0_bound, y0_bound = define_boundary_positions(rdisk, rhole_rspv, rhole_ripv, rhole_lipv, rhole_lspv, rhole_laa, xhole_center, yhole_center, laa_hole_center_x, laa_hole_center_y, s9size, s10size, s11size, s12size, pv_laa_segment_lengths.astype(int), t_v5, t_v6, t_v7, t_v8, args.cut_laa)

plt.plot(x0_bound, y0_bound, 'ro')
plt.plot(x0_const, y0_const, 'bx')
plt.title('2D template with boundary (red) and regional (blue) constraint points')
plt.show()


m_flat = flat_w_constraints(m_open, seq_contour_ids.astype(int), seq_constraints_ids.astype(int), x0_bound, y0_bound, x0_const, y0_const)

# writevtk(m_flat, to_be_flat_filename)

m_final = flat(m_flat, seq_contour_ids.astype(int), x0_bound, y0_bound)   # Refine boundary

# # Add region (R1, R2, R3, R4, R5) label to the _to_be_flat mesh and the final flat mesh
# # summarize and write all dividing lines in a txt file
line_textfile = args.meshfile[0:len(args.meshfile)-4] + '_div_lines.txt'
if args.cut_laa == 0:
    nlines = 9
else:
    nlines = 8

locator = vtk.vtkPointLocator()
locator.SetDataSet(m_open)
locator.BuildLocator()
f = open(line_textfile, 'w')

for i in range(1, nlines+1):
    if i == 1:
        path = path1_clipped_prop
    elif i == 2:
        path = path2_clipped_prop
    elif i == 3:
        path = path3_clipped_prop
    elif i == 4:
        path = path4_clipped_prop
    elif i == 5:
        path = path5_clipped_prop
    elif i == 6:
        path = path6_clipped_prop
    elif i == 7:
        path = path7_clipped_prop
    elif i == 8:
        if args.cut_laa == 0:
            path = path_laa1_clipped_prop
        else:
            path = path8_clipped_prop
    elif i == 9:
        path = path_laa2_clipped_prop
    ids = np.arange(0, path.GetNumberOfPoints())
    for p in range(path.GetNumberOfPoints()):
        id_p = locator.FindClosestPoint(path.GetPoint(ids[p]))
        f.write(str(id_p))
        f.write(' ')
    f.write('\n')
f.close()

# Read all lines and divide/cut mesh
m_aux = set_piece_label(m_open, line_textfile, m_seeds)
writevtk(m_aux, to_be_flat_filename)

# print('\nProjecting information...')
transfer_all_scalar_arrays_by_point_id(m_open, m_final)
m_final.GetCellData().AddArray(m_aux.GetCellData().GetArray('region'))
# # remove ad hoc scalar arrays
m_final.GetPointData().RemoveArray('pv')
m_final.GetPointData().RemoveArray('autolabels')
m_final.GetPointData().RemoveArray('hole')
print('\nRemoving ad hoc scalar arrays: autolabels, pv, and hole')
writevtk(m_final, m_out)
