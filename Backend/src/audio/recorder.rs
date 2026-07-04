use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use std::sync::{Arc, Mutex};

pub struct AudioRecorder {
    stream: Option<cpal::Stream>,
    is_recording: Arc<Mutex<bool>>,
}

impl AudioRecorder {
    pub fn new() -> Self {
        Self {
            stream: None,
            is_recording: Arc::new(Mutex::new(false)),
        }
    }

    pub fn start_recording(&mut self) -> Result<(), String> {
        let host = cpal::default_host();
        let device = host.default_input_device().ok_or("No input device found")?;
        let config = device.default_input_config().map_err(|e| e.to_string())?;

        let is_recording = self.is_recording.clone();
        *is_recording.lock().unwrap() = true;

        let stream = device.build_input_stream(
            config.into(),
            move |_: &[f32], _: &cpal::InputCallbackInfo| {
                // Here we would send audio packets to WebRTC
            },
            |err| eprintln!("Error in audio stream: {}", err),
            None,
        ).map_err(|e| e.to_string())?;

        stream.play().map_err(|e| e.to_string())?;
        self.stream = Some(stream);
        Ok(())
    }

    pub fn stop_recording(&mut self) {
        *self.is_recording.lock().unwrap() = false;
        self.stream = None;
    }
}
