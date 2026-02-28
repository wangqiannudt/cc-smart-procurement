# 智慧采购系统（CC Smart Procurement）

面向采购业务原型阶段的全栈系统，提供“登录鉴权 + 多模块分析 + 综合工作台 + 管理后台 + 自动化测试 + 演示资产”闭环。

## 当前状态

- 仓库分支：`codex`（原型持续迭代）
- 最后核验时间：2026-02-28
- 运行形态：前后端分离（FastAPI + Vue 3）

## 核心能力

1. 用户体系与权限
- 登录、注册、改密
- 角色：`handler`（承办人）、`processor`（经办人）、`admin`（管理员）
- 管理员可进行用户激活/停用/改角色

2. 业务功能模块
- 系统概览：统计卡片、智能推荐、预警信息、快捷入口
- AI 对话：会话历史、场景分析、价格建议、综合建议
- 需求审查：文本/文件输入、问题分级、草稿缓存恢复
- 价格参考：筛选查询、趋势图、预测、市场洞察、草稿缓存恢复
- 合同分析：文本/文件输入、风险识别、建议输出、草稿缓存恢复
- 综合分析工作台：模板填充、跨模块分析、证据链、历史复用
- 管理后台：用户管理与统计视图

3. 工程化能力
- 前端单测（Vitest）
- 后端单测（Pytest）
- E2E 冒烟与联调（Playwright）
- GitHub Actions CI：Backend / Frontend / E2E
- 演示视频生成脚本与多版本 MP4 资产

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- 业务组件：需求审查、价格参考、合同分析、聊天与综合分析服务

### 前端
- Vue 3 + Vite
- Vue Router
- Element Plus
- Axios
- ECharts（按需运行时加载）
- Playwright / Vitest

## 快速开始

### 1) 环境要求
- Python 3.11+（本地建议 3.12）
- Node.js 22.12+

### 2) 安装依赖

```bash
# backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# frontend
cd ../frontend
npm install
```

### 3) 启动系统

方式 A：一键脚本（推荐）

```bash
cd /Users/ali/dev/cc-smart-procurement
./dev_new.sh
```

方式 B：手动启动

```bash
# backend
cd /Users/ali/dev/cc-smart-procurement/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# frontend
cd /Users/ali/dev/cc-smart-procurement/frontend
npm run dev
```

### 4) 访问地址
- 前端：`http://localhost:5173`
- 后端：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`

### 5) 默认管理员（启动时自动初始化）
- 用户名：`admin`
- 密码：`admin123`

## 常用测试命令

```bash
# backend
cd backend
./venv/bin/python -m pytest -q

# frontend unit
cd frontend
npm run test:run

# frontend build
npm run build

# e2e smoke (mock API)
npm run test:e2e:smoke

# e2e integration (real backend)
npm run test:e2e:integration
```

## 本次实测结果（2026-02-28）

- 后端测试：`20 passed`
- 前端单测：`10 files, 28 tests passed`
- E2E 冒烟：`3 passed`
- 前端构建：通过
- 性能基线：生成 `docs/worklogs/2026-02-28-frontend-perf-baseline.md`

## 文档导航

- 后端说明：`/Users/ali/dev/cc-smart-procurement/backend/README.md`
- 前端说明：`/Users/ali/dev/cc-smart-procurement/frontend/README.md`
- 当前功能总览：`/Users/ali/dev/cc-smart-procurement/docs/worklogs/2026-02-27-current-feature-summary.md`
- 当前性能基线：`/Users/ali/dev/cc-smart-procurement/docs/worklogs/2026-02-28-frontend-perf-baseline.md`
- 演示视频索引：`/Users/ali/dev/cc-smart-procurement/docs/worklogs/demos/2026-02-18-all-demo-paths/README.md`
