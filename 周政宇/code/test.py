import os
import cv2
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score, recall_score, f1_score
import segmentation_models_pytorch as smp
from torch.utils.data import DataLoader

# 导入train.py中的必要组件
from train import Config, DRExudatesDataset, get_transforms, dice_coefficient

DATA_ROOT = './' 


# 扩展配置以包含测试相关参数
class TestConfig(Config):
    TEST_BATCH_SIZE = 4
    RESULT_DIR = os.path.join(DATA_ROOT, 'test_results')
    OVERLAY_ALPHA = 0.4  # 用于叠加显示的透明度
    
    # 创建结果目录
    os.makedirs(RESULT_DIR, exist_ok=True)

cfg = TestConfig()

def load_model(checkpoint_path):
    """加载训练好的模型"""
    model = smp.UnetPlusPlus(
        encoder_name=cfg.ENCODER,
        encoder_weights=None,  # 测试时不需要预训练权重
        in_channels=3,
        classes=cfg.NUM_CLASSES,
        activation=None
    )
    
    model.load_state_dict(torch.load(checkpoint_path))
    model.to(cfg.DEVICE)
    model.eval()
    
    return model

def denormalize(tensor):
    """将归一化后的图像张量转换回原始RGB图像"""
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(tensor.device)
    std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(tensor.device)
    return tensor * std + mean

def predict_single_image(model, image_path, save_path=None):
    """对单张图像进行预测并可视化结果"""
    # 读取图像
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 应用变换
    transform = get_transforms("valid")
    transformed = transform(image=image)
    input_tensor = transformed["image"].unsqueeze(0).to(cfg.DEVICE)
    
    # 进行预测
    with torch.no_grad():
        output = model(input_tensor)
        pred_mask = torch.sigmoid(output) > 0.5
    
    # 将预测结果转换为NumPy数组
    pred_mask = pred_mask.cpu().numpy().squeeze()
    
    # 可视化结果
    plt.figure(figsize=(15, 5))
    
    # 原始图像
    plt.subplot(1, 3, 1)
    plt.title('Original Image')
    plt.imshow(image)
    plt.axis('off')
    
    # 预测掩码
    plt.subplot(1, 3, 2)
    plt.title('Predicted Mask')
    plt.imshow(pred_mask, cmap='gray')
    plt.axis('off')
    
    # 叠加效果
    plt.subplot(1, 3, 3)
    plt.title('Overlay')
    plt.imshow(image)
    plt.imshow(pred_mask, cmap='hot', alpha=cfg.OVERLAY_ALPHA)
    plt.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
        print(f"预测结果已保存到: {save_path}")
    else:
        plt.show()
    
    plt.close()
    
    return pred_mask

def test_batch(model, test_loader, num_samples=4):
    """测试一批图像并可视化结果"""
    # 获取单批次数据
    images, masks = next(iter(test_loader))
    images = images[:num_samples].to(cfg.DEVICE)
    masks = masks[:num_samples]
    
    # 进行预测
    with torch.no_grad():
        outputs = model(images)
        pred_masks = torch.sigmoid(outputs) > 0.5
    
    # 反归一化图像
    images_np = denormalize(images).cpu().numpy().transpose(0, 2, 3, 1)
    masks_np = masks.cpu().numpy().squeeze()
    pred_masks_np = pred_masks.cpu().numpy().squeeze()
    
    # 可视化
    fig, axes = plt.subplots(num_samples, 3, figsize=(15, num_samples * 5))
    
    for i in range(num_samples):
        # 原图
        axes[i, 0].imshow(images_np[i])
        axes[i, 0].set_title('Original Image')
        axes[i, 0].axis('off')
        
        # 真实掩码
        axes[i, 1].imshow(masks_np[i], cmap='gray')
        axes[i, 1].set_title('Ground Truth')
        axes[i, 1].axis('off')
        
        # 预测掩码
        axes[i, 2].imshow(pred_masks_np[i], cmap='gray')
        axes[i, 2].set_title('Prediction')
        axes[i, 2].axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(cfg.RESULT_DIR, 'batch_predictions.png'))
    print(f"批量预测结果已保存到: {os.path.join(cfg.RESULT_DIR, 'batch_predictions.png')}")
    plt.close()

def evaluate_model(model, test_loader):
    """评估模型在测试集上的性能"""
    dice_scores = []
    precisions = []
    recalls = []
    f1_scores = []
    
    with torch.no_grad():
        for images, masks in tqdm(test_loader, desc="Evaluating"):
            images = images.to(cfg.DEVICE)
            masks = masks.to(cfg.DEVICE)
            
            outputs = model(images)
            pred_masks = torch.sigmoid(outputs) > 0.5
            
            # 计算Dice系数
            batch_dice = dice_coefficient(masks, pred_masks).item()
            dice_scores.append(batch_dice)
            
            # 计算其他指标
            masks_flat = masks.cpu().numpy().flatten()
            preds_flat = pred_masks.cpu().numpy().flatten()
            
            precisions.append(precision_score(masks_flat, preds_flat, zero_division=1))
            recalls.append(recall_score(masks_flat, preds_flat, zero_division=1))
            f1_scores.append(f1_score(masks_flat, preds_flat, zero_division=1))
    
    # 计算平均值
    avg_dice = np.mean(dice_scores)
    avg_precision = np.mean(precisions)
    avg_recall = np.mean(recalls)
    avg_f1 = np.mean(f1_scores)
    
    print(f"测试集结果:")
    print(f"平均Dice系数: {avg_dice:.4f}")
    print(f"平均精确率: {avg_precision:.4f}")
    print(f"平均召回率: {avg_recall:.4f}")
    print(f"平均F1分数: {avg_f1:.4f}")
    
    # 绘制直方图
    plt.figure(figsize=(10, 6))
    plt.hist(dice_scores, bins=20, alpha=0.7)
    plt.title('Dice Coefficient Distribution')
    plt.xlabel('Dice Coefficient')
    plt.ylabel('Count')
    plt.grid(alpha=0.3)
    plt.axvline(avg_dice, color='r', linestyle='--', label=f'Mean: {avg_dice:.4f}')
    plt.legend()
    plt.savefig(os.path.join(cfg.RESULT_DIR, 'dice_distribution.png'))
    plt.close()
    
    return {
        'dice': avg_dice,
        'precision': avg_precision,
        'recall': avg_recall,
        'f1': avg_f1
    }

def generate_error_analysis(model, test_loader):
    """生成错误分析可视化，找出模型表现最好和最差的样本"""
    results = []
    img_paths = []
    
    # 收集所有测试样本的结果
    with torch.no_grad():
        for idx, (images, masks) in enumerate(tqdm(test_loader, desc="Collecting results")):
            images = images.to(cfg.DEVICE)
            masks = masks.to(cfg.DEVICE)
            
            outputs = model(images)
            pred_masks = torch.sigmoid(outputs) > 0.5
            
            for i in range(images.shape[0]):
                dice = dice_coefficient(masks[i:i+1], pred_masks[i:i+1]).item()
                results.append({
                    'idx': idx * test_loader.batch_size + i,
                    'dice': dice,
                    'image': images[i].cpu(),
                    'mask': masks[i].cpu(),
                    'pred': pred_masks[i].cpu()
                })
    
    # 按Dice系数排序
    results.sort(key=lambda x: x['dice'])
    
    # 选择最差的3个样本和最好的3个样本
    worst_samples = results[:3]
    best_samples = results[-3:]
    
    # 可视化
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # 最差的样本
    for i, sample in enumerate(worst_samples):
        img = denormalize(sample['image'].unsqueeze(0)).squeeze().permute(1, 2, 0).numpy()
        mask = sample['mask'].squeeze().numpy()
        pred = sample['pred'].squeeze().numpy()
        
        # 计算并叠加错误区域（红色：假阳性，蓝色：假阴性）
        error_map = np.zeros((*mask.shape, 3), dtype=np.float32)
        error_map[pred > mask, 0] = 1  # 假阳性标红
        error_map[pred < mask, 2] = 1  # 假阴性标蓝
        
        axes[0, i].imshow(img)
        axes[0, i].imshow(error_map, alpha=0.5)
        axes[0, i].set_title(f"Worst #{i+1}, Dice={sample['dice']:.4f}")
        axes[0, i].axis('off')
    
    # 最好的样本
    for i, sample in enumerate(best_samples):
        img = denormalize(sample['image'].unsqueeze(0)).squeeze().permute(1, 2, 0).numpy()
        mask = sample['mask'].squeeze().numpy()
        pred = sample['pred'].squeeze().numpy()
        
        # 同样显示错误区域，但预期很少
        error_map = np.zeros((*mask.shape, 3), dtype=np.float32)
        error_map[pred > mask, 0] = 1
        error_map[pred < mask, 2] = 1
        
        axes[1, i].imshow(img)
        axes[1, i].imshow(error_map, alpha=0.5)
        axes[1, i].set_title(f"Best #{i+1}, Dice={sample['dice']:.4f}")
        axes[1, i].axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(cfg.RESULT_DIR, 'error_analysis.png'))
    print(f"错误分析结果已保存到: {os.path.join(cfg.RESULT_DIR, 'error_analysis.png')}")
    plt.close()

def create_overlay_comparison(model, test_loader, num_samples=6):
    """创建原图-叠加展示比较"""
    all_images = []
    all_masks = []
    all_preds = []
    
    # 收集多个批次的图像
    with torch.no_grad():
        for images, masks in test_loader:
            if len(all_images) * test_loader.batch_size + len(images) > num_samples:
                # 只取需要的数量
                remaining = num_samples - len(all_images) * test_loader.batch_size
                if remaining <= 0:
                    break
                images = images[:remaining]
                masks = masks[:remaining]
            
            images = images.to(cfg.DEVICE)
            outputs = model(images)
            pred_masks = torch.sigmoid(outputs) > 0.5
            
            all_images.append(denormalize(images).cpu())
            all_masks.append(masks)
            all_preds.append(pred_masks.cpu())
            
            if len(all_images) * test_loader.batch_size >= num_samples:
                break
    
    # 拼接所有批次的结果
    all_images = torch.cat(all_images, dim=0)[:num_samples]
    all_masks = torch.cat(all_masks, dim=0)[:num_samples]
    all_preds = torch.cat(all_preds, dim=0)[:num_samples]
    
    # 转换为numpy数组用于绘图
    images_np = all_images.numpy().transpose(0, 2, 3, 1)
    masks_np = all_masks.numpy().squeeze()
    preds_np = all_preds.numpy().squeeze()
    
    # 计算每行显示的图像数量
    cols = 3
    rows = (num_samples + cols - 1) // cols
    
    # 创建画布
    fig, axes = plt.subplots(rows, cols * 2, figsize=(cols * 5, rows * 4))
    
    for i in range(num_samples):
        row = i // cols
        col = (i % cols) * 2
        
        # 原图
        axes[row, col].imshow(images_np[i])
        axes[row, col].set_title(f"Image {i+1}")
        axes[row, col].axis('off')
        
        # 叠加效果（真实掩码与预测掩码的对比）
        axes[row, col+1].imshow(images_np[i])
        
        # 创建颜色编码的叠加层:
        # - 绿色: 真实掩码和预测掩码都为1（正确预测的病变）
        # - 红色: 只有预测掩码为1（假阳性）
        # - 蓝色: 只有真实掩码为1（假阴性）
        overlay = np.zeros((*images_np[i].shape[:2], 4))
        
        # 正确预测的区域 (真阳性) - 绿色
        overlay[..., 1][np.logical_and(masks_np[i] == 1, preds_np[i] == 1)] = 1
        overlay[..., 3][np.logical_and(masks_np[i] == 1, preds_np[i] == 1)] = 0.7
        
        # 假阳性 - 红色
        overlay[..., 0][np.logical_and(masks_np[i] == 0, preds_np[i] == 1)] = 1
        overlay[..., 3][np.logical_and(masks_np[i] == 0, preds_np[i] == 1)] = 0.7
        
        # 假阴性 - 蓝色
        overlay[..., 2][np.logical_and(masks_np[i] == 1, preds_np[i] == 0)] = 1
        overlay[..., 3][np.logical_and(masks_np[i] == 1, preds_np[i] == 0)] = 0.7
        
        axes[row, col+1].imshow(overlay)
        axes[row, col+1].set_title(f"Overlay (G=TP, R=FP, B=FN)")
        axes[row, col+1].axis('off')
    
    # 移除多余的空子图
    for i in range(num_samples, rows * cols):
        row = i // cols
        col = (i % cols) * 2
        if col < axes.shape[1]:
            axes[row, col].axis('off')
            axes[row, col+1].axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(cfg.RESULT_DIR, 'overlay_comparison.png'))
    print(f"叠加比较结果已保存到: {os.path.join(cfg.RESULT_DIR, 'overlay_comparison.png')}")
    plt.close()

def main():
    # 读取CSV文件
    df = pd.read_csv(cfg.CSV_FILE, header=None)
    df.columns = ['image', 'mask']
    
    # 为了演示效果，使用部分数据作为测试集
    from sklearn.model_selection import train_test_split
    _, test_df = train_test_split(df, test_size=0.2, random_state=42)
    print(f"测试集数量: {len(test_df)} 样本")
    
    # 加载测试集
    test_dataset = DRExudatesDataset(test_df, transforms=get_transforms("valid"))
    test_loader = DataLoader(
        test_dataset,
        batch_size=cfg.TEST_BATCH_SIZE,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    # 加载训练好的模型
    model_path = os.path.join(cfg.CHECKPOINT_DIR, 'best_model.pth')
    if not os.path.exists(model_path):
        print(f"错误: 找不到模型文件 {model_path}")
        return
    
    model = load_model(model_path)
    print(f"模型已加载: {model_path}")
    
    # 显示一些随机样本的预测结果
    print("生成批量预测可视化...")
    test_batch(model, test_loader)
    
    # 定量评估模型性能
    print("评估模型性能...")
    metrics = evaluate_model(model, test_loader)
    
    # 生成错误分析
    print("生成错误分析...")
    generate_error_analysis(model, test_loader)
    
    # 创建叠加图像比较
    print("创建叠加比较可视化...")
    create_overlay_comparison(model, test_loader)
    
    # 对特定图像进行测试 (如果需要)
    # 找到图像列表中的第一个文件
    if len(test_df) > 0:
        sample_img = os.path.join(cfg.DATA_ROOT, test_df.iloc[0]['image'])
        print(f"对单张图像进行预测: {sample_img}")
        predict_single_image(
            model, 
            sample_img, 
            os.path.join(cfg.RESULT_DIR, 'single_prediction.png')
        )
    
    print(f"所有测试结果已保存到: {cfg.RESULT_DIR}")
    
    # 将测试结果保存为文本文件
    with open(os.path.join(cfg.RESULT_DIR, 'test_results.txt'), 'w') as f:
        f.write("测试集评估结果:\n")
        f.write(f"样本数量: {len(test_df)}\n")
        f.write(f"平均Dice系数: {metrics['dice']:.4f}\n")
        f.write(f"平均精确率: {metrics['precision']:.4f}\n")
        f.write(f"平均召回率: {metrics['recall']:.4f}\n")
        f.write(f"平均F1分数: {metrics['f1']:.4f}\n")

if __name__ == "__main__":
    main()
