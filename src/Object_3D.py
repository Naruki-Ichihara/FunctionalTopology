import numpy as np
import trimesh as tr
import matplotlib.pyplot as plt
from trimesh.transformations import euler_matrix
from vedo import *

class Object_3D():
    def __init__(self, file):
        self.object = tr.load_mesh(file)
        self.bounds = self.object.bounds
        self.volume = self.object.volume
        self.centroid = self.object.centroid

    def tlanslate_to_origin(self, origin=[0, 0, 0]):
        translate = np.array(origin) - np.array(self.centroid)
        self.object = self.object.apply_transform(tr.transformations.scale_and_translate(scale=1.0, translate=translate))
        self.bounds = self.object.bounds
        self.centroid = self.object.centroid
        pass

    def apply_rotation_matrix(self, eular_vector=[0, 0, 0], origin=[0, 0, 0]):
        roll = eular_vector[0]
        pitch = eular_vector[1]
        yaw = eular_vector[2]
        R = euler_matrix(roll, pitch, yaw, 'sxyz')
        self.object = self.object.apply_transform(R)
        self.bounds = self.object.bounds
        self.centroid = self.object.centroid
        pass

    def apply_scale_matrix(self, scale=1.0):
        self.object = self.object.apply_transform(tr.transformations.scale_and_translate(scale=scale))
        self.bounds = self.object.bounds
        self.centroid = self.object.centroid
        pass

    def slice_and_area(self, z_step=1.0, normal=[0, 0, 1]):
        z_ext = self.bounds[:, 2]
        z_levels = np.arange(*z_ext, step=z_step)
        sections_ = self.object.section_multiplane(plane_origin=self.bounds[1],
                                                plane_normal=normal,
                                                heights=z_levels)
        sections = list(filter(lambda x:x is not None, sections_))
        self.sliced_area = 0
        for section in sections:
            self.sliced_area += section.area
        return self.sliced_area

    def overhang_checker(self, limit_angle=45.0):
        normals = np.array(self.object.face_normals)
        cdt = normals[:, 2] < -np.cos(np.deg2rad(limit_angle))
        id = np.arange(len(self.object.faces))[cdt].tolist()
        submesh = self.object.submesh([id], append=True)#.split(only_watertight=False)
        return submesh


obj = Object_3D('/workdir/models/bracket.stl')
print(obj.bounds)
obj.tlanslate_to_origin()
print(obj.bounds)
obj.apply_scale_matrix(0.5)
print(obj.bounds)
obj.apply_rotation_matrix([1,1,1])
print(obj.bounds)
        