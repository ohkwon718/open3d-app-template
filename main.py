import open3d.visualization.gui as gui
from ui import MainWindow


def main():
    app = gui.Application.instance
    app.initialize()
    
    main_window = MainWindow(window_size=(1680, 1050))
    main_window.init()
    app.run()


if __name__ == "__main__":
    main()
