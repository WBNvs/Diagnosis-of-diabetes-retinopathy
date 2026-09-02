import os
from PIL import Image, ImageEnhance
import random
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.ndimage import median_filter

# 再次修改相关参数
SPARSITY = 0.1    # 稀疏噪声参数
MAX_ANGLE = 60    # 最大旋转角度
RANDOM_PROBABILITY = 0.5    # 随机数据强化操作概率
SIGMA = 3    # 扩大布针参数（扩大标准差）
RADIUS = 8    # 扩大布针参数（扩大半径）

def random_brightness_batch(images, low=0.5, high=1.5):
    enhanced_images = []
    x = random.uniform(low, high)
    for img in images:
        enhanced_img = ImageEnhance.Brightness(img).enhance(x)
        enhanced_images.append(enhanced_img)
    return enhanced_images

def random_contrast_batch(images, low=0.5, high=1.5):
    enhanced_images = []
    x = random.uniform(low, high)
    for img in images:
        enhanced_img = ImageEnhance.Contrast(img).enhance(x)
        enhanced_images.append(enhanced_img)
    return enhanced_images

def random_color_batch(images, low=0.5, high=1.5):
    enhanced_images = []
    x = random.uniform(low, high)
    for img in images:
        enhanced_img = ImageEnhance.Color(img).enhance(x)
        enhanced_images.append(enhanced_img)
    return enhanced_images

def random_sharpness_batch(images, low=0.5, high=1.5):
    enhanced_images = []
    x = random.uniform(low, high)
    for img in images:
        enhanced_img = ImageEnhance.Sharpness(img).enhance(x)
        enhanced_images.append(enhanced_img)
    return enhanced_images

def random_rotate_batch(images, low=-MAX_ANGLE, high=MAX_ANGLE):
    enhanced_images = []

    # 生成随机旋转角度
    angle = random.randint(low, high)

    for img in images:
        # 获取原图尺寸
        original_size = img.size

        # 获取左上角像素的值
        top_left_pixel = img.getpixel((0, 0))

        # 获取图片种类
        mode = img.mode

        # 旋转图片，expand=True 使图片大小适应旋转后可能的最大尺寸
        rotated_img = img.rotate(angle, expand=True, fillcolor=top_left_pixel)

        # 创建一个与原图大小相同的黑色背景图片
        background = Image.new(mode=mode, size=original_size, color=top_left_pixel)

        # 将旋转后的图片粘贴到黑色背景图片的中心
        offset = ((original_size[0] - rotated_img.size[0]) // 2, (original_size[1] - rotated_img.size[1]) // 2)
        background.paste(rotated_img, offset)

        enhanced_images.append(background)

    return enhanced_images

# def random_noise_batch(images, low=0, high=10, sparsity=SPARSITY):
#     enhanced_images = []
#     img = np.asarray(images[0])
#
#     sigma = np.random.uniform(low, high)
#     noise = np.random.randn(img.shape[0], img.shape[1]) * sigma
#     # noise_RGB = np.random.randn(img.shape[0], img.shape[1], 3) * sigma
#
#     # 生成稀疏掩码
#     mask = np.random.choice([0, 1], size=img.shape, p=[1 - sparsity, sparsity])
#     # mask_RGB = np.stack([mask] * 3, axis=-1)
#
#     # 应用掩码到噪声，使得只有部分像素添加噪声
#     sparse_noise = noise * mask
#     sparse_noise_RGB = np.stack([sparse_noise] * 3, axis=-1)
#     # sparse_noise_RGB = noise_RGB * mask_RGB
#
#     for img in images:
#         # 获取图片种类
#         mode = img.mode
#
#         img = np.asarray(img)
#
#         if mode == "L":
#             img = img + np.round(sparse_noise).astype('uint8')
#         else:
#             img = img + np.round(sparse_noise_RGB).astype('uint8')
#
#         img[img > 255], img[img < 0] = 255, 0
#         img = Image.fromarray(img)
#         enhanced_images.append(img)
#
#     return enhanced_images

def random_noise_batch(images, low=0, high=10, sparsity=0.1):
    enhanced_images = []
    # 假设所有图像都是RGB格式，直接处理
    for img in images:
        img = np.asarray(img)
        # 确保图像是RGB格式
        if len(img.shape) != 3 or img.shape[2] != 3:
            raise ValueError("Image is not in RGB format")

        # 生成随机噪声
        sigma = np.random.uniform(low, high)
        noise = np.random.randn(img.shape[0], img.shape[1]) * sigma

        # 生成稀疏掩码
        mask = np.random.choice([0, 1], size=img.shape[:2], p=[1 - sparsity, sparsity])

        # 将掩码扩展到RGB三个通道
        mask_rgb = np.stack([mask] * 3, axis=-1)

        # 应用掩码到噪声
        sparse_noise_rgb = noise[:, :, np.newaxis] * mask_rgb

        # 添加噪声到图像
        img = img + np.round(sparse_noise_rgb).astype('uint8')

        # 限制像素值在0-255范围内
        img = np.clip(img, 0, 255)

        # 转换回PIL图像
        img = Image.fromarray(img)
        enhanced_images.append(img)

    return enhanced_images

def image_augment(images, prob=RANDOM_PROBABILITY):
    post_images = images

    opts = [random_rotate_batch, random_brightness_batch, random_contrast_batch, random_color_batch, random_sharpness_batch, random_noise_batch]
    # random.shuffle(opts)
    for opt in opts:
        post_images = opt(post_images) if random.random() < prob else post_images
    return post_images

def pre_process(image_ways, save_path = ""):
    images = []

    # 打开图片
    for image_way in image_ways:
        try:
            images.append(Image.open(image_way))
        except FileNotFoundError:
            print(f"{image_way}:Image not found")
            return
    if save_path != "":
        # 获取当前脚本所在目录
        script_directory = os.path.dirname(__file__)

        # 定义要保存的文件夹
        save_directory = os.path.join(script_directory, "processed_images")

        # 如果文件夹不存在，创建它
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

    # 预处理
    post_images = image_augment(images)     # 只选其中某几个随机操作执行

    # 保存处理后的图片为 PNG 格式
    if save_path != "":
        i = 1
        for image in images:
            image.save(f"{save_path}-{i}.png")
            i += 1

    # 关闭图片
    for image in images:
        image.close()

    return post_images

def image_cut(images, save_paths, crop_area=(165, 165, 350, 350)):
    # 检查输入列表是否为空
    if not images:
        print("No images to process.")
        return
    if not save_paths:
        print("No save paths provided.")
        return
    # if len(images) != len(save_paths):
    #     print("Number of images and save paths do not match.")
    #     return

    for image in images:
        try:
            # 裁切图片(先不裁切)
            #cropped_image = image.crop(crop_area)
            cropped_image = image

            # 保存处理后的图片
            cropped_image.save(save_paths[0])

            # 关闭图片
            image.close()
        except Exception as e:
            print(f"Error processing image {image.filename}: {e}")

def gaussian(x, mu, sigma):
    return 1 / (np.exp((x - mu)**2 / (2 * sigma**2)))

# def preprocess_white_point(image_way, file_name="processed_image.png", sigma = 4, radius = 9, middle_pixel_value = 127):
#     # 打开图片
#     try:
#         image = Image.open(image_way)
#     except FileNotFoundError:
#         print(f"{image_way}:Image not found")
#         return
#
#     # 获取当前脚本所在目录
#     script_directory = os.path.dirname(__file__)
#
#     # 定义要保存的文件夹
#     save_directory = os.path.join(script_directory, "expanded_images")
#
#     # 如果文件夹不存在，创建它
#     if not os.path.exists(save_directory):
#         os.makedirs(save_directory)
#
#     # 构建保存路径
#     save_path = os.path.join(save_directory, file_name)
#
#     # 将图片转换为灰度
#     gray_image = image.convert("L")
#
#     # 复制一份图片
#     expanded_image = gray_image.copy()
#
#     # 获取图片的宽度和高度
#     width, height = gray_image.size
#     print(width, height)
#
#     # 遍历所有像素
#     for center_y in range(height):
#         for center_x in range(width):
#             # 获取像素值
#             pixel_value = gray_image.getpixel((center_x, center_y))
#
#             # 扩大白色区域
#             if pixel_value >= 250:
#                 for y in range(center_y - radius, center_y + radius + 1):
#                     for x in range(center_x - radius, center_x + radius + 1):
#                         if gray_image.getpixel((x, y)) == middle_pixel_value:
#                             r = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
#                             if r <= radius:
#                                 new_value = (pixel_value - middle_pixel_value) * gaussian(r, 0, sigma) + middle_pixel_value
#                                 expanded_image.putpixel((x, y), int(new_value))
#
#     # 保存处理后的图片为 PNG 格式
#     expanded_image.save(save_path)
#
#     # 关闭图片
#     gray_image.close()
#
#     return expanded_image

if __name__ == "__main__":
    # sigma = SIGMA
    # radius = RADIUS

    #"C:\Users\I750014\Documents\DR_project\DDR dataset\DDR-dataset\DDR-dataset\lesion_segmentation\train\image"
    # 指定图片文件夹路径
    input_folder = "./DDR dataset/DDR-dataset/DDR-dataset/lesion_segmentation/train/image/"
    output_folder = "./DDR dataset/DDR-dataset/DDR-dataset/lesion_segmentation/train/processed_images"

    # 如果输出文件夹不存在，则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 获取文件夹中所有图片文件的路径
    image_files = [f for f in os.listdir(input_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

    for image_file in image_files:
        # 构造输入和输出路径
        image_path = os.path.join(input_folder, image_file)
        save_path = os.path.join(output_folder, image_file)

        # 处理图片
        result_images = pre_process([image_path])
        image_cut(result_images, save_paths=[save_path])

