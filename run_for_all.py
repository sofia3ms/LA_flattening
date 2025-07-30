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

python 1_mesh_standardisation.py --meshfile  "F:\CARTO_MAT_FILES\2021894\FA\FA_05_14_2025_17-08-30_1-AE_vtk_mesh.vtk" --pv_dist 5 --laa_dist 5 --vis 1 --cut_laa 1

# # errors: 12025854, 12095057, 

# python 2_close_holes_project_info.py --meshfile_open "F:\CARTO_MAT_FILES\1004629\FA\FA_05_14_2025_18-25-02_1-AE_vtk_mesh_clipped.vtk" --meshfile_open_no_mitral  "F:\CARTO_MAT_FILES\1004629\FA\FA_05_14_2025_18-25-02_1-AE_vtk_mesh_clipped_mitral.vtk" --meshfile_closed "F:\CARTO_MAT_FILES\1004629\FA\FA_05_14_2025_18-25-02_1-AE_vtk_mesh_clipped_closed.vtk"


python 3_divide_LA.py --meshfile "F:\CARTO_MAT_FILES\2021894\FA\FA_05_14_2025_17-08-30_1-AE_vtk_mesh_clipped_filled.vtk" --cut_laa 1



python 4_flat_atria.py --meshfile "F:\CARTO_MAT_FILES\2021894\FA\FA_05_14_2025_17-08-30_1-AE_vtk_mesh_clipped_filled.vtk" --meshfile_o "F:\CARTO_MAT_FILES\2021894\FA\FA_05_14_2025_17-08-30_1-AE_vtk_mesh_clipped.vtk" --cut_laa 1


# -i "F:\CARTO_MAT_FILES\1026643\FAredo\FAredo_05_15_2025_19-42-20_1-AE_vtk_mesh_clipped.vtk" -o "F:\CARTO_MAT_FILES\1026643\FAredo\mesh_closed.vtk"

python fill_holes.py "F:\CARTO_MAT_FILES\1004629\FA\FA_05_14_2025_18-25-02_1-AE_vtk_mesh_clipped_mitral.vtk"

# 2020229 mitral valve constraint is wrong
# 2021894 erro, mitral valve constraint is wrong. laa too large?
# 3010340 mitral valve constraint is wrong. laa too large?
# 3011120 no voltage??
# 5051033 nontriangular cell?

"F:\CARTO_MAT_FILES\5051033\fa3\fa3_05_14_2025_22-13-37_1-AE_vtk_mesh_clipped_mitral_filled.vtk"
