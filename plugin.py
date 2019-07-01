# Basic Python Plugin Example
#
# Author: Dynodix
#
"""
<plugin key="sensibo" name="Sensibo plugin" author="dynodix" version="1.0.0" externallink="http://www.redox.si/">>
    <params>
            <param field="Mode1" label="Sensibo API Key" width="200px" required="true" default=""/>
            <param field="Mode2" label="POD or Device name" width="90px" required="true" default=""/>
    </params>
</plugin>
"""
import Domoticz
import subprocess
import json
import pySensibo_Sky
# ssh prerequisites
# ssh-keygen -t rsa
#  scp -r /root/.ssh/id_rsa.pub  Admin@<IP of mPort>:/var/etc/persistent/.ssh/authorized_keys

class BasePlugin:
    enabled = False
    pluginState = "Not Ready"
    socketOn = "FALSE"
    sessionCookie = ""
    




    def __init__(self):
        return

    def onStart(self):
        # Starting
        API_KEY = Parameters["Mode1"]
        DEVICE_NAME = Parameters["Mode2"]
        client = pySensibo_Sky.Client(API_KEY)
        device = client.get_device(DEVICE_NAME)
        #mode = device.mode
        # Startup ended now configure
        # read params directly from sensibo
        modes = dict()
        domNameMode = "|".join(str(mode.name) for mode in device.supported_modes)
        #mode = device.mode
        swingNameMode = "|".join(str(swinga) for swinga in device.mode.supported_swing_modes)
        fanNameMode = "|".join(str(fans) for fans in device.mode.supported_fan_levels)
        temperatureNameMode = "|".join(str(temper) for temper in device.mode.supported_temps)
        #
        if Parameters["Mode6"] == "Debug":
             Domoticz.Debugging(1)
        if (len(Devices) == 0):
             Domoticz.Device(Name="Switch", Unit=1, TypeName="Switch", Image=9, Used=1).Create()
             Domoticz.Log("Switch Device created.")
             Domoticz.Device(Name="Temp and Hum", Unit=2, TypeName="Temp+Hum", Used=1).Create()
             Domoticz.Log("Temperature and hum sensor created.")
             OptionsMode = {"LevelActions": "||||","LevelNames": domNameMode,"LevelOffHidden": "True","SelectorStyle": "1"}
             Domoticz.Device(Name="Mode", Unit=3, TypeName="Selector Switch", Image=16, Options=OptionsMode, Used=1).Create()
             Domoticz.Log("Mode selector created.")
             OptionsSwing = {"LevelActions": "||||","LevelNames": swingNameMode,"LevelOffHidden": "false","SelectorStyle": "1"}
             Domoticz.Device(Name="Swing", Unit=4, TypeName= "Selector Switch", Image=7, Options=OptionsSwing, Used=1).Create()
             Domoticz.Log("Swing selector created.")
             OptionsFan = {"LevelActions": "||||","LevelNames": fanNameMode,"LevelOffHidden": "false","SelectorStyle": "1"}
             Domoticz.Device(Name="Fan", Unit=5, TypeName= "Selector Switch", Image=7, Options=OptionsFan, Used=1).Create()
             Domoticz.Log("Fan selector created.") 
             OptionsTemperature = {"LevelActions": "||||","LevelNames": temperatureNameMode,"LevelOffHidden": "false","SelectorStyle": "1"}
             Domoticz.Device(Name="Temperature", Unit=6, TypeName= "Selector Switch", Image=16, Options=OptionsTemperature, Used=1).Create()
             Domoticz.Log("Temperature selector created.") 
        pluginState = "Ready"
        DumpConfigToLog()
# seconds for recconect and report
        Domoticz.Heartbeat(20)
#        Domoticz.Connect()
        Domoticz.Debug("onStart called")

    def onStop(self):
        Domoticz.Debug("onStop called")


    def onConnect(self, Status, Description):
        Domoticz.Log("onConnect called")
#        self.mPortLogin()
        if (Status == 0):
            Domoticz.Log("sensibo connected successfully.")
        else:
            self.pluginState = "Not Ready"
#            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"])
#            Domoticz.Debug("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"]+" with error: "+Description)

    def onMessage(self, Data, Status, Extra):
        Domoticz.Debug("on Message called ")

    def onCommand(self, Unit, Command, Level, Hue):
        API_KEY = Parameters["Mode1"]
        DEVICE_NAME = Parameters["Mode2"]
        client = pySensibo_Sky.Client(API_KEY)
        device = client.get_device(DEVICE_NAME)
        power = 1 if device.power else 0
        if (Unit == 1):
           if Command == 'Off' :
              device.power =  False
              Devices[Unit].Update(0,'Off')
              power = 0
           else :
              device.power =  True
              Devices[Unit].Update(1,'On')
              power = 1
        if (Unit == 3):
              modeNames =str(" ".join(str(mode.name) for mode in device.supported_modes)).split()
              modes = dict()
              for mode in device.supported_modes:
                  modes[mode.name] = mode
              mode = modes[modeNames[Level // 10]]
              mode.activate()
              Devices[3].Update(power, str(Level))
        if (Unit == 4):
              swingNames = str(" ".join(str(swinga) for swinga in device.mode.supported_swing_modes)).split()
              device.mode.swing = swingNames[Level // 10]
              Devices[4].Update(power, str(Level))
        if (Unit == 5):
              fanNames = str(" ".join(str(fans) for fans in device.mode.supported_fan_levels)).split()
              device.mode.fan_level = fanNames[Level // 10]
              Devices[5].Update(power, str(Level))
        if (Unit == 6):
              temperatureNames = str(" ".join(str(tempers) for tempers in device.mode.supported_temps)).split()
              device.mode.temp = temperatureNames[Level // 10]
              Devices[6].Update(power, str(Level))
        
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        # write here the switch on command

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        self.SensiboGetValues()
        Domoticz.Debug("onHeartbeat called")


    def SensiboGetValues(self ):
        API_KEY = Parameters["Mode1"]
        DEVICE_NAME = Parameters["Mode2"]
        codemode = ' '
        client = pySensibo_Sky.Client(API_KEY)
        device = client.get_device(DEVICE_NAME)
        temperatura = '%.3f' % device.room_temp
        vlaga = '%.3f' % device.room_humidity
        Devices[2].Update(0, temperatura + ';' + vlaga + ';0')
        power = 1 if device.power else 0
        modes = dict()
        domNameMode = " ".join(str(mode.name) for mode in device.supported_modes)
        domNames = str(domNameMode).split()
        codemode = str(10 * domNames.index(device.mode.name))
        #mode = device.mode
        acmode = device.mode.name
        ModeImage = 16
        if acmode == 'auto':
           ModeImage = 16
        if acmode == 'cool':
           ModeImage = 16
        if acmode == 'dry':
           ModeImage = 11
        if acmode == 'fan':
           ModeImage = 7
        if acmode == 'heat':
           ModeImage = 15
        swingNames = str(" ".join(str(swinga) for swinga in device.mode.supported_swing_modes)).split()
        swingmode = str(10 * swingNames.index(device.mode.swing))
        fanNames = str(" ".join(str(fans) for fans in device.mode.supported_fan_levels)).split()
        fanmode = str(10 * fanNames.index(device.mode.fan_level))
        temperatureNames = str(" ".join(str(tempe) for tempe in device.mode.supported_temps)).split()
        temperature = str(10 * temperatureNames.index(str(device.mode.temp)))
        Devices[1].Update(power, '')
        Devices[3].Update(power, codemode, Image=ModeImage)
        Devices[4].Update(power, swingmode)
        Devices[5].Update(power, fanmode)
        Devices[6].Update(power, temperature, Image=ModeImage)
        #Domoticz.Log("Sensibo get temperatura "+temperatura+" mode=  ; " + codemode)


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Status, Description):
    global _plugin
    _plugin.onConnect(Status, Description)

def onMessage(Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect():
    global _plugin
    _plugin.onDisconnect()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return