import sys
import os
# Ensure repository root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from oxie_backend import Backend
from Modules.tui_components import AppTUI
from Modules.persistence import UserProfile, create_db_and_tables, save_profile

def test_backend_init():
    backend = Backend()
    assert backend is not None

def test_mdns():
    backend = Backend()
    # Test call doesn't crash
    backend.register_service("testuser", 1234)
    peers = backend.browse_services()
    assert isinstance(peers, list)

def test_tui_components():
    backend = Backend()
    create_db_and_tables()
    profile = save_profile("testuser_test", "bio_test", "links_test")

    # We pass a dummy manager as we don't need to run the full UI loop for this test
    class DummyManager:
        def remove(self, window):
            pass
        def add(self, window):
            pass

    manager = DummyManager()
    tui = AppTUI(manager, backend, profile)

    # Ensure UI main window and chat window can be created without raising exceptions
    main_window = tui.create_main_window()
    assert main_window is not None

    # Simulate a peer name
    tui.active_peer = "other_peer"
    chat_window = tui.create_chat_window()
    assert chat_window is not None
