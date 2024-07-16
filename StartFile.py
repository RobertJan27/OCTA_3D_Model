import tkinter as tk

from Licenta_Director.ModelReconstruction import ModelReconstruction
from Licenta_Director.WhitePixelsPlotterGUI import WhitePixelsPlotterGUI


def main():
    root = tk.Tk()
    model_reconstruction = ModelReconstruction()
    app = WhitePixelsPlotterGUI(root, model_reconstruction)
    root.mainloop()

if __name__ == "__main__":
    main()
