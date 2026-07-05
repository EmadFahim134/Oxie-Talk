use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use std::sync::{Arc, Mutex};
use log::{info, error, trace};

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
        info!("Initializing audio host...");
        let host = cpal::default_host();

        info!("Selecting default input device...");
        let device = host.default_input_device().ok_or_else(|| {
            error!("No input device found during PTT start");
            "No input device found"
        })?;

        let config = device.default_input_config().map_err(|e| {
            error!("Failed to get default input config: {}", e);
            e.to_string()
        })?;

        let is_recording = self.is_recording.clone();
        *is_recording.lock().unwrap() = true;

        info!("Building audio input stream...");
        let stream = device.build_input_stream(
            config.into(),
            move |data: &[f32], _: &cpal::InputCallbackInfo| {
                if *is_recording.lock().unwrap() {
                    // Logic to send audio packets to WebRTC would go here
                    // For debug mode, we log activity at trace level
                    if !data.is_empty() {
                        trace!("Captured {} audio samples", data.len());
                    }
                }
            },
            |err| error!("Error in audio stream: {}", err),
            None,
        ).map_err(|e| {
            error!("Failed to build input stream: {}", e);
            e.to_string()
        })?;

        stream.play().map_err(|e| {
            error!("Failed to start audio stream playback: {}", e);
            e.to_string()
        })?;

        self.stream = Some(stream);
        info!("Audio recording stream active.");
        Ok(())
    }

    pub fn stop_recording(&mut self) {
        info!("Stopping audio recording...");
        *self.is_recording.lock().unwrap() = false;
        self.stream = None;
    }
}
