# Frontend - 智慧采购系统前端应用

## 简介

智慧采购系统前端应用，基于 Vue 3 + Vite 构建，提供科技感、交互友好的用户界面。

## 技术栈

- Vue 3.5
- Vite 7.3
- Element Plus 2.9
- Vue Router 4.5
- Axios 1.7
- ECharts 5.6
- Unplugin Auto Import / Components

## 安装

```bash
npm install
```

## 运行

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173

### 生产构建

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── views/
│   │   ├── Home.vue           # 首页 - 系统概览
│   │   ├── Requirements.vue   # 需求审查页面
│   │   ├── Price.vue          # 价格参考页面
│   │   └── Contract.vue       # 合同分析页面
│   ├── router/
│   │   └── index.js           # 路由配置
│   ├── App.vue                # 根组件（包含主布局）
│   ├── main.js                # 应用入口
│   └── style.css              # 全局样式
├── public/                    # 静态资源
├── index.html                 # HTML 模板
├── vite.config.js             # Vite 配置
├── package.json
└── README.md
```

## 页面说明

### 首页 (Home)
- 系统概览大屏展示
- 统计数据展示
- 智能体状态监控
- 最近活动记录
- 快速操作入口

### 需求审查 (Requirements)
- 文件上传组件（支持拖拽）
- 审查结果展示
- 问题列表（按严重程度分类）
- 完整度评分可视化
- 修改建议展示

### 价格参考 (Price)
- 搜索筛选表单
- 价格对比表格
- 价格趋势图表（ECharts）
- 价格统计分析

### 合同分析 (Contract)
- 文件上传组件
- 合同要素识别结果
- 风险条款提示
- 整体风险评估
- 修改建议展示

## 设计风格

### 配色方案
- 主色调：科技蓝 (#409EFF)
- 成功色：绿色 (#67C23A)
- 警告色：橙色 (#E6A23C)
- 危险色：红色 (#F56C6C)
- 背景色：深色渐变 (#0f0f1a → #1a1a2e → #16213e)

### 设计特点
- 玻璃拟态效果
- 平滑动画过渡
- 响应式布局
- 悬停交互反馈

## 组件使用

项目使用 Element Plus 组件库，通过 unplugin-auto-import 和 unplugin-vue-components 自动导入，无需手动 import。

### 常用组件

```vue
<template>
  <!-- 按钮 -->
  <el-button type="primary" @click="handleClick">点击</el-button>

  <!-- 表单输入 -->
  <el-input v-model="value" placeholder="请输入" />

  <!-- 表格 -->
  <el-table :data="tableData">
    <el-table-column prop="name" label="名称" />
  </el-table>

  <!-- 消息提示 -->
  <el-message>这是一条消息</el-message>

  <!-- 对话框 -->
  <el-dialog v-model="visible" title="标题">
    内容
  </el-dialog>

  <!-- 上传 -->
  <el-upload>
    <el-button>上传文件</el-button>
  </el-upload>

  <!-- 标签 -->
  <el-tag type="success">成功</el-tag>

  <!-- 图标 -->
  <el-icon><Search /></el-icon>
</template>
```

## 开发指南

### 添加新页面

1. 在 `src/views/` 目录下创建新的 Vue 组件
2. 在 `src/router/index.js` 中配置路由
3. 在 `src/App.vue` 的侧边栏菜单中添加导航项

### 使用 API

通过 axios 调用后端 API：

```javascript
import axios from 'axios'

// GET 请求
const response = await axios.get('/api/price-reference', {
  params: { category: '服务器' }
})

// POST 请求
const formData = new FormData()
formData.append('file', file)
const response = await axios.post('/api/review-requirements', formData)
```

### 使用 ECharts

```javascript
import * as echarts from 'echarts'

// 初始化图表
const chart = echarts.init(chartRef.value)
chart.setOption({
  // 配置项
})
```

## 配置说明

### Vite 配置 (vite.config.js)

- 自动导入 Element Plus 组件
- 自动导入 Element Plus API
- API 代理配置（/api 代理到 http://localhost:8000）

### 环境变量

可以在项目根目录创建 `.env` 文件配置环境变量：

```
VITE_API_BASE_URL=http://localhost:8000
```

## 注意事项

1. 所有样式使用 scoped 作用域，避免样式污染
2. 遵循 Vue 3 Composition API 规范
3. 使用 setup script 语法糖
4. 组件名使用大驼峰命名
5. 文件名使用短横线命名
