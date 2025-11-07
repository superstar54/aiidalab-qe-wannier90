from aiida import orm
import numpy as np
from ase.io import read
from skimage import measure

def read_xsf_density(folder: orm.FolderData, filename: str):

    with folder.open(filename, 'r') as f:
        atoms = read(f, format='xsf')
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'BEGIN_DATAGRID_3D' in line:
            grid_start = i + 1
            break
    nx, ny, nz = map(int, lines[grid_start].split())
    origin = np.array([float(x) for x in lines[grid_start + 1].split()])
    lattice_vectors = np.array([list(map(float, lines[grid_start + j].split())) for j in range(2, 5)])
    density_data = []
    for line in lines[grid_start + 5:]:
        if 'END_DATAGRID_3D' in line:
            break
        density_data.extend(map(float, line.split()))
    expected_size = nx * ny * nz
    actual_size = len(density_data)
    if actual_size != expected_size:
        raise ValueError(f'Mismatch in density data size: expected {expected_size}, got {actual_size}')
    density_array = np.array(density_data).reshape((nz, ny, nx), order='F')
    return atoms, nx, ny, nz, origin, lattice_vectors, density_array

def find_isovalue(density_array, percentile=90):
    """Find the isovalue for the isosurface by taking the 90th percentile of the density values """

    return np.percentile(density_array, percentile)

def compute_isosurface(density_array, isovalue, origin, lattice_vectors, step_size=1):

    verts, faces, _, _ = measure.marching_cubes(density_array, level=isovalue, step_size=step_size)
    # Convert vertices from grid to Cartesian coordinates
    cartesian_verts = np.dot((verts / np.array(density_array.shape)), lattice_vectors) + origin
    # flatten the vertices and faces
    cartesian_verts = cartesian_verts.flatten()
    faces = faces.flatten()
    return cartesian_verts, faces

def process_xsf_file(folder: orm.FolderData, prefix: str = '', isovalue: float = None):

    data = {}
    mesh_data = {}
    try:
        key = prefix
        filename = f'{prefix}.xsf'
        atoms, nx, ny, nz, origin, lattice_vectors, density_array = read_xsf_density(folder, filename)
        data['atoms'] = atoms
        if isovalue is None:
            isovalue = abs(find_isovalue(density_array))
        data['isovalue'] = isovalue
        verts, faces = compute_isosurface(density_array, isovalue, origin, lattice_vectors)
        verts_neg, faces_neg = compute_isosurface(density_array, -isovalue, origin, lattice_vectors)
        # the verts is in a nx, ny, nz grid, we need to transform it to fractional coordinates
        # then to cartesian coordinates using the lattice vectors
        mesh_data[f'{key}_positive_vertices'] = verts
        mesh_data[f'{key}_positive_faces'] = faces
        mesh_data[f'{key}_negative_vertices'] = verts_neg
        mesh_data[f'{key}_negative_faces'] = faces_neg
        data['mesh_data'] = mesh_data
    except Exception as e:
        print(f'Error processing xsf file {filename}: {e}')
        return None

    return data
