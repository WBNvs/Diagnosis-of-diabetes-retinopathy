import os
import cv2
import torch
import random
import numpy as np
import pandas as pd
from tqdm import tqdm
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import albumentations as A
from albumentations.pytorch import ToTensorV2
import segmentation_models_pytorch as smp
from torch.utils.tensorboard import SummaryWriter
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# 设置随机种子，确保结果可复现
def set_seed(seed=42):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

set_seed()

# 配置参数
class Config:
    DATA_ROOT = '/root/autodl-tmp/ex/'
    CSV_FILE = os.path.join(DATA_ROOT, 'train.csv')
    BATCH_SIZE = 8
    IMAGE_SIZE = 512
    EPOCHS = 10
    LEARNING_RATE = 1e-4
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
    ENCODER = 'efficientnet-b3'
    ENCODER_WEIGHTS = 'imagenet'
    NUM_CLASSES = 1  # 二分类任务
    EARLY_STOPPING_PATIENCE = 10
    CHECKPOINT_DIR = os.path.join(DATA_ROOT, 'checkpoints')
    LOG_DIR = os.path.join(DATA_ROOT, 'logs')

    # 创建目录
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

cfg = Config()

# 数据增强策略
def get_transforms(phase):
    if phase == "train":
        return A.Compose([
            A.Resize(height=cfg.IMAGE_SIZE, width=cfg.IMAGE_SIZE),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.1, rotate_limit=15, p=0.5),
            A.OneOf([
                A.GridDistortion(p=1.0),
                A.ElasticTransform(p=1.0)
            ], p=0.25),
            A.RandomBrightnessContrast(p=0.5),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2(),
        ])
    else:  # valid or test
        return A.Compose([
            A.Resize(height=cfg.IMAGE_SIZE, width=cfg.IMAGE_SIZE),
            A.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
            ToTensorV2(),
        ])

# 自定义数据集类
class DRExudatesDataset(Dataset):
    def __init__(self, df, transforms=None):
        self.df = df
        self.transforms = transforms
        self.data_root = cfg.DATA_ROOT

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = os.path.join(self.data_root, row['image'])
        mask_path = os.path.join(self.data_root, row['mask'])
        
        # 读取图像和掩码
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        # 转换掩码为二值图像
        # 将所有非零像素设置为1，0保持为0
        mask = np.where(mask > 0, 1, 0).astype(np.uint8)
        
        # 应用数据增强
        if self.transforms:
            augmented = self.transforms(image=image, mask=mask)
            image = augmented['image']
            mask = augmented['mask'].unsqueeze(0).float()
        
        return image, mask

# 定义损失函数
class DiceBCEFocalLoss(nn.Module):
    def __init__(self, weight=None, size_average=True):
        super(DiceBCEFocalLoss, self).__init__()
        self.bce_loss = nn.BCEWithLogitsLoss(weight=weight)
        self.dice_loss = smp.losses.DiceLoss(mode='binary')
        self.focal_loss = smp.losses.FocalLoss(mode='binary')
        
    def forward(self, inputs, targets):
        bce = self.bce_loss(inputs, targets)
        dice = self.dice_loss(inputs, targets)
        focal = self.focal_loss(inputs, targets)
        return bce * 0.3 + dice * 0.4 + focal * 0.3

# 指标评估函数
def dice_coefficient(y_true, y_pred):
    smooth = 1e-6
    y_true_f = y_true.view(-1)
    y_pred_f = y_pred.view(-1)
    intersection = torch.sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (torch.sum(y_true_f) + torch.sum(y_pred_f) + smooth)

# 训练一个epoch的函数
def train_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    dice_score = 0
    pbar = tqdm(loader, desc='Training')
    
    for images, masks in pbar:
        images = images.to(device)
        masks = masks.to(device)
        
        # 前向传播
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, masks)
        
        # 反向传播
        loss.backward()
        optimizer.step()
        
        # 计算Dice系数
        with torch.no_grad():
            pred_masks = torch.sigmoid(outputs) > 0.5
            batch_dice = dice_coefficient(masks, pred_masks)
            
        total_loss += loss.item() * images.size(0)
        dice_score += batch_dice.item() * images.size(0)
        pbar.set_postfix({'Loss': loss.item(), 'Dice': batch_dice.item()})
    
    return total_loss / len(loader.dataset), dice_score / len(loader.dataset)

# 验证一个epoch的函数
def valid_epoch(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    dice_score = 0
    
    with torch.no_grad():
        pbar = tqdm(loader, desc='Validation')
        for images, masks in pbar:
            images = images.to(device)
            masks = masks.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, masks)
            
            pred_masks = torch.sigmoid(outputs) > 0.5
            batch_dice = dice_coefficient(masks, pred_masks)
            
            total_loss += loss.item() * images.size(0)
            dice_score += batch_dice.item() * images.size(0)
            pbar.set_postfix({'Loss': loss.item(), 'Dice': batch_dice.item()})
    
    return total_loss / len(loader.dataset), dice_score / len(loader.dataset)

# 主训练函数
def train():
    print(f"Using device: {cfg.DEVICE}")
    
    # 读取CSV文件
    df = pd.read_csv(cfg.CSV_FILE, header=None)
    df.columns = ['image', 'mask']
    
    # 划分训练集和验证集
    train_df, valid_df = train_test_split(df, test_size=0.2, random_state=42)
    print(f"Training set: {len(train_df)} samples")
    print(f"Validation set: {len(valid_df)} samples")
    
    # 创建数据加载器
    train_dataset = DRExudatesDataset(train_df, transforms=get_transforms("train"))
    valid_dataset = DRExudatesDataset(valid_df, transforms=get_transforms("valid"))
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=cfg.BATCH_SIZE,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    
    valid_loader = DataLoader(
        valid_dataset,
        batch_size=cfg.BATCH_SIZE,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    # 创建模型
    model = smp.UnetPlusPlus(
        encoder_name=cfg.ENCODER,
        encoder_weights=cfg.ENCODER_WEIGHTS,
        in_channels=3,
        classes=cfg.NUM_CLASSES,
        activation=None  # 使用BCEWithLogitsLoss，所以不需要激活函数
    )
    
    model.to(cfg.DEVICE)
    
    # 优化器和学习率调度器
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=5, verbose=True
    )
    
    # 损失函数
    criterion = DiceBCEFocalLoss()
    
    # TensorBoard
    writer = SummaryWriter(log_dir=cfg.LOG_DIR)
    
    # 训练循环
    best_dice = -1
    early_stopping_counter = 0
    
    for epoch in range(cfg.EPOCHS):
        print(f"Epoch {epoch+1}/{cfg.EPOCHS}")
        
        # 训练阶段
        train_loss, train_dice = train_epoch(model, train_loader, optimizer, criterion, cfg.DEVICE)
        
        # 验证阶段
        val_loss, val_dice = valid_epoch(model, valid_loader, criterion, cfg.DEVICE)
        
        # 更新学习率
        scheduler.step(val_dice)
        
        # 记录指标
        writer.add_scalar('Loss/train', train_loss, epoch)
        writer.add_scalar('Loss/valid', val_loss, epoch)
        writer.add_scalar('Dice/train', train_dice, epoch)
        writer.add_scalar('Dice/valid', val_dice, epoch)
        writer.add_scalar('LR', optimizer.param_groups[0]['lr'], epoch)
        
        print(f"Train Loss: {train_loss:.4f}, Train Dice: {train_dice:.4f}")
        print(f"Valid Loss: {val_loss:.4f}, Valid Dice: {val_dice:.4f}")
        
        # 保存最佳模型
        if val_dice > best_dice:
            best_dice = val_dice
            torch.save(model.state_dict(), os.path.join(cfg.CHECKPOINT_DIR, 'best_model.pth'))
            print(f"Best model saved with Dice: {best_dice:.4f}")
            early_stopping_counter = 0
        else:
            early_stopping_counter += 1
            
        # 每个epoch都保存一个检查点
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'train_loss': train_loss,
            'val_loss': val_loss,
            'train_dice': train_dice,
            'val_dice': val_dice,
        }, os.path.join(cfg.CHECKPOINT_DIR, f'checkpoint_epoch_{epoch+1}.pth'))
        
        # 早停机制
        if early_stopping_counter >= cfg.EARLY_STOPPING_PATIENCE:
            print(f"Early stopping triggered after {epoch+1} epochs!")
            break
    
    writer.close()
    print("Training completed!")
    
    # 加载最佳模型并进行示例预测
    visualize_predictions(model, valid_loader, cfg.DEVICE)

# 可视化预测结果
def visualize_predictions(model, loader, device):
    model.load_state_dict(torch.load(os.path.join(cfg.CHECKPOINT_DIR, 'best_model.pth')))
    model.eval()
    
    # 随机选择一批数据进行可视化
    images, masks = next(iter(loader))
    
    with torch.no_grad():
        images = images.to(device)
        outputs = model(images)
        pred_masks = torch.sigmoid(outputs) > 0.5
    
    # 反归一化图像用于可视化
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(device)
    std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(device)
    images = images * std + mean
    images = images.cpu().numpy().transpose(0, 2, 3, 1)
    
    # 绘制图像、真实掩码和预测掩码
    fig, axes = plt.subplots(min(4, len(images)), 3, figsize=(15, 12))
    
    for i in range(min(4, len(images))):
        axes[i, 0].imshow(images[i])
        axes[i, 0].set_title('Image')
        axes[i, 0].axis('off')
        
        axes[i, 1].imshow(masks[i].cpu().numpy().squeeze(), cmap='gray')
        axes[i, 1].set_title('Ground Truth')
        axes[i, 1].axis('off')
        
        axes[i, 2].imshow(pred_masks[i].cpu().numpy().squeeze(), cmap='gray')
        axes[i, 2].set_title('Prediction')
        axes[i, 2].axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(cfg.DATA_ROOT, 'predictions.png'))
    plt.close()

if __name__ == "__main__":
    train()
