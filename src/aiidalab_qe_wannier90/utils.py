def process_xsf_files(folder: str = 'parent_folder'):
    import os
    import numpy as np
    from ase.io import read
    from skimage import measure

    def read_xsf_density(filename):
        with open(filename, 'r') as f:
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
        return nx, ny, nz, origin, lattice_vectors, density_array

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

    parameters = {}
    mesh_data = {}
    for filename in os.listdir(folder):
        if filename.endswith('.xsf'):
            filepath = os.path.join(folder, filename)
            atoms = read(filepath)
            key = filename[:-4]
            try:
                nx, ny, nz, origin, lattice_vectors, density_array = read_xsf_density(filepath)
                isovalue = abs(find_isovalue(density_array))
                verts, faces = compute_isosurface(density_array, isovalue, origin, lattice_vectors)
                verts_neg, faces_neg = compute_isosurface(density_array, -isovalue, origin, lattice_vectors)
                # the verts is in a nx, ny, nz grid, we need to transform it to fractional coordinates
                # then to cartesian coordinates using the lattice vectors
                parameters[key] = {'isovalue': isovalue}
                mesh_data[f'{key}_positive_vertices'] = verts
                mesh_data[f'{key}_positive_faces'] = faces
                mesh_data[f'{key}_negative_vertices'] = verts_neg
                mesh_data[f'{key}_negative_faces'] = faces_neg
            except Exception as e:
                parameters[key] = {'error': f'Failed to process file {filename}'}
    return {'atoms': atoms,
            'parameters': parameters,
            'mesh_data': mesh_data}
