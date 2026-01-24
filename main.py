import click
import open3d.visualization.gui as gui
from ui import MainWindow

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--webrtc",
    is_flag=True,
    default=False,
    help="Enable Open3D WebRTC visualizer (stream GUI to browser).",
)
def main(webrtc: bool):
    if webrtc:
        try:
            import open3d as o3d

            # Must be called before creating/initializing windows.
            o3d.visualization.webrtc_server.enable_webrtc()
        except Exception as e:
            click.echo(f"[WARN] Failed to enable WebRTC: {e}", err=True)

    app = gui.Application.instance
    app.initialize()
    
    main_window = MainWindow(window_size=(1680, 1050))
    main_window.init()
    app.run()


if __name__ == "__main__":
    main()
