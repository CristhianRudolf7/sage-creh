# Microbenchmark de orquestación de subagentes: configuración experimental congelada

Versión 1.0, 13 de septiembre de 2026. Este protocolo local se escribe antes de la evaluación reservada; no es un prerregistro externo. Se incluyen papers cuya primera versión en arXiv se publicó en 2026, hasta el 13 de septiembre. Sus resultados se usan como contexto y no se mezclan con el experimento.

## Pregunta y alcance

Medir si cuatro formas acotadas de coordinación mejoran el cumplimiento exacto lo suficiente para justificar sus tokens y tiempo. Se incluye un agente único como referencia y un experimento adicional sobre carga de skills. Son ejecuciones reales de API con tareas sintéticas y toda la información proporcionada. No evalúan comandos de terminal, autonomía prolongada, navegación web, fiabilidad de producción ni RAM por agente. Python se usa en un arnés de investigación independiente.

## Configuraciones

| ID | Flujo | Llamadas al modelo | Trabajadores paralelos |
| --- | --- | --- | --- |
| single | Un único solucionador completo | 1 | 1 |
| sequential | Extracción → resolución → integración final; cada etapa recibe el original y el último traspaso | 3 | 1 |
| parallel | Dos especialistas complementarios fijos → integración | 3 | 2 |
| hierarchical | Supervisor crea 1–2 encargos → trabajadores → integración del supervisor | 3–4 | 2 |
| reflexive | Propuesta → crítica; revisión si se rechaza; máximo dos rondas de crítica/revisión | 2–5 | 1 |
| hierarchical_all_skills | Mismo flujo jerárquico, con los diez skills completos en cada nodo | 3–4 | 2 |

Cada nodo es una invocación independiente con un rol específico y el mismo modelo. Todas las llamadas reciben el original completo, los metadatos de diez skills y el skill pertinente. Solo el experimento adicional carga los diez cuerpos completos. La selección utiliza la etiqueta conocida del tipo de tarea, sin búsqueda ni llamada de clasificación: aísla el coste de la carga y no evalúa el enrutamiento real de skills. No se hereda historial ni estado oculto. Son implementaciones simplificadas de patrones, no reproducciones de los sistemas citados.

## Tareas y controles

Doce instancias fijas, dos por grupo: deduplicación y suma de registros, intersección de calendarios con desfases UTC fijos, planificación de un DAG y ruta crítica, selección óptima con restricciones, reducción de memoria por ámbito y generación de consultas SQLite. Se proporcionan todos los datos y restricciones. Diez exigen una respuesta estructurada exacta; las dos SQL deben superar tres bases de prueba cada una, con entidades vacías y casos de uniones y desempates. Las referencias se calculan mediante reducción determinista, enumeración exhaustiva o cálculos por base. Nunca se envían al modelo ni se devuelven como feedback. La salida debe ser un objeto JSON que contenga únicamente `answer`.

Dos repeticiones por tarea y configuración: 12 × 2 × 6 = 144 ejecuciones, 24 por configuración. Las cuatro arquitecturas con subagentes y el agente único conforman la comparación principal de 120 ejecuciones; la carga completa aporta otras 24. Se aleatorizan los bloques tarea/repetición y el orden interno de las configuraciones con semilla 20260913. Solo se ejecuta una evaluación a la vez; los flujos compatibles permiten dos solicitudes simultáneas dentro de ella. Se repiten los mismos datos: existen 12 tareas distintas, no 144 tareas independientes.

Modelo `gpt-5.6-luna`, pensamiento `low`, API Responses, modo objeto JSON, `store:false`, sin streaming y máximo de 1.536 tokens de salida por llamada, incluido razonamiento. Sin temperatura ni semilla del modelo explícitas. Se registra el modelo resuelto que informa la API. Sin reintentos HTTP automáticos. Máximo de cinco llamadas; no puede iniciarse otra después de 240 segundos. Los límites HTTP de conexión/lectura son 10/60 segundos: el plazo de inicio no es una interrupción estricta del tiempo total. Sin caché de respuestas propia; la caché de entrada del proveedor se registra, sin desactivarla. Se cuentan también las llamadas de coordinación e integración.

Antes de la evaluación se ejecuta un piloto de las seis configuraciones con una instancia contable aparte, DEV01, semilla 901. Sus datos no se mezclan. Solo se corrigen problemas del arnés/protocolo encontrados antes de la evaluación y se conserva la evidencia del piloto. El manifiesto congela hashes del código y se contrastan al terminar. No se ajustan prompts, tareas, límites ni evaluadores después de observar resultados. Los planes inválidos, respuestas incompletas, consumo ausente y errores de transporte se registran como fallos; no se repiten selectivamente resultados desfavorables.

## Medición y análisis

El éxito principal exige completar toda la tarea; los aciertos parciales de SQL son secundarios. El tiempo transcurre desde la creación de la ejecución hasta la respuesta final o error, incluida orquestación, espera de API/red y escritura de trazas; excluye el evaluador. También se suma el tiempo de las llamadas, que no equivale a latencia cuando se solapan.

Se suman tokens de entrada y salida informados por el proveedor en todas las llamadas: supervisor, crítica, intentos fallidos con consumo y traspasos repetidos. El total ya incluye razonamiento y entrada cacheada; no se vuelven a sumar. Se registran por separado caché, razonamiento y máxima entrada de una llamada. El consumo ausente sigue marcado como incompleto: los totales observados son cotas inferiores y no permiten declarar un ganador en eficiencia. No se reemplazan por estimaciones.

Se publican aciertos/24, porcentaje, latencia media y mediana, tokens totales y medios, llamadas, aciertos por 100.000 tokens y aciertos por minuto de tiempo acumulado. Esta última es eficiencia de una carga secuencial, no capacidad de un servidor saturado. Se incluyen todos los intentos, no solo los exitosos, además de resultados por tarea y errores. La comparación de Pareto utiliza éxito mayor, tokens medios menores y tiempo medio menor; igual éxito no demuestra capacidad general equivalente.

Bootstrap pareado por tarea, 10.000 remuestreos, semilla 20260913: se eligen doce identificadores con reemplazo, conservando sus dos repeticiones y todas las configuraciones comparadas. Se informan intervalos descriptivos del 95 % para éxito, tokens medios, tiempo medio y diferencias de carga de skills. No se tratan las 24 ejecuciones repetidas como 24 tareas independientes. La muestra sintética pequeña solo permite conclusiones exploratorias, no superioridad universal ni garantías de servicio.

## Reproducibilidad y límites

Se entregan definiciones, evaluador, prompts de roles/skills, hashes, orden aleatorio, texto de solicitudes, salida visible, consumo, tiempos, respuesta y evaluación por llamada/ejecución. Se excluyen credenciales, encabezados de autorización y razonamiento privado. El manifiesto registra Python, cliente HTTP, plataforma, modelo pedido y esfuerzo; las trazas registran el modelo y nivel de servicio devueltos. Se entregan datos CSV/XLSX para gráficos y papers en ambos idiomas.

Límites principales: pocas tareas diseñadas por el autor, un modelo con pensamiento bajo, contextos cortos, entrada completa compartida, prompts fijos, consumo naturalmente desigual dentro de un límite común, skill correcto predeterminado, caché/latencia del proveedor en un día, ausencia de acciones externas o programación en múltiples archivos y solo dos repeticiones. Una decisión de producción requiere tareas reales reservadas y más modelos. Las recomendaciones deben separar lo medido del diseño todavía no probado.

Nota editorial (2026-09-13): el título y el enfoque del alcance se revisaron después de la evaluación. La configuración experimental no cambia. `editorial-amendments.json` registra los hashes originales y actualizados de los documentos; los manifiestos históricos conservan sus hashes originales.
