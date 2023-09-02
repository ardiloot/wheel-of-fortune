import os
import numpy as np
from glob import glob
from stl import mesh

for filename in glob(
    os.path.join(os.path.dirname(__file__), "..", "hw/**/*.stl"), recursive=True
):
    print(os.path.basename(filename))
    stl_mesh = mesh.Mesh.from_file(filename)
    print(stl_mesh.name)
    if b"numpy-stl" in stl_mesh.name:
        print("SKIP")
        continue

    stl_mesh.rotate(np.array([1, 0, 0]), np.deg2rad(90))
    stl_mesh.save(filename)
