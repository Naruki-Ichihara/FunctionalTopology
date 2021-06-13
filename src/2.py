import numpy as np
import trimesh as tr
import matplotlib.pyplot as plt
from vedo import *

import_path = '/workdir/models/bracket.stl'
theta = 45.0

mesh = tr.load_mesh(import_path, face_colors='blue')
z_ext = mesh.bounds[:, 2]
z_levels = np.arange(*z_ext, step=0.4)
sections_ = mesh.section_multiplane(plane_origin=mesh.bounds[1],
                                   plane_normal=[0,0,1],
                                   heights=z_levels)
sections = list(filter(lambda x:x is not None, sections_))
area_sum = 0
edge_sum = 0
for path in sections:
    area_sum += path.area
    edge_sum += path.length
print(area_sum)

normals = np.array(mesh.face_normals)
cdt = normals[:, 2] < -np.cos(np.deg2rad(theta))
idx = np.arange(len(mesh.faces))[cdt].tolist()
print(len(idx))
submesh = mesh.submesh([idx], append=True)
subsubmesh = submesh.split(only_watertight=False)
print(type(trimesh2vedo(subsubmesh[0]).projectOnPlane()))
write(trimesh2vedo(subsubmesh[0]).projectOnPlane(), 'sub.stl')

