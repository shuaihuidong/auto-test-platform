import { get, post, put, del } from './request'
import type { Project, ProjectForm } from '@/types/project'

export interface ProjectMember {
  id: string | number
  user_id: number
  username: string
  email: string
  role: 'owner' | 'admin' | 'member'
  joined_at: string
  is_owner: boolean
}

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

// 项目成员相关API
export async function getMembers(projectId: number): Promise<ProjectMember[]> {
  return get(`/projects/${projectId}/members/`)
}

export async function addMember(projectId: number, data: { user: number; role: string }): Promise<ProjectMember> {
  return post(`/projects/${projectId}/members/`, data)
}

export async function removeMember(projectId: number, memberId: number): Promise<void> {
  return del(`/projects/${projectId}/members/${memberId}/`)
}

export async function changeMemberRole(
  projectId: number,
  memberId: number,
  role: string
): Promise<ProjectMember> {
  return put(`/projects/${projectId}/members/${memberId}/`, { role })
}

// 导出 API 对象供组件使用
export const projectApi = {
  getList: getProjectList,
  get: getProject,
  getDetail: getProjectDetail,
  create: createProject,
  update: updateProject,
  delete: deleteProject,
  getMembers,
  addMember,
  removeMember,
  changeMemberRole
}
