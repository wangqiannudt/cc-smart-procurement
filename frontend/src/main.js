import { createApp } from 'vue'
// Element Plus 样式由 unplugin-vue-components 自动按需引入
import './styles/themes.css'  // 主题变量（必须在 style.css 之前）
import './style.css'
import App from './App.vue'
import router from './router'
import api, { request, apiEndpoints } from './api'

// 按需引入使用的图标（减少打包体积约 200KB）
import {
  // 导航和菜单
  Menu, Close, DataAnalysis, ChatDotRound, Document, TrendCharts, DocumentCopy,
  // 聊天相关
  RefreshRight, User, Service, Promotion,
  // 上传和文档
  Upload, UploadFilled, DocumentChecked,
  // 操作和状态
  Search, Aim, Check, CircleCheck, CircleClose, ArrowRight, List,
  // 图表和数据
  DataBoard, Connection, Files, Grid, Monitor,
  // 智能和分析
  Opportunity, MagicStick, Lightning, Cpu, Clock, Collection,
  // 警告和建议
  Warning, Timer, Top, Bottom, Minus, ChatLineRound,
  // 设置
  Setting
} from '@element-plus/icons-vue'

const app = createApp(App)

// Element Plus 组件由 vite 插件自动按需引入
app.use(router)

// 只注册使用的图标
const icons = {
  Menu, Close, DataAnalysis, ChatDotRound, Document, TrendCharts, DocumentCopy,
  RefreshRight, User, Service, Promotion,
  Upload, UploadFilled, DocumentChecked,
  Search, Aim, Check, CircleCheck, CircleClose, ArrowRight, List,
  DataBoard, Connection, Files, Grid, Monitor,
  Opportunity, MagicStick, Lightning, Cpu, Clock, Collection,
  Warning, Timer, Top, Bottom, Minus, ChatLineRound,
  Setting
}

for (const [name, component] of Object.entries(icons)) {
  app.component(name, component)
}

// 全局挂载 API 服务
app.config.globalProperties.$api = api
app.config.globalProperties.$request = request
app.config.globalProperties.$apiEndpoints = apiEndpoints

app.mount('#app')
