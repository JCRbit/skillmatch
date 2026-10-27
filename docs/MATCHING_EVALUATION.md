# Matching: baseline, evaluación y criterio de promoción

## Fase A — baseline sin entrenamiento pretendido

1. Definir un esquema de skills (normalizadas y sinónimos) y evidencia de proyectos.
2. Generar embeddings de perfil/oferta con modelo versionado y evaluar corpus español/inglés representativo.
3. Obtener candidatos top-k por Qdrant y aplicar filtros estructurados explícitos.
4. Calcular un score explicable con componentes visibles (skill match, evidencia, preferencias explícitas, requisitos esenciales). Ponderaciones son hipótesis documentadas, no verdades del modelo.
5. Devolver factores/evidencias usando datos calculados, no que un LLM fabrique motivos.

## Qué significa score

Normalizar un score a 0–100 no lo convierte en probabilidad. La UI debe describirlo como `indicador de compatibilidad` y mostrar los factores. Si se desea interpretar como probabilidad, necesita datos, calibración, intervalos, validación externa y revisión de riesgos.

## Fase B — ranking aprendido (solo si viable)

- Confirmar datos etiquetados apropiados, permisos, representatividad y definición de relevancia.
- Establecer split sin fuga por candidato/empresa/tiempo. Evitar usar el mismo candidato/empresa en train y test de forma que infle métricas.
- Comparar contra baseline simple; registrar hiperparámetros, semilla, dataset versionado y artefactos.
- Evaluar NDCG@k, MRR, Recall@k, cobertura, ranking por categorías, calibración si aplica y análisis de errores.
- Si el dataset válido no existe, mantener baseline; no fabricar etiquetas para presumir un modelo “entrenado”.

## Latencia

Prueba determinista con versiones de software/modelo, tamaño de corpus, dimensiones, hardware, concurrencia, filtros, top-k y warm/cold cache. Reportar p50/p95/p99 y throughput.

- Target acordado: vector retrieval p95 <300 ms bajo la configuración documentada.
- Reportar por separado embedding, DB/vector retrieval, reranking y generación LLM. LLM externo puede tardar más; no ocultarlo en la cifra de retrieval.
- No hacer un claim de producción con solo una llamada manual o una muestra pequeña.

## Conjunto de evaluación

Usar ofertas y perfiles sintéticos al principio; incluir casos claros, difíciles, multilingües, falsos amigos, descripciones vacías, CV con datos faltantes, perfiles equivalentes con nombres diferentes, y pruebas de atributos/proxies indebidos. Versionar guía de anotación, etiquetas y conjunto de test.
