# TTM4115 - Design av kommuniserende systemer 💥

This is a semester project in the course TTM4115 - Design av kommuniserende systemer. It includes a system specification which documents the planned system. The system is introduced in the system specification. Our implementation is also covered here, especially in the "implementation comments" section.


## How to run 🚀

There are multiple libraries required to run the application. The requirements should be specified in the "requirements.txt", which should be possible to install by "pip". 

To run the application, run the Python file "GUI_component.py".


## Repository structure 🎨

- [**audio_files**](/audio_files) which is sent, as well as the channel.
- [**img**](/img) used in the GUI.
- [**log_files**](/log_files) which contains a transcribed version of the messages sent.
- [**state_machines**](/state_machines) used in the application.
- [**utils**](/utils) files used for logging and noise reduction. The noise reduction is not currently in use.


## User interface 💄

![UI](https://gitlab.stud.idi.ntnu.no/sindsolh/team13_walkietalkie/-/tree/main/img/ui.png)


## System 📝

The system is implemented using MQTT. A MQTT broker hosted by NTNU is used as the broker, in which our devices, i.e., multiple walkie-talkies, subscribe to a desired channel.  

