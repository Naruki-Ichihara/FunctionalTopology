from vedo import *
import numpy as np
from pyvista import *
from pyacvd import Clustering
import trimesh as tr

obj = load('/workdir/models/bracket.stl')
vista = wrap(obj.polydata())
vista.compute_normals(point_normals=False, inplace=True)
ids = np.arange(vista.n_cells)[vista['Normals'][:,2] > 0.0]
crop = vista.extract_cells(ids)

write(croped, 'volume.stl')



