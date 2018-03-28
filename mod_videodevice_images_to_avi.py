# -*- coding: cp1252 -*-

# vedi prova_videodevice.py
# Conversione immagini jpeg in avi(m-jpeg) con mencoder 

import time
from naoqi import ALProxy
import Image
import os

IP = '127.0.0.1'
Port = 9559

p = ALProxy("ALVideoDevice", IP, Port)
camindex = p.getActiveCamera()

# Subscribe

resolution = 2 # VGA
colorspace = 11 # RGB
fps = 30

nameId = 'python_GVM' # nome default?
nameId = p.subscribe(nameId, resolution, colorspace, fps)
path = "C:\\Users\\Federico\\Desktop\\"

# Cammina (per verificare corretta registrazione video
po = ALProxy("ALRobotPosture", IP, Port)
po.goToPosture("Stand", 0.5)
mo = ALProxy("ALMotion", IP, Port)
mo.stiffnessInterpolation("Body", 1, 1)
mo.moveInit()
mo.moveToward(0.5, 0, 0)

print "Recording"
t0 = time.time()

max = 20
for i in range(0, max):
    print i
    image = p.getImageRemote(nameId)

    image_width = image[0]
    image_height = image[1]
    array = image[6]
    # Salva frame
    im = Image.fromstring("RGB", (image_width, image_height), array)
    im.save(path + "naoimages\\" + str(i) + ".jpeg", "JPEG")

    p.releaseImage(nameId)
    time.sleep(0.003)

t1 = time.time()
print "Stopping"
print t1 - t0

p.stopVideo(nameId)
p.unsubscribe(nameId)

print "Done"

# mencoder
# http://www.mplayerhq.hu/DOCS/HTML/en/menc-feat-enc-images.html

os.chdir("C:\\Users\\Federico\\Desktop\\naoimages\\")
os.system("mencoder mf://*.jpeg -mf w=320:h=240:fps=20:type=jpg -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -oac copy -o output.avi")
