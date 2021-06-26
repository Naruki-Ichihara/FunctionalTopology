import numpy as np
import trimesh as tr
import matplotlib.pyplot as plt
from trimesh.transformations import euler_matrix
from vedo import *
from tqdm import tqdm
from scipy.spatial.qhull import Delaunay
from trimesh import Trimesh, transformations
from trimesh.geometry import plane_transform
from mpl_toolkits.mplot3d import Axes3D

def _remove_overlapping_triangles(m: Trimesh) -> Trimesh:
    cleaned_mesh = Trimesh()
    used_faces = []
    face_indices = np.arange(0, m.faces.shape[0])

    # For all facets reconstruct the surfaces using Delaunay triangulation
    for facet_faces in m.facets:
        if len(facet_faces):
            used_faces.extend(facet_faces)
            selected_faces = m.faces[facet_faces].flatten()
            facet_vertices = m.vertices[selected_faces]
            to_2d = plane_transform(facet_vertices[0], m.face_normals[facet_faces[0]])
            vertices_2d = transformations.transform_points(
                facet_vertices,
                matrix=to_2d)[:, :2]
            tri = Delaunay(vertices_2d)
            split = Trimesh(vertices=facet_vertices, faces=tri.simplices)
            cleaned_mesh += split

    # Create a mask of faces that were not part of a facet
    mask = np.ones(face_indices.size, dtype=bool)
    mask[np.unique(used_faces)] = False

    # Add those remaining faces back in
    cleaned_mesh += m.submesh([face_indices[mask]], only_watertight=False)
    cleaned_mesh.visual = m.visual
    return cleaned_mesh

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
        print('Sub process start')
        z_ext = self.bounds[:, 2]
        z_levels = np.arange(*z_ext, step=z_step)
        sections_ = self.object.section_multiplane(plane_origin=self.bounds[1],
                                                plane_normal=normal,
                                                heights=z_levels)
        sections = list(filter(lambda x:x is not None, sections_))
        self.sliced_area = 0
        for section in sections:
            self.sliced_area += section.area
        print('Sub process end')
        return self.sliced_area

    def overhang_checker(self, limit_angle=45.0):
        normals = np.array(self.object.face_normals)
        cdt = normals[:, 2] < -np.cos(np.deg2rad(limit_angle))
        id = np.arange(len(self.object.faces))[cdt].tolist()
        submesh = self.object.submesh([id], append=True)
        return submesh

    def generate_support_volume(self, limit_angle=45.0, build_plane=None):
        ''' TO DO '''
        pitch = 1.5
        if build_plane is None:
            build_plane = Plane(pos=self.bounds[0, :], sx=1000, sy=1000)
        m = self.overhang_checker(limit_angle)
        #v = m.vertices
        v,f = tr.remesh.subdivide_to_size(m.vertices, m.faces, pitch/2)
        hit = (v / pitch)
        hit = np.vstack((np.ceil(hit), np.floor(hit))).astype(int)
        u,i = tr.grouping.unique_rows(hit)
        occupieds = hit[u]*pitch
        z = []
        for occuped in occupieds:
            z.append(occuped[2])
        z = np.array(z)
        ars = []
        for i in range(len(z)):
            ar_z = np.arange(np.min(z), z[i])
            ar_x = np.full(ar_z.shape, occupieds[i, 0])
            ar_y = np.full(ar_z.shape, occupieds[i, 1])
            ar = np.stack([ar_x, ar_y, ar_z], 1)
            ars.append(ar)
        ar = np.concatenate(ars, 0)

        cdt = self.object.contains(ar)
        ar_ = ar[not cdt]
        print(ar.shape[0]*pitch**3)

        return ar_.shape[0]*pitch**3

print('Process start')
print('Loading mesh')
obj = Object_3D('/workdir/models/bracket.stl')
obj.tlanslate_to_origin()
obj.apply_rotation_matrix((np.deg2rad(20), 0, 0))
obj.apply_scale_matrix(0.5)
print('Support')
vol = obj.generate_support_volume()
obj.object.export('mesh.stl')
print(vol)