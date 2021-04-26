from threading import Thread
from stmpy import Machine, Driver
from os import system
from utils.reduceNoise import reduce_noise
import paho.mqtt.client as mqtt
import os
import pyaudio
import wave

broker, port = "mqtt.item.ntnu.no", 1883
        
class Player:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(broker, port)
        self.channel = open("audio_files/channel.txt", "r").readline()
        # TODO: We have to make sure that the on_message (callback?) for 'emg'-channel is prioritized
        self.client.subscribe(self.channel)
        self.client.subscribe("emg")
        self.filename = 'audio_files/output_audio/output.wav'
        self.emg_mode = False

        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()

    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))
        f = open(self.filename, 'wb')
        f.write(msg.payload)
        f.close()

        reduce_noise(self.filename)
        self.stm.send("start")
        
    def play(self):
        if not self.emg_mode:
            # Set chunk size of 1024 samples per data frame
            chunk = 1024  

            # Open the sound file 
            wf = wave.open(self.filename, 'rb')

            # Create an interface to PortAudio
            p = pyaudio.PyAudio()

            # Open a .Stream object to write the WAV file to
            # 'output = True' indicates that the sound will be played rather than recorded
            stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                            channels = wf.getnchannels(),
                            rate = wf.getframerate(),
                            output = True)

            # Read data in chunks
            data = wf.readframes(chunk)
            # Play the sound by writing the audio data to the stream
            while data != (b'') and not self.emg_mode:
                stream.write(data)
                data = wf.readframes(chunk)

            # Close and terminate the stream
            print("Message is finished")
            stream.close()
            p.terminate()
        else:
            # TODO: Test if an incoming message on a channel subscribed is ignored if a emg msg is playing
            # Remember to argue for this in the systemSpec. It is also not likely that a person is
            # sending a msg while an emg msg is played
            print("Emergency mode ON - can't play incoming message")

    def switch_emg_mode(self):
        self.emg_mode = not self.emg_mode
        print("Emergency mode switched to: " + str(self.emg_mode) + " in playback_stm")

    def change_channel(self):
        self.client.unsubscribe(self.channel)
        self.channel = open("audio_files/channel.txt", "r").readline()
        self.client.subscribe(self.channel)

    def create_machine(self, name):
        t0 = {'source': 'initial', 'target': 'ready'}
        t1 = {'trigger': 'start', 'source': 'ready', 'target': 'playing'}
        t2 = {'trigger': 'done', 'source': 'playing', 'target': 'ready'}
        t8 = {'trigger': 'abort', 'source': 'playing', 'target': 'ready'}
        t5 = {'trigger': 'emg_msg', 'source': 'ready', 'target': 'ready', 'effect': 'switch_emg_mode'}
        t6 = {'trigger': 'emg_msg', 'source': 'playing', 'target': 'ready', 'effect': 'switch_emg_mode'}
        t7 = {'trigger': 'change_channel_signal', 'source': 'ready', 'target': 'ready', 'effect': 'change_channel'}
        
        s_playing = {'name': 'playing', 'do': 'play()'}


        stm = Machine(name=name, transitions=[t0, t1, t2, t5, t6, t7, t8], states=[s_playing], obj=self)
        self.stm = stm
        return self.stm