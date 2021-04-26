import wave
import speech_recognition as sr
import logging
from threading import Thread
import paho.mqtt.client as mqtt
from playsound import playsound
import pyaudio
import numpy as np
import json
from time import sleep

class MessageListener:
    def __init__(self, topic):

        # MQTT settings
        self.broker = "mqtt.item.ntnu.no"
        self.port = 1883
        self.topic = topic

        # Audio settings
        self.channels = 1
        self.sample_format = pyaudio.paInt16
        self.fs = 44100
        self.chunk = 256

        # Received messages
        self.messages = []
        self.sending_user = ""
        self.initial_mes_time = ""
        self.mes_number = 0

        # Setup
        self.setup_logging()
        self.setup_mqtt
        self.p = pyaudio.PyAudio()
        self.recognizer = sr.Recognizer() # speech recognizer

        # Save loop
        Thread(target=self.save_loop)
        print("hi")

    def setup_logging(self):
        logging.basicConfig(format='%(asctime)s %(message)s',
                                filename='speech_to_text_log.txt',
                                filemode='w',
                                level=logging.DEBUG)

    def setup_mqtt(self):
        client = mqtt.Client()
        client.on_message = self.on_message
        client.connect(self.broker, self.port)
        client.subscribe(self.topic)
        thread = Thread(target=client.loop_forever)
        thread.start()

    def on_message(self, client, userdata, msg):
        try:
            # Parse json
            data_in = json.loads(msg.payload)

            # Add new packets to:

            # Existing message
            if (data_in["user"] == self.sending_user) and \
            (data_in["time"] == self.initial_mes_time):

                self.messages[self.mes_number]["msg_chunk_list"] = \
                    self.messages[self.mes_number]["msg_chunk_list"] + \
                    "".join(data_in["audio"])

                self.mes_number += 1

            # New message
            else:

                self.messages.append({
                    "user" : data_in["user"],
                    "time" : data_in["time"],
                    "msg_chunk_list" : "".join(data_in["msg_chunk_list"]),
                })

                self.sending_user = data_in["user"]
                self.initial_mes_time = data_in["time"]
                self.mes_number = 1

        except ValueError:
            pass

    def save_loop(self):
        while 1:
            if self.messages:
                for i in range(len(self.messages)):
                    self.log_audio_as_text(self.messages[i])
                    self.save_audio_msg(self.messages[i])
                
                self.messages = []

            sleep(5)

    def log_audio_as_text(self, message):
       
        # Open
        audio_file = sr.AudioFile(bytes.fromhex(message["msg_chunk_list"]))

        with audio_file as source:
            rec_audio = self.recognizer.record(source)

        # Interpret
        interpretation = self.recognizer.recognize_google(rec_audio)

        # Log
        logging.info("{} {}:\n{}\n".format(message["time"], message["user"], interpretation))

    def save_audio_msg(self, message):
        wf = wave.open("{}: {}".format(message["time"], message["user"]), 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(bytes.fromhex(message))
        wf.close()

ml = MessageListener("1")