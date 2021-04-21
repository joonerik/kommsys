import stmpy
from appJar import gui
import time
from record_logic import Recorder
from GUI_component import GUI
from playback import Player


stm_driver = stmpy.Driver()
stm_driver.start(keep_active=True)



gui_wt = GUI()
recorder = Recorder()
playback = Player()

driver = stmpy.Driver()
driver.add_machine(gui_wt.create_machine('gui_wt'))
driver.add_machine(recorder.create_machine('stm'))
driver.add_machine(playback.create_machine('playback'))
driver.start()

gui_wt.create_gui()
