import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, getUserInfo } from '@/api/user'
import type { User } from '@/types/user'

const STORAGE_KEY = 'user_info'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  const isLoggedIn = computed(() => !!user.value)

  // 从 localStorage 恢复用户状态
  function restoreState() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const userData = JSON.parse(saved)
        user.value = userData
      }
    } catch (e) {
      console.error('Failed to restore user state:', e)
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  // 保存用户状态到 localStorage
  function saveState() {
    if (user.value) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(user.value))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  async function login(username: string, password: string) {
    const res = await loginApi(username, password)
    user.value = res.user
    saveState()
    return res
  }

  async function logout() {
    await logoutApi()
    user.value = null
    token.value = null
    saveState()
  }

  async function fetchUserInfo() {
    const res = await getUserInfo()
    user.value = res
    saveState()
    return res
  }

  function setUser(userData: User) {
    user.value = userData
    saveState()
  }

  return {
    user,
    token,
    isLoggedIn,
    login,
    logout,
    fetchUserInfo,
    setUser,
    restoreState
  }
})
