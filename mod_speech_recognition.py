# -*- encoding: UTF-8 -*-

'''
    Altro
    - ALAudioSourceLocalization
    - Sound Tracking
'''

# from msvcrt import getch
import sys
import math

from naoqi import ALProxy
from naoqi import ALModule
from naoqi import ALBroker

IP   = 'nao.local'
PORT = 9559

memoryProxy = ALProxy("ALMemory", IP, PORT)
speechProxy = ALProxy("ALSpeechRecognition", IP, PORT)
ttsProxy    = ALProxy("ALTextToSpeech", IP, PORT)
# aslProxy  = ALProxy("ALAudioSourceLocalization", IP, PORT)
ad          = ALProxy("ALAudioDevice", 'nao.local', 9559)
ad.setOutputVolume(10)
#ar          = ALProxy("ALAudioRecorder", 'nao.local', 9559)
#ap          = ALProxy("ALAudioPlayer", 'nao.local', 9559)

print "Proxy OK"

# Event Handling 

EventManager = None

class EventManagerModule(ALModule):
    
    def __init__(self, name):
        ALModule.__init__(self, name)

        global memoryProxy

        # front e rear attivano/disattivano speech recognition
        memoryProxy.subscribeToEvent(
            "FrontTactilTouched", "EventManager", "onFrontTactilTouched")
        memoryProxy.subscribeToEvent(
            "RearTactilTouched", "EventManager", "onRearTactilTouched")
    #

    enabled = False
    # WordRecognized, LastWordRecognized, SpeechDetected
    eventname = "LastWordRecognized"

    front_control = False
    front_touched = 0
    def onFrontTactilTouched(self, *_args):
        #global memoryProxy
        
        if self.front_control == False:
            self.front_touched += 1
            # print "front", self.front_touched

            try:
                print "Unregistering..."
                # do stuff
                memoryProxy.unsubscribeToEvent(
                    self.eventname, "EventManager")
                # memoryProxy.unsubscribeToEvent(
                #    "SoundLocated", "EventManager")
                # memoryProxy.unsubscribeToEvent("SpeechDetected", "EventManager")

                memoryProxy.unregisterModuleReference("EventManager")
                print "Unregistered"
            except Exception as e:
                print "Unregistering: Error occurred"
                print e
            else:
                self.enabled = False
            
            self.front_control = True
        else:
            self.front_control = False
    #

    rear_control = False
    rear_touched = 0
    def onRearTactilTouched(self, *_args):
        #global memoryProxy
        
        if self.rear_control == False:
            self.rear_touched += 1
            # print "rear ", self.rear_touched

            try:
                print "Registering..."
                # do stuff
                
                speechProxy.setAudioExpression(False)
                speechProxy.setVisualExpression(True)
                speechProxy.setLanguage("English")
                # speechProxy.setWordListAsVocabulary(['yes', 'no'])
                speechProxy.setVocabulary(
                    ["every", "device"]
                    , False)
                
                memoryProxy.subscribeToEvent(
                    self.eventname, "EventManager", "onSpeechDetected")
                # memoryProxy.subscribeToEvent(
                #    "SoundLocated", "EventManager", "onSoundLocated")
                # memoryProxy.subscribeToEvent(
                #    "SpeechDetected", "EventManager", "onSoundLocated")
                
                print "Registered"
            except Exception as e:
                print "Registering: Error occurred"
                print e
            else:
                self.enabled = True
                
            self.rear_control = True
        else:
            self.rear_control = False
    #

    spdec_counter = 0
    def onSpeechDetected(self, *_args):
        self.spdec_counter += 1
        print "- onSpeechDetected ", self.spdec_counter, ": "

        # print _args
        
        try:
            
            phrases = _args[1][::2]
            probs   = _args[1][1::2]

            for i in range(len(phrases)):
                print "- ", phrases[i], probs[i]

            '''
            problema: il robot riconosce la sua stessa voce e va in loop:
            risolvo facendo unsubscribe/subscribe prima/dopo tts.say
            '''

            #memoryProxy.unsubscribeToEvent(self.eventname, "EventManager")
            # phrases[0] è la frase con riconoscimento massimo
            #ttsProxy.say(phrases[0])
            #print "i spoke"
            #memoryProxy.subscribeToEvent(self.eventname, "EventManager", "onSpeechDetected")
            
        except Exception as e:
            print e
    #
    
    def onSoundLocated(self, *_args):
        print "dect"
        # print _args[1]
    #

# End of EventManager        

myBroker = ALBroker("myBroker", "0.0.0.0", 0, IP, PORT)
EventManager = EventManagerModule("EventManager")

print "Broker OK"

# Main

EventManager.onRearTactilTouched()
# ttsProxy.say("device")
c = raw_input("Waiting...")

EventManager.onFrontTactilTouched()


'''
Esempio: problema con LastWordRecognized
(senza word spotting)
- hello
- hello, i'm nao
su input "hello, i'm nao"
vince "hello" (riconosciuta per prima)

- hello, i'm nao
- nao
su "hello, i'm nao"
vince "nao" (perché?)

possibile soluzione: la virgola introduce una pausa (il che equivale a spezzare la frase)
senza virgola, c'è un buon grado di riconoscimento per entrambe

Altro esempio:
su "hello nao"
- hello
- hello nao
- nao
(sembra plausibile)

su "hellonao"
risultati più incerti

'''
