import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer

class Signaling:
    def __init__(self):
        self.config = RTCConfiguration(iceServers=[RTCIceServer(urls="stun:stun.l.google.com:19302")])

    async def create_offer(self):
        pc = RTCPeerConnection(self.config)

        # Create a data channel for messaging
        channel = pc.createDataChannel("chat")

        @channel.on("open")
        def on_open():
            print("Data channel open")

        @channel.on("message")
        def on_message(message):
            print(f"Received message: {message}")

        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        return pc, pc.localDescription

    async def handle_offer(self, offer_sdp):
        pc = RTCPeerConnection(self.config)

        @pc.on("datachannel")
        def on_datachannel(channel):
            @channel.on("message")
            def on_message(message):
                print(f"Received message: {message}")

        offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
        await pc.setRemoteDescription(offer)

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return pc, pc.localDescription
