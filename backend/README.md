# Backend - 智慧采购系统后端

## 1. 概览

后端基于 FastAPI，提供认证、用户管理、需求审查、价格参考、合同分析、AI 对话、综合分析工作流、统计等 API。

## 2. 技术栈

- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- 业务依赖：langchain / sentence-transformers / openai / statsmodels

依赖文件：`/Users/ali/dev/cc-smart-procurement/backend/requirements.txt`

## 3. 本地运行

```bash
cd /Users/ali/dev/cc-smart-procurement/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问：
- Swagger：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`
- 健康检查：`http://localhost:8000/api/health`

## 4. 认证与初始化

- 启动时会初始化数据库
- 默认管理员自动创建：`admin / admin123`

## 5. API 路由清单（按模块）

## 5.1 auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/change-password`

## 5.2 users
- `GET /api/users`
- `PUT /api/users/{user_id}/activate`
- `PUT /api/users/{user_id}/deactivate`
- `PUT /api/users/{user_id}/role`

## 5.3 requirements
- `GET /api/categories`
- `GET /api/categories/{category_id}/fields`
- `POST /api/review-requirements`
- `POST /api/review-requirements/text`

## 5.4 requirements_mgmt
- `GET /api/requirements`
- `POST /api/requirements`
- `GET /api/requirements/{req_id}`
- `PUT /api/requirements/{req_id}/status`
- `PUT /api/requirements/{req_id}/assign`

## 5.5 price
- `GET /api/price-reference`
- `GET /api/price-reference/categories`
- `GET /api/price-reference/product/{product_name}`
- `POST /api/price-reference/analyze`
- `GET /api/price-reference/predict`
- `GET /api/price-reference/market-insights`

## 5.6 contract
- `POST /api/contract-analysis`

## 5.7 chat
- `POST /api/chat/conversation`
- `POST /api/chat/new-session`
- `GET /api/chat/history/{session_id}`
- `DELETE /api/chat/session/{session_id}`
- `POST /api/chat/procurement-analysis`
- `POST /api/chat/price-recommendation`
- `POST /api/chat/comprehensive-analysis`

## 5.8 analysis
- `POST /api/analysis/workflow`
- `GET /api/analysis/history`
- `POST /api/analysis/history/{history_id}/reuse`

## 5.9 statistics
- `GET /api/statistics/overview`
- `GET /api/statistics/processor-workload`
- `GET /api/statistics/submitter-requests`
- `GET /api/statistics/processing-time`
- `GET /api/statistics/category-summary`

## 6. 测试

```bash
cd /Users/ali/dev/cc-smart-procurement/backend
./venv/bin/python -m pytest -q
```

当前结果（2026-02-28）：`20 passed`

## 7. 目录结构（核心）

```text
backend/
├── app/
│   ├── api/
│   ├── agents/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── data/
├── tests/
└── requirements.txt
```
