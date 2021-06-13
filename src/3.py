import numpy as np
import trimesh as tr
import matplotlib.pyplot as plt
from vedo import *

import_path = '/workdir/models/bracket.stl'
theta = 45.0

mesh = tr.load_mesh(import_path, face_colors='blue')
z_ext = mesh.bounds
print(mesh.bounds)