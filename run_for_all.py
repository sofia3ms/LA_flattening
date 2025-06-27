import os
import fnmatch

def find_files(directory, pattern):
    """Recursively find all files in a directory that match a pattern."""
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
    return matches

pattern = "*_clipped_mitral.vtk"

path = r"F:/CARTO_MAT_FILES"

files = find_files(path, pattern)


for i in files:
    print(i)
    
    # if "crinkle" not in i and "mitral" not in i and "closed" not in i:

    os.system("python fill_holes.py {}".format(i))
          
        #   .format(i))

# python 1_mesh_standardisation.py --meshfile "F:\CARTO_MAT_FILES\19040065\FA\FA_05_15_2025_23-18-41_1-AE_vtk_mesh.vtk" --pv_dist 5 --laa_dist 5 --vis 1

# # errors: 12025854, 12095057, 

# python 2_close_holes_project_info.py --meshfile_open "F:\CARTO_MAT_FILES\1004629\FA\FA_05_14_2025_18-25-02_1-AE_vtk_mesh_clipped.vtk" --meshfile_open_no_mitral  "F:\CARTO_MAT_FILES\1004629\FA\FA_05_14_2025_18-25-02_1-AE_vtk_mesh_clipped_mitral.vtk" --meshfile_closed "F:\CARTO_MAT_FILES\1004629\FA\FA_05_14_2025_18-25-02_1-AE_vtk_mesh_clipped_closed.vtk"


# python 3_divide_LA.py --meshfile "F:\CARTO_MAT_FILES\8003127\REDOFA\REDOFA_05_13_2025_17-27-12_1-Map_vtk_mesh_clipped_mitral_filled.vtk"


# python 4_flat_atria.py --meshfile "F:\CARTO_MAT_FILES\1004629\FA\FA_05_14_2025_18-25-02_1-AE_vtk_mesh_clipped_closed.vtk"

# -i "F:\CARTO_MAT_FILES\1026643\FAredo\FAredo_05_15_2025_19-42-20_1-AE_vtk_mesh_clipped.vtk" -o "F:\CARTO_MAT_FILES\1026643\FAredo\mesh_closed.vtk"