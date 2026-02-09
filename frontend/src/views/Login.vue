<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="bg-circle circle-1"></div>
      <div class="bg-circle circle-2"></div>
      <div class="bg-circle circle-3"></div>
      <div class="bg-grid"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- 左侧品牌区 -->
      <div class="card-brand">
        <div class="brand-content">
          <div class="brand-logo">
            <div class="logo-wrapper">
              <CodeOutlined class="logo-icon" />
            </div>
          </div>
          <h2 class="brand-title">自动化测试<br>管理平台</h2>
          <p class="brand-desc">Visual Automated Testing Platform</p>

          <div class="brand-features">
            <div class="feature-tag">
              <RocketOutlined />
              <span>可视化编辑</span>
            </div>
            <div class="feature-tag">
              <ThunderboltOutlined />
              <span>多框架支持</span>
            </div>
            <div class="feature-tag">
              <BarChartOutlined />
              <span>数据报告</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="card-form">
        <div class="form-content">
          <h1 class="form-title">欢迎回来</h1>
          <p class="form-subtitle">登录您的账号以继续</p>

          <a-form
            :model="formState"
            name="login"
            @finish="handleLogin"
            autocomplete="off"
            @submit.prevent
          >
            <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
              <a-input
                v-model:value="formState.username"
                size="large"
                placeholder="用户名"
                class="input-field"
              >
                <template #prefix>
                  <UserOutlined class="input-icon" />
                </template>
              </a-input>
            </a-form-item>

            <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
              <a-input-password
                v-model:value="formState.password"
                size="large"
                placeholder="密码"
                class="input-field"
              >
                <template #prefix>
                  <LockOutlined class="input-icon" />
                </template>
              </a-input-password>
            </a-form-item>

            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                size="large"
                block
                :loading="loading"
                class="submit-btn"
              >
                <span>登 录</span>
                <ArrowRightOutlined class="btn-icon" />
              </a-button>
            </a-form-item>
          </a-form>

          <div class="form-footer">
            <p>默认账号: <code>admin</code> / <code>admin123</code></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  UserOutlined,
  LockOutlined,
  CodeOutlined,
  RocketOutlined,
  ThunderboltOutlined,
  BarChartOutlined,
  ArrowRightOutlined
} from '@ant-design/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const formState = ref({
  username: '',
  password: ''
})

async function handleLogin() {
  loading.value = true
  try {
    await userStore.login(formState.value.username, formState.value.password)
    message.success('登录成功', 1.5)  // 1.5秒后消失
    const redirect = router.currentRoute.value.query.redirect as string
    router.push(redirect || '/projects')
  } catch (error) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}
</script>

<style>
/* 全局样式覆盖 */
.login-page .ant-form-item {
  margin-bottom: 20px;
}

.login-page .ant-form-item-explain-error {
  font-size: 12px;
  margin-top: 6px;
}

.login-page .ant-input-affix-wrapper,
.login-page .ant-input {
  font-size: 15px;
  padding: 13px 16px;
  border-radius: 10px;
  border: 2px solid #e5e7eb;
  background: #f9fafb;
  color: #1f2937;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-page .ant-input-affix-wrapper:hover,
.login-page .ant-input:hover {
  border-color: #c7d2fe;
  background: #ffffff;
}

.login-page .ant-input-affix-wrapper:focus,
.login-page .ant-input-affix-wrapper-focused,
.login-page .ant-input:focus {
  border-color: #6366f1;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.08);
  outline: none;
}

.login-page .ant-input-affix-wrapper > input {
  background: transparent !important;
  color: #1f2937 !important;
}

.login-page .ant-input::placeholder,
.login-page .ant-input-affix-wrapper > input::placeholder {
  color: #9ca3af !important;
}

.login-page .ant-input-prefix {
  margin-right: 12px;
  color: #9ca3af;
}

.login-page .ant-input-password-icon {
  color: #9ca3af;
  transition: color 0.2s ease;
}

.login-page .ant-input-password-icon:hover {
  color: #6366f1;
}

.login-page .submit-btn {
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
  border: none;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-page .submit-btn:hover {
  background: linear-gradient(135deg, #5558f3 0%, #7c4ff0 50%, #9333ea 100%);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
  transform: translateY(-1px);
}

.login-page .submit-btn:active {
  transform: translateY(0);
}

.login-page .submit-btn .btn-icon {
  font-size: 14px;
  transition: transform 0.3s ease;
}

.login-page .submit-btn:hover .btn-icon {
  transform: translateX(4px);
}
</style>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
  animation: float 25s ease-in-out infinite;
}

.circle-1 {
  width: 700px;
  height: 700px;
  background: radial-gradient(circle, #6366f1 0%, #4338ca 100%);
  top: -250px;
  right: -150px;
  animation-delay: 0s;
}

.circle-2 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #8b5cf6 0%, #6d28d9 100%);
  bottom: -200px;
  left: -150px;
  animation-delay: -8s;
}

.circle-3 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #a855f7 0%, #7c3aed 100%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -16s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(40px, -40px) scale(1.1);
  }
  66% {
    transform: translate(-30px, 30px) scale(0.9);
  }
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(139, 92, 246, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(139, 92, 246, 0.05) 1px, transparent 1px);
  background-size: 60px 60px;
}

/* 登录卡片 */
.login-card {
  position: relative;
  z-index: 1;
  display: flex;
  width: 90%;
  max-width: 900px;
  background: #ffffff;
  border-radius: 24px;
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  overflow: hidden;
}

/* 左侧品牌区 */
.card-brand {
  flex: 1;
  padding: 48px;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
  color: #ffffff;
  position: relative;
  overflow: hidden;
}

.card-brand::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 30%, rgba(99, 102, 241, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(139, 92, 246, 0.3) 0%, transparent 50%);
  pointer-events: none;
}

.brand-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.brand-logo {
  margin-bottom: 32px;
}

.logo-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.logo-icon {
  font-size: 32px;
  color: #ffffff;
}

.brand-title {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.3;
  margin: 0 0 12px 0;
  background: linear-gradient(135deg, #ffffff 0%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 40px 0;
  letter-spacing: 1px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
}

.feature-tag {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
}

.feature-tag:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateX(8px);
}

.feature-tag svg {
  font-size: 16px;
  color: #a5b4fc;
}

/* 右侧表单区 */
.card-form {
  flex: 1;
  padding: 48px;
  display: flex;
  align-items: center;
}

.form-content {
  width: 100%;
  max-width: 360px;
}

.form-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.form-subtitle {
  font-size: 15px;
  color: #6b7280;
  margin: 0 0 36px 0;
}

.input-field {
  width: 100%;
}

.input-icon {
  font-size: 16px;
}

.form-footer {
  margin-top: 28px;
  text-align: center;
}

.form-footer p {
  font-size: 13px;
  color: #9ca3af;
  margin: 0;
}

.form-footer code {
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  color: #6366f1;
  margin: 0 2px;
}

/* 响应式 */
@media (max-width: 768px) {
  .login-card {
    flex-direction: column;
    max-width: 420px;
  }

  .card-brand {
    padding: 36px;
  }

  .brand-features {
    display: none;
  }

  .card-form {
    padding: 36px;
  }

  .form-content {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .login-card {
    width: 95%;
  }

  .card-brand,
  .card-form {
    padding: 28px 24px;
  }

  .brand-title {
    font-size: 24px;
  }

  .form-title {
    font-size: 24px;
  }
}
</style>
