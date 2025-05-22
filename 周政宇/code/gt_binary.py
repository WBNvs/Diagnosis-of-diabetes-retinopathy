#!/usr/bin/env python

from PIL import Image

# from resizeimage import resizeimage
import os, sys

def resizeImage(infile, output_dir="", size=(4288,2848)):
     outfile = os.path.splitext(infile)[0]
     extension = os.path.splitext(infile)[1]

     if extension != ".tif":
        return

     infile_path = os.path.join(input_dir, infile)

     if infile != outfile:
        try :
            im = Image.open(infile_path)
            gray = im.convert('L')
            bw = gray.point(lambda x: 0 if x<50 else 255, '1')
            # im = resizeimage.resize_cover(im, [960, 640])
            bw.save(output_dir+outfile+extension,"JPEG",quality=100)
        except IOError:
            print ("cannot reduce image for ", infile)
    
     print("resized image for ", infile)


if __name__=="__main__":
    output_dir = "training_set/"
    dir = os.getcwd()
    input_dir = os.path.join(os.getcwd(), "mask")

    if not os.path.exists(os.path.join(dir,output_dir)):
        os.mkdir(output_dir)

    for file in os.listdir(input_dir):
        resizeImage(file,output_dir)