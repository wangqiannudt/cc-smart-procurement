# IT设备采购知识

## 服务器选型指南

### 机架式服务器 vs 塔式服务器
- **机架式服务器**：适合机房部署，密度高，易于管理
  - 推荐场景：数据中心、云计算环境
  - 代表产品：Dell PowerEdge R系列、HP ProLiant DL系列

- **塔式服务器**：适合办公室环境，噪音低，扩展性好
  - 推荐场景：中小企业、分支机构
  - 代表产品：Dell PowerEdge T系列、HP ProLiant ML系列

### 关键配置参数
1. **CPU**：核心数、主频、缓存
   - 通用计算：Intel Xeon Silver/Gold
   - 高性能计算：Intel Xeon Platinum
   - AI训练：AMD EPYC或Intel Xeon Max

2. **内存**：容量、频率、ECC功能
   - 基础配置：64GB-128GB
   - 虚拟化环境：256GB以上
   - 大数据处理：512GB以上

3. **存储**：类型、容量、RAID
   - 系统盘：SSD，容量500GB-1TB
   - 数据盘：SAS/SATA HDD，容量根据需求
   - 高速存储：NVMe SSD，适合数据库

## 工作站选型指南

### 图形工作站
主要用于3D建模、渲染、视频编辑等
- CPU：Intel Xeon W或AMD Threadripper Pro
- GPU：NVIDIA RTX A系列或 professional 卡
- 内存：32GB起步，推荐64GB-128GB

### 计算工作站
主要用于科学计算、仿真分析等
- CPU：高主频多核心
- GPU：根据需求选择
- 内存：大容量ECC内存