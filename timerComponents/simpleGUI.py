from appJar import gui

class simple_gui:

    def __init__(self):
        self.create_gui()

    def create_gui(self):
        self.app = gui()

        self.app.setBg('light blue', override=False, tint=False)
        self.app.setFg('#121212', override=False)

        self.app.startLabelFrame('Starting walkie talkie/ Home screen:')
        self.app.addButton('Record message', None)
        self.app.addButton('Emergency', None)
        self.app.addLabelEntry("Type Channel", None)
        self.app.addButton('Change channel', None)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Releasing buttons:')
        self.app.addButton('Release record', None)
        self.app.addButton('Release emergency', None)
        self.app.stopLabelFrame()

        self.app.startLabelFrame('Display:')
        self.app.addLabel('Current Channel: 1', None)
        self.app.addLabel('Current Status: Listening', None)
        self.app.addLabel('Current Volume:', None)
        self.app.addSpinBoxRange("Volume", 1, 100)
        self.app.stopLabelFrame()

        self.app.go()

simple_GUI = simple_gui()