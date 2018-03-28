# -*- coding: cp1252 -*-

import os, time
from naoqi import ALProxy
import Image                    # from PIL
import multiprocessing

def recordVideo(duration, fps, ip = '127.0.0.1', port = 9559):
    vd = ALProxy("ALVideoDevice", ip, port)
    camindex = vd.getActiveCamera()

    # todo param
    resolution = 2  # VGA
    colorspace = 11 # RGB

    nameId = 'python_GVM'
    nameId = vd.subscribe(nameId, resolution, colorspace, fps)

    # vd.setResolution("python_GVM", 2) # non sembra avere effetto 

    parent = "C:\\Users\\Federico\\Desktop\\"
    path = parent + "naoimages\\"

    print "recordVideo: Recording"
    t0 = time.time()

    image_width = 640 # image[0]
    image_height = 480 # image[1]
    images = []

    for i in range(0, duration*fps):
        ta = time.time()
        print "recordVideo: Frame " + str(i)
        image = vd.getImageRemote(nameId)
        images.append(image[6])
        vd.releaseImage(nameId) 
        tb = time.time()
        #print (1/float(fps)) - (tb - ta)
        time.sleep((1/float(fps)) - (tb - ta)) #(float(1/fps))
        #time.sleep(1/float(fps))
        
    t1 = time.time()
    print "recordVideo: " + str(t1 - t0) + " s elapsed. Done"
    vd.unsubscribe(nameId)
    
    for i in range(0, duration*fps): 
        im = Image.fromstring("RGB", (image_width, image_height), images[i])
        im.save(path + str(i) + ".jpeg", "JPEG")
    
    # mencoder
    os.chdir("C:\\Users\\Federico\\Desktop\\naoimages\\")
    os.system("mencoder mf://*.jpeg -mf w=640:h=480:fps=" + str(fps) +
        ":type=jpg -ovc lavc -lavcopts vcodec=mpeg4:mbd=2:trell -oac copy -o output.avi")
    
    pass

IP = '127.0.0.1'
Port = 9559
mo = ALProxy("ALMotion", IP, Port)
po = ALProxy("ALRobotPosture", IP, Port)

def loophead():
    print "started"
    mo.stiffnessInterpolation("Body", 1, 1)
    mo.moveInit()

    d = 0
    while True:
        mo.setAngles("HeadYaw", d, 0.1)
        time.sleep(1)
        d = 1 - d
    pass
#

# po.goToPosture("Stand", 0.5)
mo.stiffnessInterpolation("Body", 1, 1)
mo.moveInit()
mo.moveToward(0.5, 0, 0)

# problema: sia recordvideo che loophead vanno in loop e si escludono
# (modo per mettere in coda chiamate asincrone?)
# TODO: rendere lopphead asincrona senza fare impallare tutto

loophead()
#recordVideo(10, 25)

# p = multiprocessing.Process(target = loophead)
# p.start()
