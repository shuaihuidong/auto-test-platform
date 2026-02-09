import { get, post, put, del } from './request'
import type { Project, ProjectForm } from '@/types/project'

export async function getProjectList(params?: any): Promise<{ results: Project[]; count: number }> {
  return get('/projects/', params)
}

export async function getProject(id: number): Promise<Project> {
  return get(`/projects/${id}/`)
}

export async function getProjectDetail(id: number): Promise<Project> {
  return get(`/projects/${id}/`)
}

export async function createProject(data: ProjectForm): Promise<Project> {
  return post('/projects/', data)
}

export async function updateProject(id: number, data: Partial<ProjectForm>): Promise<Project> {
  return put(`/projects/${id}/`, data)
}

export async function deleteProject(id: number): Promise<void> {
  return del(`/projects/${id}/`)
}

// 导出 API 对象供组件使用
export const projectApi = {
  getList: getProjectList,
  get: getProject,
  getDetail: getProjectDetail,
  create: createProject,
  update: updateProject,
  delete: deleteProject
}
