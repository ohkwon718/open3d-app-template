import open3d as o3d
import numpy as np
from ui import MainWindow


def main():
    window = MainWindow(window_size=(1680, 1050))
    window.init()        
    window.run()


if __name__ == "__main__":
    main()