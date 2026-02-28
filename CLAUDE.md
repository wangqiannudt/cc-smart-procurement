# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

智慧采购系统 - 为研究采购服务中心构建的智能采购原型系统，集成AI聊天助手、知识库和多智能体协调器。

### 核心功能
- **用户认证与权限管理**: 支持承办人/经办人/管理员三种角色
- **需求审查**: 基于规则的智能需求文档分析
- **价格参考**: 历史价格查询、趋势分析与价格预测
- **合同分析**: 合同风险识别与评估
- **综合分析工作台**: 多维度整合分析，生成证据链
- **AI智能助手**: 多LLM支持的对话式交互
- **管理后台**: 用户管理、统计分析

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

### 测试命令
```bash
# 前端单元测试
cd frontend && npm run test

# 前端测试覆盖率
cd frontend && npm run test:coverage

# E2E测试
cd frontend && npm run test:e2e

# 后端测试
cd backend && pytest
```

## 架构概述

### 技术栈
- **后端**: FastAPI (端口8000)
  - 数据库: SQLAlchemy + SQLite
  - 认证: JWT Token (python-jose)
  - AI: langchain, chromadb, sentence-transformers, jieba
  - 分析: statsmodels, scipy
- **前端**: Vue 3 + Vite + Element Plus (端口5173)
  - 图表: ECharts
  - 安全: DOMPurify (XSS防护)
  - 测试: Vitest + Playwright
- **代理**: Vite proxy 将 `/api/*` 转发到 `http://localhost:8000`

### 智能体架构
```
AgentCoordinator (agent_coordinator.py)
├── RequirementReviewer  - 需求审查，jieba分词检测模糊表达
│   ├── RuleEngine       - YAML规则加载与管理
│   ├── FieldExtractor   - 上下文感知字段提取
│   └── RiskDetector     - 品牌/型号/模糊表述风险检测
├── PriceReference       - 历史价格查询与趋势分析
├── ContractAnalyzer     - 合同风险识别(三级风险关键词)
├── ChatAgent            - AI对话，支持多LLM提供商
│   ├── GLM (智谱AI)     - 优先级最高
│   ├── 通义千问         - 优先级第二
│   ├── OpenAI           - 优先级第三
│   └── 关键词匹配        - 无LLM时降级
└── KnowledgeBase        - 向量语义搜索(SentenceTransformers)
```

### 核心模块 (backend/app/core/)
- `rule_engine.py` - 加载品类规则配置，管理字段定义和风险规则
- `field_extractor.py` - 基于jieba分词的上下文感知字段提取
- `risk_detector.py` - 检测品牌指向性、型号指定、模糊表述等风险
- `database.py` - SQLAlchemy 数据库配置
- `security.py` - JWT Token 生成与验证、密码哈希
- `deps.py` - FastAPI 依赖注入（用户认证、权限检查）

### 数据模型 (backend/app/models/)
- `user.py` - 用户模型，支持 handler/processor/admin 三种角色
- `requirement.py` - 需求工单模型，支持 pending/processing/completed 状态
- `analysis_history.py` - 分析历史模型，存储综合分析工作流记录

### 服务层 (backend/app/services/)
- `analysis_workflow.py` - 分析工作流服务，编排需求/价格/合同分析，生成证据链

### 规则配置 (backend/data/rules/)
支持8大品类：server, workstation, terminal, display, communication, uav_platform, instrument, accelerator
每个品类有独立的YAML规则文件，定义P0/P1/P2优先级字段和风险规则

### 目录结构
```
backend/
├── data/
│   ├── rules/                    # 规则配置
│   │   ├── category_rules.yaml   # 品类主配置
│   │   └── rules/                # 各品类规则 (8个)
│   └── knowledge/                # 知识库文件
└── app/
    ├── main.py                   # FastAPI入口
    ├── core/                     # 核心模块
    │   ├── rule_engine.py
    │   ├── field_extractor.py
    │   ├── risk_detector.py
    │   ├── database.py
    │   ├── security.py
    │   └── deps.py
    ├── models/                   # 数据模型
    │   ├── user.py
    │   ├── requirement.py
    │   └── analysis_history.py
    ├── services/                 # 业务服务
    │   └── analysis_workflow.py
    ├── api/                      # API路由
    │   ├── auth.py               # 用户认证
    │   ├── users.py              # 用户管理(管理员)
    │   ├── chat.py               # AI对话
    │   ├── requirements.py       # 需求审查
    │   ├── requirements_mgmt.py  # 需求工单管理
    │   ├── price.py              # 价格参考
    │   ├── contract.py           # 合同分析
    │   ├── statistics.py         # 统计数据
    │   └── analysis.py           # 综合分析工作流
    ├── agents/                   # 智能体实现
    │   ├── agent_coordinator.py
    │   ├── chat_agent.py
    │   ├── requirement_reviewer.py
    │   ├── price_reference.py
    │   └── contract_analyzer.py
    └── knowledge/
        └── knowledge_base.py

frontend/src/
├── App.vue                       # 根组件
├── router/index.js               # 路由配置(含路由守卫)
├── styles/
│   └── themes.css                # 多主题样式系统
├── composables/                  # 可复用逻辑
│   ├── useChat.js                # 对话逻辑
│   ├── useResponsive.js          # 响应式布局
│   ├── useFormat.js              # 格式化工具
│   ├── useAuth.js                # 认证逻辑
│   ├── useTheme.js               # 主题切换
│   ├── useAnalysisWorkflow.js    # 分析工作流
│   └── useDraftCache.js          # 草稿缓存
├── components/
│   ├── common/
│   │   └── StateBlock.vue        # 通用状态展示
│   ├── analysis/                 # 分析工作台组件
│   │   ├── InputPanel.vue
│   │   ├── ResultPanel.vue
│   │   └── EvidencePanel.vue
│   ├── requirements/
│   │   └── RequirementsScoreOverview.vue
│   ├── price/
│   │   ├── PriceSearchCard.vue
│   │   └── PriceStatsCard.vue
│   └── contract/
│       └── ContractRiskOverview.vue
└── views/
    ├── Home.vue                  # 系统概览仪表板
    ├── Login.vue                 # 用户登录
    ├── Register.vue              # 用户注册
    ├── Chat.vue                  # AI智能助手
    ├── AnalysisWorkbench.vue     # 综合分析工作台
    ├── Requirements.vue          # 需求审查
    ├── Price.vue                 # 价格参考
    ├── Contract.vue              # 合同分析
    └── Admin.vue                 # 管理后台
```

### API端点

#### 认证模块
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/me` | GET | 获取当前用户信息 |
| `/api/auth/change-password` | POST | 修改密码 |

#### 用户管理(管理员)
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/users` | GET | 获取用户列表 |
| `/api/users/{id}/activate` | PUT | 激活用户 |
| `/api/users/{id}/deactivate` | PUT | 停用用户 |
| `/api/users/{id}/role` | PUT | 修改用户角色 |

#### 需求审查
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/categories` | GET | 获取可用品类列表 |
| `/api/categories/{id}/fields` | GET | 获取品类字段定义 |
| `/api/review-requirements` | POST | 需求文档审查(文件上传) |
| `/api/review-requirements/text` | POST | 需求文本审查 |

#### 需求工单管理
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/requirements` | GET | 获取需求列表(按角色过滤) |
| `/api/requirements` | POST | 提交新需求(承办人) |
| `/api/requirements/{id}` | GET | 获取需求详情 |
| `/api/requirements/{id}/status` | PUT | 更新需求状态 |
| `/api/requirements/{id}/assign` | PUT | 分配经办人 |

#### 价格参考
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/price-reference` | GET | 查询价格参考 |
| `/api/price-reference/categories` | GET | 获取价格分类 |
| `/api/price-reference/product/{name}` | GET | 获取产品价格 |
| `/api/price-reference/analyze` | POST | 分析报价合理性 |
| `/api/price-reference/predict` | GET | 价格预测 |
| `/api/price-reference/market-insights` | GET | 市场洞察 |

#### 合同分析
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/contract-analysis` | POST | 分析合同文档 |

#### AI聊天
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/chat/conversation` | POST | AI对话 |
| `/api/chat/new-session` | POST | 创建新会话 |
| `/api/chat/history/{id}` | GET | 获取会话历史 |
| `/api/chat/session/{id}` | DELETE | 清空会话历史 |
| `/api/chat/procurement-analysis` | POST | 采购场景分析 |
| `/api/chat/price-recommendation` | POST | 价格建议 |
| `/api/chat/comprehensive-analysis` | POST | 综合分析(多智能体) |

#### 统计数据
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/statistics/overview` | GET | 综合概览 |
| `/api/statistics/processor-workload` | GET | 经办人工作量 |
| `/api/statistics/submitter-requests` | GET | 承办人需求量 |
| `/api/statistics/processing-time` | GET | 处理时效 |
| `/api/statistics/category-summary` | GET | 采购分类统计 |

#### 综合分析工作流
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/analysis/workflow` | POST | 运行综合分析工作流 |
| `/api/analysis/history` | GET | 获取分析历史 |
| `/api/analysis/history/{id}/reuse` | POST | 复用历史记录 |

#### 健康检查
| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/health` | GET | 健康检查 |

### 前端路由

| 路由 | 组件 | 权限 | 功能 |
|------|------|------|------|
| `/login` | Login.vue | 公开 | 用户登录 |
| `/register` | Register.vue | 公开 | 用户注册 |
| `/` | Home.vue | 登录 | 系统概览仪表板 |
| `/chat` | Chat.vue | 登录 | AI智能助手 |
| `/analysis-workbench` | AnalysisWorkbench.vue | 登录 | 综合分析工作台 |
| `/requirements` | Requirements.vue | 登录 | 需求审查 |
| `/price` | Price.vue | 登录 | 价格参考 |
| `/contract` | Contract.vue | 登录 | 合同分析 |
| `/admin` | Admin.vue | 管理员 | 管理后台 |

### 用户角色与权限

| 角色 | 英文名 | 权限说明 |
|------|--------|---------|
| 承办人 | handler | 提交需求、查看自己的需求、使用分析功能 |
| 经办人 | processor | 处理需求、更新状态、分配任务 |
| 管理员 | admin | 用户管理、查看所有数据、系统配置 |

## 前端样式系统

### 多主题支持
位于 `frontend/src/styles/themes.css`，支持三种风格：

1. **default (深邃星空)** - 深色科技感，专业沉稳
2. **nord (北欧冷调)** - 北极冰川蓝灰，专业冷静
3. **apple (Apple)** - 极简高端，大量留白

### 主题特性
- 完整的 CSS 变量定义
- Element Plus 组件主题覆盖
- 深色/浅色模式支持
- 自定义滚动条样式
- 主题持久化到 localStorage

### 使用方式
```javascript
import { useTheme } from '@/composables/useTheme'
const { currentTheme, setTheme } = useTheme()
setTheme('nord') // 切换主题
```

## 重要注意事项

1. **字段提取**: 提取器使用field_id作为上下文来优先匹配相关模式（如CPU核心数优先匹配"数字+核"模式）
2. **规则热更新**: 规则YAML文件修改后需重启服务生效（uvicorn --reload会自动检测Python文件）
3. **CORS**: `allow_origins=["*"]` 仅适用于开发环境
4. **LLM配置**: 支持多种 LLM 提供商，通过环境变量配置
   - 在 `backend/` 目录创建 `.env` 文件
   - 优先级: `GLM_API_KEY` > `DASHSCOPE_API_KEY` > `OPENAI_API_KEY`
   - 示例: `GLM_API_KEY=your_key` + `LLM_MODEL=glm-4-flash`
   - 无配置时自动降级为关键词匹配模式
5. **端口**: 后端8000，前端5173，演示模式8080
6. **中文处理**: 依赖jieba分词，系统主要处理中文内容
7. **知识库**: 自动从 `backend/data/knowledge/` 加载，支持md/txt文件
8. **数据库**: 默认使用 SQLite，数据库文件位于 `backend/procurement.db`
9. **草稿缓存**: 前端表单自动保存到 localStorage，可通过 useDraftCache 管理

## 添加新智能体

1. 在 `backend/app/agents/` 创建智能体类
2. 在 `agent_coordinator.py` 中注册
3. 在 `api/chat.py` 添加对应端点
4. 前端添加UI组件和API调用

## 添加新API端点

1. 在 `backend/app/api/` 创建路由文件
2. 在 `main.py` 中注册路由
3. 如需认证，使用 `deps.py` 中的依赖注入
4. 前端在相应 composable 中添加 API 调用

## 添加新页面

1. 在 `frontend/src/views/` 创建 Vue 组件
2. 在 `router/index.js` 添加路由配置
3. 如需认证，设置 `meta.requiresAuth: true`
4. 如需管理员权限，设置 `meta.requiresAdmin: true`
5. 更新导航菜单
