#*********This script is used to send all the IIOT data from device to server**************************

#importing of required libraries
from time import sleep
import sqlite3
import requests as req
from datetime import datetime
import configuration as config

#making a connection with the database
conn2 = sqlite3.connect(config.DATABASENAME)

#create a cursor object to execute all sql queries
curs2 = conn2.cursor()
curs2 = conn2.execute('PRAGMA journal_mode = wal')

#Function which sends AlarmInfo  data
#parameters :  endpoint - at which endpoint to send the data
#no return type for the fucntion
def SendAlarmData(endpoint):
   print("****************SENDING ALARM DATA********************")
   try:
             curs2.execute("select * from alarm ")
             result = curs2.fetchall()
             if result is not None:
               data = {}
               for colm in result:
                 Id = colm[0]
                 data["ID"] = colm[0]
                 data["MachineID"] = colm[1]
                 data["OperatorName"] = colm[2]
                 data["JobID"] = colm[3]
                 data["Shift"] = colm[4]
                 data["Component"] = colm[5]
                 data["ModelName"] = colm[6]
                 data["Operation"] = colm[7]
                 data["TimeStamp"] = colm[8]
                 data["Reason"] = colm[9]
                 data['ErrorCode'] = colm[10]
                 response = req.post(endpoint, data = data, timeout = 2)
                 if(response.status_code >= 200 and response.status_code <= 206):
                         curs2.execute("delete from alarm where id=(?)", (Id,))
                         conn2.commit()
                         print("{} entry send to server and deleted from local database ").format(Id)
                 else:
                    print(response.status_code) 
                    print("didnot get good response from server") 
                    return
             else:
                print("no data to send ...")
   except Exception as e:
              print("Exception occured : ",e)
              return

#Function which sends liveStatus data
#parameters :  endpoint - at which endpoint to send the data
#no return type for the fucntion
def SendLiveStatus(endpoint):
         print("****************SENDING LIVE SIGNALS DATA********************")
         try:
           curs2.execute("select * from live_status")
           result = curs2.fetchone()
           if result is not None:
             Id = str(result[0])
             machineId = result[1]
             machineType = result[2]
             status = str(result[3])
             signalColor = result[4]
             signalName = result[5]
             response = req.post(endpoint + "?ID=" + Id + "&MachineID=" + machineId + "&MachineType=" + machineType + "&Status=" + status + "&SignalName=" + signalName + "&SignalColor=" + signalColor, timeout = 2)
             if(response.status_code >= 200 and response.status_code <= 206):
                    print("Current Live Status : {}".format(signalName))
                    print(" Live Status data successfully sent ")
             else:
                 print("Did not get good response from server")
                 return
           else:
               print("No data to send....")
         except Exception as e:
              print("Exception occured : ", e)
              return

#Function which sends production data
#parameters :  endpoint - at which endpoint to send the data
#no return type for the fucntion
def SendProductionData(endpoint):
   print("********************SENDING PRODUCTION DATA****************************")
   try:
           curr_time = datetime.now()
           formatted_time = curr_time.strftime('%H:%M:%S')
           print("$$$$$$$$$$$$$$$$$",formatted_time)
           if(str(formatted_time) == "7:00:00" or str(formatted_time) == "7:00:01" or str(formatted_time) == "7:00:02"):
               curs2.execute("delete from production")
               conn2.commit()
           productionLastRow = curs2.execute("SELECT * FROM production order by id desc")
           if productionLastRow is not None:
             jobProgress = curs2.fetchone()[13]
             if jobProgress == 'finished':
                curs2.execute("select * from production_status")
                idNo=curs2.fetchone()[1]
                print("Production Last value : " + str(idNo))
                curs2.execute("select * from production where id>(?) ",(idNo,))
                result = curs2.fetchall()
                if result is not None:
                    data = {}
                    for colm in result:
                        Id = colm[0]
                        data["ID"] = colm[0]
                        data["OperatorName"] = colm[1]
                        data["JobID"] = colm[2]
                        data["Shift"] = colm[3]
                        data["Component"] = colm[4]
                        data["ModelName"] = colm[5]
                        data["Operation"] = colm[6]
                        data["CycleTime"] = float(colm[7])
                        data["InspectionStatus"] = colm[8]
                        Status_data = int(colm[9])
                        data["Status"] = bool(Status_data)
                        data["TimeStamp"] = datetime.strptime(colm[10], '%Y/%m/%d %H:%M:%S') 
                        data["MachineID"] = colm[11]

                        response = req.post(endpoint, timeout = 2, data = data)
                        if(response.status_code >= 200 and response.status_code <= 206):
                              curs2.execute("update production_status set value=(?) where id=(?)", (Id, 1))
                              print("{} entry updated..".format(Id))
                              conn2.commit()
                        else:
                              print("Did not get good response from server")
                              return
                else:
                       print("No data to send ...")
   except Exception as e:
            print("Exception occured : ", e)
            return

#continously run the loop to send data to server every 2 seconds
'''while(1):

    #Function call of 'SendLiveStatus' Function
    SendLiveStatus("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/PostMachineStatus")

    #Function call of 'SendProductionData' Function
    SendProductionData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/Production")

    #Function call of 'SendAlarmData' Function
    SendAlarmData("http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/AlarmInfo")

    #wait for 5 seconds
    sleep(5)'''
