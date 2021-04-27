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

        # Received messages
        self.messages = []
        self.sending_id = ""
        self.first_msg_time = ""
        self.mes_number = 0

        # Setup
        self.setup_logging()
        self.setup_mqtt()
        self.p = pyaudio.PyAudio()
        self.recognizer = sr.Recognizer() # speech recognizer

        # Save loop
        thread = Thread(target=self.save_loop)
        thread.start()

    def setup_logging(self):
        logging.basicConfig(format='%(asctime)s %(message)s',
                            filename= "Log " + datetime.now().strftime("%H:%M:%S") + ".txt",
                            filemode='w',
                            level=logging.DEBUG)

    def setup_mqtt(self):
        print("hi")

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
            if (data_in["id"] == self.sending_id) and \
            (data_in["first_msg_time"] == self.first_msg_time):

                self.messages[0]["msg_chunk_list"] = \
                    self.messages[0]["msg_chunk_list"] + \
                    "".join(data_in["audio"])

            # New message
            else:
                # Add new message
                self.messages.insert(0, {
                    "id" : data_in["id"],
                    "first_msg_time" : data_in["first_msg_time"],
                    "msg_chunk_list" : "".join(data_in["audio"]),
                })

                self.sending_id = data_in["id"]
                self.first_msg_time = data_in["first_msg_time"]
                self.mes_number = 1

        except ValueError:
            pass

    def save_loop(self):
        while 1:
            if self.messages:
                for i in range(len(self.messages)):
                    time_since_first_msg = datetime.now() - datetime.strptime(self.messages[i]["first_msg_time"], "%Y-%m-%d %H:%M:%S.%f")

                    # Save audio and speech log for messages older than 30 seconds
                    if time_since_first_msg > timedelta(seconds=10):
                        audio_filename = self.save_audio_msg(self.messages[i])
                        self.log_audio_as_text(self.messages[i], audio_filename)

                        # Delete message
                        del self.messages[i]

            sleep(5)

    # Save audio and return its filename
    def save_audio_msg(self, message):
        filename = "Audio {}: {}".format(message["first_msg_time"], message["id"])
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(bytes.fromhex(message["msg_chunk_list"]))
        wf.close()
        return filename

    def log_audio_as_text(self, message, filename): 
        print("1")   
        # Open
        audio_file = sr.AudioFile(filename)
        print("2")   

        with audio_file as source:
            rec_audio = self.recognizer.record(source)
        print("3")   

        # Interpret
        interpretation = self.recognizer.recognize_google(rec_audio)
        print("4")   

        # Log
        logging.info("{} {}:\n{}\n".format(message["first_msg_time"], message["id"], interpretation))
        print("5")   

ml = MessageListener("5")