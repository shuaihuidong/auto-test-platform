import { get, post, put, del } from './request'
import type { Script, ScriptForm } from '@/types/script'

export async function getScriptList(projectId: number, params?: any): Promise<{ results: Script[]; count: number }> {
  return get(`/scripts/`, { project: projectId, ...params })
}

export async function getScript(id: number): Promise<Script> {
  return get(`/scripts/${id}/`)
}

export async function createScript(data: ScriptForm): Promise<Script> {
  return post('/scripts/', data)
}

export async function updateScript(id: number, data: Partial<ScriptForm>): Promise<Script> {
  return put(`/scripts/${id}/`, data)
}

export async function deleteScript(id: number): Promise<void> {
  return del(`/scripts/${id}/`)
}

export async function getScriptModules(params?: any): Promise<Script[]> {
  return get('/scripts/modules/', params)
}

export async function duplicateScript(id: number): Promise<Script> {
  return post(`/scripts/${id}/duplicate/`)
}

// 导出 API 对象供组件使用
export const scriptApi = {
  getList: (projectId: number, params?: any) => getScriptList(projectId, params),
  get: getScript,
  create: createScript,
  update: updateScript,
  delete: deleteScript,
  getModules: getScriptModules,
  duplicate: duplicateScript
}
