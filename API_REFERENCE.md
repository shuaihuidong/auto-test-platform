# API 参考文档

本文档详细描述了自动化测试平台的所有 API 端点。

## 目录

- [认证](#认证)
- [通用说明](#通用说明)
- [认证接口](#认证接口)
- [用户管理](#用户管理)
- [项目管理](#项目管理)
- [脚本管理](#脚本管理)
- [测试计划](#测试计划)
- [执行管理](#执行管理)
- [执行器管理](#执行器管理)
- [报告管理](#报告管理)
- [驱动管理](#驱动管理)
- [变量管理](#变量管理)
- [RabbitMQ用户管理](#rabbitmq用户管理)
- [WebSocket接口](#websocket接口)
- [错误码](#错误码)

---

## 认证

API 使用 Token 认证和 Session 认证两种方式。

### Token 认证（推荐）

在请求头中添加 Authorization 字段：

```
Authorization: Token your_token_here
```

### Session 认证

登录后 Django 会创建 Session，浏览器会自动携带 Cookie。

> **注意**: 使用 Session 认证时，POST/PUT/DELETE 请求需要 CSRF Token

---

## 通用说明

### 基础 URL

```
http://your-domain/api/
```

### 请求格式

```
Content-Type: application/json
```

### 响应格式

```json
{
  "data": {...},
  "message": "success"
}
```

### 分页

列表接口支持分页：

```
GET /api/users/?page=1&page_size=20
```

响应：

```json
{
  "count": 100,
  "next": "http://...?page=2",
  "previous": null,
  "results": [...]
}
```

---

## 认证接口

### 登录

```
POST /api/auth/login/
```

**请求体：**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应：**

```json
{
  "message": "登录成功",
  "token": "a1b2c3d4e5f6...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "super_admin",
    "role_display": "超级管理员"
  }
}
```

### 登出

```
POST /api/auth/logout/
```

**权限**: 认证用户

**响应：**

```json
{
  "message": "登出成功"
}
```

---

## 用户管理

### 获取用户列表

```
GET /api/users/
```

**权限**: 测试人员及以上

**响应：**

```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "super_admin",
      "role_display": "超级管理员",
      "rabbitmq_enabled": true,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

### 创建用户

```
POST /api/users/
```

**权限**: 管理员及以上

**请求体：**

```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "role": "tester",
  "rabbitmq_enabled": false
}
```

### 获取单个用户

```
GET /api/users/{id}/
```

**权限**: 认证用户

### 更新用户

```
PUT /api/users/{id}/
```

**权限**:
- 用户可以更新自己的信息（仅 email 和 password）
- 管理员可以更新所有用户

**请求体：**

```json
{
  "email": "newemail@example.com",
  "password": "newpassword"
}
```

### 删除用户

```
DELETE /api/users/{id}/
```

**权限**: 管理员及以上

### 获取当前用户信息

```
GET /api/users/me/
```

**权限**: 认证用户

### 获取当前用户权限

```
GET /api/users/permissions/
```

**权限**: 认证用户

**响应：**

```json
{
  "role": "super_admin",
  "role_display": "超级管理员",
  "permissions": ["view", "list", "create", "update", "delete", "execute", "manage_users", "manage_settings"]
}
```

### 设置用户角色

```
POST /api/users/{id}/set_role/
```

**权限**: 超级管理员

**请求体：**

```json
{
  "role": "admin"
}
```

### 重置用户密码

```
POST /api/users/{id}/reset_password/
```

**权限**: 管理员及以上

**响应：**

```json
{
  "message": "用户 xxx 的密码已重置为默认密码",
  "default_password": "123456"
}
```

### 修改自己的密码

```
POST /api/users/change_password/
```

**权限**: 认证用户

**请求体：**

```json
{
  "old_password": "oldpass",
  "new_password": "newpass"
}
```

### 获取角色列表

```
GET /api/users/roles/
```

**权限**: 测试人员及以上

**响应：**

```json
{
  "results": [
    {
      "value": "super_admin",
      "label": "超级管理员",
      "level": 4,
      "permissions": [...],
      "user_count": 1
    }
  ]
}
```

---

## 项目管理

### 获取项目列表

```
GET /api/projects/
```

**权限**: 测试人员及以上

### 创建项目

```
POST /api/projects/
```

**权限**: 测试人员及以上

**请求体：**

```json
{
  "name": "我的项目",
  "description": "项目描述",
  "type": "web",
  "framework": "selenium"
}
```

### 获取/更新/删除项目

```
GET /api/projects/{id}/
PUT /api/projects/{id}/
DELETE /api/projects/{id}/
```

### 获取项目成员

```
GET /api/projects/{project_id}/members/
```

### 添加项目成员

```
POST /api/projects/{project_id}/members/
```

### 绑定执行器

```
POST /api/projects/{id}/bind_executor/
```

---

## 脚本管理

### 获取脚本列表

```
GET /api/scripts/
```

**权限**: 测试人员及以上

**查询参数：**
- `project`: 项目ID
- `search`: 搜索关键词

### 创建脚本

```
POST /api/scripts/
```

**请求体：**

```json
{
  "name": "登录测试",
  "project": 1,
  "description": "测试用户登录功能",
  "framework": "selenium",
  "steps": [...]
}
```

### 获取/更新/删除脚本

```
GET /api/scripts/{id}/
PUT /api/scripts/{id}/
DELETE /api/scripts/{id}/
```

### 复制脚本

```
POST /api/scripts/{id}/copy/
```

### 获取脚本模块

```
GET /api/scripts/modules/
```

### 保存为模块

```
POST /api/scripts/{id}/save_as_module/
```

### 调试脚本

```
POST /api/scripts/{id}/debug/
```

### 数据源管理

```
GET /api/scripts/datasources/
POST /api/scripts/datasources/
GET /api/scripts/datasources/{id}/
PUT /api/scripts/datasources/{id}/
DELETE /api/scripts/datasources/{id}/
```

---

## 测试计划

### 获取计划列表

```
GET /api/plans/
```

### 创建计划

```
POST /api/plans/
```

**请求体：**

```json
{
  "name": "回归测试计划",
  "project": 1,
  "scripts": [1, 2, 3],
  "execution_mode": "sequential"
}
```

### 获取/更新/删除计划

```
GET /api/plans/{id}/
PUT /api/plans/{id}/
DELETE /api/plans/{id}/
```

### 执行计划

```
POST /api/plans/{id}/execute/
```

---

## 执行管理

### 获取执行记录列表

```
GET /api/executions/
```

**查询参数：**
- `project`: 项目ID
- `status`: 执行状态 (pending/running/completed/failed)
- `script`: 脚本ID

### 创建执行

```
POST /api/executions/
```

**请求体：**

```json
{
  "script": 1,
  "executor": "executor-uuid"
}
```

### 获取执行详情

```
GET /api/executions/{id}/
```

### 停止执行

```
POST /api/executions/{id}/stop/
```

### 获取执行日志

```
GET /api/executions/{id}/logs/
```

### 获取执行步骤详情

```
GET /api/executions/{id}/steps/
```

---

## 执行器管理

### 获取执行器列表

```
GET /api/executors/
```

### 获取执行器详情

```
GET /api/executors/{id}/
```

### 执行器注册

```
POST /api/executor/register/
```

**权限**: 公开

**请求体：**

```json
{
  "name": "本地执行机",
  "uuid": "generated-uuid",
  "ip_address": "192.168.1.100",
  "system_info": {
    "os": "Windows 10",
    "cpu": "Intel i7",
    "memory": "16GB"
  }
}
```

### 执行器心跳

```
POST /api/executor/heartbeat/
```

**权限**: 公开

**请求体：**

```json
{
  "executor_uuid": "uuid-string",
  "status": "idle",
  "cpu_usage": 30.5,
  "memory_usage": 45.2,
  "running_tasks": 0
}
```

### 执行器分组管理

```
GET /api/executor-groups/
POST /api/executor-groups/
GET /api/executor-groups/{id}/
PUT /api/executor-groups/{id}/
DELETE /api/executor-groups/{id}/
```

### 执行器标签管理

```
GET /api/executor-tags/
POST /api/executor-tags/
GET /api/executor-tags/{id}/
PUT /api/executor-tags/{id}/
DELETE /api/executor-tags/{id}/
```

---

## 报告管理

### 获取报告列表

```
GET /api/reports/
```

### 获取报告详情

```
GET /api/reports/{id}/
```

### 导出报告

```
GET /api/reports/{id}/export/
```

**查询参数：**
- `format`: 导出格式 (html/pdf)

### 删除报告

```
DELETE /api/reports/{id}/
```

---

## 驱动管理

### 获取驱动列表

```
GET /api/drivers/
```

### 获取驱动详情

```
GET /api/drivers/{id}/
```

### 上传驱动

```
POST /api/drivers/
```

### 删除驱动

```
DELETE /api/drivers/{id}/
```

---

## 变量管理

### 获取变量列表

```
GET /api/variables/
```

**查询参数：**
- `project`: 项目ID
- `scope`: 变量范围 (project/script)

### 创建变量

```
POST /api/variables/
```

**请求体：**

```json
{
  "name": "base_url",
  "value": "https://example.com",
  "project": 1,
  "is_sensitive": false
}
```

### 更新/删除变量

```
PUT /api/variables/{id}/
DELETE /api/variables/{id}/
```

---

## RabbitMQ用户管理

### 获取用户RabbitMQ配置

```
GET /api/users/{id}/get_rabbitmq_config/
```

**权限**: 本人或管理员

**响应：**

```json
{
  "username": "user123",
  "password": "decrypted_password",
  "host": "192.168.1.100",
  "port": 5672,
  "vhost": "/"
}
```

### 启用/禁用用户RabbitMQ功能

```
POST /api/users/{id}/toggle_rabbitmq/
```

**权限**: 管理员及以上

**请求体：**

```json
{
  "enable": true
}
```

### 创建独立RabbitMQ用户

```
POST /api/users/create_rabbitmq_user/
```

**权限**: 超级管理员

**请求体：**

```json
{
  "username": "executor_user",
  "password": "secure_password",
  "tags": "management"
}
```

### 获取RabbitMQ用户列表

```
GET /api/users/list_rabbitmq_users/
```

**权限**: 超级管理员

### 删除RabbitMQ用户

```
POST /api/users/delete_rabbitmq_user/
DELETE /api/users/delete_rabbitmq_user/
```

**权限**: 超级管理员

**请求体：**

```json
{
  "username": "executor_user"
}
```

### 修改RabbitMQ用户密码

```
POST /api/users/update_rabbitmq_user_password/
```

**权限**: 超级管理员

**请求体：**

```json
{
  "username": "executor_user",
  "password": "new_password"
}
```

---

## WebSocket接口

### 执行器状态监听

```
WS /ws/executor-status/
```

**认证**: 需要在 URL 参数中携带 token

```
ws://domain/ws/executor-status/?token=your_token
```

**消息格式：**

```json
{
  "type": "executor_status",
  "data": {
    "executor_id": "uuid",
    "status": "running",
    "task_id": 123
  }
}
```

### 执行进度监听

```
WS /ws/execution/{execution_id}/
```

**消息格式：**

```json
{
  "type": "step_update",
  "data": {
    "step_index": 0,
    "status": "passed",
    "message": "步骤执行成功"
  }
}
```

---

## 错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无返回内容） |
| 400 | 请求参数错误 |
| 401 | 未认证/认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 405 | 请求方法不允许 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用（如 RabbitMQ 连接失败） |

### 错误响应格式

```json
{
  "error": "错误描述信息",
  "detail": "详细错误信息"
}
```

---

## 权限等级说明

| 角色 | 等级 | 权限范围 |
|------|------|----------|
| super_admin | 4 | 全部权限 + 用户管理 + 系统设置 + RabbitMQ管理 |
| admin | 3 | 查看、创建、更新、删除、执行 |
| tester | 2 | 查看、创建脚本、执行测试、管理自己的账号 |
| guest | 1 | 仅查看权限 |

---

**最后更新**: 2026-03-07
