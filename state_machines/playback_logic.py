from threading import Thread
from stmpy import Machine, Driver
from os import system
from utils.reduceNoise import reduce_noise
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
        self.channel = open("audio_files/channel.txt", "r").readline()
        # TODO: We have to make sure that the on_message (callback?) for 'emg'-channel is prioritized
        self.client.subscribe(self.channel)
        self.client.subscribe("emg")
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
            print("set to new user: " + str(self.current_user))

        # play_audio(self.current_user, data_id, msg)
        # TODO: use play_audio function instead, as the logic is similar
        # TODO: fix logic where emg is prioritized
        if (str(msg.topic) == "emg"):
            self.current_user = data_id
            if (len(self.emergency) < 1):
                self.emergency.append(self.current_user)
            print(self.emergency)
            
            if ((json.loads(msg.payload))["type"] == "bye"):
                self.current_user = None
                self.emg_mode = False
                self.emergency = []

            # missing logic for having the channel occupied if multiple emg messages is played
            elif (str(self.id) != str(data_id) and self.current_user == self.emergency[0]):
                self.emg_mode = True
                try:
                    data = json.loads(msg.payload)
                    audiochunks = data["audio"]
                    for i in range(10):
                        # TODO: check emg mode if ongoing receiving msg
                        # while not self.emg_mode:
                        self.player.write(bytes.fromhex(audiochunks[i]), 256)
                except ValueError:
                    print("ValueError raised !!!")
                    pass
        else:
            if ((json.loads(msg.payload))["type"] == "bye"):
                self.current_user = None
                print("Current user: " + str(self.current_user))
                print("only here once")
            elif (str(self.id) != str(data_id) and self.current_user == data_id):
                print("inside elif")
                if not self.emg_mode:
                    print("soon player write")
                    try:
                        data = json.loads(msg.payload)
                        audiochunks = data["audio"]
                        for i in range(10):
                            # TODO: check emg mode if ongoing receiving msg
                            # while not self.emg_mode:
                            self.player.write(bytes.fromhex(audiochunks[i]), 256)
                    except ValueError:
                        print("ValueError raised !!!")
                        pass 
    
    def play_audio(self, current_user, data_id, msg):
        if ((json.loads(msg.payload))["type"] == "bye"):
                self.current_user == None
        elif (str(self.id) != str(data_id) and self.current_user == data_id):
            if not self.emg_mode:
                try:
                    data = json.loads(msg.payload)
                    audiochunks = data["audio"]
                    for i in range(10):
                        # TODO: check emg mode if ongoing receiving msg
                        # while not self.emg_mode:
                        self.player.write(bytes.fromhex(audiochunks[i]), 256)
                except ValueError:
                    print("ValueError raised !!!")
                    pass

        
    def switch_emg_mode(self):
        self.emg_mode = not self.emg_mode
        print("Emergency mode switched to: " + str(self.emg_mode) + " in playback_stm")

    def change_channel(self):
        self.client.unsubscribe(self.channel)
        self.channel = open("audio_files/channel.txt", "r").readline()
        self.client.subscribe(self.channel)

    def create_machine(self, name):
        t0 = {'source': 'initial', 'target': 'ready'}
        t5 = {'trigger': 'emg_msg', 'source': 'ready', 'target': 'ready', 'effect': 'switch_emg_mode'}
        t7 = {'trigger': 'change_channel_signal', 'source': 'ready', 'target': 'ready', 'effect': 'change_channel'}

        stm = Machine(name=name, transitions=[t0, t5, t7], obj=self)
        self.stm = stm
        return self.stm