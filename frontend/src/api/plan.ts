import request from './request'

// 计划接口类型定义
export interface Plan {
  id: number
  project: number
  name: string
  description: string
  script_ids: number[]
  execution_order: 'sequential' | 'parallel'
  continue_on_failure: boolean
  cron_expression: string
  status: 'active' | 'disabled'
  last_status: string
  last_run: string
  script_count: number
  created_by: number
  created_at: string
  updated_at: string
}

export interface PlanForm {
  project: number
  name: string
  description?: string
  script_ids: number[]
  execution_order?: 'sequential' | 'parallel'
  continue_on_failure?: boolean
  cron_expression?: string
}

// 计划管理 API
export const planApi = {
  // 获取计划列表
  getList: (params?: { project?: number; status?: string }) => {
    return request.get<{ results: Plan[]; count: number }>('/plans/', { params })
  },

  // 获取计划详情
  getDetail: (id: number) => {
    return request.get<Plan>(`/plans/${id}/`)
  },

  // 创建计划
  create: (data: PlanForm) => {
    return request.post<Plan>('/plans/', data)
  },

  // 更新计划
  update: (id: number, data: Partial<PlanForm>) => {
    return request.put<Plan>(`/plans/${id}/`, data)
  },

  // 删除计划
  delete: (id: number) => {
    return request.delete(`/plans/${id}/`)
  },

  // 运行计划
  run: (id: number) => {
    return request.post(`/plans/${id}/run/`)
  }
}
