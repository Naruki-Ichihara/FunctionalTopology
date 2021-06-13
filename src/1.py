import numpy as np
import trimesh as tr
import matplotlib.pyplot as plt
from vedo import *

import_path = '/workdir/models/bracket.stl'
theta = 45.0

mesh = tr.load_mesh(import_path, face_colors='blue')
normals = np.array(mesh.face_normals)
cdt = normals[:, 2] < -np.cos(np.deg2rad(theta))
idx = np.arange(len(mesh.faces))[cdt].tolist()
print(len(idx))
submesh = mesh.submesh([idx], append=True)
subsubmesh = submesh.split(only_watertight=False)
vedomesh = trimesh2vedo(subsubmesh[0])
a = mesh2Volume(vedomesh, spacing=(0.1, 0.1, 0.1))
write(a, 'test.vtk')

