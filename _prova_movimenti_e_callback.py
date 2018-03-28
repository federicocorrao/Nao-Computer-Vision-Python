# -*- encoding: UTF-8 -*- 

import sys
import motion
import time
import math

#
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
from optparse import OptionParser
#

HumanGreeter = None
memory = None

class HumanGreeterModule(ALModule):
    
    def __init__(self, name):
        ALModule.__init__(self, name)

        # nota self.tts
        #self.tts = ALProxy("ALTextToSpeech")

        # Subscribe to the FaceDetected event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("SonarLeftDetected",
            "HumanGreeter",
            "lsonar")
        memory.subscribeToEvent("SonarRightDetected",
            "HumanGreeter",
             "rsonar")

    def lsonar(self, *_args):
        print "Left Sonar"

    def rsonar(self, *_args):
        print "Right Sonar"

def main2():
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip='127.0.0.1',
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port

    # Warning: HumanGreeter must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global HumanGreeter
    HumanGreeter = HumanGreeterModule("HumanGreeter")
#

def CreateProxy(proxy_name, ip = '127.0.0.1', port = 9559):
    # TODO: Check types
    try:
        proxy = ALProxy(proxy_name, ip, port)
    except Exception, e:
        print 'Could not create proxy to ' + proxy_name + ' on ' + ip + ':' + str(port)
        print 'Error was:\n ', e
        return
    else:
        print 'Proxy ' + proxy_name + ' was created'
        return proxy

# End of CreateProxy


def StiffnessOn(proxy):
    # Names, StiffnessLists, TimeLists
    proxy.stiffnessInterpolation('Body', 1.0, 1.0)

# End of StiffnessOn


def Walk(Proxy, X, Y, Theta, Frequency):
    Proxy.setWalkTargetVelocity(X, Y, Theta, Frequency)

# End of Walk

def cb(eventName, val, subscriberIdentifier):
    print "callback"


def main():
    main2()

    IP = '127.0.0.1'
    Port = 9559
    
    # Init proxies
    motionProxy  = CreateProxy("ALMotion", IP, Port)
    postureProxy = CreateProxy("ALRobotPosture", IP, Port)
    
    # Set NAO in Stiffness On
    StiffnessOn(motionProxy)

    # Send NAO to Pose Init
    postureProxy.goToPosture("StandInit", 0.5)
    motionProxy.moveInit()

    motionProxy.setWalkArmsEnabled(True, True)
    motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])

    #stato motion
    #print motionProxy.getSummary()
    #print motionProxy.getRobotPosition(False)
    #print motionProxy.getBodyNames("Body")
    #print motionProxy.getLimits("Body")
    #print motionProxy.getRobotConfig()
    #print motionProxy.getSummary()
    #print motionProxy.getMass("Body")
    #print postureProxy.getPostureList()

# Movimenti
    
    # Apri/chiudi mano
    #motionProxy.openHand("RHand")
    #motionProxy.closeHand("RHand")
    ##motionProxy.openHand("LHand")
    #motionProxy.closeHand("LHand")

    # Esempio muovere testa
    #names  = ["HeadYaw", "HeadPitch"]
    #angles  = [0.2, -0.2]
    #fractionMaxSpeed  = 0.2
    #motionProxy.setAngles(names, angles, fractionMaxSpeed)
    #motionProxy.move(0, 0, math.pi) # params velocità assoluta
    #motionProxy.moveToward(1, 0, 0) # params velocità relativa
    #motionProxy.moveTo(0.2, 0, 0) # params distanza relativa
    #motionProxy.moveTo(0, 0.2, 0) # params distanza relativa
    #motionProxy.moveTo(0, 0.2, math.pi/2) # params distanza (relativa)
    #motionProxy.waitUntilMoveIsFinished() # (per chiamate non bloccanti)

    # Prova tutte le posture
    #postures = postureProxy.getPostureList()
    #for i in postures:
    #    print i
    #    postureProxy.goToPosture(i, 0.5)
    
    #TARGET VELOCITY
    #Walk(Proxy = motionProxy,
    #     X = 0.2,
    #     Y = -0.5,
    #     Theta = 0.2,
    #     Frequency = 1.0
    #     )
    #time.sleep(2.0)
    #motionProxy.waitUntilMoveIsFinished()

# Altro

    # Moduli caricati
    mod = CreateProxy("ALLauncher")
    print mod.getGlobalModuleList()

    # s.getOutputNames()
    s = CreateProxy("ALSonar")
    #fsr = CreateProxy("ALFsr")
    #n = CreateProxy("ALNavigation")
    n = CreateProxy("ALMotion")
    mem = CreateProxy("ALMemory")

    print "sonar period: " + str(s.getCurrentPeriod())
    print "sonar precision: " + str(s.getCurrentPrecision())

    s.subscribe("my_Sonar_Left_Detected")
    s.subscribe("my_Sonar_Right_Detected")
      
    #n.moveTo(0, 0, math.pi/4)

    rec_left = True
    rec_right = None
    while rec_left == None and rec_right == None:
        n.moveTo(0.2, 0, 0)
        #motionProxy.waitUntilMoveIsFinished()
        rec_left = mem.getData("SonarLeftDetected")
        rec_right = mem.getData("SonarRightDetected")
        #print motionProxy.getRobotPosition(False)
        print [rec_left, rec_right]
        #print mem.getData('footContact')

    # cambiare periodo 
    s.updatePeriod("HumanGreeterSonarLeftDetected", 20)
    s.updatePrecision("HumanGreeterSonarLeftDetected", 0.1)
    print s.getSubscribersInfo()
    
    print "done"
    return

# End of main

main()
