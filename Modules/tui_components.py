import pytermgui as ptg

class AppTUI:
    def __init__(self, manager, backend, user_profile):
        self.manager = manager
        self.backend = backend
        self.user_profile = user_profile

    def create_main_window(self):
        peer_list = ptg.Container(ptg.Label("Finding peers..."))

        def refresh_peers(button):
            peers = self.backend.browse_services()
            peer_list.get_lines().clear()
            if not peers:
                peer_list.lazy_add(ptg.Label("No peers found."))
            for name, addr in peers:
                peer_list.lazy_add(ptg.Button(f"{name} ({addr})"))

        def toggle_ptt(button):
            if button.label == "Start PTT":
                try:
                    self.backend.start_ptt()
                    button.label = "Stop PTT"
                except Exception as e:
                    self.manager.toast(f"Error: {e}")
            else:
                self.backend.stop_ptt()
                button.label = "Start PTT"

        window = (
            ptg.Window(
                f"[bold]Welcome, {self.user_profile.username}![/bold]",
                "",
                ptg.Label("Peers Online:"),
                peer_list,
                "",
                ptg.Button("Refresh Peers", onclick=refresh_peers),
                ptg.Button("Start PTT", onclick=toggle_ptt),
                ptg.Button("Exit", onclick=lambda _: self.manager.stop()),
            )
            .set_title("Oxie-Talk Main")
            .center()
        )
        return window
