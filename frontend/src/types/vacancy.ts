export type SeniorityLevel = 'junior' | 'mid' | 'senior'
export type WorkMode = 'remote' | 'hybrid' | 'onsite'
export type ContractType = 'indefinido' | 'practicas' | 'determinado' | 'freelance'
export type VacancyStatus = 'draft' | 'published'

export interface ObjectiveConditions {
  location: string
  mode: WorkMode
  contract_type: ContractType
  salary_min: number | null
  salary_max: number | null
  currency: string
}

export interface VacancyCreatePayload {
  title: string
  description: string
  seniority: SeniorityLevel
  essential_requirements: string[]
  desirable_requirements: string[]
  objective_conditions: ObjectiveConditions
  status: VacancyStatus
}

export interface VacancyRecord extends VacancyCreatePayload {
  id: string
  created_at: string
}
