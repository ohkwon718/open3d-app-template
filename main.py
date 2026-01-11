import open3d.visualization.gui as gui
from ui.main_window import MainWindow
from app.app_service import AppService
from controllers.interaction_controller import InteractionController


def main():
    app = gui.Application.instance
    app.initialize()
    
    app_service = AppService()
    main_window = MainWindow(window_size=(1680, 1050))
    
    controller = InteractionController(
        window=main_window.window,
        scene_view=main_window.scene_view,
        settings_panel=main_window.settings_panel,
        app_service=app_service
    )
    
    controller.setup_callbacks()
    main_window.init()
    app.run()


if __name__ == "__main__":
    main()
