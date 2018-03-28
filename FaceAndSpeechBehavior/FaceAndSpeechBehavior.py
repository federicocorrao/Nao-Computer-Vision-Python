# -*- coding: cp1252 -*-

''' TODO
- Aggiornare il BehaviorTemplate
- Risolvere problema delle inclusioni
- Il periodo FD tende a rimanere stabile se si fa una sleep:
    ricorda comunque di separare sleep FD e SD
- Implementare raccolta dati

- Altra possibile soluzione più efficiente
    anziché mantenere il face detection sempre attivo e scartare valori con if
    attivare/disattivare direttamente il face detection con subscribe/unsubscribe
    a inizio/fine ascolto?
'''


# Includes

import os, math, time, random
import pickle

from naoqi import ALProxy
from naoqi import ALModule
from naoqi import ALBroker

import cv2, cv2.cv
cv = cv2.cv


# Globals

DEBUG       = True   # Utile
caller      = None    # self pubblico (comodo per proc utili che hanno bisogno di self)
LOCAL       = True    # indica se lo script è in esecuzione sul nao o in locale (eqv caller == None)

IP          = 'localhost' # | nao.local
PORT        = 9559
FacePeriod  = 100 # ms (sembra non scendere oltre gli 80 ms, mediamente è sui 100, 110)
Vocabulary  = ['yes', 'no']
WINDOW_NAME = 'CV'

memoryProxy     = None
speechProxy     = None
faceProxy       = None
sensorsProxy    = None
ttsProxy        = None


# Utils

def log(message):
    global LOCAL
    if not LOCAL:
        caller.log(message)
    else:
        print message
    pass

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

def saveData(data):
    s = getRandomSessionName()
    while os.path.exists("Sessions/s" + s + ".txt"):
        s = getRandomSessionName()
    fh = open("Sessions/s" + s + ".txt", "w")
    pickle.dump(data, fh)
    fh.close()
    pass


# Procs

def DrawPoints(FaceDetected, image, mouth_color):
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

    drawPointFromAngles(image, ma, mb, (0, 255, 0, 0))

    for i in range(8):
        drawPointFromAngles(image, mouthPoints[2*i], mouthPoints[2*i+1], mouth_color)

        x = toRelative(mouthPoints[0], mouthPoints[1])
        y = toRelative(mouthPoints[2], mouthPoints[3])
        cv.Line(image, x, y, (255, 255, 255, 0), 1)
        x = toRelative(mouthPoints[4], mouthPoints[5])
        y = toRelative(mouthPoints[6], mouthPoints[7])
        cv.Line(image, x, y, (255, 255, 255, 0), 1)
    pass


# Eventi Behavior

def Load(self):
    # Questa proc. viene invocata SOLO quando lo script è in
    # esecuzione sul nao (come behavior -> esiste self)
    # Inizializza caller
    global caller, LOCAL
    caller = self
    LOCAL = False
    pass

def Start():
    # Main call
    if LOCAL:
        print "RUNING LOCAL"
    else:
        caller.log("RUNNING ON NAO")
    
    log("--- Start INIT")
    
    global memoryProxy, speechProxy, faceProxy, sensorsProxy, ttsProxy

    memoryProxy     = ALProxy('ALMemory'            , IP, PORT)
    speechProxy     = ALProxy('ALSpeechRecognition' , IP, PORT)
    faceProxy       = ALProxy('ALFaceDetection'     , IP, PORT)
    sensorsProxy    = ALProxy('ALSensors'           , IP, PORT)
    ttsProxy        = ALProxy('ALTextToSpeech'      , IP, PORT)
    
    speechProxy.setAudioExpression(False)
    speechProxy.setVisualExpression(True)
    speechProxy.setLanguage('English')
    speechProxy.setWordListAsVocabulary(Vocabulary)    

    log("-- Proxies DONE")

    faceProxy.subscribe('MyFaceDetection', FacePeriod, 0.0)
    speechProxy.subscribe('MySpeechRecognition')
    sensorsProxy.subscribe('MySensors')        

    log("-- Subscribe DONE")
    log("-- Main INIT")
    
    main()
    # auto onUnload
    pass

def Stop():
    # Stop da input esterno
    log("--- Stop INIT")

    # auto onUnload
    pass

def Unload():
    # Rilascia risorse
    log("--- Unload INIT")

    faceProxy.unsubscribe("MyFaceDetection")
    speechProxy.unsubscribe("MySpeechRecognition")
    sensorsProxy.unsubscribe("MySensors")
    
    log("-- Unsubscribe DONE")        
    pass


# Main

def main():

    face_detected_count     = 0
    speech_detected_count   = 0
    loop_count              = 0
    listening               = False

    main_data               = []
    #init_speech_time        = 0
    mouth_data              = {} # current (temp) mouth data
    
    pause                   = False                 # LOCAL only
    mouth_color             = (255, 255, 255, 0)    # LOCAL only
    image                   = None                  # LOCAL only

    if LOCAL:
        cv.NamedWindow(WINDOW_NAME, cv.CV_WINDOW_AUTOSIZE)
        image = cv.CreateImage((640, 480), cv.IPL_DEPTH_32F, 3)

    if DEBUG: mouth_data["Frames"] = []

    while True:
        # se script in locale e finestra in pausa
        if LOCAL and pause: continue
        
        loop_count += 1

        FaceDetected        = memoryProxy.getData("FaceDetected")
        SpeechDetected      = memoryProxy.getData("SpeechDetected")
        WordRecognized      = memoryProxy.getData("WordRecognized")
        FrontTactilTouched  = memoryProxy.getData("FrontTactilTouched")

        # Uscita (unsubscribe)
        if FrontTactilTouched:
            if LOCAL: cv.DestroyWindow(WINDOW_NAME)
            break

        if SpeechDetected: # inizio ascolto
            if not listening:
                mouth_data['InitSpeechTime'] = time.time()
                mouth_data['Frames'] = []
                # NOTA: questo tempo presenta un ritardo di qualche millisecondo!
                log("- SpeechDetected: Begin Listening @ " + str(mouth_data['InitSpeechTime']))                
                listening = True
                speech_detected_count += 1
                if LOCAL: mouth_color = (0, 0, 255, 0)
        else: # fine ascolto
            if listening:
                mouth_data['EndSpeechTime'] = time.time()
                log("- SpeechDetected: Stop listening @ " + str(mouth_data['EndSpeechTime']))
                listening = False
                main_data.append(mouth_data)
                mouth_data = { }
                if LOCAL: mouth_color = (255, 255, 255, 0)
        # calcolare elapsed in ms: 1000 * (end - init)

        # Face Detection

        FaceDetectedData = []
        
        if( # listening and
           FaceDetected and isinstance(FaceDetected, list) and len(FaceDetected) >= 2):
            face_detected_count += 1
            log(str(face_detected_count) + "FD " + str(FaceDetected[0])) # time.time

            FaceDetectedData = FaceDetected            
            memoryProxy.insertData("FaceDetected", [])
            # collect data
            current_frame = {
                'FaceDetectionTimestamp': FaceDetectedData[0] #,
                 # 'MouthPoints': FaceDetectedData[1][0][1][8]
                }
            mouth_data['Frames'].append(current_frame)

        # osservazione: sicuramente wordrecognized avviene dopo l'end
        # di speechdetected, allora posso aggire sull'ultimo mouth_data,
        # che è salvato in main_data (append)
        # TODO: risolvere problemi di sincronizzazione qui
        # (questo codice andrebe modifcato) [se l'ultimo mouth_data non è ancora stato messo
        # in main data?]
        if WordRecognized[0] != '':
            log(WordRecognized)
            main_data[-1]['WordRecognized'] = WordRecognized
            memoryProxy.insertData("WordRecognized", [''])

        
        # CV window etc

        if LOCAL: # local sleep (cv)
            k = cv.WaitKey(FacePeriod)
            if k == 13:
                cv.DestroyWindow(WINDOW_NAME)
                break
            elif k != -1: pause = not pause

            cv.Set(image, cv.CV_RGB(0, 0, 0))
            if FaceDetectedData != []:
                DrawPoints(FaceDetectedData, image, mouth_color)
            cv.ShowImage(WINDOW_NAME, image)

        else: # NAO sleep
            time.sleep(0.1)

    # end of loop
    
    #saveData(main_data) # risolvere problema cartella non esistente in remoto
    #log(main_data)
    if DEBUG: main_data = mouth_data
    global md
    md = main_data
    time.sleep(1)
    log("-- Main DONE")
    pass

#

# LOCAL
# Anche qui si avverte il problema ella lentezza nel caricamento dei proxy,
# quando LOCAL == True

if __name__ == '__main__':

    IP = "nao.local"
    Start()
    Unload()


'''
Commenti

1) Periodo FD dovrebbe essere basso (problema: non sembra scendere oltre 80 ms)
    -> per parole troppo piccole non viene rionosciuto neanche un frame
2) SD effettuaot in continuazione o con una sleep?
    per maggior precisione, preferibilmente in continuazione, ma ciò
    può incrementare il carico di lavoro e ridurre il periodo del FD
3) Tenere conto dei casi in cui i punti della bocca non sono validi
    (outliers?)
'''

''' Ongi elemento di main_data è una collezione:

main_data: [
    0: {
        InitSpeechTime: (float, time.time())
        EndSpeechTime:  (float, time.time())
        Frames: [
            Frame1: {
                FaceDetectionTimestamp: [secs, msecs]
                MouthPoints: [... (16)]
            }
            Frame2: { ... }
            Frame3: { ... }
        ]
    }
    1 ...
    2 ...
]

'''

'''
# Tempo di sistema in nanosecondi
from subprocess import Popen, PIPE
p = Popen(["date", "+%s %N"], stdout=PIPE, stderr=PIPE)
(stdout, stderr) = p.communicate()
self.log(stdout)
# utile da remoto, o più semplicemente, se lo script gira sulla macchina: time.time()
'''

