# -*- encoding: UTF-8 -*- 
'''
filtri particellari
(kalman estesi)
camshift
'''
# Imports

import time, math
from naoqi import ALProxy, ALBroker, ALModule


# Proxies

IP = "nao.local"
PORT = 9559

faceProxy   = ALProxy("ALFaceDetection", IP, PORT)
memoryProxy = ALProxy("ALMemory", IP, PORT)
motionProxy = ALProxy("ALMotion", IP, PORT)
FTProxy     = ALProxy("ALFaceTracker", IP, PORT)


# Metodo callback

FaceGreeter = None

class FaceGreeterModule(ALModule):
    def __init__(self, name):
        ALModule.__init__(self, name)
        
        global memory
        memoryProxy.subscribeToEvent("FrontTactilTouched", # "FaceDetected",
                        "FaceGreeter", "onFaceDetected")

    def onFaceDetected(self, *_args):
        print "reco callback"
        global pause
        pause = False
        global period
        faceProxy.subscribe("Test_Face", period, 0.0)
        # ...
        pass

myBroker = ALBroker("myBroker", "0.0.0.0", 0, IP, PORT)
FaceGreeter = FaceGreeterModule("FaceGreeter")
# exit(0)


# Metodo sincrono

period = 200
faceProxy.subscribe("Test_Face", period, 0.0)
reco_count = 1
# motionProxy.wakeUp()
# motionProxy.rest()

# Accendo solo i motori della testa (surriscald.)
# motionProxy.stiffnessInterpolation(["HeadYaw", "HeadPitch"], 1, 1)

#YawLimit    = motionProxy.getLimits("HeadYaw")[0][2]       # max speed yaw
#PitchLimit  = motionProxy.getLimits("HeadPitch")[0][2]     # max speed pitch
#print YawLimit * 0.05, PitchLimit
#print motionProxy.getSummary()
#print motionProxy.getRobotConfig()

#exit(0)

pause = False

while True:

    if pause:
        continue

    val = memoryProxy.getData("FaceDetected")
    print val

    if(val and isinstance(val, list) and len(val) >= 2):
        timeStamp       = val[0]
        faceInfoArray   = val[1]

        # nota: bisognerebbe lavorare con una faccia sola
        # for face_index in range(len(faceInfoArray) - 1):
        #   faceInfo = faceInfoArray[face_index]

        # Selezioni dati faccia di interesse 
        faceInfo        = faceInfoArray[0]  # Seleziono la prima faccia
        faceShapeInfo   = faceInfo[0]
        faceExraInfo    = faceInfo[1]
        alpha   = faceShapeInfo[1]
        beta    = faceShapeInfo[2]
        sizeX   = faceShapeInfo[3]
        sizeY   = faceShapeInfo[4]

        joints = ["HeadYaw", "HeadPitch"]
        motionProxy.changeAngles(joints, [alpha, 0], 0.05)
        # motionProxy.angleInterpolation(joints, [alpha, 0], 0.05, False)

        # ... aspetta o callback 

        memoryProxy.insertData("FaceDetected", [])
        faceProxy.unsubscribe("Test_Face")
        pause = True

        time.sleep(0.5)

        pause = False
        faceProxy.subscribe("Test_Face", period, 0.0)
        memoryProxy.insertData("FaceDetected", [])
        print "start"

        print "reco", reco_count, timeStamp
        reco_count += 1
        
