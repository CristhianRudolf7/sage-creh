## Qué se investigó

¿Cuándo compensa que un asistente delegue en otros agentes? Este estudio de CREH Labs revisa nueve papers de arXiv publicados inicialmente en 2026 y compara cuatro formas de gestionar subagentes. Se añade un agente único como referencia y una variante para comprobar el coste de cargar todos los skills.

**En esta muestra, el agente único tuvo el menor consumo y tiempo medio.** Entre los equipos, el reflexivo consumió menos tokens y el paralelo tuvo menor latencia media. Son resultados de tareas cortas, con toda la información disponible; no establecen una arquitectura universalmente mejor.

## Las cuatro arquitecturas

| Arquitectura | Funcionamiento implementado | Llamadas por tarea |
| --- | --- | ---: |
| Secuencial | Un trabajador extrae evidencia, otro resuelve y un tercero integra la respuesta. | 3 |
| Paralela | Dos especialistas complementarios trabajan simultáneamente y un integrador reúne sus resultados. | 3 |
| Jerárquica | Un supervisor decide uno o dos encargos, los trabajadores ejecutan y el supervisor integra. | 3–4 |
| Reflexiva | Un agente propone, otro critica y se revisa si hay objeciones, con dos rondas como máximo. | 2–5 |

Son implementaciones simplificadas de patrones, no réplicas de los frameworks citados. La comparación documental de estas cuatro familias aporta un punto de partida; el resto de la revisión incorpora autoridad, contexto y skills. [Kulkarni y Kulkarni, 2026](https://arxiv.org/html/2603.22651v1).

## Benchmark ejecutado

Se realizaron **144 ejecuciones reales, 416 llamadas al modelo y 568.283 tokens informados por la API**. Se utilizó GPT-5.6 Luna con pensamiento bajo, el 13 de septiembre de 2026. El identificador y esfuerzo se contrastaron con la [documentación oficial del modelo](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

Son **12 tareas distintas**, dos repeticiones y seis configuraciones, con 24 ejecuciones por configuración. Los grupos son registros contables, calendarios, dependencias, selección con restricciones, memoria por proyecto y generación SQL. Diez tareas usan respuestas exactas; las dos SQL deben superar tres bases de prueba cada una. El piloto de seis ejecuciones se conserva por separado y no se cuenta en las métricas.

El modelo, datos y límites máximos son comunes. Cada trabajador recibe la tarea original completa y un skill pertinente. Se aleatoriza el orden y solo se evalúa una tarea a la vez, permitiendo hasta dos llamadas paralelas dentro del flujo. Se cuentan coordinación, crítica, entradas repetidas y fallos. Se compara el cómputo consumido por cada configuración, no un presupuesto idéntico ya gastado.

## Resultados

| Configuración | Aciertos estrictos | Tras normalizar SQL | Tokens medios | Segundos medios |
| --- | ---: | ---: | ---: | ---: |
| Agente único | 20/24 | 23/24 | 1,143 | 4.72 |
| Secuencial | 20/24 | 24/24 | 3,410 | 13.72 |
| Paralela | 19/24 | 23/24 | 3,520 | 8.14 |
| Jerárquica | 20/24 | 24/24 | 4,373 | 11.19 |
| Reflexiva | 20/24 | 24/24 | 2,714 | 9.77 |
| Jerárquica + todos los skills | 21/24 | 24/24 | 8,518 | 11.93 |

Los tokens son entrada más salida, incluido el razonamiento. La latencia es tiempo transcurrido, con red y orquestación, excluyendo el evaluador final. Las tablas completas incluyen medianas, consumo por llamada e intervalos descriptivos del 95% con bootstrap por tarea. No se suman duraciones de llamadas solapadas para simular la espera del usuario.

![Comparación de éxito estricto, tokens y tiempo medio; las líneas indican intervalos del 95% por tarea.](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/comparison-es.png)

### Un hallazgo sobre el formato SQL

El evaluador principal exigía una estructura JSON concreta. En 22 salidas, el modelo entregó una cadena SQL dentro de `answer`, en lugar del objeto anidado con campo `sql`. **Las puntuaciones estrictas originales se conservaron.**

Un análisis posterior, identificado como tal, normalizó únicamente ese envoltorio y ejecutó la consulta original: el total pasó de 120/144 a 142/144. No hubo cambios de consultas, correcciones mediante otro modelo ni repeticiones selectivas. Los dos errores restantes fueron de propagación de dependencias en T05: se adelantaban los inicios de H y K aunque el tiempo total era correcto.

Esto explica por qué una clasificación basada solo en la columna estricta mezcla formato y solución. El análisis normalizado tampoco demuestra corrección fuera de las tareas y bases probadas.

### Skills específicos o catálogo completo

Con el mismo flujo jerárquico, cargar los diez skills completos elevó el consumo medio de **4.373 a 8.518 tokens: un 94,8% adicional**. El intervalo pareado del incremento es 87,9%–101,9%. El éxito estricto pasó de 20/24 a 21/24, mientras el resultado normalizado fue 24/24 en ambos. La diferencia media de tiempo fue 0,74 segundos, con intervalo de −0,24 a 1,83 segundos.

Aquí el skill correcto se selecciona con la etiqueta de la tarea. No se evalúan los errores ni el coste de descubrirlo desde una conversación real. La separación entre catálogo, instrucciones elegidas y recursos de apoyo es coherente con la revisión de [Xu y Yan](https://arxiv.org/html/2602.12430v4); nuestro experimento solo mide esta variante concreta de carga.

## Cómo elegir una arquitectura de subagentes

La recomendación es un **maestro con delegación opcional**: conservar la vía directa y crear trabajadores cuando exista trabajo separable suficiente para compensar planificación e integración. El maestro conoce los metadatos del catálogo; cada trabajador recibe skills pertinentes y referencias de la tarea. Puede pedir más recursos si hacen falta.

Un nivel de delegación y dos trabajadores simultáneos son un punto inicial de implementación, no valores óptimos demostrados. El motor debe gestionar dependencias, cancelación, permisos y escrituras incompatibles. Las decisiones sin resolver se escalan al coordinador.

Esta política adaptativa y el contexto reducido de producción **son hipótesis todavía no evaluadas**. No se demuestra una arquitectura universalmente mejor: en estas tareas breves, el agente único fue la opción más económica; entre los patrones con subagentes, el reflexivo consumió menos tokens en promedio y el paralelo tuvo menor latencia media.

## Alcance y materiales

Es un preprint exploratorio sin revisión por pares. La muestra es pequeña y sintética, con un modelo y contextos cortos; no evalúa terminal, navegación, programación en varios archivos, autonomía prolongada ni RAM. La latencia depende del proveedor y la red. Hace falta reservar tareas reales, añadir modelos y comparar delegación adaptativa a presupuestos equivalentes.

- [Paper completo en español](/investigacion/documentos/subagentes-arquitecturas-tokens-tiempo-2026-v1-es.pdf).
- [Full paper in English](/investigacion/documentos/subagentes-arquitecturas-tokens-tiempo-2026-v1-en.pdf).
- [Código, fuentes LaTeX, tareas y todas las trazas](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/source-and-data.zip).
- [Hoja de cálculo con datos de los gráficos](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/benchmark-data.xlsx).
- [Tabla resumen CSV](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/summary.csv) y [resultados por ejecución CSV](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/runs.csv).
- [Sensibilidad al formato SQL](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/format-sensitivity.csv) y [hashes de los archivos descargables](/investigacion/datos/subagentes-arquitecturas-tokens-tiempo-2026-v1/SHA256SUMS.txt).

El paquete conserva el protocolo fijado, hashes del código, orden aleatorio, respuestas visibles, tiempos y tokens. No contiene credenciales ni razonamiento privado.

## Fuentes de la revisión

Las fechas siguientes corresponden al primer envío a arXiv; las versiones consultadas están identificadas en cada enlace. No se combinaron puntuaciones de distintos papers ni se trataron simuladores y propuestas cualitativas como experimentos equivalentes.

- [Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward](https://arxiv.org/html/2602.12430v4) — 2026-02-12.
- [Benchmarking Multi-Agent LLM Architectures for Financial Document Processing: A Comparative Study of Orchestration Patterns, Cost-Accuracy Tradeoffs and Production Scaling Strategies](https://arxiv.org/html/2603.22651v1) — 2026-03-24.
- [CRAFT: Grounded Multi-Agent Coordination Under Partial Information](https://arxiv.org/html/2603.25268v2) — 2026-03-26.
- [EvoAgent: An Evolvable Agent Framework with Skill Learning and Multi-Agent Delegation](https://arxiv.org/html/2604.20133v3) — 2026-04-22.
- [Swarm Skills: A Portable, Self-Evolving Multi-Agent System Specification for Coordination Engineering](https://arxiv.org/html/2605.10052v2) — 2026-05-11.
- [When Does Hierarchy Help? Benchmarking Agent Coordination in Event-Driven Industrial Scheduling](https://arxiv.org/html/2605.13172v1) — 2026-05-13.
- [Beyond Sequential Interaction: Benchmarking Parallel Execution and Coordination for GUI Agents](https://arxiv.org/html/2607.22689v1) — 2026-07-17.
- [OrchBench: Evaluating Multi-Agent Orchestration Plans in Isolation via Deterministic Simulation](https://arxiv.org/html/2607.25656v1) — 2026-07-28.
- [Subagents vs Agent Skills: Executing Reusable Knowledge for Long-Horizon Agentic Tasks](https://arxiv.org/html/2609.09233v1) — 2026-09-07.
