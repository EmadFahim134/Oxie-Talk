import asyncio
import json
import logging
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer

class Signaling:
    def __init__(self, on_message_callback):
        self.config = RTCConfiguration(iceServers=[RTCIceServer(urls="stun:stun.l.google.com:19302")])
        self.on_message_callback = on_message_callback
        self.pcs = set()

    async def create_offer(self):
        pc = RTCPeerConnection(self.config)
        self.pcs.add(pc)

        channel = pc.createDataChannel("chat")

        @channel.on("open")
        def on_open():
            logging.info("WebRTC Data channel open")

        @channel.on("message")
        def on_message(message):
            logging.info(f"Received WebRTC message: {message}")
            self.on_message_callback(message)

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        return pc, channel, pc.localDescription

    async def handle_offer(self, offer_sdp):
        pc = RTCPeerConnection(self.config)
        self.pcs.add(pc)

        @pc.on("datachannel")
        def on_datachannel(channel):
            logging.info("WebRTC Data channel received")
            @channel.on("message")
            def on_message(message):
                logging.info(f"Received WebRTC message: {message}")
                self.on_message_callback(message)

        offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
        await pc.setRemoteDescription(offer)

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return pc, pc.localDescription

    async def close_all(self):
        for pc in self.pcs:
            await pc.close()
        self.pcs.clear()
