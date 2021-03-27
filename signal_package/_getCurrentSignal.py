from datetime import datetime
import requests as req
import json
from ._globalVariables import PRODUCTION_ARRAY
from ._holdMachine import holdMachine
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)

#PRODUCTION MATCHING ARRAY
PRODUCTION_ARRAY=["cycleON","m30OFF"]

#DICTONARY WHICH STORES THE DEFAULT STATUS VALUES FOR EVERY LIVE STATUS SIGNAL
LIVE_STATUS_CODES =  {
    "machineIdle" : 0,
    "cycle" : 2,
    "emergency" : 3,
    "alarm" : 4
       }

#global FLAG VARIABLES WHICH KEEPS A TRACK OF STATUS OF THE EVERY SIGNAL , WHETHER THE SIGNAL IS ON OR OFF
#FLAG = 0  SIGNAL IS OFF 
#FLAG = 1 SIGNAL IS ON
cycleflag=0
spindleflag=0
resetflag=0
emergencyflag=0
alarmflag=0
runoutnotokflag=0
machineflag=0
m30flag=0

TEMP_PRODUCTION_ARRAY =  []

def getCurrentSignal(self,InputPin,processOn,processOff):
    flag=getFlagStatus(processOn)
    #Read signal from the Raspberry pi 
    SignalStatus=GPIO.input(InputPin)
    #check the time at which this signal is raised
    timeObj = datetime.now()
    timeStamp=timeObj.strftime("%Y/%m/%d %H:%M:%S")
    #machine on conditions
    if(flag == 0 and SignalStatus==1):
        process=processOn
        print(process)
        print(timeStamp)
        setFlagStatus(process,1)
        insertSignalToLocalDb(self,self.machineId,process,timeStamp)
        if process=="alarmON":
	    GPIO.output(11, False)
            updateLiveStatus(self,LIVE_STATUS_CODES['alarm'],"Alarm","red")
            holdMachine(self,)
            jobProgress(self,"finished")
        elif process=="machineON":
            updateLiveStatus(self,LIVE_STATUS_CODES['machineIdle'],"Machine Idle","orange")
            holdMachine(self,)
        elif process=="emergencyON":
	    GPIO.output(11, False)
            updateLiveStatus(self,LIVE_STATUS_CODES['emergency'],"Emergency","red")
            jobProgress(self,"finished")
        elif process=="cycleON":
	    GPIO.output(11, True)
            TEMP_PRODUCTION_ARRAY.clear()
            TEMP_PRODUCTION_ARRAY.append(process)
            updateLiveStatus(self,LIVE_STATUS_CODES['cycle'],"Cycle","green")
            #update progress of job as job running
            jobProgress(self,"running")
                                      
        else:
            pass

    #machine off condition
    if(flag == 1 and SignalStatus == 0):
        process=processOff
        print(process)
        print(timeStamp)
        setFlagStatus(process,0)
        insertSignalToLocalDb(self,self.machineId,process,timeStamp)
        if (process=="emergencyOFF" or process=="cycleOFF" or process=="alarmOFF"):
            updateLiveStatus(self,LIVE_STATUS_CODES['machineIdle'],"Machine Idle","orange") 
            holdMachine(self,)
        if (process=="cycleOFF"):
	    GPIO.output(11, False)
            #update progress of job has finished 
            jobProgress(self,"finished")

        elif process=="m30OFF":
            TEMP_PRODUCTION_ARRAY.append(process)
            if(PRODUCTION_ARRAY==TEMP_PRODUCTION_ARRAY[0:2]):
               print("Array matched")
               #make production status as 1 and progress as job finished
               productionOk(self,"finished")

        else:
            pass

def insertSignalToLocalDb(self,machineId,process,timeStamp):       
      sql="INSERT INTO signals(machineId,process,timeStamp) VALUES(?,?,?)"               
      values=(machineId,process,timeStamp)
      try:
          if(self.cursor.execute(sql,values)):
              self.connection.commit()
              print("successfully inserted into local database")
      except:
          print("unable to insert into local database")

def productionOk(self,progress):
      data=self.cursor.execute("SELECT MAX(id) FROM production")
      lastId=self.cursor.fetchone()[0]
      sql="update production set status=?,progress=? where id=?"
      values=("1",progress,lastId)
      try:
          result=self.cursor.execute(sql,values)
          self.connection.commit()
          print("updated status  1 to last production job ")
      except:   
          print("failed to update status  1 to last production job")

def jobProgress(self,progress):
      data=self.cursor.execute("SELECT MAX(id) FROM production")
      lastId=self.cursor.fetchone()[0]
      sql="update production set progress=? where id=?"
      values=(progress,lastId)
      try:
          result=self.cursor.execute(sql,values)
          self.connection.commit()
          print("updated progress as {} to last production job ".format(progress))
      except:   
          print("failed to update progress of job to last production job")


def updateLiveStatus(self,status,signal,color):
      try:
         query = "update live_status set status=?,signalName=?,color=? where id=?" 
         values = (status,signal,color,1) 
         self.cursor.execute(query,values) 
         self.connection.commit()
         print("live status machine idle updated")  
      except Exception as e:
         print("failed to update live status")          

def getFlagStatus(process):
          global cycleflag,spindleflag,machineflag,m30flag,resetflag,emergencyflag,alarmflag,runoutnotokflag
          if(process=="cycleON" or process=="cycleOFF"):
              return cycleflag
          elif(process=="spindleON" or process=="spindleOFF"):
              return spindleflag
          elif(process=="machineON" or process=="machineOFF"):
              return machineflag
          elif(process=="m30ON" or process=="m30OFF"):
              return m30flag
          elif(process=="resetON" or process=="resetOFF"):
              return resetflag
          elif(process=="emergencyON" or process=="emergencyOFF"):
              return emergencyflag
          elif(process=="alarmON" or process=="alarmOFF"):
              return alarmflag
          else:
              return  runoutnotokflag

def setFlagStatus(process,flag):
          global cycleflag,spindleflag,machineflag,m30flag,resetflag,emergencyflag,alarmflag,runoutnotokflag
          if(process=="cycleON" or process=="cycleOFF"):
              cycleflag=flag
              return cycleflag
          elif(process=="spindleON" or process=="spindleOFF"):
              spindleflag=flag
              return spindleflag
          elif(process=="machineON" or process=="machineOFF"):
              machineflag=flag
              return machineflag
          elif(process=="m30ON" or process=="m30OFF"):
              m30flag=flag     
              return m30flag
          elif(process=="resetON" or process=="resetOFF"):
              resetflag=flag     
              return resetflag
          elif(process=="emergencyON" or process=="emergencyOFF"):
              emergencyflag=flag     
              return emergencyflag
          elif(process=="alarmON" or process=="alarmOFF"):
              alarmflag=flag     
              return alarmflag
          else:
              runoutnotokflag=flag
              return  runoutnotokflag 

              



