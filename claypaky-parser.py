# Add logging 
# Neaten up function calls
# Add safety 
  # Authentication
  # Data collection
  # Zabbix processing
# Add threading

import logging
from logging.handlers import TimedRotatingFileHandler

from bs4 import BeautifulSoup
from pyzabbix import ZabbixMetric, ZabbixSender


import configparser

import sys
from time import sleep
import json
import os

from Sharpy import Sharpy, SharpyHelper

logger = logging.getLogger('claypaky-parse')
configPath = filename=os.path.join(sys.path[0], "config.ini")




zabbix_ip="192.168.0.116"
zabbix_packet = []

sharpys = []

#--------- PROGRAM START ----------

log_file_handler = TimedRotatingFileHandler(filename=os.path.join(sys.path[0], "runtime.log"), when='D', interval=1, backupCount=10,
                                    encoding='utf-8',
                                    delay=False)

log_console_handler = logging.StreamHandler(sys.stdout)

log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log_file_handler.setFormatter(log_formatter)
log_console_handler.setFormatter(log_formatter)


logger.setLevel(logging.DEBUG)

logger.addHandler(log_file_handler)
logger.addHandler(log_console_handler)

logger.info("Entering program")

# Logging initialised

zabbixServer = ZabbixSender(zabbix_server=zabbix_ip, timeout=1)

for i in range(81, 83):
  sharpy = Sharpy(logger, "192.168.0." + str(i), str(i))
  sharpys.append(sharpy)

# TODO make this all happen in parallel in the future
while True:
  for sharpy in sharpys:
    SharpyHelper.update(logger, sharpy)
    zabbixPacket = SharpyHelper.generatePacket(logger, sharpy)
    logger.debug(zabbix_packet)
    serverResponse = zabbixServer.send(zabbix_packet) 
    logger.info(serverResponse)

  sleep(5)




###########__________OLD CODE___________#############


packet=[]

for IP_address in IP_address_List:  
  #---------Pull Sensor Status-----------------

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


