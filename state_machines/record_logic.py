
import paho.mqtt.client as mqtt
broker, port = "mqtt.item.ntnu.no", 1883

#channel="team13"
from threading import Thread
import stmpy
from os import system
import os
import pyaudio
import wave
import uuid

class Recorder:
    def __init__(self):
        self.start(broker, port)
        self.recording = False
        self.emg_mode = False
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 1
        self.fs = 44100  # Record at 44100 samples per second
        self.filename = "audio_files/input_audio/" + str(uuid.uuid4()) + ".wav"
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
        if not self.emg_mode:
            self.p = pyaudio.PyAudio() 
            stream = self.p.open(format=self.sample_format,
                    channels=self.channels,
                    rate=self.fs,
                    frames_per_buffer=self.chunk,
                    input=True)
            self.frames = []  # Initialize array to store frames
            # Store data in chunks for 3 seconds
            self.recording = True
            while self.recording:
                data = stream.read(self.chunk)
                # print(type(data))
                self.frames.append(data)
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
    
    def process(self):
        newChannel = open("audio_files/channel.txt", "r")
        channel = newChannel.readline()

        # Save the recorded data as a WAV file
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        f = open(self.filename, "rb")
        imagestring = f.read()
        f.close()

        byteArray = bytearray(imagestring)

        # Send message over mqtt
        self.client.publish(channel, byteArray)

    def switch_emg_mode(self):
        print("before " + str(self.emg_mode))
        self.emg_mode = not self.emg_mode
        print("after " + str(self.emg_mode))
         
    def create_machine(self, name): 
        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'recording'}
        t2 = {'trigger': 'done', 'source': 'recording', 'target': 'processing'}
        t3 = {'trigger': 'done', 'source': 'processing', 'target': 'ready'}
        t4 = {'trigger': 't', 'source': 'recording', 'target': 'ready', 'effect': 'timeout'}
        t5 = {'trigger': 'emg_msg', 'source': 'ready', 'target': 'ready', 'effect': 'switch_emg_mode'}
        t6 = {'trigger': 'emg_msg', 'source': 'recording', 'target': 'recording', 'effect': 'switch_emg_mode'}
        
        s_recording = {'name': 'recording', 'do': 'record()', "stop": "stop()", 'entry': 'start_timer("t", 30000)'}
        s_processing = {'name': 'processing', 'do': 'process()'}

        stm = stmpy.Machine(name=name, transitions=[t0, t1, t2, t3, t4, t5, t6], states=[s_recording, s_processing], obj=self)
        self.stm = stm
        return self.stm