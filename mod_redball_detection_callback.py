
from naoqi import ALProxy
from naoqi import ALBroker, ALModule

IP = '127.0.0.1'
Port = 9559

# Callback
# Global variable to store the (RBModule) module instance
RB = None
memory = None

class RBModule(ALModule):

    def __init__(self, name):
        ALModule.__init__(self, name)

        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("redBallDetected",
            "RB",
            "onRedBallDetected")
    #
    
    def onRedBallDetected(self, *_args):
        print "callback"
    #
#


rb = ALProxy("ALRedBallDetection", IP, Port)
rb.subscribe("prv")

# We need this broker to be able to construct
# NAOqi modules and subscribe to other modules
# The broker must stay alive until the program exists
myBroker = ALBroker("myBroker",
    "0.0.0.0",   # listen to anyone
    0,           # find a free port and use it
    IP,         # parent broker IP
    Port)       # parent broker port

RB = RBModule("RB")    

print 'done'
