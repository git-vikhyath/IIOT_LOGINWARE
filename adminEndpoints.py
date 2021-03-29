from flask import Blueprint, request, jsonify
from models import *
from flask_sqlalchemy import SQLAlchemy

admin = Blueprint('admin', __name__)

@admin.route('/getServerIP', methods = ['GET'])
def getServerIP():
    try:
        result = serverConf.query.get(1)
        if result != None:
            serverIp = result.ip
            print(serverIp)
            return jsonify({"result" : {"status" : 1, "data" : serverIp, "message" : "Success"}})
        else:
            return jsonify({"result" : {"status" : 1, "message" : "No previous data found", "data" : ""}})
    except Exception as e:
        print(e)
        return jsonify({"result" : {"status" : 0, "data" : "", "message" : "Failed"}})
       
@admin.route('/updateServerIP', methods = ['POST'])
def serverConfiguration():
  endpoint = request.get_json()['endpoint'] 
  try:
      result=serverConf.query.filter_by(id = 1).scalar()
      if result != None:
          db.session.query(serverConf).filter(serverConf.id == 1).update({serverConf.ip:endpoint})
          db.session.commit()
          return jsonify({"result" : {"message" : "Server credentials updated successfully", "status" : 1}})
      else:
          serverConfObj = serverConf(id = 1,ip = endpoint)
          db.session.add(serverConfObj) 
          db.session.commit()
          return jsonify({"result" : {"message" : "Server credentials saved successfully", "status" : 1}})  
  except Exception as e:
      print(e)   
      return jsonify({"result" : {"message" : "something went wrong", "status" : 0}})
      
@admin.route('/updateNetworkDetails', methods = ['POST'])
def UpdatenetworkDetails():
    ip = request.get_json()['ip']
    gateway = request.get_json()['gateway']
    dns = request.get_json()['dns']
    networkFileData = "interface eth0 \n static ip_address = {}\n static routers = {}\n static domain_name_servers = {}".format(ip, gateway, dns)
    print(networkFileData)
    try:
        result = networkConf.query.filter_by(id = 1).scalar()
        if result != None:
            db.session.query(networkConf).filter(networkConf.id == 1).update({"ip" : ip, "gateway" : gateway, "dns" : dns})
            db.session.commit()
            with open('/etc/dhcpcd.conf', 'w') as f:
                f.write(networkFileData)
                f.close()
            return jsonify({"result" : {"status" : 1, "message" : "Network details updated successfully"}})
        else:
            networkConfObject = networkConf(ip = ip, gateway = gateway, dns = dns)
            db.session.add(networkConfObject)
            db.session.commit()
            with open('/etc/dhcpcd.conf', 'w') as f:
                f.write(networkFileData)
                f.close()
            return jsonify({"result" : {"status" : 1, "message" : "Network details saved successfully"}})
    except Exception as e:
        return jsonify({"result" : {"status" : 0, "message" : "Something went wrong"}})
        
@admin.route('/updateSignalsDetails', methods = ['POST'])
def UpdateSignalsDetails():
    resultList = []
    objinList = {}
    for i in range(1, 13):
        objinList["signal" + str(i)] = request.get_json()['signal' + str(i)]
        objinList["pin" + str(i)] = request.get_json()['pin' + str(i)]
        objinList["enable" + str(i)] = request.get_json()['enable' + str(i)]
        resultList.append(objinList)
        objinList = {}
    try:
        result = pinout.query.filter_by(signalName = 'cycle').scalar()
        if result != None:
            db.session.query(pinout).delete()
            db.session.commit()
        for i, data in enumerate(resultList):
            pinoutObject = pinout(machineId = "JG-20", signal = data['signal' + str(i + 1)], pin = data['pin' + str(i + 1)], status = data['enable' + str(i + 1)])
            db.session.add(pinoutObject)
            db.session.commit()
        return jsonify({"result" : {"status" : 1, "message" : "Network details saved successfully"}})
    except Exception as e:
        print(e)
        return jsonify({"result" : {"status" : 0, "message" : "Something went wrong"}})

@admin.route('/getNetworkConf', methods = ['GET'])
def getNetworkConf():
    data = {}
    try:
        result = networkConf.query.get(1)
        if result != None:
            data['ip'] = result.ip
            data['dns'] = result.dns
            data['gateway'] = result.gateway
            return jsonify({"result" : {"status" : 1, "data" : data, "message" : "Successfully fetched and saved data"}})
        else:
            return jsonify({"result" : {"status" : 1, "message" : "No previous data found", "data" : {} }})
    except Exception as e:
        print(e)
        return jsonify({"result" : {"status" : 0, "data" : {}, "message" : "Failed"}})
        
@admin.route('/updateOtherSettings', methods = ['POST'])
def otherSettingsFunction():
    data = request.get_json()
    machineId = data['machineId']
    batchSize = data['batchSize']
    holdingRelay = data['holdingRelay']
    machineBypass = data['machineBypass']
    idleTimeout = data['idleTimeout']
    cleaningInterval = data['cleaningInterval']
    machineType = data['machineType']
    try:
        result = otherSettings.query.filter_by(id = 1).scalar()
        if result != None:
            db.session.query(otherSettings).filter(otherSettings.id == 1).update({"machineId" : machineId, "batchSize" : batchSize, "holdingRelay" : holdingRelay, "machineBypass" : machineBypass, "idleTimeout" : idleTimeout, "cleaningInterval" : cleaningInterval, "machineType" : machineType})
            db.session.commit()
            return jsonify({"result" : {"status" : 1, "message" : "Other settings updated successfully"}})
        else:
         otherSettingsConfObject = otherSettings(machineId=machineId,batchSize=batchSize,holdingRelay=holdingRelay,machineBypass=machineBypass,idleTimeout=idleTimeout,cleaningInterval=cleaningInterval,machineType=machineType)
         db.session.add(otherSettingsConfObject)
         db.session.commit()
         return jsonify({"result": {"status" : 1,"message":"Other settings saved successfully"}})   
    except Exception as e:
        print(e)
        return jsonify({"result": {"status" : 0,"message":"Something went wrong"}})  

@admin.route('/getOtherSettings', methods=['GET'])
def getOtherSettings():
   data={}
   try:
      result=otherSettings.query.get(1)
      if result!=None:
         data['machineId']=result.machineId
         data['batchSize']=result.batchSize
         data['holdingRelay']=result.holdingRelay
         data['machineBypass']=result.machineBypass
         data['idleTimeout']=result.idleTimeout
         data['cleaningInterval']=result.cleaningInterval
         data['machineType']=result.machineType         
         return jsonify({"result": {"status":1,"data":data,"message":"Successfully fetched saved data"}})
      else:
         return jsonify({"result":{"status":1,"message":"No previous data found","data":{}}})
   except Exception as e:
      print(e)
      return jsonify({"result":{"status":0,"data":{},"message":"Failed"}}) 
