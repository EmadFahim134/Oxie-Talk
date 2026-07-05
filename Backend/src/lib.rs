use pyo3::prelude::*;
use std::sync::Arc;
use parking_lot::Mutex;
use tokio::sync::mpsc;
use log::info;

mod discovery;
mod audio;
mod logging;

#[pyclass]
struct Backend {
    mdns: discovery::mdns::MdnsDiscovery,
    recorder: Mutex<audio::recorder::AudioRecorder>,
    _dht_tx: mpsc::Sender<String>,
    logs: Arc<Mutex<Vec<String>>>,
}

#[pymethods]
impl Backend {
    #[new]
    fn new() -> Self {
        let logs = Arc::new(Mutex::new(Vec::new()));
        logging::init(logs.clone());

        info!("Rust Backend initializing...");

        let (tx, rx) = mpsc::channel(100);

        // Spawn DHT in background if runtime is available
        if let Ok(handle) = tokio::runtime::Handle::try_current() {
            handle.spawn(async move {
                if let Ok(node) = discovery::dht::DhtNode::new().await {
                    node.run(rx).await;
                }
            });
        } else {
            // This happens in tests or non-async environments
            // We'll just drop rx and tx for now
        }

        Backend {
            mdns: discovery::mdns::MdnsDiscovery::new(),
            recorder: Mutex::new(audio::recorder::AudioRecorder::new()),
            _dht_tx: tx,
            logs,
        }
    }

    fn fetch_logs(&self) -> PyResult<Vec<String>> {
        let mut logs = self.logs.lock();
        let fetched = logs.clone();
        logs.clear();
        Ok(fetched)
    }

    fn register_service(&self, username: String, port: u16) -> PyResult<()> {
        info!("Registering service for user: {} on port: {}", username, port);
        self.mdns.register(&username, port);
        Ok(())
    }

    fn browse_services(&self) -> PyResult<Vec<(String, String)>> {
        info!("Browsing for services...");
        Ok(self.mdns.browse())
    }

    fn start_ptt(&self) -> PyResult<()> {
        info!("Starting Push-To-Talk...");
        let mut recorder = self.recorder.lock();
        recorder.start_recording().map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))
    }

    fn stop_ptt(&self) -> PyResult<()> {
        info!("Stopping Push-To-Talk...");
        let mut recorder = self.recorder.lock();
        recorder.stop_recording();
        Ok(())
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn oxie_backend(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Backend>()?;
    Ok(())
}
