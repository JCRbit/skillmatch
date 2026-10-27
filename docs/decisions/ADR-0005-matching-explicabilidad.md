# ADR-0005 — Matching explicable y entrenamiento responsable

- Estado: Propuesto

Construir primero una línea base reproducible que combina filtros legítimos, similitud semántica y evidencia de competencias/proyectos. La explicación se genera a partir de datos estructurados y factores efectivamente usados, no de una justificación libre inventada por un LLM.

No confundir score normalizado con probabilidad de contratación. Para usar el término “modelo de ranking entrenado”, debe haber dataset etiquetado con origen y derechos conocidos, separación train/validation/test, baseline, métricas de ranking (p. ej. NDCG@k/Recall@k/MRR apropiadas), análisis de subgrupos/errores, versión y model card. Si no hay datos apropiados, entregar baseline explicable y documentar la brecha.

No utilizar atributos sensibles ni proxies como objetivos de ranking. La auditoría de equidad debe revisar posibles efectos de características no obvias. Mantener humano en el bucle.
