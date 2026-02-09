import request from './request'

// 执行机接口类型定义
export interface Executor {
  id: number
  uuid: string
  name: string
  owner: number
  owner_name: string
  status: string
  status_display: string
  scope: string
  scope_display: string
  max_concurrent: number
  current_tasks: number
  browser_types: string[]
  platform: string
  groups: Array<{ id: number; name: string; color: string }>
  tags: Array<{ id: number; name: string; color: string }>
  bound_projects: Array<{ id: number; name: string }>
  last_heartbeat: string | null
  version: string
  is_enabled: boolean
  description: string
  is_online: boolean
  is_available: boolean
  created_at: string
  updated_at: string
}

export interface ExecutorGroup {
  id: number
  name: string
  description: string
  color: string
  sort_order: number
}

export interface ExecutorTag {
  id: number
  name: string
  color: string
  sort_order: number
}

export interface Variable {
  id: number
  name: string
  value: any
  type: string
  type_display: string
  scope: string
  scope_display: string
  project: number | null
  script: number | null
  description: string
  is_sensitive: boolean
  created_by: number
  creator_name: string
  created_at: string
  updated_at: string
}

export interface TaskQueue {
  id: number
  execution: number
  executor: number | null
  status: string
  status_display: string
  priority: string
  priority_display: string
  script_data: any
  error_message: string
  assigned_at: string | null
  started_at: string | null
  completed_at: string | null
  duration: number
  created_at: string
}

// 执行机 API
export const executorApi = {
  // 获取执行机列表
  getList: (params?: { status?: string; scope?: string; platform?: string; is_enabled?: boolean }) => {
    return request.get<Executor[]>('/executors/', { params })
  },

  // 获取在线执行机
  getOnline: () => {
    return request.get<Executor[]>('/executors/online/')
  },

  // 获取可用执行机
  getAvailable: (params?: { project_id?: number }) => {
    return request.get<Executor[]>('/executors/available/', { params })
  },

  // 获取执行机详情
  getDetail: (id: number) => {
    return request.get<Executor>(`/executors/${id}/`)
  },

  // 创建执行机
  create: (data: Partial<Executor>) => {
    return request.post<Executor>('/executors/', data)
  },

  // 更新执行机
  update: (id: number, data: Partial<Executor>) => {
    return request.put<Executor>(`/executors/${id}/`, data)
  },

  // 删除执行机
  delete: (id: number) => {
    return request.delete(`/executors/${id}/`)
  },

  // 获取执行机状态日志
  getStatusLogs: (id: number) => {
    return request.get(`/executors/${id}/status_logs/`)
  },

  // 获取执行机配置
  getConfig: (id: number) => {
    return request.get(`/executors/${id}/config/`)
  },

  // 心跳（执行机调用）
  heartbeat: (id: number, data: {
    status?: string
    current_tasks?: number
    cpu_usage?: number
    memory_usage?: number
    disk_usage?: number
    message?: string
  }) => {
    return request.post(`/executors/${id}/heartbeat/`, data)
  }
}

// 执行机分组 API
export const executorGroupApi = {
  getList: () => {
    return request.get<ExecutorGroup[]>('/executor-groups/')
  },

  create: (data: Partial<ExecutorGroup>) => {
    return request.post<ExecutorGroup>('/executor-groups/', data)
  },

  update: (id: number, data: Partial<ExecutorGroup>) => {
    return request.put<ExecutorGroup>(`/executor-groups/${id}/`, data)
  },

  delete: (id: number) => {
    return request.delete(`/executor-groups/${id}/`)
  }
}

// 执行机标签 API
export const executorTagApi = {
  getList: () => {
    return request.get<ExecutorTag[]>('/executor-tags/')
  },

  create: (data: Partial<ExecutorTag>) => {
    return request.post<ExecutorTag>('/executor-tags/', data)
  },

  update: (id: number, data: Partial<ExecutorTag>) => {
    return request.put<ExecutorTag>(`/executor-tags/${id}/`, data)
  },

  delete: (id: number) => {
    return request.delete(`/executor-tags/${id}/`)
  }
}

// 变量管理 API
export const variableApi = {
  // 获取变量列表
  getList: (params?: { scope?: string; type?: string; project?: number; script?: number }) => {
    return request.get<Variable[]>('/variables/', { params })
  },

  // 获取项目变量
  getByProject: (projectId: number) => {
    return request.get<Variable[]>(`/variables/by_project/?project_id=${projectId}`)
  },

  // 获取脚本变量（包含项目变量）
  getByScript: (scriptId: number) => {
    return request.get<Variable[]>(`/variables/by_script/?script_id=${scriptId}`)
  },

  create: (data: Partial<Variable>) => {
    return request.post<Variable>('/variables/', data)
  },

  update: (id: number, data: Partial<Variable>) => {
    return request.put<Variable>(`/variables/${id}/`, data)
  },

  delete: (id: number) => {
    return request.delete(`/variables/${id}/`)
  }
}

// 任务队列 API
export const taskQueueApi = {
  // 获取任务列表
  getList: (params?: { status?: string; priority?: string; executor?: number }) => {
    return request.get<TaskQueue[]>('/tasks/', { params })
  },

  // 获取待处理任务（执行机调用）
  getPending: (executorId: number) => {
    return request.get<TaskQueue[]>(`/tasks/pending/?executor_id=${executorId}`)
  },

  // 分配任务
  assign: (taskId: number, executorId: number) => {
    return request.post(`/tasks/${taskId}/assign/`, { executor_id: executorId })
  },

  // 开始任务
  start: (taskId: number) => {
    return request.post(`/tasks/${taskId}/start/`)
  },

  // 完成任务
  complete: (taskId: number, data: { result: any; logs?: any[]; screenshots?: any[] }) => {
    return request.post(`/tasks/${taskId}/complete/`, data)
  },

  // 取消任务
  cancel: (taskId: number) => {
    return request.post(`/tasks/${taskId}/cancel/`)
  }
}
