import os
from PIL import Image

# 获取当前目录下的 labels 文件夹路径
labels_dir = os.path.join(os.getcwd(), 'labels')

# 检查 labels 文件夹是否存在
if not os.path.exists(labels_dir):
    print(f"目录 {labels_dir} 不存在")
else:
    # 遍历 labels 文件夹中的所有文件
    for filename in os.listdir(labels_dir):
        if filename.endswith('.tif'):
            tif_path = os.path.join(labels_dir, filename)
            jpg_path = os.path.join(labels_dir, os.path.splitext(filename)[0] + '.jpg')
            
            # 打开 .tif 文件并转换为 .jpg 格式
            try:
                with Image.open(tif_path) as img:
                    # 转换模式：通常医学图像建议转为 'L' (灰度)，如果是彩色图则转为 'RGB'
                    img = img.convert("RGB")  # 或者 img.convert("L")
                    img.save(jpg_path, 'JPEG')
                print(f"已转换: {filename} -> {os.path.basename(jpg_path)}")
            except Exception as e:
                print(f"转换 {filename} 时出错: {e}")
