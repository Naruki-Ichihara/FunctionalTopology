import pyvista as pv
import numpy as np
import time
import trimesh as tr

resolution = 300
limit_angle = 45.0

mesh = pv.read('/workdir/models/bracket.stl')
normals = np.array(mesh.cell_normals)
cdt = normals[:, 2] < -np.cos(np.deg2rad(limit_angle))
id = np.arange(mesh.n_cells)[cdt]
top = mesh.extract_cells(id)
surf = top.extract_surface()
tr_mesh = tr.base.Trimesh(surf.points, surf.faces)

surf.save('normal.stl')
'''
voxel = pv.voxelize(mesh, density=mesh.length/resolution, check_surface=False)
voxel.compute_implicit_distance(surf, inplace=True)
#
voxel = voxel.threshold(value = [-0.1, 0.1], scalars='implicit_distance')
array = voxel.points
print(array)
voxel.save('mesh.vtk')
'''
tr_mesh.export('tr.stl')
