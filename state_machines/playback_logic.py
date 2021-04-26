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
        if str(self.id) != str(data_id):
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