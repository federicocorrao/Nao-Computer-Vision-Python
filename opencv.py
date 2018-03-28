# -*- coding: cp1252 -*-

import cv2, cv2.cv
cv = cv2.cv

import math, time
from naoqi import ALProxy

# Const

HAAR_PATH = "C:/opencv/data/haarcascades/"

HAAR_FACE_PATH      = HAAR_PATH + "haarcascade_frontalface_default.xml"
HAAR_FACE_ALT_PATH  = HAAR_PATH + "haarcascade_frontalface_alt.xml"
HAAR_FACE_ALT2_PATH = HAAR_PATH + "haarcascade_frontalface_alt2.xml"
HAAR_FACE_TREE_PATH = HAAR_PATH + "haarcascade_frontalface_alt_tree.xml"

HAAR_EYE_PATH       = HAAR_PATH + "haarcascade_eye.xml"
HAAR_LEFT_EYE_PATH  = HAAR_PATH + "haarcascade_mcs_lefteye.xml"
HAAR_RIGHT_EYE_PATH = HAAR_PATH + "haarcascade_mcs_righteye.xml"
HAAR_BOTH_EYES_PATH = HAAR_PATH + "haarcascade_mcs_eyepair_big.xml"

CAMERA_INDEX = 0

COLOR_WHITE = (255, 255, 255, 0)
COLOR_RED   = (0, 0, 255, 0)

NaoLinked = None
WINDOW_NAME = "Video"

FOV = (math.radians(60.9), math.radians(47.6))  # (Field Of View)
Width   = 640
Height  = 480
WindowSize = (Width, Height)
CenterScreen = (WindowSize[0] / 2, WindowSize[1] / 2)

# Funcs

def draw_axes(image):
    cv.Line(image, (0, Height/2), (Width, Height/2), COLOR_WHITE)
    cv.Line(image, (Width/2, 0), (Width/2, Height), COLOR_WHITE)
    cv.Circle(image, (Width/2, Height/2), 1, COLOR_RED, 2)

def draw_points(image, points, color = (0, 255, 0, 0), radius = 1, thickness = 2):
    for (x, y) in points:
        cv.Circle(image, (int(x), int(y)), radius, color, thickness)

# Scorciatoia per (x, y, x + w, y + h)
def draw_rectangle_from_size(image, rect, color = COLOR_WHITE):
    cv.Rectangle(image, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), color)
    pass

# A partire da (x, y, w, h)
def get_rect_center(rect):
    return (rect[0] + rect[2]/2, rect[1] + rect[3]/2)

# Riferimento top-left -> center screen (a partire da (x, y))
def toRelative(point, window_size = WindowSize):
    return (point[0] - window_size[0]/2,
            -(point[1] - window_size[1]/2))

# Da punto/lunghezza a angolo (per nao, con determinato field of view in angoli)
def toAngles(point, window_size = WindowSize, fov = FOV):
    return (
        (point[0] / float(window_size[0])) * fov[0],
        (point[1] / float(window_size[1])) * fov[1]
         )

def HaarDetect(image, casc):
    features = []
    detected = cv.HaarDetectObjects(image, casc, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (100, 100))
    if detected:
        for (x,y,w,h),n in detected:
            features.append((x,y,w,h))
    return features

# TODO: Generalizzare
def toGreyScale(image):
    grey = cv.CreateImage(cv.GetSize(image), 8, 1)
    cv.CvtColor(image, grey, cv.CV_BGR2GRAY)
    return grey

def GoodFeaturesToTrack(image, max_count = 100, quality = 0.1, min_distance = 1):
        grey = toGreyScale(image)
        eig  = cv.CreateImage(cv.GetSize(grey), 32, 1)
        temp = cv.CreateImage(cv.GetSize(grey), 32, 1)
        
        return cv.GoodFeaturesToTrack(grey, eig, temp,
            max_count, quality, min_distance,
            None, 3, 0, 0.04)
            # TODO: e questi altri parametri?

def Canny(image, low_thr = 50, hi_thr = 150):
    # PERFETTO: le pupille (a distanza ravvicinata) sembrano essere
    # prese bene... TODO: smanettare con i parametri di canny
    yuv  = cv.CreateImage(cv.GetSize(image), 8, 3)
    gray = cv.CreateImage(cv.GetSize(image), 8, 1)
    cv.CvtColor(image, yuv, cv.CV_BGR2YCrCb)
    cv.Split(yuv, gray, None, None, None)
    canny = cv.CreateImage(cv.GetSize(image), 8, 1)
    cv.Canny(gray, canny, low_thr, hi_thr)
    cv.NamedWindow('Canny')
    cv.ShowImage('Canny', canny)

# TODO: Harris output scaling
def Harris(image):
    gray = cv.CreateImage(cv.GetSize(image), 8, 1)
    harris = cv.CreateImage(cv.GetSize(image), cv.IPL_DEPTH_32F, 1)

    cv.CornerHarris(gray, harris, 5, 5, 0.1)

    #for y in range(0, 640):
    #    for x in range(0, 480):
    #      harris = cv.Get2D(harris_c, y, x) # get the x,y value
    #      # check the corner detector response
    #      if harris[0] > 10e-06:
    #       # draw a small circle on the original image
    #           cv.Circle(harris, (x, y), 2, cv.RGB(155, 0, 25))

    # I recommend using cvMinMaxLoc to find the min and max values and then use 
    # cvConvertScale to shift the range [min..max] to [0..255] into an 8bit 
    # image.

    print cv.MinMaxLoc(harris)
    gray2 = cv.CreateImage(cv.GetSize(image), 8, 1)
    cv.ConvertScale(harris, gray2) # scale/shift?

    cv.NamedWindow('Harris')
    cv.ShowImage('Harris', gray) 

# Main

if __name__ == "__main__":

    # Inizializzazione: camera, files, etc 

    # Controlla se il simulatore/nao è attivo
    try:
        motion = ALProxy("ALMotion", 'localhost', 9559)
        motion.stiffnessInterpolation("Body", 1, 1)
    except:
        NaoLinked = False
    else:
        NaoLinked = True

    # Creo finestra?
    cv.NamedWindow(WINDOW_NAME, cv.CV_WINDOW_AUTOSIZE)
 
    # capture = cv.CaptureFromCAM(CAMERA_INDEX)
    capture = cv.CreateCameraCapture(CAMERA_INDEX)
    cv.SetCaptureProperty(capture, 3, 640)
    cv.SetCaptureProperty(capture, 4, 480)
    
    storage = cv.CreateMemStorage()

    # Carico file per riconoscimento features 
    cascade_face        = cv.Load(HAAR_FACE_PATH)
    cascade_alt_face    = cv.Load(HAAR_FACE_ALT_PATH)
    cascade_alt2_face   = cv.Load(HAAR_FACE_ALT2_PATH)
    cascade_tree_face   = cv.Load(HAAR_FACE_TREE_PATH)
    cascade_eye         = cv.Load(HAAR_EYE_PATH)
    cascade_left_eye    = cv.Load(HAAR_LEFT_EYE_PATH)
    cascade_right_eye   = cv.Load(HAAR_RIGHT_EYE_PATH)
    cascade_both_eyes   = cv.Load(HAAR_BOTH_EYES_PATH)

    # Rettangoli features riconosciute 
    faces = []
    eye = []
    left_eye = []
    right_eye = []
    both_eyes = []
    
    i = 0 
    pause = False
    
    while True:
        i += 1
        
        # Gestione pausa e uscita (attesa per pressione tasto) 
        k = cv.WaitKey(10)
        if k == 13:
            # Invio: uscita 
            cv.DestroyWindow(WINDOW_NAME)
            break
        elif k != -1:
            # Qualsiasi altro tasto: pausa (toggle)
            pause = not pause

        if pause == True:
            continue;

        # Update

        t_init = time.time()
        print i

        # Ottengo immagine dalla camera 
        image = cv.QueryFrame(capture)
    
        # Detection con Haar (feature "principali")
        faces       = HaarDetect(image, cascade_face)
        # eye       = HaarDetect(image, cascade_eye)
        # left_eye  = HaarDetect(image, cascade_left_eye)
        # right_eye = HaarDetect(image, cascade_right_eye)
        # both_eyes = HaarDetect(image, cascade_both_eyes)

        # PROVVISORIO: divisione del rettangono della faccia in parti
        # (top/occhi - bottom/bocca, center/naso) per poter applicare
        # HaarDetect solo sulle parti interessate (e non tutta l'immagine)
        # TODO foreach face
        
        roi = None
        if len(faces) > 0:
            diff = 20
            x = faces[0][0] + diff
            y = faces[0][1] + diff
            w = faces[0][2] - 2 * diff
            h = faces[0][3] - 2 * diff
            roi = (x, y, w, h)

            top_roi_pts = (roi[0], roi[1] + roi[3]/2,
                           roi[0] + roi[2], roi[1] + roi[3]/2)
            cent_roi_pts = (roi[0], roi[1] + 3*roi[3]/4,
                            
                            roi[0] + roi[2], roi[1] + 3*roi[3]/4)
            # TODO: hai disegnato le linee, adesso dovresti estrarre i
            # rettangoli e passarli a SetImageROI
            # cv.SetImageROI(image, roi)
            
        # FEATURE DETECTION
        # CANNY
        th = 40
        # Canny(image, th, 3 * th)

        # HARRIS
        # Harris(image)
    
        # GoodFeaturesToTrack
        features = GoodFeaturesToTrack(image)
        # Disegno punti ottenuti
        draw_points(image, features)

        # Esamino/disengo rettangoli features ottenute
         
        for (x, y, w, h) in faces:
            # Centro faccia (assoluto)
            (abs_centerX, abs_centerY) = get_rect_center((x, y, w, h))
            # Centro faccia (relativo)
            (rel_centerX, rel_centerY) = toRelative((abs_centerX, abs_centerY))
            # Conversione in angoli (per testa nao)
            (alpha, beta)  = toAngles((rel_centerX, rel_centerY))
            (sizeX, sizeY) = toAngles((w, h))

            # TODO: una faccia alla volta
            if NaoLinked == True:
                #motion.angleInterpolation("HeadYaw", -alpha, 0.1, True)
                #motion.angleInterpolation("HeadPitch", -beta, 0.1, True)

                # il problema dovrebbe essere che alpha e beta in questo caso
                # sono assoluti, mentre nel robot reale sono relativi
                # quindi usa setAngles invece di changeAngles o converti gli
                # angoli in misura relativa
                motion.setAngles(["HeadYaw", "HeadPitch"],
                        [-alpha, -beta], 0.1)

                # Questo dovrebbe essere il codice corretto, ma sicuramente
                # c'è qualcosa di errato nella conversione pixel -> angoli
                #motion.changeAngles(["HeadYaw", "HeadPitch"],
                #        [(alpha + sizeX)/2, (beta + sizeY)/2], 0.1, True)

            # Disegna faccia
            draw_rectangle_from_size(image, (x, y, w, h))
            # Disegna centro faccia
            draw_points(image, [get_rect_center((x, y, w, h))], COLOR_RED)
            # TODO: considera sottorettangoli (roi?)
            # draw_rectangle_from_size(image, roi)

            #cv.Line(image,
            #    (cent_roi_pts[0], cent_roi_pts[1]),
            #    (cent_roi_pts[2], cent_roi_pts[3]),
            #    COLOR_WHITE)
            #cv.Line(image,
            #    (top_roi_pts[0], top_roi_pts[1]),
            #    (top_roi_pts[2], top_roi_pts[3]),
            #    COLOR_WHITE)
            
        for (x, y, w, h) in eye:
            draw_rectangle_from_size(image, (x, y, w, h), COLOR_WHITE)
        for (x, y, w, h) in left_eye:
            draw_rectangle_from_size(image, (x, y, w, h), (0, 255, 255, 0))
        for (x, y, w, h) in right_eye:
            draw_rectangle_from_size(image, (x, y, w, h), (0, 255, 255, 0))
        for (x, y, w, h) in both_eyes:
            draw_rectangle_from_size(image, (x, y, w, h), COLOR_WHITE)

        # Disegna assi, centro e immagine 
        draw_axes(image)
        cv.ShowImage(WINDOW_NAME, image)

        t_end = time.time()
        dt = t_end - t_init
        if(dt > 0.1): dt = 0.1
        time.sleep(0.1 - dt)
        # print 0.1 - dt
        # (sleep per un minimo di 0.1 secondi)

exit(0)

'''
NOTE
    - il centro della faccia è quasi sempre posizionato al centro del naso
    (più o meno)
    - eye non funziona sempre
    - lefteye/righteye non sembra funzionare bene
    - eyepair non sembra funzionare affatto

OBIETTIVI
    - HaarFeatureDetection solo su occhi, naso, bocca
    - Canny (Edge), Harris (Corner)

ALTRO
    - image2 = cv.CloneImage(image) # copia
    - image2 = image # copia ref

Controlla anche
PreCornerDetect, CornerEigenValsAndVecs
e le altre funzioni!

''' 
