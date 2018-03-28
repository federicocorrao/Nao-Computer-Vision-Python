# -*- encoding: UTF-8 -*-

import time, math
from naoqi import ALProxy, ALBroker, ALModule

IP = "nao.local"
PORT = 9559

faceProxy   = ALProxy("ALFaceDetection", IP, PORT)
memoryProxy = ALProxy("ALMemory", IP, PORT)
motionProxy = ALProxy("ALMotion", IP, PORT)
FTProxy     = ALProxy("ALFaceTracker", IP, PORT)

period = 70
faceProxy.subscribe("Test_Face", period, 0.0)
reco_count = 1

alpha_queue = []
beta_queue = []

while True:
    val = memoryProxy.getData("FaceDetected")
    
    if(val and isinstance(val, list) and len(val) >= 2):
        memoryProxy.insertData("FaceDetected", [])
        
        timeStamp       = val[0]
        faceInfoArray   = val[1]

        faceInfo        = faceInfoArray[0]
        faceShapeInfo   = faceInfo[0]
        faceExraInfo    = faceInfo[1]
        alpha   = faceShapeInfo[1]
        beta    = faceShapeInfo[2]
        sizeX   = faceShapeInfo[3]
        sizeY   = faceShapeInfo[4]

        alpha_queue.append(alpha)
        beta_queue.append(beta)
        
        # print len(alpha_queue)
        lim = 3

        if len(alpha_queue) == lim:
            ma = math.fsum(alpha_queue) / lim
            mb = math.fsum(beta_queue) / lim

            print ma, mb

            alpha_queue = []
            beta_queue  = []
            
            joints = ["HeadYaw", "HeadPitch"]
            motionProxy.changeAngles(joints, [ma, mb], 0.05)
        
            # print "reco", reco_count, timeStamp
            reco_count += 1
        
