    
import pyaudio
import wave
import uuid

#remove
import paho.mqtt.client as mqtt

class LiveRecorder:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

        self.recording = False
        self.chunk = 4096  # Record in chunks of 4096 samples              old:"Record in chunks of 1024 samples" (was 1024)
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 1
        self.fs = 44100  # Record at 44100 samples per second
        self.p = pyaudio.PyAudio()


    def record(self, topic):
        stream = self.p.open(format=self.sample_format,
                channels=self.channels,
                rate=self.fs,
                frames_per_buffer=self.chunk,
                input=True)
        
        # Store data in chunks
        self.recording = True

        while self.recording:
            # Read bytes
            data = stream.read(self.chunk)
            ba_data = bytearray(data) # necessary?
            # Publish
            self.mqtt_client.publish(topic, ba_data)
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        # Terminate the PortAudio interface
        self.p.terminate()

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
    