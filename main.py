import pytermgui as ptg
import sys
import os
import logging
from Modules.persistence import save_profile, get_profile, create_db_and_tables
from Modules.tui_components import AppTUI
from Modules.logger import setup_logging
from oxie_backend import Backend

def main():
    # OS Specific adjustments
    is_windows = sys.platform == "win32"
    if is_windows:
        # Enable ANSI support for Windows 10+ consoles
        os.system("color")

    shared_logs = []
    logger = setup_logging(shared_logs)
    logger.info(f"Oxie-Talk starting on {sys.platform}")

    create_db_and_tables()
    backend = Backend()

    profile = get_profile("testuser")

    with ptg.WindowManager() as manager:
        if not profile:
            def on_submit(button: ptg.Button):
                username = username_input.value
                bio = bio_input.value
                links = links_input.value
                new_profile = save_profile(username, bio, links)
                manager.remove(setup_window)
                app_tui = AppTUI(manager, backend, new_profile, shared_logs)
                manager.add(app_tui.create_main_window())
                backend.register_service(username, 5000)

            username_input = ptg.InputField("", prompt="Username: ")
            bio_input = ptg.InputField("", prompt="Bio: ")
            links_input = ptg.InputField("", prompt="Links: ")

            setup_window = (
                ptg.Window(
                    "[bold]Oxie-Talk Setup[/bold]",
                    "",
                    username_input,
                    bio_input,
                    links_input,
                    "",
                    ptg.Button("Submit", onclick=on_submit),
                )
                .center()
            )
            manager.add(setup_window)
        else:
            app_tui = AppTUI(manager, backend, profile, shared_logs)
            manager.add(app_tui.create_main_window())
            backend.register_service(profile.username, 5000)

        manager.run()

if __name__ == "__main__":
    main()
