from threading import Thread
import paho.mqtt.client as mqtt
import pyaudio
import json

# MQTT settings
broker = "mqtt.item.ntnu.no"
port = 1883
topic = '1'

# Audio settings
channels = 1
sample_format = pyaudio.paInt16
fs = 44100
p = pyaudio.PyAudio()
chunk = 256

# Audio player
player = p.open(format=pyaudio.paInt16, 
                        channels=1, 
                        rate=44100, 
                        frames_per_buffer = chunk,
                        output=True)

# MQTT setup
def start_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port)
    client.subscribe(topic)
    thread = Thread(target=client.loop_forever)
    thread.start()

# Play incoming audio 
def on_message(client, userdata, msg):
    try:
        data_in = json.loads(msg.payload)

        audiochunks = data_in["audio"]

        for i in range(10):
            player.write(bytes.fromhex(audiochunks[i]), chunk)

    except ValueError:
        pass

# Run
start_mqtt()
