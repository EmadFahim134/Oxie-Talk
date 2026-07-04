use mdns_sd::{ServiceDaemon, ServiceInfo};
use std::collections::HashMap;

pub struct MdnsDiscovery {
    daemon: ServiceDaemon,
    service_type: String,
}

impl MdnsDiscovery {
    pub fn new() -> Self {
        Self {
            daemon: ServiceDaemon::new().expect("Failed to create mdns daemon"),
            service_type: "_oxie-talk._tcp.local.".to_string(),
        }
    }

    pub fn register(&self, username: &str, port: u16) {
        let hostname = format!("{}.local.", username);
        let mut properties = HashMap::new();
        properties.insert("username".to_string(), username.to_string());

        let service_info = ServiceInfo::new(
            &self.service_type,
            username,
            &hostname,
            "",
            port,
            Some(properties),
        ).expect("Failed to create service info");

        self.daemon.register(service_info).expect("Failed to register service");
    }

    pub fn browse(&self) -> Vec<(String, String)> {
        let receiver = self.daemon.browse(&self.service_type).expect("Failed to browse");
        let mut peers = Vec::new();

        // This is a simplified browse. In a real app, we'd handle events.
        // For now, we'll just check what's currently found.
        while let Ok(event) = receiver.try_recv() {
            if let mdns_sd::ServiceEvent::ServiceResolved(info) = event {
                let username = info.get_fullname().to_string();
                let addresses = info.get_addresses();
                if let Some(addr) = addresses.iter().next() {
                    peers.push((username, addr.to_string()));
                }
            }
        }
        peers
    }
}
