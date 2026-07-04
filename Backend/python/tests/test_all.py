from oxie_backend import Backend

def test_backend_init():
    backend = Backend()
    assert backend is not None

def test_mdns():
    backend = Backend()
    # Test call doesn't crash
    backend.register_service("testuser", 1234)
    peers = backend.browse_services()
    assert isinstance(peers, list)
