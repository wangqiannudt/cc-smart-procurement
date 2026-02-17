# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

智慧采购系统 - 为研究采购服务中心构建的智能采购原型系统，集成AI聊天助手、知识库和多智能体协调器。

## 开发命令

### 环境设置
```bash
# 后端依赖
cd backend && pip install -r requirements.txt

# 前端依赖
cd frontend && npm install
```

### 启动服务
```bash
./dev_new.sh          # 推荐：完整AI功能启动
./dev.sh              # 基础版启动
./quick-start.sh      # 仅前端演示(无后端)

# 手动启动后端
cd backend && source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 停止服务
```bash
./stop_new.sh         # 推荐
./stop.sh             # 基础版
```

### 构建前端
```bash
cd frontend && npm run build && npm run preview
```

## 架构概述

### 技术栈
- **后端**: FastAPI (端口8000)，依赖: langchain, chromadb, sentence-transformers, jieba
- **前端**: Vue 3 + Vite + Element Plus (端口5173)
- **代理**: Vite proxy 将 `/api/*` 转发到 `http://localhost:8000`

### 智能体架构
```
AgentCoordinator (agent_coordinator.py)
├── RequirementReviewer  - 需求审查，jieba分词检测模糊表达
├── PriceReference       - 历史价格查询与趋势分析
├── ContractAnalyzer     - 合同风险识别(三级风险关键词)
└── KnowledgeBase        - 向量语义搜索(SentenceTransformers)
```

### 目录结构
```
backend/app/
├── main.py                    # FastAPI入口，CORS配置
├── api/                       # API路由
│   ├── chat.py                # AI对话端点
│   ├── requirements.py        # 需求审查API
│   ├── price.py               # 价格参考API
│   └── contract.py            # 合同分析API
├── agents/                    # 智能体实现
│   ├── agent_coordinator.py   # 多智能体协调
│   ├── chat_agent.py          # 对话智能体
│   ├── requirement_reviewer.py
│   ├── price_reference.py
│   └── contract_analyzer.py
└── knowledge/
    └── knowledge_base.py      # 向量知识库

frontend/src/
├── App.vue                    # 根组件(深色主题)
├── router/index.js            # 路由配置
├── composables/               # 可复用逻辑
│   ├── useChat.js             # 对话逻辑封装
│   ├── useResponsive.js       # 响应式布局
│   └── useFormat.js           # 格式化工具
└── views/                     # 页面组件
    ├── Home.vue, Requirements.vue, Price.vue, Contract.vue
```

### API端点
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/review-requirements` | POST | 需求文档审查(文件上传) |
| `/api/price-reference` | GET | 价格查询 |
| `/api/price-reference/analyze` | POST | 价格分析 |
| `/api/contract-analysis` | POST | 合同分析(文件上传) |
| `/api/chat/conversation` | POST | AI对话 |
| `/api/chat/new-session` | POST | 创建新会话 |
| `/api/chat/history/{session_id}` | GET | 获取会话历史 |
| `/api/chat/procurement-analysis` | POST | 采购场景分析 |
| `/api/chat/price-recommendation` | POST | 价格建议 |
| `/api/chat/comprehensive-analysis` | POST | 综合分析(多智能体) |
| `/api/price-reference/predict` | GET | 价格预测 |
| `/api/price-reference/market-insights` | GET | 市场洞察 |
| `/api/price-reference/categories` | GET | 获取品类列表 |

### 前端路由
- `/` - 系统概览仪表板
- `/requirements` - 需求审查(上传+分析)
- `/price` - 价格参考(搜索+图表)
- `/contract` - 合同分析(上传+风险评估)

## 重要注意事项

1. **CORS**: `allow_origins=["*"]` 仅适用于开发环境
2. **LLM配置**: 支持多种 LLM 提供商，通过环境变量配置
   - 在 `backend/` 目录创建 `.env` 文件
   - 优先级: `GLM_API_KEY` > `DASHSCOPE_API_KEY` > `OPENAI_API_KEY`
   - 示例: `GLM_API_KEY=your_key` + `LLM_MODEL=glm-4-flash`
   - 无配置时自动降级为关键词匹配模式
3. **端口**: 后端8000，前端5173，演示模式8080
4. **中文处理**: 依赖jieba分词，系统主要处理中文内容
5. **知识库**: 自动从 `backend/data/knowledge/` 加载，支持md/txt文件

## 添加新智能体

1. 在 `backend/app/agents/` 创建智能体类
2. 在 `agent_coordinator.py` 中注册
3. 在 `api/chat.py` 添加对应端点
4. 前端添加UI组件和API调用

## 前端样式

- Element Plus组件库
- 主色调: #409EFF
- 背景渐变: #0f0f1a → #1a1a2e → #16213e