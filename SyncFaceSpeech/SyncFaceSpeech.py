# -*- coding: cp1252 -*-

# Includes

import math, time, random
import pickle

from naoqi import ALProxy
from naoqi import ALModule
from naoqi import ALBroker

import cv2
import cv2.cv
cv = cv2.cv

# Utils

def toRelative(alpha, beta,
               width = 640.0, height = 480.0,
               fovx = 60.9, fovy = 47.6):

    cx = -(width * alpha / math.radians(fovx)) + width/2
    cy = (height * beta / math.radians(fovy)) + height/2
    return (int(cx), int(cy))

def drawPointFromAngles(image, alpha, beta, color = (0, 0, 255, 0),
                           width = 640.0, height = 480.0,
                           fovx = 60.9, fovy = 47.6):

    cx = -(width * alpha / math.radians(fovx)) + width/2
    cy = (height * beta / math.radians(fovy)) + height/2
            
    cv.Circle(image, (int(cx), int(cy)), 1, color, 2)
    pass

def getRandomSessionName():
    session_name = []
    for i in range(0, 10):
        session_name.append(str(int(random.uniform(0, 9))))
    session_name = ''.join(session_name)
    return session_name

# todo, rivedere approccio
def saveData(data): # un file per ogni elemento dell'array
    for i in data:
        fh = open("Sessions/s" + getRandomSessionName() + ".txt", "w")
        pickle.dump(i, fh)
        fh.close()
    pass

# Globals

IP          = 'nao.local'
PORT        = 9559
Period      = 50 # ms (in realtà forse non scende al di sotto dei 75 circa...)
Vocabulary  = ['yes', 'no']
WINDOW_NAME = 'CV'

DEBUG       = False

# Proxies

memoryProxy = ALProxy('ALMemory'            , IP, PORT)
speechProxy = ALProxy('ALSpeechRecognition' , IP, PORT)
faceProxy   = ALProxy('ALFaceDetection'     , IP, PORT)

speechProxy.setAudioExpression(False)
speechProxy.setVisualExpression(True)
speechProxy.setLanguage('English')
speechProxy.setWordListAsVocabulary(Vocabulary)

print "Proxies OK"

# EventManager Module & Callbacks

EventManager = None

class EventManagerModule(ALModule):
    
    def __init__(self, name):
        ALModule.__init__(self, name)

        # memoryProxy.subscribeToEvent("SpeechDetected", "EventManager", "onSpeechDetected")
        # memoryProxy.subscribeToEvent("WordRecognized", "EventManager", "onWordRecognized")
        # memoryProxy.subscribeToEvent("LastWordRecognized", "EventManager", "onLastWordRecognized")
        # memoryProxy.subscribeToEvent("FrontTactilTouched", "EventManager", "onFrontTactilTouched")
        pass

    '''
    def onWordRecognized(self, *_args):
        print "*** on Word Recognized ***"
        print _args[1]
        pass
    '''
    
    def onFrontTactilTouched(self, *_args):
        # memoryProxy.unsubscribeToEvent("SpeechDetected", "EventManager")
        # memoryProxy.unsubscribeToEvent("WordRecognized", "EventManager")
        # memoryProxy.unsubscribeToEvent("LastWordRecognized", "EventManager")
        # memoryProxy.unsubscribeToEvent("FrontTactilTouched", "EventManager")

        memoryProxy.unregisterModuleReference("EventManager")

        faceProxy.unsubscribe("MyFaceDetection")
        speechProxy.unsubscribe("MySpeechRecognition")

        # salva dati acquisiti
        # saveData(speech_sessions)
        pass
    
# End of EventManager

myBroker = ALBroker("myBroker", "0.0.0.0", 0, IP, PORT)
EventManager = EventManagerModule("EventManager")

faceProxy.subscribe('MyFaceDetection', Period, 0.0)
if not DEBUG:
    speechProxy.subscribe('MySpeechRecognition')

print "Events, Callbacks, Subscribe OK"

# Main

# speech_sessions = []

def main():
    
    face_detected_count     = 0
    speech_detected_count   = 0
    loop_count              = 0
    pause                   = False
    listening               = False
    # mouth_data              = []
    init_speech_time        = 0
    mouth_color             = (255, 255, 255, 0)

    cv.NamedWindow(WINDOW_NAME, cv.CV_WINDOW_AUTOSIZE)
    image = cv.CreateImage((640, 480), cv.IPL_DEPTH_32F, 3)

    while True:
        loop_count += 1
        
        k = cv.WaitKey(Period) # ! da modificare
        
        if k == 13:
            # Unsusbcribe
            faceProxy.unsubscribe('MyFaceDetection')
            if not DEBUG:
                speechProxy.unsubscribe('MySpeechRecognition')

            cv.DestroyWindow(WINDOW_NAME) 
            break
        elif k != -1: pause = not pause
        if   pause: continue

        cv.Set(image, cv.CV_RGB(0, 0, 0))

        FaceDetected    = memoryProxy.getData("FaceDetected")
        SpeechDetected  = memoryProxy.getData("SpeechDetected")
        WordRecognized  = memoryProxy.getData("WordRecognized")

        if SpeechDetected:
            if not listening:
                print "- SpeechDetected: Begin Listening"
                listening = True
                speech_detected_count += 1
                init_speech_time = time.time() * 1000
                mouth_color = (0, 0, 255, 0)
        else:
            if listening:
                print "- SpeechDetected: Stop listening"
                listening = False
                # speech_sessions.append(mouth_data)
                # mouth_data = []
                print (time.time() * 1000) - init_speech_time, " elapsed"
                init_speech_time = 0
                mouth_color = (255, 255, 255, 0)
                pass

        # listening and
        if(FaceDetected and isinstance(FaceDetected, list) and len(FaceDetected) >= 2):
            face_detected_count += 1

            timeStamp       = FaceDetected[0]
            faceInfoArray   = FaceDetected[1]
            
            # Temporaneamente, solo per la prima faccia 
            faceInfo        = faceInfoArray[0] 
            shapeInfo       = faceInfo[0]
            extraInfo       = faceInfo[1]

            # Ci interessano i punti della bocca
            mouthPoints     = extraInfo[8]

            # Punto medio
            alphas = mouthPoints[::2]
            betas = mouthPoints[1::2]
            ma = sum(alphas)/len(alphas)
            mb = sum(betas)/len(betas)

            # Lunghezze
            # punto right - punto left
            # punto bottom - punto top
            # (potrebbero interessarmi solo x e y)
            drawPointFromAngles(image, ma, mb, (0, 255, 0, 0))

            for i in range(8):
                drawPointFromAngles(image, mouthPoints[2*i], mouthPoints[2*i+1]
                                       , mouth_color)

            x = toRelative(mouthPoints[0], mouthPoints[1])
            y = toRelative(mouthPoints[2], mouthPoints[3])
            cv.Line(image, x, y, (255, 255, 255, 0), 1)
            x = toRelative(mouthPoints[4], mouthPoints[5])
            y = toRelative(mouthPoints[6], mouthPoints[7])
            cv.Line(image, x, y, (255, 255, 255, 0), 1)

        # Osservazione banale: ogni WordRecognized dovrebbe essere preceduto
        # dai relativi SpeechDetected (True, False)
        if WordRecognized[0] != '':
            print "- WordRecognized: ", WordRecognized
            memoryProxy.insertData("WordRecognized", [''])
        
        cv.ShowImage(WINDOW_NAME, image)

main()
print "Done"

'''
Commenti

1) Il periodo del FD dovrebbe essere basso (es 100 ms ha poco senso)
2) Lo SD dovrebbe essere effettuato in continuazione, senza sleep, per
    maggior precisione (permette di risolvere problemi di sincronizz. tra
    speech temporalmente molto vicini)
3) Va fissato quindi un periodo di attesa per il FD, per evitare ripetizioni
    di valori inutili, o comunque scartare valori consecutivi uguali,
    o ancora meglio resettare FaceDetected ([]) e attendere che sia il
    periodo "nativo" del subscribe a fare il lavoro (oneroso, troppe chiamate
    intermedie di ALMemory), oppure usando dei timer e condizioni di selezione
    (comunque senza sleep(), questo approccio prevede risorse utilizzate a vuoto)
    [significativo solo per il salvataggio dati, non per disegnare i punti con opencv]
OK] Utile: quanto dura mediamente il processo di SpeechDetection in ms?
SEMI-OK] Memorizzare punti mouth, view con opencv (facile, periodo noto a priori)
6) Eventuale regisrazione allegata per verifica, parametri e timestamp
    SpeechRecognition (inizio/fine speech, face detection, etc)
SEMI-OK] Sincronizzare infine [Last]WordRecognized con SpeechDetected

if time.time() - t0 > period: # do stuff (ci potrebbe stare)

TODO:
- Avviare il modulo nel robot (BehaviorManager?)
-> Trasformare uno script in un behavior?
- Comando prendere timestamp robot shell con subrocess.call

Modo scarso: uppare script via ftp, avviare da ssh (python script.py)
Oppure creare nuovo modulo python
Unix timestamp: date +%s [linux only!]
'''
