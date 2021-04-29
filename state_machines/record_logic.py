from threading import Thread
from os import system
import paho.mqtt.client as mqtt
import stmpy
import os
import pyaudio
import uuid
import json
import time
from datetime import datetime

broker, port = "mqtt.item.ntnu.no", 1883

class Recorder:
    def __init__(self, id):
        self.start(broker, port)
        self.recording = False
        self.emg_mode = False
        self.chunk = 256  
        self.sample_format = pyaudio.paInt16 
        self.channels = 1
        self.fs = 44100 
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
            topic = "team13/" + open("audio_files/channel.txt", "r").readline()
            first_packet_time = datetime.now()
            while self.recording:
                audiochunks = []
                for i in range(10):
                    audiochunks.append(stream.read(self.chunk).hex())
                
                data_dict = {"id": self.id, "first_packet_time": str(first_packet_time), "type": "data", "audio": audiochunks}
                
                self.client.publish(topic, json.dumps(data_dict), qos=1)

            # Last packet
            data_dict = {"id": self.id, 
                         "first_packet_time": str(first_packet_time), 
                         "type" : "bye",
                         "audio": ""}

            self.client.publish(topic, json.dumps(data_dict), qos=1)
            
            # Stop and close the stream
            stream.stop_stream()
            stream.close()

        else:
            print("Emergency mode ON - can't start recording")
        
    def stop(self):
        self.recording = False
        time.sleep(0.1)
        self.stm.stop_timer('t')

    def timeout(self):
        self.stop()

    def switch_emg_mode(self):
        self.emg_mode = not self.emg_mode
         
    def create_machine(self, name): 
        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'recording'}
        t3 = {'trigger': 'stop', 'source': 'recording', 'target': 'ready', 'effect': 'stop'}
        t4 = {'trigger': 't', 'source': 'recording', 'target': 'ready', 'effect': 'timeout'}
        t5 = {'trigger': 'emg_msg', 'source': 'ready', 'target': 'ready', 'effect': 'switch_emg_mode'}
        t6 = {'trigger': 'emg_msg', 'source': 'recording', 'target': 'recording', 'effect': 'switch_emg_mode; stop'}
        
        s_recording = {'name': 'recording', 'entry': 'start_timer("t", 30000); record'}

        stm = stmpy.Machine(name=name, transitions=[t0, t1, t3, t4, t5, t6], states=[s_recording], obj=self)
        self.stm = stm
        return self.stm