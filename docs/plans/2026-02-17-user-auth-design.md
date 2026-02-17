# 用户认证与权限管理设计文档

## 概述

为智慧采购系统添加用户登录和权限管理功能，支持三种角色（承办人、经办人、管理员），实现数据隔离和业务统计。

## 角色定义

| 角色 | 英文标识 | 职责 | 数据权限 |
|------|---------|------|---------|
| 承办人 | handler | 项目组成员，提交采购需求 | 只看自己提交的需求 |
| 经办人 | processor | 采购中心工作人员，处理采购流程 | 看所有待处理需求 |
| 管理员 | admin | 采购中心主任，管理用户、监控统计 | 看全部数据 |

## 用户注册流程

1. 用户自注册（填写用户名、邮箱、密码、选择角色）
2. 账号创建后默认 `is_active=False`
3. 管理员在后台审核，激活用户
4. 用户登录后可正常使用系统

## 需求状态流转

```
待处理 (pending) → 处理中 (processing) → 已完成 (completed)
```

## 统计指标

1. **经办人工作量统计** - 每个经办人处理的需求数量
2. **承办人需求量统计** - 每个承办人提交的需求数量
3. **处理时效统计** - 需求从提交到完成的平均时间
4. **采购分类统计** - 各品类的采购数量

---

## 架构设计

### 整体架构变化

```
当前架构                          新增架构
┌─────────────┐                  ┌─────────────┐
│  Vue 3 前端  │                  │  Vue 3 前端  │
│  (无认证)    │      →          │  + 认证守卫   │
└──────┬──────┘                  └──────┬──────┘
       │                                │
       ▼                                ▼
┌─────────────┐                  ┌─────────────┐
│  FastAPI    │                  │  FastAPI    │
│  (无数据库)  │      →          │  + JWT认证   │
└─────────────┘                  │  + SQLite   │
                                 └─────────────┘
```

### 新增文件结构

```
backend/
├── app/
│   ├── core/
│   │   ├── database.py      # SQLite连接
│   │   ├── security.py      # JWT/密码处理
│   │   └── deps.py          # 获取当前用户依赖
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # 用户模型
│   │   └── requirement.py   # 需求模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── auth.py
│   └── api/
│       ├── auth.py          # 认证API
│       ├── users.py         # 用户管理API
│       └── statistics.py    # 统计API

frontend/src/
├── composables/
│   └── useAuth.js           # 认证逻辑
├── views/
│   ├── Login.vue            # 登录页
│   ├── Register.vue         # 注册页
│   └── Admin.vue            # 管理后台
└── router/index.js          # 添加路由守卫
```

---

## 数据库模型

### User 用户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String(50) | 用户名，唯一 |
| email | String(100) | 邮箱，唯一 |
| hashed_password | String | 加密密码 |
| role | Enum | 角色：handler/processor/admin |
| is_active | Boolean | 是否激活 |
| created_at | DateTime | 创建时间 |

### Requirement 需求表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String(200) | 需求标题 |
| content | Text | 需求内容 |
| category | String(50) | 品类 |
| status | Enum | 状态：pending/processing/completed |
| submitter_id | ForeignKey | 提交人（承办人） |
| processor_id | ForeignKey | 处理人（经办人） |
| created_at | DateTime | 提交时间 |
| updated_at | DateTime | 更新时间 |
| completed_at | DateTime | 完成时间 |

---

## API 设计

### 认证相关 `/api/auth`

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/register` | POST | 用户注册 | 公开 |
| `/login` | POST | 登录，返回JWT | 公开 |
| `/me` | GET | 获取当前用户信息 | 需登录 |
| `/change-password` | POST | 修改密码 | 需登录 |

### 用户管理 `/api/users`

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/` | GET | 获取用户列表 | 管理员 |
| `/{id}/activate` | PUT | 激活用户 | 管理员 |
| `/{id}/deactivate` | PUT | 停用用户 | 管理员 |
| `/{id}/role` | PUT | 修改用户角色 | 管理员 |

### 需求管理 `/api/requirements`

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/` | GET | 获取需求列表（按角色过滤） | 需登录 |
| `/` | POST | 提交新需求 | 承办人 |
| `/{id}` | GET | 获取需求详情 | 需登录+数据权限 |
| `/{id}/status` | PUT | 更新需求状态 | 经办人 |
| `/{id}/assign` | PUT | 分配经办人 | 经办人/管理员 |

### 统计分析 `/api/statistics`

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/processor-workload` | GET | 经办人工作量统计 | 管理员 |
| `/submitter-requests` | GET | 承办人需求量统计 | 管理员 |
| `/processing-time` | GET | 处理时效统计 | 管理员 |
| `/category-summary` | GET | 采购分类统计 | 管理员 |
| `/overview` | GET | 综合概览 | 管理员 |

---

## 前端设计

### 新增页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 登录页 | `/login` | 用户名+密码登录 |
| 注册页 | `/register` | 用户名+邮箱+密码+角色选择 |
| 管理后台 | `/admin` | 用户管理+统计仪表板 |

### 角色可见菜单

| 菜单 | 承办人 | 经办人 | 管理员 |
|------|--------|--------|--------|
| 首页 | ✓ | ✓ | ✓ |
| 需求审查 | ✓（提交） | ✓（处理） | ✓（全部） |
| 价格参考 | ✓ | ✓ | ✓ |
| 合同分析 | ✓ | ✓ | ✓ |
| AI助手 | ✓ | ✓ | ✓ |
| 管理后台 | ✗ | ✗ | ✓ |

---

## 一期功能清单

### 后端

- [ ] SQLite 数据库集成
- [ ] User 模型 + Requirement 模型
- [ ] JWT 认证中间件
- [ ] 注册/登录 API
- [ ] 用户管理 API（审核激活）
- [ ] 需求管理 API
- [ ] 基础统计 API

### 前端

- [ ] 登录页 + 注册页
- [ ] useAuth composable
- [ ] 路由守卫
- [ ] 侧边栏用户信息展示
- [ ] 管理后台页面
- [ ] 需求提交/处理功能

---

## 二期预留功能

- [ ] 处理时效趋势图表
- [ ] 采购分类饼图/柱状图
- [ ] 批量用户导入
- [ ] 操作日志审计
- [ ] 数据导出功能
