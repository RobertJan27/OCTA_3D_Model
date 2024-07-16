import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import LassoSelector
from matplotlib.path import Path
from scipy.spatial import cKDTree
import plotly.graph_objs as go
import plotly.io as pio

class ModelReconstruction:
    def __init__(self):
        self.binary_arrays = []
        self.excluded_pixels = set()
        self.current_row = -1
        self.spacing = 1

    def images_to_binary_arrays(self, folder_path):
        self.binary_arrays = []
        filenames = sorted(
            [f for f in os.listdir(folder_path) if f.endswith((".png", ".jpg", ".jpeg"))],
            key=lambda x: int(os.path.splitext(x)[0])
        )
        for filename in filenames:
            image_path = os.path.join(folder_path, filename)
            image = Image.open(image_path).convert('L')
            image_array = np.array(image)
            binary_array = np.where(image_array == 0, 0, 1)
            self.binary_arrays.append(binary_array)

    def plot_3d_white_pixels(self, row):
        x_points = []
        y_points = []
        z_points = []
        colors = []
        previous_indices = None

        for z, binary_array in enumerate(self.binary_arrays):
            if row == -1 or row == z:
                indices = np.argwhere(binary_array == 1)

                if indices.size == 0:
                    continue
                indices = np.array([idx for idx in indices if (z, idx[0], idx[1]) not in self.excluded_pixels])

                if indices.size == 0:
                    continue
                z_coord = z * self.spacing
                row_color = [255, 0, 0]
                if previous_indices is not None:
                    tree = cKDTree(previous_indices)
                    _, indices_to_connect = tree.query(indices, k=1)
                    for i, idx in enumerate(indices):
                        p_idx = previous_indices[indices_to_connect[i]]

                        for t in np.linspace(0, 1, 5):
                            x_points.append(p_idx[0] * (1 - t) + idx[0] * t)
                            y_points.append(p_idx[1] * (1 - t) + idx[1] * t)
                            z_points.append(previous_z_coord * (1 - t) + z_coord * t)
                            colors.append(row_color)
                x_points.extend(indices[:, 0])
                y_points.extend(indices[:, 1])
                z_points.extend([z_coord] * len(indices))
                colors.extend([row_color] * len(indices))
                previous_indices = indices
                previous_z_coord = z_coord
        fig = go.Figure(data=[go.Scatter3d( x=x_points,y=y_points,z=z_points,mode='markers+lines',
            marker=dict(size=2, color=colors),
            line=dict(color='rgba(0,0,0,0.1)', width=1)
        )])
        fig.update_layout(scene=dict(xaxis_title='X',yaxis_title='Y',zaxis_title='Z'),
            width=700,
            margin=dict(r=10, l=10, b=10, t=10)
        )

        pio.show(fig)

    def select_pixels(self):
        combined_image = np.zeros_like(self.binary_arrays[0])
        for binary_array in self.binary_arrays:
            combined_image = np.maximum(combined_image, binary_array)

        fig, ax = plt.subplots()
        ax.imshow(combined_image, cmap='gray')

        lasso = LassoSelector(ax, onselect=self.on_select)
        plt.show()

    def on_select(self, verts):
        path = Path(verts)
        for z, binary_array in enumerate(self.binary_arrays):
            for i in range(binary_array.shape[0]):
                for j in range(binary_array.shape[1]):
                    if binary_array[i, j] == 1 and path.contains_point((j, i)):
                        self.excluded_pixels.add((z, i, j))

    def compute_volume_and_elongation(self):
        all_indices = []
        for z, binary_array in enumerate(self.binary_arrays):
            indices = np.argwhere(binary_array == 1)
            filtered_indices = [idx for idx in indices if (z, idx[0], idx[1]) not in self.excluded_pixels]
            all_indices.extend([(z, idx[0], idx[1]) for idx in filtered_indices])

        if not all_indices:
            return None, None

        all_indices = np.array(all_indices)
        volume = len(all_indices)

        min_coords = np.min(all_indices, axis=0)
        max_coords = np.max(all_indices, axis=0)
        bounding_box_dims = max_coords - min_coords
        elongation = max(bounding_box_dims) / min(bounding_box_dims) if min(bounding_box_dims) > 0 else float('inf')

        return volume, elongation

    def reset_excluded_pixels(self):
        self.excluded_pixels.clear()
