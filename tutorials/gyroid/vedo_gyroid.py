from vedo import *
import numpy as np

x, y, z = np.mgrid[:30, :30, :30] * 0.4
U = sin(x)*cos(y) + sin(y)*cos(z) + sin(z)*cos(x)

gyr = Volume(U).isosurface(0).smoothLaplacian().subdivide()

write(gyr, 'gyroid.stl')