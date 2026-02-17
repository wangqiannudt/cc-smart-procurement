# Backend - 智慧采购系统后端服务

## 简介

智慧采购系统后端服务，基于 FastAPI 构建，提供三大核心智能体的 API 接口。

## 技术栈

- Python 3.8+
- FastAPI 0.109.0
- Uvicorn 0.27.0
- Pydantic 2.5.3
- python-docx 1.1.0
- PyPDF2 3.0.1
- jieba 0.42.1

## 安装

### 创建虚拟环境

```bash
python -m venv venv
```

### 激活虚拟环境

Linux/Mac:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

### 开发模式

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── api/
│   │   ├── __init__.py
│   │   ├── requirements.py  # 需求审查 API
│   │   ├── price.py        # 价格参考 API
│   │   └── contract.py     # 合同分析 API
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── requirement_reviewer.py  # 需求审查智能体
│   │   ├── price_reference.py       # 价格参考智能体
│   │   └── contract_analyzer.py    # 合同分析智能体
│   └── models/
│       └── __init__.py
├── requirements.txt
└── README.md
```

## API 接口说明

### 需求审查

#### POST /api/review-requirements

审查需求文档，返回问题和建议。

**请求参数：**
- file: 需求文档文件（.docx 或 .txt）

**响应示例：**
```json
{
  "success": true,
  "data": {
    "issues": [...],
    "suggestions": [...],
    "completeness_score": 85,
    "issue_count": 5,
    "error_count": 1,
    "warning_count": 3,
    "info_count": 1
  }
}
```

### 价格参考

#### GET /api/price-reference

查询价格参考信息。

**请求参数：**
- category: 商品分类（可选）
- keyword: 关键词（可选）
- min_price: 最低价格（可选）
- max_price: 最高价格（可选）

**响应示例：**
```json
{
  "success": true,
  "data": {
    "records": [...],
    "categories": [...],
    "total": 10,
    "trend_data": [...],
    "price_range": {
      "min": 32000,
      "max": 58000,
      "avg": 45000
    }
  }
}
```

### 合同分析

#### POST /api/contract-analysis

分析合同文档，识别要素和风险。

**请求参数：**
- file: 合同文档文件（.docx 或 .txt）

**响应示例：**
```json
{
  "success": true,
  "data": {
    "elements": {...},
    "risks": [...],
    "risk_level": "中风险",
    "completeness": 87.5,
    "suggestions": [...]
  }
}
```

## 开发指南

### 添加新的 API 端点

1. 在 `app/api/` 目录下创建新的路由文件
2. 使用 FastAPI 路由装饰器定义端点
3. 在 `app/main.py` 中导入并注册路由

### 添加新的智能体

1. 在 `app/agents/` 目录下创建新的智能体类
2. 实现智能体的核心逻辑
3. 在对应的 API 文件中调用智能体方法

## 测试

```bash
# 健康检查
curl http://localhost:8000/api/health

# 查看所有接口
curl http://localhost:8000/docs
```
