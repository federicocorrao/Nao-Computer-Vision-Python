
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

IP      = '127.0.0.1'
Port    = 9559

MemoryProxy = None
Manager = None

class EventManagerModule(ALModule):
    # Constuctor

    # MemoryProxy = None

    def __init__(self, name):
        # Base
        ALModule.__init__(self, name)
        #global MemoryProxy
        #self.MemoryProxy = ALProxy('ALMemory', IP, Port)
        #MemoryProxy = ALProxy('ALMemory')
    #

    def subscribeToEvent(self, event, callback_name, callback_body):
        setattr(self, callback_name, callback_body)

        global MemoryProxy #self.
        MemoryProxy = ALProxy("ALMemory")
        MemoryProxy.subscribeToEvent(
            event, 'Manager', callback_name)
    #
#

def ciao(self, *_args):
    print "red ball detected callback"

rbprox = ALProxy("ALRedBallDetection", IP, Port)
rbprox.subscribe("prova")

myBroker = ALBroker("myBroker", "0.0.0.0", 0, IP, Port)
Manager = EventManagerModule('Manager')

Manager.subscribeToEvent("redBallDetected", "rbd_callback", ciao)

print "done"
