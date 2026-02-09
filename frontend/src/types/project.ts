export interface Project {
  id: number
  name: string
  description: string
  type: 'web' | 'mobile' | 'api'
  creator: number
  creator_name: string
  script_count: number
  plan_count: number
  created_at: string
  updated_at: string
}

export interface ProjectForm {
  name: string
  description: string
  type: 'web' | 'mobile' | 'api'
}
