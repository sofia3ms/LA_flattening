from pathlib import Path
from clip_aux_functions import *

from vtkmodules.vtkCommonColor import vtkNamedColors




def get_program_parameters():
    import argparse
    description = 'Close holes in a mesh and identify the holes.'
    epilogue = '''
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file_name', nargs='?', default=None,
                        help='The polydata source file name,e.g. Torso.vtp.')
    args = parser.parse_args()

    return args.file_name

import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk



def main():

    file_name = get_program_parameters()
    poly_data = None
    if file_name:
        if Path(file_name).is_file():
            poly_data = readvtk(file_name)
            # if surface:
            #     # Convert the surface to polydata.
            #     poly_data = vtkDataSetSurfaceFilter(input_data=surface).output
        else:
            print(f'{file_name} not found.')
    if file_name is None or poly_data is None:
        print('Error')


    #Use vtkFillHolesFilter to fill holes in the mesh
    fill_holes_filter = vtk.vtkFillHolesFilter()
    fill_holes_filter.SetInputData(poly_data)
    fill_holes_filter.SetHoleSize(1000)  # Set the maximum hole size to fill    
    fill_holes_filter.Update()
    filled_mesh = fill_holes_filter.GetOutput() 
    print("filled")
    
    original_num_cells = poly_data.GetNumberOfCells()
    new_cell_indices = list(range(original_num_cells, filled_mesh.GetNumberOfCells()))
    
    point_labels = vtk.vtkIntArray()
    point_labels.SetName("hole")
    point_labels.SetNumberOfValues(filled_mesh.GetNumberOfPoints())
    point_labels.Fill(0)  # Initialize all as original points
    
    # First mark points that are directly on new polygons
    for cell_idx in new_cell_indices:
        cell = filled_mesh.GetCell(cell_idx)
        for i in range(cell.GetNumberOfPoints()):
            point_id = cell.GetPointId(i)
            point_labels.SetValue(point_id, 1)  # Mark as on new poly
            
    filled_mesh.GetPointData().AddArray(point_labels)

    
    writevtk(filled_mesh,file_name.split('.')[0] + '_filled.vtk')
    
    print("saved")
    
    
if __name__ == '__main__':
    main()