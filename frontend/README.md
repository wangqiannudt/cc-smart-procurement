# Frontend - 智慧采购系统前端

## 1. 概览

前端基于 Vue 3 + Vite，包含登录、系统概览、AI 对话、综合分析、需求审查、价格参考、合同分析、管理后台等页面。

## 2. 技术栈

- Vue 3
- Vite 7
- Vue Router
- Element Plus
- Axios
- ECharts 6（按需/懒加载运行时）
- Vitest / Playwright

## 3. 安装与运行

```bash
cd /Users/ali/dev/cc-smart-procurement/frontend
npm install
npm run dev
```

默认开发地址：`http://localhost:5173`

生产构建：

```bash
npm run build
npm run preview
```

## 4. 路由页面

- `/login` 登录
- `/register` 注册
- `/` 系统概览
- `/chat` AI 对话
- `/analysis-workbench` 综合分析
- `/requirements` 需求审查
- `/price` 价格参考
- `/contract` 合同分析
- `/admin` 管理后台

## 5. 关键实现点

1. 路由守卫
- 未登录自动跳转 `/login`
- 管理后台按角色限制

2. 草稿缓存
- 需求/价格/合同页面支持自动保存、自动恢复开关、手动恢复、清空

3. 统一确认弹框样式
- 统一封装确认框，避免默认白底样式
- 统一居中与按钮风格（退出、草稿恢复等）

4. 登录交互
- 支持回车提交与按钮点击提交

5. 图表加载优化
- ECharts 运行时入口拆分，降低首次加载压力

## 6. 测试与脚本

`package.json` 脚本：

```bash
npm run test:run              # Vitest
npm run test:e2e:smoke        # Playwright smoke
npm run test:e2e:integration  # Playwright + real backend
npm run build                 # 构建
npm run perf:baseline         # 构建并生成性能基线 Markdown
```

当前结果（2026-02-28）：
- `npm run test:run` -> `10 files, 28 tests passed`
- `npm run test:e2e:smoke` -> `3 passed`
- `npm run build` -> 通过

## 7. 目录结构（核心）

```text
frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── composables/
│   ├── router/
│   ├── styles/
│   ├── tooling/
│   ├── views/
│   ├── App.vue
│   └── main.js
├── scripts/
├── tests/e2e/
└── package.json
```
