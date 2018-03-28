# -*- coding: cp1252 -*-

# Esempi 
# Recording a .arv video file
# file:///C:/Program%20Files%20(x86)/Aldebaran/Choregraphe%201.14.1.16/doc/naoqi/vision/alvideodevice-tuto.html#alvideodevice-tuto-record-arv

# Replaying an .arv video file (ALVideoDeviceProxy.setVideo ... )
# file:///C:/Program%20Files%20(x86)/Aldebaran/Choregraphe%201.14.1.16/doc/naoqi/vision/alvideodevice-tuto.html#alvideodevice-tuto-replay-arv

# Modifying camera parameters
# file:///C:/Program%20Files%20(x86)/Aldebaran/Choregraphe%201.14.1.16/doc/naoqi/vision/alvideodevice-tuto.html#alvideodevice-cameraparameters

import time
from naoqi import ALProxy
# import vision_definitions
# Usa PIL (Python Imaging Library) per lavorare con le immagini
import Image

IP = '127.0.0.1'
Port = 9559

p = ALProxy("ALVideoDevice", IP, Port)
camindex = p.getActiveCamera()
# vedi anche setActiveCamera(...)

# (Valori ritorno documentati)
# print p.getCameraModel(camindex)
# print p.getFrameRate(camindex)
# print p.getResolution(camindex)
# print p.getColorSpace(camindex)
# vedi anche getCameraParameter(...)
# Queste costanti dovrebbero trovarsi in [import] vision_definitions

resolution = 2 # VGA
colorspace = 11 # RGB
fps = 30

# Subscribe
nameId = 'python_GVM' # nome default?
nameId = p.subscribe(nameId, resolution, colorspace, fps)

# Record (formato arv)
path = "C:\\Users\\Federico\\Desktop\\"
totalnumber = 3500
period = 1 # ?
recording = p.recordVideo(nameId, path + "new_video", totalnumber, period)

print "Recording"
t0 = time.time()

# Prende 20 immagini 
max = 20
for i in range(0, max):
    print i
    image = p.getImageRemote(nameId)
    p.releaseImage(nameId)
    time.sleep(0.003)

t1 = time.time()
print "Stopping"
print t1 - t0

p.stopVideo(nameId)
p.unsubscribe(nameId)

print "Done"

# Eempio salvataggio immagine

# image (da getImageRemote) è un array contenente info sull'immagine,
# image[6] dovrebbe contenere l'immagine come array di char ASCII

image_width = image[0]
image_height = image[1]
array = image[6]

# Usa PIL
im = Image.fromstring("RGB", (image_width, image_height), array)
im.save(path + "last_image.png", "PNG")
# attenzione, senza resolution = 2 (VGA) e colorspace = 11 (RGB) mi dà problemi

# image[0] : [int] width of the image
# image[1] : [int] height of the image
# image[2] : [int] number of layers of the image
# image[3] : [int] colorspace of the image
# image[4] : [int] time stamp in second
# image[5] : [int] time stamp in microsecond (and under second)
# image[6] : [int] data of the image
# image[7] : [int] camera ID
# image[8] : [float] camera FOV left angle (radian)
# image[9] : [float] camera FOV top angle (radian)
# image[10]: [float] camera FOV right angle (radian)
# image[11]: [float] camera FOV bottom angle (radian)
