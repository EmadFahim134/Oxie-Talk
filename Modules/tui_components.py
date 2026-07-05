import pytermgui as ptg
import logging
import asyncio
from Modules.signaling import Signaling

class AppTUI:
    def __init__(self, manager, backend, user_profile, shared_logs):
        self.manager = manager
        self.backend = backend
        self.user_profile = user_profile
        self.shared_logs = shared_logs
        self.log_container = ptg.Container()
        self.message_container = ptg.Container()
        self.active_peer = None
        self.signaling = Signaling(self.on_webrtc_message)
        self.active_channel = None

    def on_webrtc_message(self, message):
        self.message_container.lazy_add(ptg.Label(f"[bold]{self.active_peer}:[/bold] {message}"))
        logging.info(f"UI updated with message from {self.active_peer}")

    def create_main_window(self):
        peer_list = ptg.Container(ptg.Label("Finding peers..."))

        def start_chat(peer_name):
            self.active_peer = peer_name
            logging.info(f"Starting chat with {peer_name}")
            # In a real app, we'd trigger signaling here
            # For this prototype, we'll just show the window
            self.manager.remove(main_window)
            self.manager.add(self.create_chat_window())

        def refresh_peers(button):
            logging.info("User requested peer refresh")
            peers = self.backend.browse_services()
            peer_list.get_lines().clear()
            if not peers:
                peer_list.lazy_add(ptg.Label("No peers found."))
            for name, addr in peers:
                peer_list.lazy_add(ptg.Button(f"{name} ({addr})", onclick=lambda b, n=name: start_chat(n)))

        def toggle_ptt(button):
            if button.label == "Start PTT":
                try:
                    self.backend.start_ptt()
                    button.label = "Stop PTT"
                    logging.info("PTT Started")
                except Exception as e:
                    self.manager.toast(f"Error: {e}")
                    logging.error(f"Failed to start PTT: {e}")
            else:
                self.backend.stop_ptt()
                button.label = "Start PTT"
                logging.info("PTT Stopped")

        def update_debug_logs():
            rust_logs = self.backend.fetch_logs()
            for log in rust_logs:
                self.shared_logs.append(log)

            if len(self.shared_logs) > 0:
                self.log_container.get_lines().clear()
                for log in self.shared_logs[-5:]:
                    self.log_container.lazy_add(ptg.Label(log))

            self.manager.submit_callback(update_debug_logs, delay=1.0)

        self.manager.submit_callback(update_debug_logs, delay=1.0)

        main_window = (
            ptg.Window(
                f"[bold]Welcome, {self.user_profile.username}![/bold]",
                "",
                ptg.Label("Peers Online (Click to Chat):"),
                peer_list,
                "",
                ptg.Label("[bold]Debug Logs:[/bold]"),
                self.log_container,
                "",
                ptg.Button("Refresh Peers", onclick=refresh_peers),
                ptg.Button("Start PTT", onclick=toggle_ptt),
                ptg.Button("Exit", onclick=lambda _: self.manager.stop()),
            )
            .set_title("Oxie-Talk (Debug Mode)")
            .center()
        )
        return main_window

    def create_chat_window(self):
        input_field = ptg.InputField("", prompt="Message: ")

        def send_msg(button):
            msg = input_field.value
            if msg:
                self.message_container.lazy_add(ptg.Label(f"[bold]You:[/bold] {msg}"))
                input_field.value = ""
                logging.info(f"Sent message to {self.active_peer}")
                if self.active_channel:
                    self.active_channel.send(msg)

        def go_back(button):
            self.manager.remove(chat_window)
            self.manager.add(self.create_main_window())

        chat_window = (
            ptg.Window(
                f"[bold]Chatting with {self.active_peer}[/bold]",
                "",
                self.message_container,
                "",
                input_field,
                ptg.Button("Send", onclick=send_msg),
                "",
                ptg.Button("Back", onclick=go_back),
            )
            .set_title(f"Chat: {self.active_peer}")
            .center()
        )
        return chat_window
