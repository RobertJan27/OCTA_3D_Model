import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class WhitePixelsPlotterGUI:
    def __init__(self, root, model_reconstruction):
        self.root = root
        self.model_reconstruction = model_reconstruction

        self.root.title("3D White Pixels Plotter")
        self.root.geometry("600x400")
        self.root.configure(bg="orange")

        self.frame = tk.Frame(self.root, bg="orange")
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.browse_button = tk.Button(self.frame, text="Browse Folder", command=self.browse_folder)
        self.browse_button.pack(pady=10)

        self.folder_path_entry = tk.Entry(self.frame, width=50)
        self.folder_path_entry.pack(pady=5)

        self.row_label = tk.Label(self.frame, text="Row number to plot (-1 for all rows):", bg="orange")
        self.row_label.pack(pady=5)

        self.row_entry = tk.Entry(self.frame, width=5)
        self.row_entry.pack(pady=5)
        self.row_entry.insert(0, "-1")
        self.row_entry.config(state=tk.DISABLED)

        self.plot_button = tk.Button(self.frame, text="Plot Row", command=self.plot_row)
        self.plot_button.pack(pady=10)
        self.plot_button.config(state=tk.DISABLED)

        self.select_pixels_button = tk.Button(self.frame, text="Select Pixels", command=self.select_pixels)
        self.select_pixels_button.pack(pady=10)
        self.select_pixels_button.config(state=tk.DISABLED)

        self.compute_button = tk.Button(self.frame, text="Compute Volume and Elongation", command=self.compute_volume_and_elongation)
        self.compute_button.pack(pady=10)
        self.compute_button.config(state=tk.DISABLED)

        self.reset_button = tk.Button(self.frame, text="Reset Excluded Pixels", command=self.reset_excluded_pixels)
        self.reset_button.pack(pady=10)
        self.reset_button.config(state=tk.DISABLED)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.folder_path_entry.delete(0, tk.END)
        self.folder_path_entry.insert(0, folder_path)
        if folder_path:
            self.model_reconstruction.excluded_pixels.clear()
            self.model_reconstruction.images_to_binary_arrays(folder_path)
            if self.model_reconstruction.binary_arrays:
                self.row_entry.config(state=tk.NORMAL)
                self.plot_button.config(state=tk.NORMAL)
                self.select_pixels_button.config(state=tk.NORMAL)
                self.compute_button.config(state=tk.NORMAL)
                self.reset_button.config(state=tk.NORMAL)

    def plot_row(self):
        try:
            row = int(self.row_entry.get())
            if row < -1 or row >= len(self.model_reconstruction.binary_arrays):
                messagebox.showerror("Error", f"Row number must be between -1 and {len(self.model_reconstruction.binary_arrays) - 1}")
            else:
                self.model_reconstruction.current_row = row
                self.model_reconstruction.plot_3d_white_pixels(row)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid row number")

    def select_pixels(self):
        self.model_reconstruction.select_pixels()
        self.model_reconstruction.plot_3d_white_pixels(self.model_reconstruction.current_row)

    def compute_volume_and_elongation(self):
        volume, elongation = self.model_reconstruction.compute_volume_and_elongation()
        if volume is not None and elongation is not None:
            messagebox.showinfo("Result", f"Volume: {volume}\nElongation: {elongation:.2f}")
        else:
            messagebox.showinfo("Result", "No white pixels found after exclusion.")

    def reset_excluded_pixels(self):
        self.model_reconstruction.reset_excluded_pixels()
        messagebox.showinfo("Info", "Ignored pixels have been reset.")
