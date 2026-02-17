# 智慧采购系统

> 为科研采购服务中心构建的智能采购系统，集成AI对话、价格预测、智能推荐等先进功能

## 系统亮点

- 🤖 **AI智能对话** - 支持GLM/通义千问/OpenAI，专业采购领域问答
- 📈 **价格预测** - 基于历史数据的趋势预测，提供购买时机建议
- 🔗 **跨智能体协作** - 需求、价格、合同综合分析，风险评分
- 💡 **智能推荐** - 主动推荐采购建议，价格预警提醒
- 🎨 **现代UI** - 响应式设计，深色科技风格

## 功能模块

### 1. 系统概览（首页）
- 智能推荐横幅（基于市场趋势）
- 价格预警提示
- 四大智能体状态监控
- 快捷操作入口
- AI快捷分析（服务器/网络/存储/软件）

### 2. AI智能对话
- 多轮对话，上下文理解
- 多会话管理（UUID隔离）
- 采购专业领域知识
- 建议操作自动生成

### 3. 需求审查
- 上传.docx/.txt需求文档
- 六要素完整性检查
- 模糊表述识别（"等"、"约"等）
- 技术参数审核
- 完整度评分

### 4. 价格参考
- 历史价格查询（7大类别）
- **价格趋势预测**（1-6个月）
- 95%置信区间
- 购买时机建议
- 市场洞察分析
- 报价合理性评估

### 5. 合同分析
- 合同要素识别
- 风险条款分级（高/中/低）
- 模糊表述检测
- 修改建议生成

## 技术架构

### 后端
| 技术 | 用途 |
|------|------|
| FastAPI | Web框架 |
| LangChain | LLM编排 |
| SentenceTransformers | 语义嵌入 |
| jieba | 中文分词 |
| OpenAI SDK | LLM API调用 |

### 前端
| 技术 | 用途 |
|------|------|
| Vue 3 | 前端框架 |
| Vite | 构建工具 |
| Element Plus | UI组件库 |
| ECharts | 图表可视化 |
| Axios | HTTP客户端 |

### 智能体架构
```
AgentCoordinator（协调器）
├── ChatAgent          - AI对话（支持GLM/通义/OpenAI）
├── RequirementReviewer - 需求审查
├── PriceReference      - 价格预测与分析
├── ContractAnalyzer    - 合同风险识别
└── KnowledgeBase       - 语义知识库
```

## 项目结构

```
cc-smart-procurement/
├── backend/
│   ├── app/
│   │   ├── agents/           # 智能体
│   │   │   ├── chat_agent.py         # AI对话
│   │   │   ├── price_reference.py    # 价格预测
│   │   │   ├── agent_coordinator.py  # 跨智能体协调
│   │   │   ├── requirement_reviewer.py
│   │   │   └── contract_analyzer.py
│   │   ├── api/              # API路由
│   │   │   ├── chat.py
│   │   │   ├── price.py
│   │   │   ├── requirements.py
│   │   │   └── contract.py
│   │   ├── knowledge/        # 知识库
│   │   └── main.py
│   ├── data/knowledge/       # 知识文件
│   ├── .env                  # LLM配置
│   └── requirements.txt
│
├── frontend/
│   └── src/
│       ├── views/
│       │   ├── Home.vue      # 智能仪表板
│       │   ├── Chat.vue      # AI对话
│       │   ├── Price.vue     # 价格预测
│       │   ├── Requirements.vue
│       │   └── Contract.vue
│       ├── api/              # API服务层
│       └── router/
│
├── dev_new.sh                # 启动脚本
├── stop_new.sh               # 停止脚本
└── README.md
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 18+

### 安装依赖

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 配置LLM（可选）

在 `backend/` 目录创建 `.env` 文件：

```bash
# GLM（智谱AI）
GLM_API_KEY=your_glm_key
LLM_MODEL=glm-4-flash

# 或通义千问
# DASHSCOPE_API_KEY=your_key
# LLM_MODEL=qwen-plus

# 或OpenAI
# OPENAI_API_KEY=your_key
# LLM_MODEL=gpt-3.5-turbo
```

> 不配置LLM时，系统自动使用关键词匹配模式

### 启动服务

```bash
# 方式一：一键启动
./dev_new.sh

# 方式二：手动启动
# 后端
cd backend && source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend && npm run dev
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:5173 |
| 后端API | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |

### 停止服务

```bash
./stop_new.sh
```

## API接口

### AI对话
| 方法 | 端点 | 功能 |
|------|------|------|
| POST | `/api/chat/conversation` | AI对话 |
| POST | `/api/chat/new-session` | 创建新会话 |
| GET | `/api/chat/history/{id}` | 获取历史 |
| POST | `/api/chat/comprehensive-analysis` | 综合分析 |

### 价格参考
| 方法 | 端点 | 功能 |
|------|------|------|
| GET | `/api/price-reference` | 查询价格 |
| GET | `/api/price-reference/predict` | **价格预测** |
| GET | `/api/price-reference/market-insights` | **市场洞察** |
| POST | `/api/price-reference/analyze` | 报价分析 |

### 其他
| 方法 | 端点 | 功能 |
|------|------|------|
| POST | `/api/review-requirements` | 需求审查 |
| POST | `/api/contract-analysis` | 合同分析 |
| GET | `/api/health` | 健康检查 |

## 智能化特性

### 价格预测算法
- 线性回归趋势分析
- 季节性因子调整
- 95%置信区间计算
- 购买时机建议

### 跨智能体分析
- 需求-合同一致性检查
- 综合风险评分（0-100）
- 预算匹配分析
- 整体采购建议

### LLM集成
- 系统提示词专业化
- 多轮上下文记忆
- 关键词匹配降级

## 界面预览

系统采用深色科技风格：
- 渐变背景（#0f0f1a → #1a1a2e → #16213e）
- 玻璃拟态卡片
- 平滑动画过渡
- 响应式布局（支持移动端）

## 许可证

本项目仅供内部使用。
