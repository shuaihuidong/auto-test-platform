import { get, post, put, del } from './request'
import type { User, LoginResponse } from '@/types/user'

export async function login(username: string, password: string): Promise<LoginResponse> {
  return post('/auth/login/', { username, password })
}

export async function logout(): Promise<{ message: string }> {
  return post('/auth/logout/')
}

export async function getUserInfo(): Promise<User> {
  return get('/users/me/')
}

export async function getUserList(params?: any): Promise<{ results: User[]; count: number }> {
  return get('/users/', params)
}

export async function getUser(id: number): Promise<User> {
  return get(`/users/${id}/`)
}

export async function createUser(data: any): Promise<User> {
  return post('/users/', data)
}

export async function updateUser(id: number, data: any): Promise<User> {
  return put(`/users/${id}/`, data)
}

export async function deleteUser(id: number): Promise<void> {
  return del(`/users/${id}/`)
}

export async function setUserRole(id: number, role: string): Promise<{ message: string; user: User }> {
  return post(`/users/${id}/set_role/`, { role })
}

export async function changePassword(oldPassword: string, newPassword: string): Promise<{ message: string }> {
  return post('/users/change_password/', { old_password: oldPassword, new_password: newPassword })
}

// 导出 API 对象供组件使用
export const userApi = {
  login,
  logout,
  getMe: getUserInfo,
  getList: getUserList,
  get: getUser,
  create: createUser,
  update: updateUser,
  delete: deleteUser,
  setRole: setUserRole,
  changePassword
}
