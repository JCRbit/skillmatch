import { useState } from 'react'
import type { FormEvent } from 'react'
import type {
  ContractType,
  SeniorityLevel,
  VacancyCreatePayload,
  VacancyStatus,
  WorkMode,
} from '../types/vacancy'

interface VacancyFormProps {
  onSubmitVacancy: (payload: VacancyCreatePayload) => Promise<void>
  isSubmitting?: boolean
}

export function VacancyForm({ onSubmitVacancy, isSubmitting = false }: VacancyFormProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [seniority, setSeniority] = useState<SeniorityLevel>('junior')

  const [essentialInput, setEssentialInput] = useState('')
  const [essentialRequirements, setEssentialRequirements] = useState<string[]>([])

  const [desirableInput, setDesirableInput] = useState('')
  const [desirableRequirements, setDesirableRequirements] = useState<string[]>([])

  const [location, setLocation] = useState('Madrid')
  const [mode, setMode] = useState<WorkMode>('hybrid')
  const [contractType, setContractType] = useState<ContractType>('indefinido')
  const [salaryMin, setSalaryMin] = useState('')
  const [salaryMax, setSalaryMax] = useState('')
  const [currency, setCurrency] = useState('EUR')
  const [status, setStatus] = useState<VacancyStatus>('published')

  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  function addEssentialRequirement() {
    const trimmed = essentialInput.trim()
    if (!trimmed) return
    if (!essentialRequirements.some((item) => item.toLowerCase() === trimmed.toLowerCase())) {
      setEssentialRequirements((prev) => [...prev, trimmed])
    }
    setEssentialInput('')
  }

  function removeEssentialRequirement(target: string) {
    setEssentialRequirements((prev) => prev.filter((item) => item !== target))
  }

  function addDesirableRequirement() {
    const trimmed = desirableInput.trim()
    if (!trimmed) return
    if (!desirableRequirements.some((item) => item.toLowerCase() === trimmed.toLowerCase())) {
      setDesirableRequirements((prev) => [...prev, trimmed])
    }
    setDesirableInput('')
  }

  function removeDesirableRequirement(target: string) {
    setDesirableRequirements((prev) => prev.filter((item) => item !== target))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setErrorMessage(null)
    setSuccessMessage(null)

    const cleanTitle = title.trim()
    const cleanDescription = description.trim()
    const cleanLocation = location.trim()

    if (cleanTitle.length < 3) {
      setErrorMessage('El titulo de la vacante debe tener al menos 3 caracteres.')
      return
    }
    if (cleanDescription.length < 15) {
      setErrorMessage('La descripcion del puesto debe detallar responsabilidades (minimo 15 caracteres).')
      return
    }
    if (essentialRequirements.length === 0) {
      setErrorMessage('Anade al menos un requisito esencial para poder evaluar el encaje con evidencia.')
      return
    }

    const parsedMin = salaryMin.trim() === '' ? null : Number(salaryMin)
    const parsedMax = salaryMax.trim() === '' ? null : Number(salaryMax)

    if ((parsedMin !== null && Number.isNaN(parsedMin)) || (parsedMax !== null && Number.isNaN(parsedMax))) {
      setErrorMessage('El rango salarial debe contener importes numericos validos.')
      return
    }
    if (parsedMin !== null && parsedMin < 0) {
      setErrorMessage('El salario minimo no puede ser negativo.')
      return
    }
    if (parsedMin !== null && parsedMax !== null && parsedMin > parsedMax) {
      setErrorMessage('El salario minimo no puede superar al salario maximo.')
      return
    }

    const payload: VacancyCreatePayload = {
      title: cleanTitle,
      description: cleanDescription,
      seniority,
      essential_requirements: essentialRequirements,
      desirable_requirements: desirableRequirements,
      objective_conditions: {
        location: cleanLocation || 'Remoto / Espana',
        mode,
        contract_type: contractType,
        salary_min: parsedMin,
        salary_max: parsedMax,
        currency,
      },
      status,
    }

    try {
      await onSubmitVacancy(payload)
      setSuccessMessage('Vacante guardada correctamente.')
      setTitle('')
      setDescription('')
      setEssentialRequirements([])
      setDesirableRequirements([])
      setSalaryMin('')
      setSalaryMax('')
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Error inesperado al guardar la vacante.')
    }
  }

  return (
    <form className="vacancy-form" onSubmit={handleSubmit} noValidate>
      <fieldset className="form-section">
        <legend>1. Definicion del puesto y seniority</legend>

        <div className="form-grid">
          <label className="form-field">
            <span>Titulo de la vacante *</span>
            <input
              type="text"
              name="title"
              placeholder="Ej. Backend Python Junior"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              required
            />
          </label>

          <label className="form-field">
            <span>Nivel de seniority *</span>
            <select
              name="seniority"
              value={seniority}
              onChange={(event) => setSeniority(event.target.value as SeniorityLevel)}
            >
              <option value="junior">Junior (0-2 anos / portfolio verificable)</option>
              <option value="mid">Mid (2-5 anos)</option>
              <option value="senior">Senior (+5 anos)</option>
            </select>
          </label>
        </div>

        <label className="form-field">
          <span>Descripcion y proposito del rol *</span>
          <textarea
            name="description"
            rows={4}
            placeholder="Describe el equipo, el impacto esperado y las tareas principales sin sesgos ni requisitos ocultos."
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            required
          />
        </label>
      </fieldset>

      <fieldset className="form-section" data-testid="essential-requirements-section">
        <legend>2. Requisitos esenciales (imprescindibles)</legend>
        <p className="section-hint">
          Competencias indispensables para desempenar el puesto. Se usan como criterios base explicables.
        </p>

        <div className="tag-input-row">
          <input
            type="text"
            aria-label="Nuevo requisito esencial"
            placeholder="Ej. Python 3.11+, SQL basico, Git"
            value={essentialInput}
            onChange={(event) => setEssentialInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                event.preventDefault()
                addEssentialRequirement()
              }
            }}
          />
          <button type="button" className="btn-secondary" onClick={addEssentialRequirement}>
            Anadir esencial
          </button>
        </div>

        {essentialRequirements.length > 0 ? (
          <ul className="tag-list" aria-label="Lista de requisitos esenciales">
            {essentialRequirements.map((req) => (
              <li key={req} className="tag-chip tag-essential">
                <span>{req}</span>
                <button
                  type="button"
                  aria-label={`Eliminar requisito esencial ${req}`}
                  onClick={() => removeEssentialRequirement(req)}
                >
                  x
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-hint">Aun no has anadido requisitos esenciales.</p>
        )}
      </fieldset>

      <fieldset className="form-section" data-testid="desirable-requirements-section">
        <legend>3. Requisitos deseables (valorables / no excluyentes)</legend>
        <p className="section-hint">
          Conocimientos complementarios que suman afinidad pero no bloquean candidaturas junior.
        </p>

        <div className="tag-input-row">
          <input
            type="text"
            aria-label="Nuevo requisito deseable"
            placeholder="Ej. Docker, pytest, FastAPI"
            value={desirableInput}
            onChange={(event) => setDesirableInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                event.preventDefault()
                addDesirableRequirement()
              }
            }}
          />
          <button type="button" className="btn-secondary" onClick={addDesirableRequirement}>
            Anadir deseable
          </button>
        </div>

        {desirableRequirements.length > 0 ? (
          <ul className="tag-list" aria-label="Lista de requisitos deseables">
            {desirableRequirements.map((req) => (
              <li key={req} className="tag-chip tag-desirable">
                <span>{req}</span>
                <button
                  type="button"
                  aria-label={`Eliminar requisito deseable ${req}`}
                  onClick={() => removeDesirableRequirement(req)}
                >
                  x
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="empty-hint">Sin requisitos deseables anadidos (opcional).</p>
        )}
      </fieldset>

      <fieldset className="form-section" data-testid="objective-conditions-section">
        <legend>4. Condiciones objetivas de la oferta</legend>

        <div className="form-grid">
          <label className="form-field">
            <span>Modalidad de trabajo</span>
            <select name="mode" value={mode} onChange={(event) => setMode(event.target.value as WorkMode)}>
              <option value="remote">Remoto</option>
              <option value="hybrid">Hibrido</option>
              <option value="onsite">Presencial</option>
            </select>
          </label>

          <label className="form-field">
            <span>Ubicacion</span>
            <input
              type="text"
              name="location"
              placeholder="Ej. Madrid / Remoto Espana"
              value={location}
              onChange={(event) => setLocation(event.target.value)}
            />
          </label>

          <label className="form-field">
            <span>Tipo de contrato</span>
            <select
              name="contract_type"
              value={contractType}
              onChange={(event) => setContractType(event.target.value as ContractType)}
            >
              <option value="indefinido">Indefinido</option>
              <option value="practicas">Practicas / Formacion</option>
              <option value="determinado">Temporal</option>
              <option value="freelance">Freelance / Mercantil</option>
            </select>
          </label>

          <label className="form-field">
            <span>Estado de publicacion</span>
            <select
              name="status"
              value={status}
              onChange={(event) => setStatus(event.target.value as VacancyStatus)}
            >
              <option value="published">Publicada</option>
              <option value="draft">Borrador</option>
            </select>
          </label>
        </div>

        <div className="form-grid salary-grid">
          <label className="form-field">
            <span>Salario minimo anual bruto</span>
            <input
              type="number"
              name="salary_min"
              min="0"
              step="500"
              placeholder="22000"
              value={salaryMin}
              onChange={(event) => setSalaryMin(event.target.value)}
            />
          </label>

          <label className="form-field">
            <span>Salario maximo anual bruto</span>
            <input
              type="number"
              name="salary_max"
              min="0"
              step="500"
              placeholder="28000"
              value={salaryMax}
              onChange={(event) => setSalaryMax(event.target.value)}
            />
          </label>

          <label className="form-field">
            <span>Divisa</span>
            <select name="currency" value={currency} onChange={(event) => setCurrency(event.target.value)}>
              <option value="EUR">EUR</option>
              <option value="USD">USD</option>
              <option value="GBP">GBP</option>
            </select>
          </label>
        </div>
      </fieldset>

      {errorMessage && (
        <p role="alert" className="feedback-error">
          {errorMessage}
        </p>
      )}
      {successMessage && (
        <p role="status" className="feedback-success">
          {successMessage}
        </p>
      )}

      <div className="form-actions">
        <button type="submit" className="btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Guardando vacante...' : 'Guardar vacante'}
        </button>
      </div>
    </form>
  )
}
