
import os

print "Running on NAO! "
os.system("uname")
os.system("date +%s")

from naoqi import ALProxy

tts = ALProxy("ALTextToSpeech", "localhost", 9559)
tts.say("hello")
