from threading import Thread
from os import system
import paho.mqtt.client as mqtt
import stmpy
import os
import pyaudio
import uuid
import json
from datetime import datetime

broker, port = "mqtt.item.ntnu.no", 1883

class Recorder:
    def __init__(self, id):
        self.start(broker, port)
        self.recording = False
        self.emg_mode = False
        self.chunk = 256  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 1
        self.fs = 44100  # Record at 44100 samples per second
        self.filename = "audio_files/input_audio/" + str(uuid.uuid4()) + ".wav"
        self.p = pyaudio.PyAudio()
        self.id = id

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
            stream = self.p.open(format=pyaudio.paInt16,  # 16 bits per sample
                             channels=1,
                             rate=44100,   # Record at 44100 samples per second
                             frames_per_buffer=self.chunk,   # Record in chunks
                             input=True)
        
            self.recording = True

            # Record loop
            topic = open("audio_files/channel.txt", "r").readline()
            while self.recording:
                audiochunks = []

                for i in range(10):
                    audiochunks.append(stream.read(self.chunk).hex())
                
                now = datetime.now()
                data_dict = {"id": self.id, "time": now, "audio": audiochunks}
                
                self.client.publish(topic, json.dumps(data_dict))
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()

            # Terminate the PortAudio interface
            self.p.terminate()
        else:
            print("Emergency mode ON - can't start recording")
        
    def stop(self):
        self.recording = False
        self.stm.stop_timer('t')

    def timeout(self):
        print("recording timed out")
        self.stop()
    
    # def process(self):
    #     if not self.emg_mode:
    #         newChannel = open("audio_files/channel.txt", "r")
    #         channel = newChannel.readline()

    #         # Save the recorded data as a WAV file
    #         wf = wave.open(self.filename, 'wb')
    #         wf.setnchannels(self.channels)
    #         wf.setsampwidth(self.p.get_sample_size(self.sample_format))
    #         wf.setframerate(self.fs)
    #         wf.writeframes(b''.join(self.frames))
    #         wf.close()
            
    #         f = open(self.filename, "rb")
    #         imagestring = f.read()
    #         f.close()

    #         byteArray = bytearray(imagestring)

    #         # Send message over mqtt
    #         self.client.publish(channel, byteArray)

    def switch_emg_mode(self):
        self.emg_mode = not self.emg_mode
        print("Emergency mode switched to: " + str(self.emg_mode) + " in record_stm")
         
    def create_machine(self, name): 
        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'recording'}
        # t2 = {'trigger': 'done', 'source': 'recording', 'target': 'processing'}
        # t3 = {'trigger': 'done', 'source': 'processing', 'target': 'ready'}
        t3 = {'trigger': 'stop', 'source': 'recording', 'target': 'ready', 'effect': 'stop'}
        t4 = {'trigger': 't', 'source': 'recording', 'target': 'ready', 'effect': 'timeout'}
        t5 = {'trigger': 'emg_msg', 'source': 'ready', 'target': 'ready', 'effect': 'switch_emg_mode'}
        t6 = {'trigger': 'emg_msg', 'source': 'recording', 'target': 'recording', 'effect': 'switch_emg_mode; stop'}
        
        s_recording = {'name': 'recording', 'do': 'record()', 'entry': 'start_timer("t", 30000)'}
        # s_processing = {'name': 'processing', 'do': 'process()'}

        stm = stmpy.Machine(name=name, transitions=[t0, t1, t3, t4, t5, t6], states=[s_recording], obj=self)
        self.stm = stm
        return self.stm