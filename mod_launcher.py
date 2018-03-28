# -*- coding: cp1252 -*-

from naoqi import ALProxy
# from naoqi import ALModule
# form naoqi import ALBroker
# from naoqi import ALBehavior

# Informazioni sui moduli naoqi
# testModules() Verifica quali siano i moduli (della documentazione)
# caricati da naoqi
# listModules() Stampa moduli caricati da naoqi
# diffModules() Ritorna i moduli caricati da naoqi, non documentati
# (utente/sistema)

def printlist(l):
    for i in l:
        print i

# Verifica quali siano i moduli documentati non caricati da NAOqi
def testModules(ip = '127.0.0.1', port = 9559, silent = 0):
    modules = [
        # CORE
        'BehaviorManager', 'ConnectionManager', 'Memory',
        'Preferences', 'ResourceManager', # 'Module',
        'Bonjour', 'Logger', 'Launcher', # DEP
        # MOTION
        'Motion', 'Navigation', 'RobotPosture',
        'MotionRecorder', # DEP
        # AUDIO
        'AudioDevice', 'AudioPlayer', 'AudioRecorder',
        'AudioSourceLocalization', 'SoundDetection',
        'SpeechRecognition', 'TextToSpeech',
        # SENSORS
        'Battery', 'Fsr', 'Infrared', 'Laser',
        'Sensors', 'Sonar', 'Leds', 
        'RobotPose', # DEP
        # TRACKERS
        'FaceTracker', 'RedBallTracker',
        # VISION
        'FaceDetection', 'BacklightingDetection', 'DarknessDetection',
        'LandmarkDetection', 'MovementDetection', 'RedBallDetection',
        'PhotoCapture', 'VideoDevice', 'VideoRecorder', 'VisionRecognition',
        'VisualCompass',
        'VisionToolBox' # DEP
        # DCM (NON 'AL' + 'DCM')
        ]

    r = []

    for m in modules:
        try:
            p = ALProxy('AL' + m, ip, port)
        except Exception as e:
            if(silent == 0):
                print "testModules(): Failed to load AL" + str(m)
        else:
            r.append('AL' + m)

    return r

# Usa ALLauncher::isModulePresent, attenzione: deprecato
# Dovrebbe essere equivalente a testModules() ma più rapida
def testModules2(ip = '127.0.0.1', port = 9559, silent = 0):
    modules = [
        # CORE
        'BehaviorManager', 'ConnectionManager', 'Memory',
        'Preferences', 'ResourceManager', # 'Module',
        'Bonjour', 'Logger', 'Launcher', # DEP
        # MOTION
        'Motion', 'Navigation', 'RobotPosture',
        'MotionRecorder', # DEP
        # AUDIO
        'AudioDevice', 'AudioPlayer', 'AudioRecorder',
        'AudioSourceLocalization', 'SoundDetection',
        'SpeechRecognition', 'TextToSpeech',
        # SENSORS
        'Battery', 'Fsr', 'Infrared', 'Laser',
        'Sensors', 'Sonar', 'Leds', 
        'RobotPose', # DEP
        # TRACKERS
        'FaceTracker', 'RedBallTracker',
        # VISION
        'FaceDetection', 'BacklightingDetection', 'DarknessDetection',
        'LandmarkDetection', 'MovementDetection', 'RedBallDetection',
        'PhotoCapture', 'VideoDevice', 'VideoRecorder', 'VisionRecognition',
        'VisualCompass',
        'VisionToolBox' # DEP
        # DCM (NON 'AL' + 'DCM')
        ]

    r = []
    
    p = ALProxy("ALLauncher", ip, port)

    for m in modules:
        if (p.isModulePresent('AL' + m)):
            r.append('AL' + m)
        else:
            if(silent == 0):
                print 'testModules2(): AL' + m + ' not present'

    return r

# Stampa moduli caricati da NAOqi
# Nota: ALLauncher è deprecato
def listModules(ip = '127.0.0.1', port = 9559, silent = 0):
    p = ALProxy('ALLauncher', ip, port)
    l = p.getGlobalModuleList()

    for m in l:
        if(silent == 0):
            print "listModules(): " + m

    return l

# Moduli non documentati ma caricati da NAOqi... (?)
def diffModules(ip = '127.0.0.1', port = 9559):
    A = testModules(ip, port, 1)
    B = listModules(ip, port, 1)
    return list(set(B) - set(A))


# testModules()

# IP = '127.0.0.1'
# Port = 9559
# p = ALProxy("ALLauncher", IP, Port)
# name = 'ALMotion'
# print p.launchLocal(name)
# print p.isModulePresent(name)
