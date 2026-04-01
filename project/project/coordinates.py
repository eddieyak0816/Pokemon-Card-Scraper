try:
    import matplotlib.pyplot as plt
except:
    os.system("pip install matplotlib")
    import matplotlib.pyplot as plt
try:
    import numpy as np
except:
    os.system("pip install opencv-python")
    import numpy as np
try:
    import easyocr
except:
    os.system("pip install easyocr")
    import easyocr
try:
    import argparse
except:
    os.system("pip install argparse")
try:
    import cv2
except:
    os.system("pip install opencv-python")


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image")
ap.add_argument("-l", "--Location", required=True,
	help="Location of the card no, if on right side enter 'r' else on left enter 'l' for Left")
args = vars(ap.parse_args())
reader = easyocr.Reader(['en'])
img = cv2.imread(args["image"],0)
location=args['Location']

#img=cv2.imread('poki5.png',0)
#img2=cv2.imread('poki9.png')
#location=args['Location']
y,x=img.shape
Y=int(y*0.2)
X=int(x/1.8)

img1= img[40:Y, 0:X]
#cv2_imshow(img1)

output = reader.readtext(img1)

y,x=img.shape
x=int(x/3)

if( location=='r' or location=='l'):
  if(location=='r'):
    imggg= img[952:1000,550:]
    #cv2_imshow(imggg)
  elif(location=='l'):
    imggg= img[955:,100:x]
    #cv2_imshow(imggg)
else:
    print('Wronge location')
    exit()


output2 = reader.readtext(imggg)


str2 = output[1][1]
try:
  strrr2 = output[2][1]
  name2=str2+strrr2
  print('Card Name : ',name2)
except:
  print('Card Name : ',str2)

print('Card No :',output2[0][1])

#if(output2[0][1]):
