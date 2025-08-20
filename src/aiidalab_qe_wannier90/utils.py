def process_cube_files(folder: str = 'parent_folder'):
    import os
    import numpy as np
    from ase.io import read
    from skimage import measure

    def find_isovalue(density_array, percentile=90):
        """Find the isovalue for the isosurface by taking the given percentile of the density values."""
        return np.percentile(density_array, percentile)

    def compute_isosurface(density_array, isovalue, cell, origin, step_size=1):
        verts, faces, _, _ = measure.marching_cubes(density_array, level=isovalue, step_size=step_size)

        # ASE cube reader provides cell vectors, so map fractional grid coordinates to Cartesian
        # verts are in fractional grid units, scale to fractional cell
        frac = verts / np.array(density_array.shape)  # normalize to [0,1]
        cartesian_verts = np.dot(frac, cell) + origin

        return cartesian_verts.flatten(), faces.flatten()

    parameters = {}
    mesh_data = {}
    atoms = None

    for filename in os.listdir(folder):
        if filename.endswith('.cube'):
            filepath = os.path.join(folder, filename)
            atoms, data = read(filepath, format='cube', read_data=True)  # ASE returns (Atoms, ndarray)
            key = filename[:-5]  # strip ".cube"

            try:
                density_array = data['data']
                origin = np.array(data['origin'])
                cell = np.array(data['cell'])

                isovalue = abs(find_isovalue(density_array))

                verts, faces = compute_isosurface(density_array, isovalue, cell, origin)
                verts_neg, faces_neg = compute_isosurface(density_array, -isovalue, cell, origin)

                parameters[key] = {'isovalue': isovalue}
                mesh_data[f'{key}_positive_vertices'] = verts
                mesh_data[f'{key}_positive_faces'] = faces
                mesh_data[f'{key}_negative_vertices'] = verts_neg
                mesh_data[f'{key}_negative_faces'] = faces_neg

            except Exception as e:
                parameters[key] = {'error': f'Failed to process file {filename}: {e}'}

    return {
        'atoms': atoms,
        'parameters': parameters,
        'mesh_data': mesh_data
    }
