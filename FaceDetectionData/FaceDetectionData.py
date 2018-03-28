# -*- coding: cp1252 -*-
'''
TODO:
    - verificare correttezza timestamp e dati
    - aggiustare fps per acquisizione faccia (sincr)
    - accedere all'orologio di sistema del nao, anziché utilizzare orari
    locali (elimina necessità di sincronizzazione per facedetection)
    - accedere al flusso video del nao direttamente con le opencv
    -> nota che i timestamp riguardanti il face detection hanno una precisione
    che arriva oltre il centesimo di secondo, mentre il video è registrato a
    10 fps. trovare un buon compromesso
    
    - conversione in i420 o yuy2 (supportati da opencv)
    mencoder in.avi -ovc raw -vf format=i420 -o out.avi
    mencoder video1146515837.avi -ovc raw -vf format=yuy2 -o out.avi
    - provare ad usare alvideorecorder con un formato diverso da mjpg?
    - impostare risoluzione più alta
'''
# Scorciatoia per (x, y, x + w, y + h)
def draw_rectangle_from_size(image, rect, color = (255,255,0,0)):
    cv.Rectangle(image, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), color)
    pass

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

def draw_point_from_angles(alpha, beta, color = (0, 0, 255, 0), width = 640.0, height = 480.0,
                           fovx = 60.9, fovy = 47.6):

    cx = -(width * alpha / math.radians(fovx)) + width/2
    cy = (height * beta / math.radians(fovy)) + height/2
            
    cv.Circle(image, (int(cx), int(cy)), 1, color, 2)
    pass


def draw_face_points(face_data):
    # todo: scrivere in modo decente sto schifo
    # altro
    extrainfo = face_data[1][0][1]
    lefteyepoints       = extrainfo[3]
    righteyepoints      = extrainfo[4]
    lefteyebrowpoints   = extrainfo[5]
    righteyebrowpoints  = extrainfo[6]
    nosepoints          = extrainfo[7]
    mouthpoints         = extrainfo[8]

    # eye
    # left
    draw_point_from_angles(lefteyepoints[0], lefteyepoints[1]) # center
    draw_point_from_angles(lefteyepoints[2], lefteyepoints[3]) # nose side
    draw_point_from_angles(lefteyepoints[4], lefteyepoints[5]) # ear side
    draw_point_from_angles(lefteyepoints[6], lefteyepoints[7]) # top
    draw_point_from_angles(lefteyepoints[8], lefteyepoints[9]) # bottom
    draw_point_from_angles(lefteyepoints[10], lefteyepoints[11]) # mid1
    draw_point_from_angles(lefteyepoints[12], lefteyepoints[13]) # mid2
    # right
    draw_point_from_angles(righteyepoints[0], righteyepoints[1]) # center
    draw_point_from_angles(righteyepoints[2], righteyepoints[3]) # nose side
    draw_point_from_angles(righteyepoints[4], righteyepoints[5]) # ear side
    draw_point_from_angles(righteyepoints[6], righteyepoints[7]) # top
    draw_point_from_angles(righteyepoints[8], righteyepoints[9]) # bottom
    draw_point_from_angles(righteyepoints[10], righteyepoints[11]) # mid1
    draw_point_from_angles(righteyepoints[12], righteyepoints[13]) # mid2
    
    # eyebrow
    # left
    COLOR_GREEN = (0, 255, 0, 0)
    draw_point_from_angles(lefteyebrowpoints[0], lefteyebrowpoints[1], COLOR_GREEN) # nose side 
    draw_point_from_angles(lefteyebrowpoints[2], lefteyebrowpoints[3], COLOR_GREEN) # center
    draw_point_from_angles(lefteyebrowpoints[4], lefteyebrowpoints[5], COLOR_GREEN) # eae side 
    # right
    draw_point_from_angles(righteyebrowpoints[0], righteyebrowpoints[1], COLOR_GREEN) # nose side 
    draw_point_from_angles(righteyebrowpoints[2], righteyebrowpoints[3], COLOR_GREEN) # center
    draw_point_from_angles(righteyebrowpoints[4], righteyebrowpoints[5], COLOR_GREEN) # eae side
    
    #nose
    COLOR_CYAN = (255, 0, 255, 0)
    draw_point_from_angles(nosepoints[0], nosepoints[1], COLOR_CYAN)
    draw_point_from_angles(nosepoints[2], nosepoints[3], COLOR_CYAN)
    draw_point_from_angles(nosepoints[4], nosepoints[5], COLOR_CYAN)

    # mouth
    COLOR_YELLOW = (0, 255, 255, 0)
    draw_point_from_angles(mouthpoints[0], mouthpoints[1], COLOR_YELLOW)
    draw_point_from_angles(mouthpoints[2], mouthpoints[3], COLOR_YELLOW)
    draw_point_from_angles(mouthpoints[4], mouthpoints[5], COLOR_YELLOW)
    draw_point_from_angles(mouthpoints[6], mouthpoints[7], COLOR_YELLOW)
    draw_point_from_angles(mouthpoints[8], mouthpoints[9], COLOR_YELLOW)
    draw_point_from_angles(mouthpoints[10], mouthpoints[11], COLOR_YELLOW)
    draw_point_from_angles(mouthpoints[12], mouthpoints[13], COLOR_YELLOW)
    draw_point_from_angles(mouthpoints[14], mouthpoints[15], COLOR_YELLOW)
    pass


# Load Face Detection Data

import math, time
import pickle
from datetime import datetime

sessionid = "3856385814"
fh = open("detection" + sessionid + ".txt", "r")
data = pickle.load(fh)

init_time = data[0]
dect_data = data[1]

print "init acquisition @ " + str(datetime.fromtimestamp(init_time))


FrameIndexes = []

for i in range(len(dect_data)):
    dect_time = dect_data[i][0]

    ix = dect_time - init_time
    print "face detected @ ", ix
    FrameIndexes.append(ix- 1) # !!!! considera ritardo (tempo interno robot!!!)

# Drawing Video + Features

import cv2
cv = cv2.cv

# path = "C:\\Users\\Federico\\Desktop\\NAO Temp\\Scripts\\FaceDetectionData\\"
# video1146515837

# uso momentaneamente il file convertito in YUY2
capture  = cv.CaptureFromFile("out.avi") #("video" + sessionid + ".avi")
n_frames = int(cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_COUNT))
fps      = cv.GetCaptureProperty(capture, cv.CV_CAP_PROP_FPS)
wait_per_frame_ms = int(1/fps * 1000/1)

print "Frames count: ", n_frames
print "Frame rate: ", fps
print wait_per_frame_ms

current_frame = 0
waited_amount = 0
ix = 0

for f in range(n_frames):
    t0 = time.time()
    
    image = cv.QueryFrame(capture)

    elapsed = float(waited_amount) / 1000
    print elapsed

    if(len(FrameIndexes) > 0): # se ci sono ancora facce
        # < 66 ms
        diff = math.fabs(FrameIndexes[0] - elapsed)
        limit = (float(wait_per_frame_ms) / 1000)
        
        if(diff < limit):
        #if(diff < limit / 2): # todo arrotondare al frame più vicino                 
            print "------------ DETECTED", FrameIndexes[0]      
            # cv.Rectangle(image, (10,10), (100, 100), (0, 0, 0, 0))

            face_data = dect_data[ix][1]
            shapeinfo = face_data[1][0][0]
            # rettangolo faccia
            alpha = shapeinfo[1]
            beta = shapeinfo[2]
            sizex = shapeinfo[3]
            sizey = shapeinfo[4]

            w = (640.0 * sizex / math.radians(60.9))
            h = (480.0 * sizey / math.radians(47.6))
            a = (-(640.0 * alpha / math.radians(60.9))) + 320 - w/2
            b = (480.0 * beta / math.radians(47.6)) + 240 - h/2
            # nota: questi valori dovrebbero funzionare:
            # iprovare con periodo di acquisizione superiore, filmati diversi, etc

            print a, b
            print w, h
    
            cv.Rectangle(image, (int(a), int(b)), (int(a + w), int(b + h)),
                (255, 255, 0, 0))

            draw_face_points(face_data)
            
            #
            FrameIndexes.pop(0)
            ix += 1

    # end of face drawing
    cv.ShowImage("Video Window", image)

    current_frame += 1

    t1 = time.time()
    dt = wait_per_frame_ms - (t1 - t0)

    k = cv.WaitKey(wait_per_frame_ms)
    
    waited_amount += wait_per_frame_ms

    if k == 13:
        break

cv.DestroyWindow("Video Window")




