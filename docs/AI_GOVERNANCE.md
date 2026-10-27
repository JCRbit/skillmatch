# Gobernanza de IA, matching y revisión humana

## Uso previsto

Asistir a candidatos y empresas a descubrir compatibilidad de competencias, comprender evidencias y preparar entrevistas. La herramienta no debe determinar automáticamente la contratación ni emitir rechazos definitivos. Esta definición de uso previsto debe mantenerse alineada con el comportamiento y la UI reales.

## Riesgo regulatorio

Los sistemas destinados a selección/reclutamiento pueden entrar en categorías de alto riesgo bajo el Reglamento de IA de la UE según finalidad y uso. La clasificación, obligaciones aplicables, calendario de aplicación y excepciones deben verificarse con asesoramiento cualificado y la versión vigente del Reglamento antes de un despliegue real. No afirmar que basta una auditoría técnica o el “human in the loop” para cumplir.

## Registro de sistema/modelo

Para cada componente AI documentar:

- nombre, finalidad, owner, versión/model/provider, hash de configuración/prompts;
- datos de entrada/origen, base de acceso/consentimiento y retención;
- features usados, qué no usa, idioma, limitaciones y condiciones de fallo;
- evaluación del matching/ranking, resultados y subgrupos donde sea apropiado/legal;
- amenazas y mitigaciones, acceso humano, logging y proceso de override;
- momento y criterio para revisión/reentrenamiento/desactivación.

## Matching responsable

- Priorizar evidencia de skills/proyectos verificables frente a proxies de pedigree (universidad, marca de empresa, años de experiencia).
- No inferir género, edad, origen, salud, personalidad o atributos sensibles desde nombre, foto, idioma o repositorio.
- No usar diversidad/cultura como un score opaco. Si se incluyen preferencias de entorno, deben ser explícitas, legítimas y auditadas.
- Mostrar factores con evidencias y huecos: “no se encontró evidencia” no significa “no sabe hacerlo”.
- Exponer escala del score y límites; nunca llamarlo probabilidad de éxito sin calibración validada.
- Mantener decisión humana final, posibilidad de corregir datos y registrar el override y motivos cuando se use.
- Auditar errores y posibles diferencias de impacto, con separación y gobernanza adecuada de datos demográficos.

## Métricas de evaluación

Retrieval: Recall@k, Precision@k, MRR/NDCG@k con conjunto etiquetado por evaluadores y guía de anotación.
Ranking: NDCG@k/MRR, tasa de false negative por skills, cobertura, estabilidad y análisis por idioma/familia de puestos.
Equidad: diferencias de resultados/errores por subgrupo solo si existe base legal y estadística suficiente; interpretar con cautela y no prometer paridad matemática universal.
RAG: factualidad respecto al corpus, citas correctas, refusal when unsupported, leakage/ACL tests e inyección adversarial.
UX: tiempo de cribado de baseline frente a asistido, tasa de corrección manual, abandono y satisfacción. Estudiar objetivo -60% con metodología definida; no presentarlo como hecho.

## Model card mínima

1. Propósito/uso previsto y usos prohibidos.
2. Datos de evaluación y derechos/origen.
3. Modelo/embedding/ranking y configuración.
4. Métricas con intervalos/muestras/limitaciones.
5. Análisis de errores y fairness.
6. Supervisión/override y logging.
7. Privacidad/retención.
8. Riesgos conocidos y mitigaciones.
9. Versionado, fecha, owner y plan de revisión.
