from PIL import Image
import numpy as np
import cv2

# 读取TIFF格式的掩码
mask_path = '/root/autodl-tmp/ex/mask/IDRiD_01_EX.tif'
mask = Image.open(mask_path).convert('L')  # 转为灰度图像

# 将掩码转换为NumPy数组
mask = np.array(mask)

# 打印唯一像素值
unique_values = np.unique(mask)
print(f"Unique values in mask: {unique_values}")

# 改进的二值化方法，将所有非零像素设置为1
binary_mask = np.where(mask > 0, 1, 0).astype(np.uint8)

# 检查是否为全黑掩码
if np.sum(binary_mask) == 0:
    print(f"Mask is completely black for {mask_path}")
else:
    print(f"Mask has non-zero values for {mask_path}")
