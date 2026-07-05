use libp2p::{
    kad::{self, store::MemoryStore},
    mdns, noise, swarm::NetworkBehaviour, swarm::SwarmEvent, tcp, yamux, PeerId, Swarm,
};
use std::error::Error;
use futures::StreamExt;
use tokio::sync::mpsc;

#[derive(NetworkBehaviour)]
pub struct OxieBehaviour {
    pub kademlia: kad::Behaviour<MemoryStore>,
    pub mdns: mdns::tokio::Behaviour,
}

pub struct DhtNode {
    swarm: Swarm<OxieBehaviour>,
}

impl DhtNode {
    pub async fn new() -> Result<Self, Box<dyn Error + Send + Sync>> {
        let mut swarm = libp2p::SwarmBuilder::with_new_identity()
            .with_tokio()
            .with_tcp(
                tcp::Config::default(),
                noise::Config::new,
                yamux::Config::default,
            ).map_err(|e| Box::new(e) as Box<dyn Error + Send + Sync>)?
            .with_behaviour(|key| {
                let peer_id = PeerId::from(key.public());
                let store = MemoryStore::new(peer_id);
                let kademlia = kad::Behaviour::new(peer_id, store);
                let mdns = mdns::tokio::Behaviour::new(mdns::Config::default(), peer_id)?;
                Ok(OxieBehaviour { kademlia, mdns })
            }).map_err(|e| Box::new(e) as Box<dyn Error + Send + Sync>)?
            .build();

        swarm.listen_on("/ip4/0.0.0.0/tcp/0".parse().map_err(|e| Box::new(e) as Box<dyn Error + Send + Sync>)?)
            .map_err(|e| Box::new(e) as Box<dyn Error + Send + Sync>)?;

        Ok(Self { swarm })
    }

    pub async fn run(mut self, mut command_receiver: mpsc::Receiver<String>) {
        loop {
            tokio::select! {
                event = self.swarm.select_next_some() => match event {
                    SwarmEvent::NewListenAddr { address, .. } => {
                        println!("Listening on {:?}", address);
                    }
                    _ => {}
                },
                command = command_receiver.recv() => {
                    if let Some(_cmd) = command {
                        // Handle commands like Put/Get
                    }
                }
            }
        }
    }
}
