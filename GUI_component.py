import stmpy
from appJar import gui
from state_machines.record_logic import Recorder
from state_machines.playback_logic import Player
from state_machines.record_emg_logic import RecorderEmergency
import socket
from random import randint

class GUI:
    def create_driver(self):
        self.id = socket.gethostname() + str(randint(0,100))
        self.recorder = Recorder(self.id)
        self.playback = Player(self.id)
        self.recorder_emg = RecorderEmergency(self.id)
        self.driver = stmpy.Driver()
        self.driver.add_machine(self.recorder.create_machine('recorder_stm'))
        self.driver.add_machine(self.playback.create_machine('playback_stm'))
        self.driver.add_machine(self.recorder_emg.create_machine('recorder_emg_stm'))
        self.driver.start()

    def recording(self):
        self.driver.send('start', 'recorder_stm')
        print("Start recording")
        self.isRecording = True
        self.app.setImage("show", "img/recording.png")
        self.app.setImageMap("show", self.click, self.coords)

    def stop_recording(self):
        self.driver.send('stop', 'recorder_stm')
        print("Stop recording")
        self.app.setImage("show", "img/idle2.png")
        self.isRecording = False
        self.app.setImageMap("show", self.click, self.coords)

    def recording_emg(self):
        if self.isRecording == True:
            self.driver.send('stop', 'recorder_stm')

        self.driver.send('emg_msg', 'recorder_stm')
        self.driver.send('emg_msg', 'playback_stm')
        self.driver.send('start', 'recorder_emg_stm')
        print("Start emergency recording")
        self.emgMode = True
        self.app.setBg("red")
        self.app.setFg("red")
        self.app.setImage("show", "img/ssos.png")
        self.app.setImageMap("show", self.click, self.coords)

    def stop_recording_emg(self):
        self.driver.send('emg_msg', 'recorder_stm')
        self.driver.send('emg_msg', 'playback_stm')
        self.driver.send('stop', 'recorder_emg_stm')
        print("Stop recording emergency")
        self.emgMode = False
        self.app.setBg("mediumslateblue")
        self.app.setFg("Pink")
        self.app.setImage("show", "img/idle2.png")
        self.app.setImageMap("show", self.click, self.coords)

    def change_channel(self, channel):
        newChannel = open("audio_files/channel.txt", "w")
        newChannel.write(channel)
        print("Change channel to: " + str(channel))
        self.driver.send('change_channel_signal', 'playback_stm')

    def __init__(self):
        self.app = gui()
        self.channel_number = open("audio_files/channel.txt", "r").readline()
        self.channelEdit = False
        self.isRecording = False
        self.emgMode = False
        self.app.setBg("mediumslateblue")
        self.app.setFg("pink")
        self.app.setExpand("NONE")
        self.coords = {
            "Record": [76, 404, 188, 483],
            "SOS": [79, 496, 178, 533],
            "1": [83,565,138,594],
            "2": [158, 565, 224, 594],
            "3": [241, 565, 301, 594],
            "4": [83, 609, 138, 637],
            "5": [158, 609, 224, 637],
            "6": [241, 609, 301, 637],
            "7": [83, 652, 138, 684],
            "8": [158, 652, 224, 684],
            "9": [241, 652, 301, 684],
            "0": [158, 702, 224, 726],
            "change channel": [83, 702, 138, 726],
            "done": [241, 702, 301, 726]
        }

        self.app.addImage("show", "img/idle.png", 0, 0)
        self.app.setImageMap("show", self.click, self.coords)
        self.app.addLabel("l1", "<click on the device>")
        self.driver = stmpy.Driver()
        self.driver.start(keep_active=True)
        self.create_driver()


    def click(self, area):
        self.app.setLabel("l1", "Latest area clicked: " + area)
        if area == "SOS":
            if not self.emgMode:
                self.recording_emg()
            else:
                self.stop_recording_emg()

        if area == "Record" and not self.emgMode:
            if not self.isRecording:
                self.recording()
            else:
                self.stop_recording()
        
        if area == "change channel" and not self.emgMode:
            self.channelEdit = True
        
        k = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        if self.channelEdit:
            if area in k:
                self.channel_number += area
            
            if area == "done":
                self.channelEdit = False
                if self.channel_number != "":
                    self.app.setLabel("channelnow", "Current channel: " + self.channel_number)
                    self.change_channel(self.channel_number)
                    self.channel_number = ""
        self.app.go()

    def create_gui(self):
        self.app.setFont(16)
        self.app.startLabelFrame('Info:', 0,2)
        self.app.addLabel("channelnow", "Current channel: " + self.channel_number)
        self.channel_number = ""
        self.app.stopLabelFrame()
        self.app.go()

gui_wt = GUI()
gui_wt.create_gui()