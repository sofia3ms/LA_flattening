#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path
from clip_aux_functions import *

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences\
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkIdTypeArray
from vtkmodules.vtkCommonDataModel import (
    vtkGenericCell,
    vtkPolyData,
    vtkSelection,
    vtkSelectionNode
)
from vtkmodules.vtkFiltersCore import (
    vtkConnectivityFilter,
    vtkPolyDataNormals
)
from vtkmodules.vtkFiltersExtraction import vtkExtractSelection
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter
from vtkmodules.vtkFiltersModeling import vtkFillHolesFilter
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOGeometry import (
    vtkBYUReader,
    vtkOBJReader,
    vtkSTLReader
)
from vtkmodules.vtkIOLegacy import vtkPolyDataReader
from vtkmodules.vtkIOPLY import vtkPLYReader
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkProperty,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor
)


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


def main():
    restore_original_normals = True

    colors = vtkNamedColors()

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
        

        
    fill_holes_filter = vtk.vtkFillHolesFilter()
    fill_holes_filter.SetInputData(poly_data)
    fill_holes_filter.SetHoleSize(100.0)
    fill_holes_filter.Update()

    data_filled = fill_holes_filter.GetOutput()
    # fill_holes_filter = vtkFillHolesFilter(input_data=poly_data, hole_size=1000.0)
    # fill_holes_filter.update()

    # Make the triangle winding order consistent.
    
    normal_filter = vtkPolyDataNormals()
    normal_filter.SetInputData(data_filled)
    normal_filter.ConsistencyOn()
    normal_filter.SplittingOff()
    normal_filter.Update()
    normals = normal_filter.GetOutput()
    
    # normals = vtkPolyDataNormals(input_data=data_filled, consistency=True, splitting=False)

    if restore_original_normals:
        
        # Restore the original normals.
        normals.GetPointData().SetNormals(poly_data.GetPointData().GetNormals())
    # Determine the number of added cells.
    num_original_cells = poly_data.GetNumberOfCells()
    num_new_cells = normals.GetNumberOfCells()

    # Iterate over the original cells.
    it = normals.NewCellIterator()
    it.InitTraversal()
    numCells = 0
    while not it.IsDoneWithTraversal() and numCells < num_original_cells:
        it.GoToNextCell()
        numCells += 1
    print(
        f'Num original: {num_original_cells}, Num new: {num_new_cells}, Num added: {num_new_cells - num_original_cells}')

    hole_poly_data = vtkPolyData()
    hole_poly_data.SetPoints(normals.GetPoints())
    hole_poly_data.Allocate(normals, num_new_cells - num_original_cells)

    # The remaining cells are the new ones from the hole filler.
    cell = vtkGenericCell()
    while not it.IsDoneWithTraversal():
        it.GetCell(cell)
        hole_poly_data.InsertNextCell(it.GetCellType(), cell.GetPointIds())
        it.GoToNextCell()

    # We have to use ConnectivityFilter and not
    # PolyDataConnectivityFilter since the latter does not create
    # RegionIds cell data.
    connectivity = vtkConnectivityFilter()
    connectivity.SetInputData(hole_poly_data)
    connectivity.SetExtractionModeToAllRegions()
    connectivity.ColorRegionsOn()
    connectivity.SetRegionIdAssignmentMode(
        connectivity.CELL_COUNT_ASCENDING)
    connectivity.Update()
    
    print(f'Found {connectivity.GetNumberOfExtractedRegions()} holes')

    # Visualize

    # Create a mapper and actor for the fill polydata.
    
    scalar_range = connectivity.GetOutput(0).GetScalarRange()
    filled_mapper = vtkDataSetMapper()
    filled_mapper.SetScalarMode(Mapper.ScalarMode.VTK_SCALAR_MODE_USE_CELL_DATA)
    filled_mapper.SetScalarRange(scalar_range)
    
    filled_actor = vtkActor()
    filled_actor.SetMapper(filled_mapper)
    
    # filled_mapper = vtkDataSetMapper(scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_CELL_DATA,
    #                                  scalar_range=scalar_range)
    # connectivity >> filled_mapper
    
    filled_mapper.SetInputData(connectivity.GetOutput(0))    
    

    # filled_actor = vtkActor(mapper=filled_mapper)
    # filled_actor.SetProperty(colors.GetColor3d('Peacock'))

    # Create a mapper and actor for the original polydata.
    original_mapper = vtkDataSetMapper()
    original_mapper.SetInputData(poly_data)
    # original_mapper = vtkPolyDataMapper(input_data=poly_data)

    backface_prop = vtkProperty()
    backface_prop.SetDiffuseColor(colors.GetColor3d('Banana'))
    # backface_prop.diffuse_color = colors.GetColor3d('Banana')

    original_actor = vtkActor()
    original_actor.SetMapper(original_mapper)
    original_actor.SetBackfaceProperty(backface_prop)
    original_actor.GetProperty().SetDiffuseColor(colors.GetColor3d('Flesh'))
    original_actor.GetProperty().SetRepresentationToWireframe()
    # original_actor = vtkActor(mapper=original_mapper)
    # original_actor.backface_property = backface_prop
    # original_actor.property.diffuse_color = colors.GetColor3d('Flesh')
    # original_actor.property.SetRepresentationToWireframe()

    # Create a renderer, render window, and interactor.
    renderer = vtkRenderer()
    renderer.SetBackground(colors.GetColor3d('Burlywood'))
    
    render_window = vtkRenderWindow()
    render_window.SetSize(512, 512)
    render_window.SetWindowName('IdentifyHoles')
    
    # renderer = vtkRenderer(background=colors.GetColor3d('Burlywood'))
    # render_window = vtkRenderWindow(size=(512, 512), window_name='IdentifyHoles')
    # render_window.AddRenderer(renderer)

    render_window_interactor = vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)
    # render_window_interactor.render_window = render_window

    # Add the actors to the scene.
    renderer.AddActor(original_actor)
    renderer.AddActor(filled_actor)

    camera = vtk.vtkCamera()
    camera.SetPosition(0, -1, 0)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)
    camera.Azimuth(60)
    camera.Elevation(30)
    renderer.SetActiveCamera(camera)

    # renderer.active_camera = vtkCamera()  
    # renderer.active_camera.position = (0, -1, 0)
    # renderer.active_camera.focal_point = (0, 0, 0)
    # renderer.active_camera.view_up = (0, 0, 1)
    # renderer.active_camera.Azimuth(60)
    # renderer.active_camera.Elevation(30)

    renderer.ResetCamera()
    # Render and interact.
    render_window.Render()

    render_window_interactor.Start()


def read_poly_data(file_name):
    if not file_name:
        print(f'No file name.')
        return None

    valid_suffixes = ['.g', '.obj', '.stl', '.ply', '.vtk', '.vtp']
    path = Path(file_name)
    ext = None
    if path.suffix:
        ext = path.suffix.lower()
    if path.suffix not in valid_suffixes:
        print(f'No reader for this file suffix: {ext}')
        return None

    reader = None
    if ext == '.ply':
        reader = vtkPLYReader(file_name=file_name)
    elif ext == '.vtp':
        reader = vtkXMLPolyDataReader(file_name=file_name)
    elif ext == '.obj':
        reader = vtkOBJReader(file_name=file_name)
    elif ext == '.stl':
        reader = vtkSTLReader(file_name=file_name)
    elif ext == '.vtk':
        reader = vtkPolyDataReader(file_name=file_name)
    elif ext == '.g':
        reader = vtkBYUReader(file_name=file_name)

    if reader:
        reader.update()
        poly_data = reader.output
        return poly_data
    else:
        return None





@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

    @dataclass(frozen=True)
    class ResolveCoincidentTopology:
        VTK_RESOLVE_OFF: int = 0
        VTK_RESOLVE_POLYGON_OFFSET: int = 1
        VTK_RESOLVE_SHIFT_ZBUFFER: int = 2

    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_DEFAULT: int = 0
        VTK_SCALAR_MODE_USE_POINT_DATA: int = 1
        VTK_SCALAR_MODE_USE_CELL_DATA: int = 2
        VTK_SCALAR_MODE_USE_POINT_FIELD_DATA: int = 3
        VTK_SCALAR_MODE_USE_CELL_FIELD_DATA: int = 4
        VTK_SCALAR_MODE_USE_FIELD_DATA: int = 5


if __name__ == '__main__':
    main()