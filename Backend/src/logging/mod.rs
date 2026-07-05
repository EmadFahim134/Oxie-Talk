use log::{Level, Metadata, Record};
use parking_lot::Mutex;
use std::sync::Arc;

pub struct SharedLogger {
    logs: Arc<Mutex<Vec<String>>>,
}

impl SharedLogger {
    pub fn new(logs: Arc<Mutex<Vec<String>>>) -> Self {
        Self { logs }
    }
}

impl log::Log for SharedLogger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        metadata.level() <= Level::Info
    }

    fn log(&self, record: &Record) {
        if self.enabled(record.metadata()) {
            let log_msg = format!("[RUST] [{}] {}", record.level(), record.args());
            let mut logs = self.logs.lock();
            logs.push(log_msg);
            if logs.len() > 500 {
                logs.remove(0);
            }
        }
    }

    fn flush(&self) {}
}

pub fn init(logs: Arc<Mutex<Vec<String>>>) {
    let logger = SharedLogger::new(logs);
    // Ignore error if logger already set (e.g. in tests)
    let _ = log::set_boxed_logger(Box::new(logger))
        .map(|()| log::set_max_level(log::LevelFilter::Info));
}
