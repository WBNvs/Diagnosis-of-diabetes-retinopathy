from PIL import Image
# from resizeimage import resizeimage
import os, sys
import numpy as np

dir = os.getcwd()
output_dir_data = "patches/"
output_dir_mask = "labels/"
if not os.path.exists(os.path.join(dir,output_dir_data)):
    os.mkdir(output_dir_data)
if not os.path.exists(os.path.join(dir,output_dir_mask)):
    os.mkdir(output_dir_mask)

dir_data = os.path.join(dir,"images/")
dir_mask = os.path.join(dir,"mask/")

# im = Image.open(os.path.join(dir_mask,"IDRiD_06.tif"))
# im_crop = im.crop((2000,0,2000+512,0+256))
# im_crop.show()
# image_np = np.array(im_crop)
# print np.sum(image_np)

negative_patches = []
positive_count = 0

for file in os.listdir(dir_mask):
    outfile = os.path.splitext(file)[0]
    extension = os.path.splitext(file)[1]
    if extension != ".tif":
        continue

    # 构造对应的原始图像文件路径
    image_file = outfile.replace("_EX", "") + ".jpg"
    if not os.path.exists(os.path.join(dir_data, image_file)):
        print(f"Warning: Corresponding image file {image_file} not found for mask {file}")
        continue

    im = Image.open(os.path.join(dir_mask,file))
    imd = Image.open(os.path.join(dir_data,image_file))
    # image_np = np.array(im)
    # print np.sum([True, True])
    # im_crop = im.crop((1900,0,1900+512,0+512))
    patch_id = 0
    for i in range(10):
    	for j in range(16):
            top_y = i*256
            if (i==9):
                top_y = 2336
            top_x = j*256
            if (j==15):
                top_x = 3776

            im_crop = im.crop((top_x,top_y,top_x+512,top_y+512))
            imd_crop = imd.crop((top_x,top_y,top_x+512,top_y+512))

            im_crop.save(os.path.join(output_dir_mask, f"{outfile}_p{patch_id}.tif"), "TIFF", quality=100)
            imd_crop.save(os.path.join(output_dir_data, f"{outfile}_p{patch_id}.jpg"), "JPEG", quality=100)
            
            if (np.sum(np.array(im_crop)) < 100):
                negative_patches.append(output_dir_mask+outfile+"_p"+str(patch_id)+extension)
            else:
                positive_count += 1

            patch_id += 1

negative_patches = np.array(negative_patches)
# np.savetxt("negative.csv", negative_patches, delimiter=",", fmt="%s")

negative_count = negative_patches.size
delete_count = negative_count - 4*positive_count
np.random.shuffle(negative_patches)
delete_patches = negative_patches[:delete_count]

for patch_path in delete_patches:
    os.remove(patch_path)
    os.remove(os.path.join(output_dir_data, os.path.basename(patch_path).replace(".tif", ".jpg")))