class Error():
    def __init__(self, logger):
        self.logger = logger

        self.system         = None
        self.pan            = None
        self.tilt           = None
        self.cyan           = None
        self.magenta        = None
        self.yellow         = None
        self.colourwheel    = None
        self.stopstrobe     = None
        self.dimmer         = None
        self.ovalierchg     = None
        self.prism_rotate   = None
        self.frost1         = None
        self.frost2         = None
        self.zoom           = None
        self.zoom_cp        = None

        self.pt3f           = None
        self.ch6            = None
        self.ch6_2          = None
        self.bus_frequency  = None
        self.bus_deviation  = None

class Fan():
    def __init__(self, logger):
        self.logger = logger

        self.power_supply   = None
        self.lamp_1         = None
        self.lamp_2         = None
        self.ballast        = None


class Sharpy():
    def __init__(self, logger, ip_address, name):
        self.logger = logger
        self.ip_address = ip_address
        self.name = name
        self.authenticated = False
        self.last_updated = None

        self.firmware_version   = None
        self.fixture_hours      = None
        self.lamp_hours         = None
        self.lamp_strikes       = None

        self.error = Error(self.logger)
        self.fans = Fan(self.logger)

        self.logger.debug("Initialised Sharpy " + str(self.name))

    def updateVariable(self, oldVariable, newVariable, name):
        if newVariable == None or newVariable == "NONE":
            return oldVariable
        if (oldVariable != newVariable):
            self.logger.info("Sharpy " + self.name + " updating " + name + ": " + str(oldVariable) + " -> " + str(newVariable))
            oldVariable = newVariable
            return newVariable

    def updateFirmware(self, firmware_version):
        self.firmware_version = self.updateVariable(self.firmware_version, firmware_version, "firmware version")

    def updateHours(self, fixture_hours, lamp_hours, lamp_strikes):
        self.fixture_hours = self.updateVariable(self.fixture_hours, fixture_hours, "fixture hours")
        self.lamp_hours = self.updateVariable(self.lamp_hours, lamp_hours, "lamp hours")
        self.lamp_strikes = self.updateVariable(self.lamp_strikes, lamp_strikes, "lamp strikes")

    def updateSensors(self, 
                      pan,
                      tilt,
                      cyan,
                      magenta,
                      yellow,
                      colourwheel,
                      stopstrobe,
                      dimmer,
                      ovalier_chg,
                      prism_rotate,
                      frost1,
                      frost2,
                      zoom,
                      zoom_cp
                      ):
        self.error.pan = self.updateVariable(self.error.pan, pan, "pan error")
        self.error.tilt = self.updateVariable(self.error.tilt, tilt, "tilt error")
        self.error.cyan = self.updateVariable(self.error.cyan, cyan, "cyan error")
        self.error.magenta = self.updateVariable(self.error.magenta, magenta, "magenta error")
        self.error.yellow = self.updateVariable(self.error.yellow, yellow, "yellow error")
        self.error.colourwheel = self.updateVariable(self.error.colourwheel, colourwheel, "color wheel error")
        self.error.stopstrobe = self.updateVariable(self.error.stopstrobe, stopstrobe, "stop/strobe error")
        self.error.dimmer = self.updateVariable(self.error.dimmer, dimmer, "dimmer error")
        self.error.ovalierchg = self.updateVariable(self.error.ovalierchg, ovalier_chg, "ovalier chg")
        self.error.prism_rotate = self.updateVariable(self.error.prism_rotate, prism_rotate, "prism rotate error")
        self.error.frost1 = self.updateVariable(self.error.frost1, frost1, "frost 1 error")
        self.error.frost2 = self.updateVariable(self.error.frost2, frost2, "frost 2 error")
        self.error.zoom = self.updateVariable(self.error.zoom, zoom, "zoom error")
        self.error.zoom_cp = self.updateVariable(self.error.zoom_cp, zoom_cp, "zoom cp error")

    def updateFans(self, power_supply, lamp_1, lamp_2, ballast):
        self.fans.power_supply = self.updateVariable(self.fans.power_supply, power_supply, "power supply fan speed")
        self.fans.lamp_1 = self.updateVariable(self.fans.lamp_1, lamp_1, "lamp 1 fan speed")
        self.fans.lamp_2 = self.updateVariable(self.fans.lamp_2, lamp_2, "lamp 2 fan speed")
        self.fans.ballast = self.updateVariable(self.fans.ballast, ballast, "ballast fan speed")

    def updateDiagnostics(self, pt3f, ch6, ch6_2, bus_frequency, bus_deviation):
        pass

import requests
from bs4 import BeautifulSoup
from pyzabbix import ZabbixMetric, ZabbixSender

class SharpyHelper():
    def __init__(self):
        pass
    
    def authenticate(logger, sharpy):
        url = "http://" + sharpy.ip_address + "/authenticating.html?passwd=cp1234"
        s = requests.session()

        try:
            response = s.post(url, timeout=2)
            status = response.status_code
            logger.debug("Sharpy " + sharpy.name + ": status = " + str(status))
            sharpy.authenticated = True
        except requests.exceptions.Timeout:
            logger.warn(sharpy.ip_address + ": connection timeout")
            sharpy.authenticated = False
        
        #except:
        #    logger.error("Unhandled error")
        #    sharpy.authenticated = False

    def pullFromWebpage(logger, sharpy, page, classes):
        try:
            url = "http://"+ sharpy.ip_address +"/" + page + ".html"
            req = requests.get(url)
            soup = BeautifulSoup(req.text, "html.parser")
            text_table=soup.find("table", classes).get_text()
            data = [line for line in text_table.split('\n') if line.strip()]

            return data
        except requests.exceptions.Timeout:
            logger.warn(sharpy.ip_address + ": connection timeout")
            sharpy.authenticated = False
        except:
            logger.error("Unknown error")

    def update(logger, sharpy):
        SharpyHelper.authenticate(logger, sharpy)
        if sharpy.authenticated == False: 
            logger.warn("Sharpy " + sharpy.name + ": Unable to authenticate")
            return False

        firmwareData = SharpyHelper.pullFromWebpage(logger, sharpy, "informations", {})
        sharpy.updateFirmware(firmwareData[13])

        hoursData = SharpyHelper.pullFromWebpage(logger, sharpy, "informations", {"class":"ShownTable"})
        sharpy.updateHours(hoursData[5], hoursData[8], hoursData[11])

        #sensorData = SharpyHelper.pullFromWebpage(logger, sharpy, "sensor_status", {})
        
        url = "http://"+ sharpy.ip_address +"/sensors_status.html"
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")

        #find the first table, which includes the firmware version
        text_table=soup.find("table").get_text()
        sensorData=[line for line in text_table.split('\n') if line.strip()]
        sharpy.updateSensors(sensorData[9],     # Pan
                             sensorData[14],    # Tilt
                             sensorData[19],    # Cyan
                             sensorData[24],    # Magenta
                             sensorData[29],    # Yellow
                             sensorData[34],    # Colour Wheel
                             sensorData[39],    # Stop/Strobe
                             sensorData[44],    # Dimmer
                             sensorData[49],    # Ovalier Chg
                             sensorData[54],    # Prism Rotate
                             sensorData[59],    # Frost 1
                             sensorData[64],    # Frost 2
                             sensorData[69],    # Zoom
                             sensorData[74],    # ZoomCp
                             )

        fansData = SharpyHelper.pullFromWebpage(logger, sharpy, "fans_monitor", {})
        sharpy.updateFans(fansData[5], fansData[8], fansData[11], fansData[14])

        #diagnosticData = SharpyHelper.pullFromWebpage(logger, sharpy, "board_diagnostic", {})
        #sharpy.updateDiagnostics(diagnosticData[24][:-2])


        return True
    
    def appendPacket(packet, host, item, data):
        if data == None: return

        packet.append(ZabbixMetric(host, item, data))
        

    def generatePacket(logger, sharpy):
        packet = []
        host = "Sharpy " + sharpy.name

        SharpyHelper.appendPacket(packet, host, "firmware.version", sharpy.firmware_version)
        SharpyHelper.appendPacket(packet, host, "fixture.hours", sharpy.fixture_hours)
        SharpyHelper.appendPacket(packet, host, "lamp.hours", sharpy.lamp_hours)

        SharpyHelper.appendPacket(packet, host, "error.pan", sharpy.error.pan)
        SharpyHelper.appendPacket(packet, host, "error.tilt", sharpy.error.tilt)
        SharpyHelper.appendPacket(packet, host, "error.cyan", sharpy.error.cyan)
        SharpyHelper.appendPacket(packet, host, "error.magenta", sharpy.error.magenta)
        SharpyHelper.appendPacket(packet, host, "error.yellow", sharpy.error.yellow)

        SharpyHelper.appendPacket(packet, host, "error.colourwheel", sharpy.error.colourwheel)
        SharpyHelper.appendPacket(packet, host, "error.stopstrobe", sharpy.error.stopstrobe)
        SharpyHelper.appendPacket(packet, host, "dimmer", sharpy.error.dimmer)
        SharpyHelper.appendPacket(packet, host, "error.ovalierchg", sharpy.error.ovalierchg)
        SharpyHelper.appendPacket(packet, host, "prism.rotate", sharpy.error.prism_rotate)
        SharpyHelper.appendPacket(packet, host, "error.frost1", sharpy.error.frost1)
        SharpyHelper.appendPacket(packet, host, "error.frost2", sharpy.error.frost2)
        SharpyHelper.appendPacket(packet, host, "zoom", sharpy.error.zoom)
        SharpyHelper.appendPacket(packet, host, "zoom.cp", sharpy.error.zoom_cp)

        SharpyHelper.appendPacket(packet, host, "fan.Powersupply", sharpy.fans.power_supply)
        SharpyHelper.appendPacket(packet, host, "fan.lampcooling", sharpy.fans.lamp_1)
        SharpyHelper.appendPacket(packet, host, "fan.lampcooling2", sharpy.fans.lamp_2)
        SharpyHelper.appendPacket(packet, host, "fan.ballast", sharpy.fans.ballast)
        
        return packet
