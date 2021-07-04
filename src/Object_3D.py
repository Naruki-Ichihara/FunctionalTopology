import numpy as np
import trimesh as tr
from trimesh.transformations import euler_matrix
from vedo import *
from tqdm import tqdm
import PVGeo as pg
import pyvista as pv

class Object_3D():
    def __init__(self, file):
        self.object = tr.load_mesh(file)
        self.bounds = self.object.bounds
        self.volume = self.object.volume
        self.centroid = self.object.centroid

    def is_watertight(self):
        return self.object.is_watertight

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

    def generate_support_volume(self, limit_angle=45.0, resolution=150, build_plane=None, export_as_vtk=False, ignore_overlap_region=True):
        if build_plane is None:
            build_plane = Plane(pos=self.bounds[0, :], sx=1, sy=1)
        overhang_submesh = self.overhang_checker(limit_angle)
        length = overhang_submesh.bounds[1, 0] - overhang_submesh.bounds[0, 0]
        pitch = length / resolution
        vox = overhang_submesh.voxelized(pitch).points
        hit = (vox / pitch)
        hit = np.vstack((np.ceil(hit), np.floor(hit)))
        u, i = tr.grouping.unique_rows(hit)
        occupied = hit[u]*pitch
        z = occupied[:, 2]
        pts = []
        for i in range(len(z)):
            pt_z = np.arange(np.min(z), z[i], pitch)
            pt_x = np.full(pt_z.shape, occupied[i, 0])
            pt_y = np.full(pt_z.shape, occupied[i, 1])
            pt = np.stack([pt_x, pt_y, pt_z], 1)
            pts.append(pt)
        grid_ = np.concatenate(pts, 0)
        u, i = tr.grouping.unique_rows(grid_)
        grid = grid_[u]

        if not ignore_overlap_region:
            vedo_volume = trimesh2vedo(self.object)
            outward_pts = vedo_volume.insidePoints(grid, invert=True)
            grid = outward_pts.points()

        if export_as_vtk:
            vtkpoints = pg.points_to_poly_data(grid)
            voxlizer = pg.filters.VoxelizePoints()
            vox = voxlizer.apply(vtkpoints)
            vox_vista = pv.wrap(vox)
            vox_vista.save('support_volume.vtk')

        return grid.shape[0]*pitch**3

    '''
    Ability for the 3D print: wall thickness checker.
    This cannot walking with memory overflow.
    def wall_thickness(self):
        print('1')
        points = self.object.triangles_center + (self.object.face_normals * -1e-4)[1]
        print('2')
        thick = tr.proximity.thickness(mesh=self.object, points=points, method='ray')
        print(thick)
        pass
    '''

    def is_in_buildvolume(self, buildvolume=[100, 100, 100]):
        l = self.bounds[1, 0] - self.bounds[0, 0]
        w = self.bounds[1, 1] - self.bounds[0, 1]
        h = self.bounds[1, 2] - self.bounds[0, 2]
    
        if l > buildvolume[0] or w > buildvolume[1] or h > buildvolume[2]:
            return False
        else:
            return True

    def estimate_cost(self):
        coefficient_work_material = 1.0
        coefficient_support_material = 1.0
        density_of_work = 1.0
        density_of_support = 1.0
        volume = self.volume
        support_volume = self.generate_support_volume()
        return coefficient_work_material*density_of_work*volume + coefficient_support_material*density_of_support*support_volume

    def estimate_delivery_time(self):
        coefficient_work_material = 1.0
        coefficient_support_material = 1.0
        density_of_work = 1.0
        density_of_support = 1.0
        volume = self.volume
        support_volume = self.generate_support_volume()
        return coefficient_work_material*density_of_work*volume + coefficient_support_material*density_of_support*support_volume

print('Process start')
print('Loading mesh')
obj = Object_3D('/workdir/models/bracket.stl')
obj.tlanslate_to_origin()
obj.apply_rotation_matrix((np.deg2rad(45), 0, 0))
obj.apply_scale_matrix(0.5)
print(obj.estimate_cost())