# -*- coding: cp1252 -*-

# Registra un video direttamente dal nao (non con frames + mencoder)
# con il modulo ALVideoRecorder (non ALVideoDevice)

import time
from naoqi import ALProxy

IP = "nao.pa.icar.cnr.it"
Port = 9559

vr = ALProxy("ALVideoRecorder", IP, Port)

# vr.setResolution(2)
# vr.setColorSpace(11)
vr.setFrameRate(10)
vr.setVideoFormat("MJPG")

print "Start Recording"
# Salva il video in un path pubblico nella memoria del robot
vr.startRecording("/home/nao/recordings/cameras", "myvideo4")

# Cattuta 20 secondi di video
time.sleep(20)

videoinfo = vr.stopRecording()
print videoinfo
