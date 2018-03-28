
# Funzioni utilizzate spesso in questi script

def toRelative(alpha, beta,
               width = 640.0, height = 480.0,
               fovx = 60.9, fovy = 47.6):

    cx = -(width * alpha / math.radians(fovx)) + width/2
    cy = (height * beta / math.radians(fovy)) + height/2
    return (int(cx), int(cy))

def drawPointFromAngles(image, alpha, beta, color = (0, 0, 255, 0),
                           width = 640.0, height = 480.0,
                           fovx = 60.9, fovy = 47.6):

    cx = -(width * alpha / math.radians(fovx)) + width/2
    cy = (height * beta / math.radians(fovy)) + height/2
            
    cv.Circle(image, (int(cx), int(cy)), 1, color, 2)
    pass

