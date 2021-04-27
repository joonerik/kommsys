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
from datetime import datetime
from datetime import timedelta

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

        # Currently received message
        self.message = {}

        # Setup
        self.setup_logging()
        self.setup_mqtt()
        self.p = pyaudio.PyAudio()

    def setup_logging(self):
        logging.basicConfig(format='%(asctime)s %(message)s',
                            filename= "Log " + datetime.now().strftime("%H:%M:%S") + ".txt",
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

            # Existing message
            if (data_in["id"] == self.message.get("id")) and \
            (data_in["first_packet_time"] == self.message.get("first_packet_time")):

                self.message["audio"] = \
                    self.message["audio"] + \
                    "".join(data_in["audio"])
                
                # Save if last packet
                if data_in.get("type") == "bye":
                    audio_filename = self.save_audio_msg() # audio
                    self.log_audio_as_text(audio_filename) # text
                    print("hi")
            # New message
            else:
                print("lol")

                # Add new message
                self.message = data_in
                self.message["audio"] = "".join(self.message["audio"]) # list to string

        except ValueError:
            pass

    # Save audio and return its filename
    def save_audio_msg(self):
        filename = "Audio {}: {}".format(self.message["first_packet_time"], self.message["id"])
        print("SAVING")
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(bytes.fromhex(self.message["audio"]))
        wf.close()

        return filename

    def log_audio_as_text(self, filename): 
        # Open
        audio_file = sr.AudioFile(filename)

        r = sr.Recognizer()

        with audio_file as source:
            rec_audio = r.record(source)

        # Interpret. Casts exeption for unintelligible sounds
        try:
            interpretation = r.recognize_google(rec_audio)
        except sr.UnknownValueError:
            pass

        # Log
        logging.info("{} {}:\n{}\n".format(self.message["first_packet_time"], self.message["id"], interpretation))

ml = MessageListener("5")