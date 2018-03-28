# -*- encoding: UTF-8 -*- 

# Esempio documentazione naoqi su face detection

import time, math, random
import pickle
import Image
from naoqi import ALProxy
import vision_definitions
from datetime import datetime
#import cv2, cv2.cv
#cv = cv2.cv
# TODO: catturare flusso video (cv?)

IP = "nao.local"
Port = PORT = 9559

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
            image_width = 640, image_height = 480,
            FOV_width = 60.9, FOV_height = 47.6):

    FOV_width = math.radians(FOV_width)
    FOV_height = math.radians(FOV_height)

    # alpha : FOW_width = x : 640
    
    x = image_width * (alpha / FOV_width)
    y = image_height * (beta / FOV_height)
    return [x, y]


# Struttura da serializzare, memorizza tutte le informazioni sul riconoscimento
# della faccia 
FaceDetectionData = []

# nome sesisone acquisizione dati
random_session_name = []
for i in range(0, 10):
    random_session_name.append(str(int(random.uniform(0, 9))))
random_session_name = ''.join(random_session_name)
print "session name is "+ random_session_name

# proxy etc
faceProxy = ALProxy("ALFaceDetection", IP, PORT)
memoryProxy = ALProxy("ALMemory", IP, PORT)

vr = ALProxy("ALVideoRecorder", IP, Port)
vr.setFrameRate(25)
vr.setVideoFormat("MJPG")
vr.setResolution(vision_definitions.kVGA) # 2
# vr.setColorSpace(11)

# Subscribe to the ALFaceDetection proxy
# This means that the module will write in ALMemory with the given period below
period = 500
faceProxy.subscribe("Test_Face", period, 0.0)

print "Start Recording"
StartRecordingTime = time.time() # tempo di inizio recording (confrontare con tempi riconoscim. faccia) 
vr.startRecording("/home/nao/recordings/cameras", "video" + random_session_name)


for i in range(0, 150):
    time.sleep(0.1)
    val = memoryProxy.getData("FaceDetected") # (key)

    print ""
    print "*****"
    print ""

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

        # salviamo i dati 
        FaceDetectionLocalTime = time.time()
        FaceDetectionData.append([FaceDetectionLocalTime, val])

        try:
            #.... questo codice non mi convince tanto [for j in range...]
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

                # (alpha positivo verso dx)
                # print datetime.fromtimestamp(float(str(timeStamp[0])+ "." + str(timeStamp[1])))
                print "  alpha %.3f - beta %.3f" % (alpha, beta)
                print "  width %.3f - height %.3f" % (sizeX, sizeY)
                print getSize(sizeX, sizeY)
                print getSize(alpha, beta)
        except Exception, e:
            print "faces detected, but it seems getData is invalid. ALValue ="
            print "Error msg %s" % (e)

        print val
    else:
        print "No face detected"

videoinfo = vr.stopRecording()
print videoinfo

# Unsubscribe the module.
faceProxy.unsubscribe("Test_Face")

print "Test terminated successfully."

fh = open("FaceDetectionData/detection" + random_session_name + ".txt", "w")
# import pickle
pickle.dump([StartRecordingTime, FaceDetectionData], fh)
fh.close()

print "Data saved"
# fh = open("serialized.txt", "r")
# FaceDetectionData = pickle.load(fh)
# fh.close() 

