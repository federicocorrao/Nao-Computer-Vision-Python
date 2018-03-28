# -*- coding: cp1252 -*-

# Esempio documentazione naoqi su face detection

import time, math
import Image
from naoqi import ALProxy

IP = 'nao.local'
PORT = 9559

# Prende una immagine dal robot (reale o simulato) e la salva con PIL
def getImage(IP = 'nao.local', Port = 9559):
    path = "C:\\Users\\Federico\\Desktop\\"
    p = ALProxy("ALVideoDevice", IP, Port)

    resolution = 2
    colorspace = 11
    fps = 30

    nameId = p.subscribe("python_GVM", resolution, colorspace, fps)

    image = p.getImageRemote(nameId)
    p.releaseImage(nameId)
    p.unsubscribe(nameId)

    image_width = image[0]
    image_height = image[1]
    array = image[6]

    # Usa PIL
    im = Image.fromstring("RGB", (image_width, image_height), array)
    im.save(path + "image.png", "PNG")

# Conversione angoli -> pixel
def getSize(alpha, beta,
            image_width = 640, image_height = 320,
            FOV_width = 60.9, FOV_height = 47.6):

    FOV_width = math.radians(FOV_width)
    FOV_height = math.radians(FOV_height)

    # alpha : FOW_width = x : 640
    
    x = image_width * (alpha / FOV_width)
    y = image_height * (beta / FOV_height)
    return [x, y]


faceProxy = ALProxy("ALFaceDetection", IP, PORT)
memoryProxy = ALProxy("ALMemory", IP, PORT)
motion = ALProxy("ALMotion", IP, PORT)
#video  = ALProxy("ALVideoDevice", IP, PORT)
facetrack = ALProxy("ALFaceTracker", IP, PORT)
#facetrack.startTracker()
#facetrack.stopTracker()

#print motion.getLimits("HeadYaw")
#exit(0)

# Subscribe to the ALFaceDetection proxy
# This means that the module will write in ALMemory with the given period below
period = 50
faceProxy.subscribe("Test_Face", period, 0.0)
#time.sleep(0.1)

# 10 volte
while True:
    
    val = memoryProxy.getData("FaceDetected") # (key)

    #print ""
    #print "*****"
    #print ""

    # Check whether we got a valid output.
    if(val and isinstance(val, list) and len(val) >= 2):
        # We detected faces !
        # For each face, we can read its shape info and ID.

        # Prende una immagine della faccia e la salva 
        # getImage()
        
        # First Field = TimeStamp.
        timeStamp = val[0]

        # Second Field = array of face_Info's.
        faceInfoArray = val[1]

        try:
            # Browse the faceInfoArray to get info on each detected face.
            for j in range( len(faceInfoArray)-1 ):
                faceInfo = faceInfoArray[j]

                # First Field = Shape info.
                faceShapeInfo = faceInfo[0]

                # Second Field = Extra info (empty for now).
                faceExtraInfo = faceInfo[1]

                alpha = faceShapeInfo[1]
                beta = faceShapeInfo[2]
                sizeX = faceShapeInfo[3]
                sizeY = faceShapeInfo[4]

                #print "  alpha %.3f - beta %.3f" % (alpha, beta)
                #print "  width %.3f - height %.3f" % (sizeX, sizeY)
                #print getSize(sizeX, sizeY)
                #print getSize(alpha, beta)

                #if (math.fabs(alpha) > math.radians(5)):
                #motion.changeAngles(["HeadYaw", "HeadPitch"],
                #                    [alpha, 0], 0.05)
                #time.sleep(0.4)

                #memoryProxy.insertData("FaceDetected", [])
                #print memoryProxy.getData("FaceDetected")
                print '-'
                    
                # velocità in funzione della distanza?
                
                #a = motion.getAngles("HeadYaw", False)[0]
                #b = motion.getAngles("HeadPitch", False)[0]
                #angles = [a + alpha, b + beta]
                #motion.setAngles(["HeadYaw", "HeadPitch"], angles, 0.1)
                time.sleep(0.05)

                #motion.angleInterpolation("HeadYaw", alpha/2, 0.05, False)
                #motion.angleInterpolation("HeadPitch", beta/2, 0.05, False)

                motion.angleInterpolation(["HeadYaw", "HeadPitch"],
                    [alpha/2, beta/2], [0.05, 0.05], False)
                
        except Exception, e:
            print "faces detected, but it seems getData is invalid. ALValue ="
            print val
            print "Error msg %s" % (str(e))
    else:
        
        # print "No face detected"
        #time.sleep(0.05)
        pass
    
# Unsubscribe the module.
faceProxy.unsubscribe("Test_Face")

print "Test terminated successfully."

