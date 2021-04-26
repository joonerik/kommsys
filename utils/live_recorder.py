import pyaudio
import wave
import uuid
import sounddevice as sd
import json
import numpy as np

#remove
import paho.mqtt.client as mqtt

class LiveRecorder:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.recording = False
        self.p = pyaudio.PyAudio()
        self.chunk = 256

    # Record and send as numpy array
    def record(self, topic):

        stream = self.p.open(format=pyaudio.paInt16,  # 16 bits per sample
                             channels=2,
                             rate=44100,   # Record at 44100 samples per second
                             frames_per_buffer=self.chunk,   # Record in chunks
                             input=True)
        
        self.recording = True

        # Record loop
        while self.recording:
            audiochunks = []

            for i in range(10):
                audiochunks.append(stream.read(self.chunk).hex())

            data_dict = {"audio" : audiochunks}
            
            # data_dict = {"audio" : stream.read(self.chunk).hex()}

            self.mqtt_client.publish(topic, json.dumps(data_dict))
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        # Terminate the PortAudio interface
        self.p.terminate()

    # Stop recording
    def stop(self):
        self.recording = False


broker = "mqtt.item.ntnu.no"
port = 1883
client = mqtt.Client()
client.connect(broker, port)

recorder = LiveRecorder(client)
recorder.record('team13')

# s_recording = {'name': 'recording', 'do': 'record()', "stop": "stop()"}

#self.mqtt_client.publish(topic, audiofile)
    