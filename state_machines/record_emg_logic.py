from threading import Thread
from os import system
import paho.mqtt.client as mqtt
import stmpy
import os
import pyaudio
import wave
import uuid
import json

broker, port = "mqtt.item.ntnu.no", 1883

class RecorderEmergency:
    def __init__(self):
        self.start(broker, port)
        self.recording = False
        # self.emg_mode = False
        self.chunk = 256  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 1
        self.fs = 44100  # Record at 44100 samples per second
        self.filename = "audio_files/input_audio/" + "emergency" + ".wav"
        self.p = pyaudio.PyAudio()

    def start(self, broker, port):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)
        
        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))
        
    def record(self):
        stream = self.p.open(format=pyaudio.paInt16,  # 16 bits per sample
                             channels=1,
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
            
            self.client.publish("emg", json.dumps(data_dict))
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        # Terminate the PortAudio interface
        self.p.terminate()
        
    def stop(self):
        self.recording = False
        self.stm.stop_timer('t')

    def timeout(self):
        print("recording timed out")
        self.stop()
    
    # def process(self):
    #     channel = "emg"
    #     # Save the recorded data as a WAV file
    #     wf = wave.open(self.filename, 'wb')
    #     wf.setnchannels(self.channels)
    #     wf.setsampwidth(self.p.get_sample_size(self.sample_format))
    #     wf.setframerate(self.fs)
    #     wf.writeframes(b''.join(self.frames))
    #     wf.close()
        
    #     f = open(self.filename, "rb")
    #     imagestring = f.read()
    #     f.close()

    #     byteArray = bytearray(imagestring)

    #     # Send message over mqtt
    #     self.client.publish(channel, byteArray)

    def create_machine(self, name): 
        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'recording'}
        t2 = {'trigger': 'stop', 'source': 'recording', 'target': 'ready', 'effect': 'stop'}
        # t3 = {'trigger': 'done', 'source': 'processing', 'target': 'ready'}
        t4 = {'trigger': 't', 'source': 'recording', 'target': 'ready', 'effect': 'timeout'}
        
        s_recording = {'name': 'recording', 'do': 'record()', "stop": "stop()", 'entry': 'start_timer("t", 30000)'}

        stm = stmpy.Machine(name=name, transitions=[t0, t1, t2, t4], states=[s_recording], obj=self)
        self.stm = stm
        return self.stm