import vtk
from aux_functions import*

import numpy as np

# import svd
from scipy.linalg import svd

def compute_best_fit_plane(points):
    """Compute best-fit plane using PCA (alternative to vtkPlane.ComputeBestFittingPlane)."""
    # Convert vtkPoints to numpy array
    pts = np.array([points.GetPoint(i) for i in range(points.GetNumberOfPoints())])
    
    # Center the points
    centroid = np.mean(pts, axis=0)
    centered = pts - centroid
    
    # Perform SVD to get the normal vector
    _, _, vh = svd(centered)
    normal = vh[2, :]  # Last row of V is the normal
    
    # Create vtkPlane
    plane = vtk.vtkPlane()
    plane.SetOrigin(centroid)
    plane.SetNormal(normal)
    return plane

def fill_holes_with_new_points(input_mesh):
    """Fill mesh holes by adding new points in the hole planes."""
    # --- Step 1: Extract hole boundaries ---
    boundary_edges = vtk.vtkFeatureEdges()
    boundary_edges.SetInputData(input_mesh)
    boundary_edges.BoundaryEdgesOn()
    boundary_edges.FeatureEdgesOff()
    boundary_edges.NonManifoldEdgesOff()
    boundary_edges.Update()
    
    # --- Step 2: Split boundaries into individual holes ---
    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputConnection(boundary_edges.GetOutputPort())
    connectivity.SetExtractionModeToAllRegions()
    connectivity.ColorRegionsOn()
    connectivity.Update()
    
    # --- Step 3: Process each hole ---
    appender = vtk.vtkAppendPolyData()
    appender.AddInputData(input_mesh)
    print(range(connectivity.GetNumberOfExtractedRegions()))

    for i in range(connectivity.GetNumberOfExtractedRegions()):
        print(i)
        print(range(i, connectivity.GetNumberOfExtractedRegions()), "Processing hole", i)
        # Extract one hole boundary
        region = vtk.vtkPolyDataConnectivityFilter()
        region.SetInputConnection(boundary_edges.GetOutputPort())
        region.SetExtractionModeToSpecifiedRegions()
        region.AddSpecifiedRegion(i)
        region.Update()
        
        # Compute best-fit plane
        plane = vtk.vtkPlane()
        points = region.GetOutput().GetPoints()
        plane=compute_best_fit_plane(points)
        
        # vtk.vtkPlane.ComputeBestFittingPlane(points, plane, normal)
        
        # Project boundary onto plane
        projector = vtk.vtkProjectPointsToPlane()
        projector.SetInputConnection(region.GetOutputPort())
        projector.SetProjectionTypeToSpecifiedPlane()
        projector.SetNormal(plane.GetNormal())
        projector.SetOrigin(plane.GetOrigin())
        
        
        
        projector.Update()
        
        # Triangulate the hole (creates new points)
        triangulator = vtk.vtkContourTriangulator()
        triangulator.SetInputConnection(projector.GetOutputPort())
        triangulator.Update()
        
        appender.AddInputData(triangulator.GetOutput())
        
        
        
        # add faces to new points
        
        
    
     # --- CRITICAL MISSING STEP ---
    # Reconstruct the surface to connect new patches
    appender.Update()
    surface_filter = vtk.vtkDataSetSurfaceFilter()
    surface_filter.SetInputConnection(appender.GetOutputPort())
    surface_filter.Update()
    
    print("Number of holes filled:", connectivity.GetNumberOfExtractedRegions())
    # --- Step 4: Merge and clean ---
    # appender.Update()
    cleaner = vtk.vtkCleanPolyData()
    cleaner.SetInputConnection(appender.GetOutputPort())
    cleaner.PointMergingOn()
    cleaner.Update()
    
    writevtk(cleaner.GetOutput(), "filled_holes.vtk")  # Save the filled mesh for inspection
    
    return cleaner.GetOutput()

# Example usage
if __name__ == "__main__":
    print("Filling holes in the mesh with new points...")
    # 1. Create or load a mesh with holes (e.g., missing faces)
    mesh_with_holes = readvtk()  # Use your own data
    print(f"Loaded mesh with {mesh_with_holes.GetNumberOfPoints()} points and {mesh_with_holes.GetNumberOfCells()} cells.")
    # 2. Fill holes and generate new points
    filled_mesh = fill_holes_with_new_points(mesh_with_holes)
    print(f"Filled mesh has {filled_mesh.GetNumberOfPoints()} points and {filled_mesh.GetNumberOfCells()} cells.")
    
    # 3. Print point/count info
    print(f"Original points: {mesh_with_holes.GetNumberOfPoints()}")
    print(f"New points after filling: {filled_mesh.GetNumberOfPoints()}")
    
