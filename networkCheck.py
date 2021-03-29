import RPi.GPIO as GPIO
import subprocess
from time import sleep
GPIO.setmode(GPIO.BOARD)
GPIO.setup(36,GPIO.OUT)


def checkNetworkConnection():
    flag = 1
    while(1):
        sleep(5)    
        result=subprocess.Popen("sudo mii-tool eth0 ",stdout=subprocess.PIPE,shell=True)
        finalResult=result.communicate()
        print(finalResult)
        if (b'eth0: no link\n' in finalResult and flag == 0):
            GPIO.output(36,False)
            print("led off")
            flag = 1
        elif (b'eth0: negotiated 100baseTx-FD flow-control, link ok\n' in finalResult and flag == 1):
            GPIO.output(36,True)
            print("led on")
            flag = 0
        else:
            pass
