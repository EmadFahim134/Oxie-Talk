use pyo3::prelude::*;
use std::sync::Mutex;
use tokio::sync::mpsc;

mod discovery;
mod audio;

#[pyclass]
struct Backend {
    mdns: discovery::mdns::MdnsDiscovery,
    recorder: Mutex<audio::recorder::AudioRecorder>,
    _dht_tx: mpsc::Sender<String>,
}

#[pymethods]
impl Backend {
    #[new]
    fn new() -> Self {
        let (tx, rx) = mpsc::channel(100);

        // Spawn DHT in background
        tokio::spawn(async move {
            if let Ok(node) = discovery::dht::DhtNode::new().await {
                node.run(rx).await;
            }
        });

        Backend {
            mdns: discovery::mdns::MdnsDiscovery::new(),
            recorder: Mutex::new(audio::recorder::AudioRecorder::new()),
            _dht_tx: tx,
        }
    }

    fn register_service(&self, username: String, port: u16) -> PyResult<()> {
        self.mdns.register(&username, port);
        Ok(())
    }

    fn browse_services(&self) -> PyResult<Vec<(String, String)>> {
        Ok(self.mdns.browse())
    }

    fn start_ptt(&self) -> PyResult<()> {
        let mut recorder = self.recorder.lock().unwrap();
        recorder.start_recording().map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e))
    }

    fn stop_ptt(&self) -> PyResult<()> {
        let mut recorder = self.recorder.lock().unwrap();
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
