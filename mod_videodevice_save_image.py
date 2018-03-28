
import Image
from naoqi import ALProxy
import vision_definitions

# Cattura una immagine e la salva nella memoria del robot
# NOTA: usare invece il modulo ALPhotoCapture!

IP = "nao.pa.icar.cnr.it"
Port = 9559
path = "C:\\Users\\Federico\\Desktop\\"

p = ALProxy("ALVideoDevice", IP, Port)

resolution = 2  # VGA, vision_definitions.kQVGA
colorspace = 11 # RGB, vision_definitions.kYUVcolorSpace
fps = 30

nameId = p.subscribe("python_GVM", resolution, colorspace, fps)

image = p.getImageRemote(nameId)
p.releaseImage(nameId)
p.unsubscribe(nameId)

image_width = image[0]
image_height = image[1]
array = image[6]

# Usa PIL
im = Image.fromstring("RGB", (image_width, image_height), array)
im.save(path + "image.png", "PNG")
