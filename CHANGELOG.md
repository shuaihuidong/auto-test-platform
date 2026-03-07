# 变更日志

所有重要的更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.4.2] - 2026-03-07

### 🐛 Bug修复

#### 前端修复
- 🐛 修复 `AccountRoleManage.vue` 中 RabbitMQ 相关 API 调用未携带 Token 的问题
  - 将原生 `axios` 替换为配置好的 `request` 实例
  - 修复 API 路径重复问题（`/api/api/...` -> `/api/...`）
  - 修复响应数据访问问题（`response.data.users` -> `response.users`）

#### 后端修复
- 🐛 优化 CSRF 中间件，对携带 Token 认证的 API 请求豁免 CSRF 检查
  - 新增 `_has_valid_token_auth()` 方法检测 Token 认证
  - Token 认证请求自动豁免 CSRF 保护

### 📚 文档
- 📄 新增 `API_REFERENCE.md` - 完整的 API 参考文档

---

## [1.4.1] - 2026-03-06

### 🔐 安全性修复

#### 新增
- ✅ **Redis Channel层** - 使用Redis替代内存Channel层，支持多进程部署
- ✅ **密钥安全检查** - 生产环境启动时强制检查密钥安全性
- ✅ **RabbitMQ密码加密** - 使用Fernet加密存储RabbitMQ密码
- ✅ **密码迁移命令** - 提供数据迁移命令 `python manage.py encrypt_rabbitmq_passwords`

#### 变更
- 🔒 **CSRF保护优化** - 从完全禁用改为精确豁免特定API端点
  - 仅豁免: `/api/auth/login/`, `/api/auth/logout/`, `/api/executor/register/`, `/api/executor/heartbeat/`
  - 其他API端点恢复CSRF保护

#### 依赖更新
- ➕ 添加 `cryptography==41.0.7` 用于密码加密
- ➕ 依赖 `channels-redis==4.2.0` 用于Channel层

#### 配置要求
- 📝 生产环境必须设置 `DJANGO_SECRET_KEY` 环境变量
- 📝 生产环境必须设置 `RABBITMQ_ENCRYPTION_KEY` 环境变量
- 📝 必须安装并启动Redis服务

#### 文档
- 📚 新增 `SECURITY.md` - 完整安全性说明文档
- 📚 新增 `QUICK_START_SECURITY.md` - 快速配置指南

---

## [1.4.0] - 2026-02-12

### 新增
- ✨ RabbitMQ 用户级集成：平台用户可直接关联 RabbitMQ 账号
- ✨ 用户可在「账号角色管理」查看自己的 RabbitMQ 配置信息
- ✨ 测试人员及以上角色可访问账号角色管理页面
- ✨ 帮助中心更新：添加配置信息获取位置说明

### 优化
- ⚡ 权限细化：用户只能编辑自己的账号信息
- ⚡ 配置向导简化：默认远程部署，移除本地安装说明
- ⚡ 执行机配置更便捷：一键复制配置信息

### 修复
- 🐛 修复项目执行机绑定弹窗无法关闭的问题
- 🐛 修复 API 返回格式不一致导致的前端错误
- 🐛 修复用户列表权限检查问题

---

## [1.3.0] - 2026-02-11

### 新增
- ✨ RabbitMQ 用户级集成：平台用户可直接关联 RabbitMQ 账号
- ✨ 超级管理员可创建/管理独立 RabbitMQ 用户
- ✨ 用户可查看自己的 RabbitMQ 配置信息
- ✨ 超级管理员可启用/禁用用户的 RabbitMQ 功能

### 优化
- ⚡ 远程执行机配置简化
- ⚡ 执行机安装向导优化

### 修复
- 🐛 修复远程执行机 RabbitMQ 连接问题

---

## 路线图

### 计划中的功能

#### v1.5.0
- [ ] 完善测试覆盖率（目标70%+）
- [ ] 添加API文档（Swagger/OpenAPI）
- [ ] 添加审计日志系统
- [ ] 性能优化（N+1查询、前端懒加载）

#### v2.0.0
- [ ] Playwright 框架支持
- [ ] Appium 移动端自动化支持
- [ ] HttpRunner API 测试支持
- [ ] CI/CD 集成 (Jenkins, GitLab CI)
- [ ] 分布式执行集群
- [ ] PostgreSQL 数据库支持
- [ ] 监控告警系统

---

## 版本命名规则

- **主版本号 (Major)**: 不兼容的API变更
- **次版本号 (Minor)**: 向后兼容的功能新增
- **修订号 (Patch)**: 向后兼容的问题修复

## 变更类型

- `新增` - 新功能
- `变更` - 现有功能的变更
- `弃用` - 即将删除的功能
- `移除` - 已删除的功能
- `修复` - Bug修复
- `安全` - 安全性修复
