import { get, post } from './request'
import type { Execution, ExecutionCreateForm } from '@/types/execution'

export async function getExecutionList(params?: any): Promise<{ results: Execution[]; count: number }> {
  return get('/executions/', params)
}

export async function getExecution(id: number): Promise<Execution> {
  return get(`/executions/${id}/`)
}

export async function createExecution(data: ExecutionCreateForm): Promise<Execution> {
  return post('/executions/', data)
}

export async function stopExecution(id: number): Promise<{ message: string }> {
  return post(`/executions/${id}/stop/`)
}

export async function getExecutionLogs(id: number): Promise<{ logs: any[] }> {
  return get(`/executions/${id}/logs/`)
}

export async function getExecutionStatistics(): Promise<any> {
  return get('/executions/statistics/')
}

// 导出 API 对象供组件使用
export const executionApi = {
  getList: getExecutionList,
  get: getExecution,
  create: createExecution,
  stop: stopExecution,
  getLogs: getExecutionLogs,
  getStatistics: getExecutionStatistics
}
