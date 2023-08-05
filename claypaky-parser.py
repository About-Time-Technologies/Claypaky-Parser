from bs4 import BeautifulSoup
import requests

from pyzabbix import ZabbixMetric, ZabbixSender

# Add logging 
# Neaten up function calls
# Add safety 
  # Authentication
  # Data collection
  # Zabbix processing
# Add threading

zabbix_ip="192.168.0.116"

packet=[]
IP_address_List = ["192.168.0.81",
                   "192.168.0.82",
                   "192.168.0.83",
                   "192.168.0.84",
                   "192.168.0.85",
                   "192.168.0.86",
                   "192.168.0.87",
                   "192.168.0.88",
                   "192.168.0.89",
                   "192.168.0.90",
                   "192.168.0.91"]

for IP_address in IP_address_List:
  #Authenticate
  #Ip address of unit to authenticate with
  url = "http://"+ IP_address + "/authenticating.html?passwd=cp1234"

  s = requests.session() 
  response = s.post(url) 
  print(response.status_code) # If the request went Ok we usually get a 200 status.

for IP_address in IP_address_List:

  Host_Name="Sharpy " + IP_address.rsplit(".",1)[1]
  print(Host_Name)

  #the url to pull Lamp & Firmware info from
  url = "http://"+ IP_address +"/informations.html"
  req = requests.get(url, headers={"Content-Type":"text"})
  soup = BeautifulSoup(req.text, "html.parser")

  #find the first table, which includes the firmware version
  text_table=soup.find("table").get_text()
  Firmware_list=[line for line in text_table.split('\n') if line.strip()]
  print("Firmware : " + Firmware_list[13]) #Firmware version
  packet.append(ZabbixMetric(Host_Name, 'firmware.version', Firmware_list[13]))
  
  #pull lamp hours, strikes fixture hours
  text_table=soup.find("table",{"class":"ShownTable"}).get_text()
  Hours_list=[line for line in text_table.split('\n') if line.strip()]
  
  print("Total Fixture Hours : " + Hours_list[5]) #total hours
  packet.append(ZabbixMetric(Host_Name, 'fixture.hours', Hours_list[5]))
  
  print("Lamp Hours : " + Hours_list[8]) #Lamp hours
  packet.append(ZabbixMetric(Host_Name, 'lamp.hours', Hours_list[8]))
  print("Lamp Strikes : " + Hours_list[11]) #Lamp strikes
  packet.append(ZabbixMetric(Host_Name, 'lamp.strikes', Hours_list[11]))
  #---------Pull Sensor Status-----------------

  #the url to pull Lamp & Firmware info from
  url = "http://"+ IP_address +"/sensors_status.html"
  req = requests.get(url)
  soup = BeautifulSoup(req.text, "html.parser")

  #find the first table, which includes the firmware version
  text_table=soup.find("table").get_text()
  Sensor_Status_list=[line for line in text_table.split('\n') if line.strip()]
  #print(Sensor_Status_list) #sensor list
  print("")
  print("Pan Errors : " + Sensor_Status_list[9]) #Pan Errors
  packet.append(ZabbixMetric(Host_Name, 'error.pan', Sensor_Status_list[9]))
  print("Tilt Errors : " + Sensor_Status_list[14]) #Tilt Error
  packet.append(ZabbixMetric(Host_Name, 'error.tilt', Sensor_Status_list[14]))
  print("Cyan Errors : " + Sensor_Status_list[19]) #Cyan Error
  packet.append(ZabbixMetric(Host_Name, 'error.cyan', Sensor_Status_list[19]))
  print("Magenta Errors : " + Sensor_Status_list[24]) #Magenta Error
  packet.append(ZabbixMetric(Host_Name, 'error.magenta', Sensor_Status_list[24]))
  print("Yellow Errors : " + Sensor_Status_list[29]) #Yellow Error
  packet.append(ZabbixMetric(Host_Name, 'error.yellow', Sensor_Status_list[29]))

  print("Colour Wheel Errors : " + Sensor_Status_list[34]) #Colour Wheel Error
  packet.append(ZabbixMetric(Host_Name, 'error.colourwheel', Sensor_Status_list[34]))
  print("Stop/Strobe Errors : " + Sensor_Status_list[39]) #Stop/Strobe Errors
  packet.append(ZabbixMetric(Host_Name, 'error.stopstrobe', Sensor_Status_list[39]))
  print("Dimmer : " + Sensor_Status_list[44]) #Dimmer Error
  packet.append(ZabbixMetric(Host_Name, 'dimmer', Sensor_Status_list[44]))
  print("Ovalier Chg : " + Sensor_Status_list[49]) #Ovalier Chg
  packet.append(ZabbixMetric(Host_Name, 'error.ovalierchg', Sensor_Status_list[49]))
  print("Prism Rotate : " + Sensor_Status_list[54]) #Prism Rotate
  packet.append(ZabbixMetric(Host_Name, 'prism.rotate', Sensor_Status_list[54]))
  print("Frost 1 : " + Sensor_Status_list[59]) #Frost 1
  packet.append(ZabbixMetric(Host_Name, 'error.frost1', Sensor_Status_list[59]))
  print("Frost 2 : " + Sensor_Status_list[64]) #Frost 2
  packet.append(ZabbixMetric(Host_Name, 'error.frost2', Sensor_Status_list[64]))
  print("Zoom : " + Sensor_Status_list[69]) #Zoom Error
  packet.append(ZabbixMetric(Host_Name, 'zoom', Sensor_Status_list[69]))
  print("ZoomCP : " + Sensor_Status_list[74]) #ZoomCp Error
  packet.append(ZabbixMetric(Host_Name, 'zoom.cp', Sensor_Status_list[74]))

  #---------Pull Fan Speeds-----------------


  #the url to pull Lamp & Firmware info from
  url = "http://"+ IP_address +"/fans_monitor.html"
  req = requests.get(url)
  soup = BeautifulSoup(req.text, "html.parser")

 #find the first table, which includes the fan seeds
  text_table=soup.find("table").get_text()
  Fan_speed_list=[line for line in text_table.split('\n') if line.strip()]
  #print(Fan_speed_list) 
  print("")
  print("Power Supply : " + Fan_speed_list[5]) #Power Supply
  packet.append(ZabbixMetric(Host_Name, 'fan.Powersupply', Fan_speed_list[5]))
  print("Lamp Cooling : " + Fan_speed_list[8]) #Lamp Cooling
  packet.append(ZabbixMetric(Host_Name, 'fan.lampcooling', Fan_speed_list[8]))
  print("Lamp Cooling 2 : " + Fan_speed_list[11]) #Lamp Cooling 2
  packet.append(ZabbixMetric(Host_Name, 'fan.lampcooling2', Fan_speed_list[11]))
  print("Ballast : " + Fan_speed_list[14]) #Ballast
  packet.append(ZabbixMetric(Host_Name, 'fan.ballast', Fan_speed_list[14]))

  #---------Pull Board communication Status-----------------


  #the url to pull board diagnostics info
  url = "http://"+ IP_address +"/board_diagnostic.html"
  req = requests.get(url)
  soup = BeautifulSoup(req.text, "html.parser")

  #find the first table, which includes the fan seeds
  text_table=soup.find("table").get_text()
  Board_Diagnostic_list=[line for line in text_table.split('\n') if line.strip()]
  #print(Board_Diagnostic_list) 

  print("")
  Board_Diagnostic_list[24]=Board_Diagnostic_list[24][:-2]
  print("PT-3f Errors : " + Board_Diagnostic_list[24]) #PT-3f Errors
  packet.append(ZabbixMetric(Host_Name, 'errors.PT3F', Board_Diagnostic_list[24]))
  Board_Diagnostic_list[32]=Board_Diagnostic_list[32][:-2]
  print("6-Ch : " + Board_Diagnostic_list[32]) #6-Ch
  packet.append(ZabbixMetric(Host_Name, 'diag.6ch', Board_Diagnostic_list[32]))
  Board_Diagnostic_list[40]=Board_Diagnostic_list[40][:-2]
  print("6-Ch-2 : " + Board_Diagnostic_list[40]) #6-Ch-2
  packet.append(ZabbixMetric(Host_Name, 'diag.6ch2', Board_Diagnostic_list[40]))

  #Bus Error Frequency
  Bus_Error_List = soup.find('p').get_text().strip("Bus error frequency:").split("-")
  Bus_Error_List[1]=Bus_Error_List[1].strip("standard deviation: Hz")
  Bus_Error_List[0]=Bus_Error_List[0].strip(" Hz ")
  print("")

  print("Bus Error Frequency: " + Bus_Error_List[0])
  packet.append(ZabbixMetric(Host_Name, 'error.busfrequency', Bus_Error_List[0]))
  print("Bus Error Stanbdard Deviation: " + Bus_Error_List[1])
  packet.append(ZabbixMetric(Host_Name, 'error.busdeviation', Bus_Error_List[1]))

  #---------Pull Error Log -----------------

  #the url to pull error log
  url = "http://"+ IP_address +"/system_errors.html"
  req = requests.get(url)
  soup = BeautifulSoup(req.text, "html.parser")

  #find the first table, which includes the fan seeds
  text_table=soup.find("table").get_text()
  system_errors_list=[line for line in text_table.split('\n') if line.strip()]
  #print(system_errors_list)

  if len(system_errors_list) > 6:
    print(system_errors_list[9])
    packet.append(ZabbixMetric(Host_Name, 'errors.system', system_errors_list[9]))

print(packet)
print(ZabbixSender(zabbix_server=zabbix_ip, timeout = 1).send(packet))


