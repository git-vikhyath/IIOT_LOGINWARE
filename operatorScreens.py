from flask import Blueprint,request,jsonify
from datetime import datetime,timedelta,time
from sqlalchemy import exc,cast,Date,func,and_
import requests as req
import json
import configuration as config
from models import *

operator = Blueprint('operator',__name__)


@operator.route('/login', methods=['GET', 'POST'])
def login():
   machineId=request.get_json()['machineId']
   username=request.get_json()['username']
   password=request.get_json()['password']
   resultData={}
   #calculate the current shift
   TimeObj=datetime.now().time()
   print("Current Time :" + str(TimeObj))
   query=db.session.query(ShiftData).filter(and_(func.time(ShiftData.fromTime)<=TimeObj,func.time(ShiftData.toTime)>=TimeObj)) 
   for row in query.all():  
     if(row.id==1):
         print("Shift 1")
         resultData['Shift']=row.shift             
     elif(row.id==2):
         print("Shift 2")
         resultData['Shift']=row.shift 
     elif(row.id==3):
         print("Shift 3")
         resultData['Shift']=row.shift                         
     else: 
         pass

   #check for admin user 
   if(username=="admin" and password=="IIotAdmin"):
         return jsonify({"result": {"status":1,"admin":True,"message":"success"}})   

   #check for a valid user or no       
   loginUrl="http://" + config.SERVER_IP + config.SERVER_ENDPOINT_START + "/Login"
   headers = config.HEADERS 
   try:
         res=req.post(loginUrl,headers=headers,data=json.dumps({"UserID":username,"Password":password,"MachineCode":machineId}),timeout=4)     
         componentList=[]
         modelList=[]
         data=res.json() 
         print(data)
         if(data['Error']!=None):
              print("error")    
              return jsonify({"result": {"status":0,"admin":False,"message":"invalid username or password"}}) 
         else:
              resultData['FullName']=data['FullName']
              data1=data['Components']
              data2=data['ProductModels']
              for datas in data1:
                 componentList.append(datas['Code'])
              for datas in data2:
                 modelObj={}
                 modelObj['code']=datas['Code']
                 modelObj['value']=datas['Value']   
                 modelList.append(modelObj)       
              resultData['Components']=componentList
              resultData['Models']=modelList
              print(resultData);
              return jsonify({"result": {"status":1,"admin":False,"message":"success","data":resultData}})      
   except Exception as e:         
         print("error while connecting to server for login details",e)
         return jsonify({"result": {"status":0,"admin":False,"message":"Something Went Wrong, Check Network Connection"}})

             
@operator.route('/', methods=['GET', 'POST'])
def loadScreen():
   #save shift data to databse
   try:
       url="http://"+config.SERVER_IP+config.SERVER_ENDPOINT_START+"/ShiftList" 
       print(url)     
       res=req.get(url,timeout=4)
       datas=res.json()
       for data in datas: 
          idNew=data['ID']
          shiftNew=data['Name']
          fromTimeNew=data['FromTime']
          toTimeNew=data['ToTime']
          fromTimeNew=datetime.strptime(fromTimeNew,"%Y-%m-%dT%H:%M:%S")
          toTimeNew=datetime.strptime(toTimeNew,"%Y-%m-%dT%H:%M:%S")
          shiftObj=ShiftData(id=idNew,shift=shiftNew,fromTime=fromTimeNew,toTime=toTimeNew)
          try:
             result=ShiftData.query.filter_by(id=idNew).scalar() 
             if(result!=None):
                 pass
             else:    
                db.session.add(shiftObj)
                db.session.commit() 
                print("added shift data to datbase") 
          except Exception as e:
             print(e)
                     
   except:
       print("something went wrong while getting shift data...." )

    
   data={}
   try:
      result=otherSettings.query.get(1)
      if(result!=None):
          data['machineId']=result.machineId
          data['idleTimeout'] = result.idleTimeout
          data['batchSize']= result.batchSize
          holdingPin = result.holdingRelay
      else:
          print("no other settings data in database")

      #get the server ip from local database
      result=serverConf.query.get(1)
      if(result!=None):
          data['serverIp'] = result.ip
      else:
          print("no server ip data in database")

      return jsonify({"result": {"message":"success","status":1,"data":data}})      
   except Exception as e:
      print(e) 
      return jsonify({"result": {"messgae":"something went wrong","status":0,"data":{}}})



@operator.route("/operator", methods=["GET", "POST"])
def operatorScreen():
    result=request.get_json()
    shift=result['shift']
    username=result['fullName']
    component=result['componentName']
    model=result['modelName']
    operation=result['operationName']  
    machineId=result['machineId']
    jobId=result['jobId']
    #calculate the current shift
    TimeObj=datetime.now().time()
    query=db.session.query(ShiftData).filter(and_(func.time(ShiftData.fromTime)<=TimeObj,func.time(ShiftData.toTime)>=TimeObj)) 
    for row in query.all():
         if(row.id==4 or row.id==5):
            pass
         elif(row.id==1):
            print("Shift 1")
            nowShift=row.shift 
         elif(row.id==2):
            print("Shift 2")
            nowShift=row.shift 
         elif(row.id==3):
            print("Shidt 3")
            nowShift=row.shift                         
         else: 
            nowShift="Second" 

    timeObj = datetime.now()
    var_time=timeObj.strftime("%Y/%m/%d %H:%M:%S")
    CurrentDate=datetime.now().date()
    CurrentTime=datetime.now().time()
    sihTime=time(6, 59,59)
    if(CurrentTime<=sihTime):
         date=CurrentDate-timedelta(1)
    else:
         date=CurrentDate
    presentDate=date.strftime("%Y-%m-%d")
    productionObj=production(operatorName=username,jobId=jobId,shift=shift,component=component,modelName=model,operation=operation,cycleTime="5.5",inspectionStatus="0",status="0",timeStamp=var_time,machineId=machineId,date=presentDate,progress="not started")
    try:
         db.session.add(productionObj)
         db.session.commit()
         print("inserting into databse")
    except Exception as e:
         print(e)
    try:
         # print("releasing machine")
         releaseUrl="http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/HoldMachine"
         headers = config.HEADERS
         res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)         
         return jsonify({"result": {"status":1,"message":"job Status Ok , proceed to cycle ","data":{"shift":nowShift}}})
    except :
         return jsonify({"result": {"status":0,"message":"something went wrong please fill details once more","data":{}}})


@operator.route('/alarmScreen', methods=['GET','POST'])
def alarmScreen():
    result=request.get_json()
    shift=result['shift']
    username=result['fullName']
    component=result['componentName']
    model=result['modelName']
    operation=result['operationName']  
    machineId=result['machineId']    
    reason=result['alarmReason']
    errorCode=result['errorCode']
    if result['jobId'] != "":
        jobId=result['jobId']
    else:
        jobId="No Job Placed"
    timeObj = datetime.now()
    time=timeObj.strftime("%Y/%m/%d %H:%M:%S")
    alarmObj=alarm(operatorName=username,jobId=jobId,shift=shift,component=component,modelName=model,operation=operation,timeStamp=time,machineId=machineId,reason=reason,errorCode=errorCode) 
    try:
         db.session.add(alarmObj)
         db.session.commit()
         print("inserting into database")
    except Exception as e:
         print(e)   
         db.session.rollback()
         return jsonify({"result": {"status":0,"message":"something went wrong"}})
    
    releaseUrl="http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/HoldMachine"
    headers = config.HEADERS
    try:
          res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)
          print(res.status_code)
    except:
          print("error..")  
          return jsonify({"result": {"status":0,"message":"something went wrong"}})   
    return jsonify({"result": {"status":1,"message":"successfully data saved"}})


@operator.route('/idleTimeout', methods=['GET','POST'])
def IdleTimeout():
    result=request.get_json()
    shift=result['shift']
    username=result['fullName']
    component=result['componentName']
    model=result['modelName']
    operation=result['operationName']  
    machineId=result['machineId']
    reason=result['idleReason']
    timeObj = datetime.now()
    time=timeObj.strftime("%Y/%m/%d %H:%M:%S")
    idleTimeoutObj=idleTimeout(operatorName=username,shift=shift,component=component,modelName=model,operation=operation,timeStamp=time,machineId=machineId,reason=reason) 
    try:
        db.session.add(idleTimeoutObj)
        db.session.commit()
        print("inserting into database")
    except Exception as e:
        print(e)   
        return jsonify({"result": {"status":0,"message":"something went wrong"}})

    releaseUrl="http://"+config.LOCALSERVER_IPADDRESS+":"+config.PORT+"/HoldMachine"
    headers = config.HEADERS
    try:
          res=req.post(releaseUrl,headers=headers,data=json.dumps({"State":"Release"}),timeout=2)
          print(res.status_code)
    except:
           print("error..")  
           return jsonify({"result": {"status":0,"message":"something went wrong"}})   
    return jsonify({"result": {"status":1,"message":"successfully data saved"}})

