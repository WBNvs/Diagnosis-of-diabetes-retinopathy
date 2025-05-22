from PIL import Image
import numpy as np

img = Image.open("/root/autodl-tmp/ex/images/IDRiD_01.jpg")
mask = Image.open("/root/autodl-tmp/ex/mask/IDRiD_01_EX.tif")

print("image shape:", np.array(img).shape)   # 应该是 (H, W, 3)
print("mask shape:", np.array(mask).shape)   # 应该是 (H, W) 或 (H, W, 1)
mask_np = np.array(Image.open("/root/autodl-tmp/ex/mask/IDRiD_01_EX.tif"))
print("mask max:", np.max(mask_np))
print("mask unique values:", np.unique(mask_np))
dataset = get_image_mask("train.csv")
for image, mask in dataset.take(1):
    print("image shape:", image.shape)
    print("mask shape:", mask.shape)
