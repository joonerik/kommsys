from threading import Thread
from stmpy import Machine, Driver
from os import system
import paho.mqtt.client as mqtt
import os
import pyaudio
import wave
import json

broker, port = "mqtt.item.ntnu.no", 1883

        
class Player:
    def __init__(self, id):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(broker, port)
        self.channel = "team13/" + open("audio_files/channel.txt", "r").readline()
        self.client.subscribe(self.channel)
        self.client.subscribe("team13/emg")
        self.filename = 'audio_files/output_audio/output.wav'
        self.emg_mode = False
        self.id = id 
        self.current_user = None
        self.emergency = []

        self.p = pyaudio.PyAudio()
        self.player = self.p.open(format=pyaudio.paInt16, 
                        channels=1, 
                        rate=44100, 
                        frames_per_buffer = 256,
                        output=True)
        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()

    def on_message(self, client, userdata, msg):
        data_id = (json.loads(msg.payload))["id"]
        if (self.current_user == None):
            self.current_user = data_id

        if (str(msg.topic) == "team13/emg"):
            self.current_user = data_id
            if (len(self.emergency) < 1):
                self.emergency.append(self.current_user)
            
            if ((json.loads(msg.payload))["type"] == "bye"):
                self.current_user = None
                self.emg_mode = False
                self.emergency = []

            elif (str(self.id) != str(data_id) and self.current_user == self.emergency[0]):
                self.emg_mode = True
                try:
                    data = json.loads(msg.payload)
                    audiochunks = data["audio"]
                    for i in range(10):
                        self.player.write(bytes.fromhex(audiochunks[i]), 256)
                except ValueError:
                    print("ValueError raised!")
                    pass
        
        else:
            if ((json.loads(msg.payload))["type"] == "bye"):
                self.current_user = None
            elif (str(self.id) != str(data_id) and self.current_user == data_id):
                if not self.emg_mode:
                    try:
                        data = json.loads(msg.payload)
                        audiochunks = data["audio"]
                        for i in range(10):
                            self.player.write(bytes.fromhex(audiochunks[i]), 256)
                    except ValueError:
                        print("ValueError raised!")
                        pass 
    
    def switch_emg_mode(self):
        self.emg_mode = not self.emg_mode

    def change_channel(self):
        self.client.unsubscribe(self.channel)
        self.channel = "team13/" + open("audio_files/channel.txt", "r").readline()
        self.client.subscribe(self.channel)

    def create_machine(self, name):
        t0 = {'source': 'initial', 'target': 'ready'}
        t5 = {'trigger': 'emg_msg', 'source': 'ready', 'target': 'ready', 'effect': 'switch_emg_mode'}
        t7 = {'trigger': 'change_channel_signal', 'source': 'ready', 'target': 'ready', 'effect': 'change_channel'}

        stm = Machine(name=name, transitions=[t0, t5, t7], obj=self)
        self.stm = stm
        return self.stm