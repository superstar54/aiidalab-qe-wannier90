def create_download_link(obj, filename, description='Download'):
    """Create a download link for a file in the AiiDA repository using a temporary directory."""
    import base64
    import shutil
    import tempfile
    import ipywidgets as ipw
    from pathlib import Path
    # Create a temporary directory to store the file
    # Copy the file from the AiiDA repository to the temporary directory
    with obj.as_path(filename) as source_path:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / filename
            shutil.copy(source_path, tmp_path)

            with open(tmp_path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode()

    # At this point, we no longer need the file; it's encoded.
    payload = f'data:application/octet-stream;base64,{b64}'
    html = f'<a download="{filename}" href="{payload}" target="_blank">{description}</a>'
    return ipw.HTML(html)

def plot_skeaf(skeaf_data):
    """Plot the de Haas van Alphen (dHvA) frequencies from a Wannier90 workchain."""
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go

    x = []         # angle values
    y = []         # freq values
    labels = []    # band names for color grouping
    xlabel = 'Rotation step'

    for band, array_node in skeaf_data.items():

        phi = array_node.get_array('phi')
        theta = array_node.get_array('theta')
        freq = array_node.get_array('freq')

        if len(np.unique(phi)) == 1:
            if len(np.unique(theta)) > 1:
                x.extend(theta)
                y.extend(freq)
                xlabel = '\u03B8, degrees'  # Greek letter theta
        elif len(np.unique(theta)) == 1:
            if len(np.unique(phi)) > 1:
                x.extend(phi)
                y.extend(freq)
                xlabel = '\u03C6, degrees'  # Greek letter phi
        elif len(np.unique(phi)) > 1 and len(np.unique(theta)) > 1:
            # Combine phi and theta into a (N, 2) array of pairs
            rotations = np.column_stack((phi, theta))

            # Get unique rotations and the inverse indices
            unique_rotations, rotation_indices = np.unique(rotations, axis=0, return_inverse=True)
            x.extend(rotation_indices)  # Use indices as x values
            y.extend(freq)
        else:
            # If neither phi nor theta has unique values, skip this band
            continue

        labels.extend([band] * len(x))  # repeat band name for each point

    # Create scatter plot
    fig = px.scatter(x=x, y=y, color=labels,
                     labels={'x': xlabel, 'y': 'Frequency (kT)', 'color': 'Band'},
                     title='Angular dependence of dHvA frequencies')
    fig.update_layout(title_x=0.5)

    return go.FigureWidget(fig)
