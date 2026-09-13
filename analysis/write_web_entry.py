"""Generate complete bilingual paper-page bodies from audited results.

This creates local Markdown only. Publishing remains a separate explicit action.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "subagentes-arquitecturas-tokens-tiempo-2026"
ASSETS = f"/investigacion/datos/{SLUG}-v1"
data = json.loads((ROOT / "results/analysis/summary.json").read_text())
labels = {
    "en": ["Single agent", "Sequential", "Parallel", "Hierarchical", "Reflexive", "Hierarchical + all skills"],
    "es": ["Agente único", "Secuencial", "Paralela", "Jerárquica", "Reflexiva", "Jerárquica + todos los skills"],
}


def result_table(language):
    if language == "es":
        lines = ["| Configuración | Aciertos estrictos | Tras normalizar SQL | Tokens medios | Segundos medios |",
                 "| --- | ---: | ---: | ---: | ---: |"]
    else:
        lines = ["| Configuration | Strict successes | After SQL normalization | Mean tokens | Mean seconds |",
                 "| --- | ---: | ---: | ---: | ---: |"]
    for label, row in zip(labels[language], data["summary"]):
        lines.append(f"| {label} | {row['successes']}/24 | {row['normalized_successes']}/24 | {row['mean_tokens']:,.0f} | {row['mean_seconds']:.2f} |")
    return "\n".join(lines)


es = f"""## Qué se investigó

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

{result_table('es')}

Los tokens son entrada más salida, incluido el razonamiento. La latencia es tiempo transcurrido, con red y orquestación, excluyendo el evaluador final. Las tablas completas incluyen medianas, consumo por llamada e intervalos descriptivos del 95% con bootstrap por tarea. No se suman duraciones de llamadas solapadas para simular la espera del usuario.

![Comparación de éxito estricto, tokens y tiempo medio; las líneas indican intervalos del 95% por tarea.]({ASSETS}/comparison-es.png)

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

- [Paper completo en español](/investigacion/documentos/{SLUG}-v1-es.pdf).
- [Full paper in English](/investigacion/documentos/{SLUG}-v1-en.pdf).
- [Código, fuentes LaTeX, tareas y todas las trazas]({ASSETS}/source-and-data.zip).
- [Hoja de cálculo con datos de los gráficos]({ASSETS}/benchmark-data.xlsx).
- [Tabla resumen CSV]({ASSETS}/summary.csv) y [resultados por ejecución CSV]({ASSETS}/runs.csv).
- [Sensibilidad al formato SQL]({ASSETS}/format-sensitivity.csv) y [hashes de los archivos descargables]({ASSETS}/SHA256SUMS.txt).

El paquete conserva el protocolo fijado, hashes del código, orden aleatorio, respuestas visibles, tiempos y tokens. No contiene credenciales ni razonamiento privado.

## Fuentes de la revisión

Las fechas siguientes corresponden al primer envío a arXiv; las versiones consultadas están identificadas en cada enlace. No se combinaron puntuaciones de distintos papers ni se trataron simuladores y propuestas cualitativas como experimentos equivalentes.
"""

en = f"""## Research question

When does delegating to other agents pay off? This CREH Labs study reviews nine arXiv papers first submitted in 2026 and compares four subagent-management patterns. A single-agent baseline and a complete-skill-library condition provide additional comparisons.

**The single agent had the lowest token consumption and mean time in this sample.** Among teams, the reflexive workflow used the fewest tokens and the parallel workflow had the lowest mean latency. These are short tasks with all information supplied; the findings do not establish a universally best architecture.

## The four architectures

| Architecture | Implemented workflow | Calls per task |
| --- | --- | ---: |
| Sequential | One worker extracts evidence, another solves, and a third integrates the answer. | 3 |
| Parallel | Two complementary specialists run concurrently and a merger combines their findings. | 3 |
| Hierarchical | A supervisor chooses one or two assignments, workers execute, and the supervisor integrates. | 3–4 |
| Reflexive | An agent proposes, another critiques, and objections trigger revision, with at most two rounds. | 2–5 |

These are simplified pattern implementations, not reproductions of the cited frameworks. A document-processing comparison of the four families supplies one starting point; the wider review considers authority, context and skills. [Kulkarni and Kulkarni, 2026](https://arxiv.org/html/2603.22651v1).

## Executed benchmark

The study ran **144 live evaluations, 416 model calls and 568,283 provider-reported tokens** using GPT-5.6 Luna with low reasoning effort on 13 September 2026. Model identity and supported effort were checked against the [official model documentation](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

There are **12 distinct tasks**, two repetitions and six conditions, with 24 runs per condition. Families cover ledgers, calendars, dependencies, constrained selection, project-scoped memory and SQL generation. Ten tasks require exact answers; each SQL task must pass three database fixtures. A separate six-run development pilot is preserved and excluded from performance metrics.

Model, data access and maximum limits are shared. Each worker receives the complete original task and a relevant skill. Run order is randomized, with one evaluation at a time and up to two concurrent calls inside eligible workflows. Coordination, criticism, repeated inputs and failures all count. The comparison measures naturally consumed compute rather than an identical spent budget.

## Results

{result_table('en')}

Tokens are input plus output, including reasoning. Latency is elapsed time with network and orchestration, excluding final grading. Complete tables include medians, per-call usage and descriptive 95% task-cluster bootstrap intervals. Overlapping request durations are not added together to represent user waiting time.

![Strict task success, token consumption and mean elapsed time; whiskers show task-cluster 95% intervals.]({ASSETS}/comparison-en.png)

### A finding about SQL formatting

The primary evaluator required a specific JSON structure. In 22 outputs, the model supplied a SQL string inside `answer` instead of a nested object containing `sql`. **Original strict scores were retained.**

An explicitly post-hoc analysis normalized only that wrapper and executed the unchanged query: total completions increased from 120/144 to 142/144. No queries were edited, no other model repaired them and no unfavorable trial was rerun. The two remaining errors involved dependency propagation in T05: H and K started too early despite a correct overall makespan.

This shows why ranking only the strict column mixes formatting and solution quality. The normalized analysis also does not establish correctness beyond the tasks and database fixtures tested.

### Selected skills or the complete catalog

Under the same hierarchical workflow, loading all ten complete skills increased mean usage from **4,373 to 8,518 tokens: 94.8% more**. The paired interval for the increase is 87.9%–101.9%. Strict success changed from 20/24 to 21/24, while normalized success was 24/24 in both conditions. The mean time difference was 0.74 seconds, with an interval from −0.24 to 1.83 seconds.

Here the relevant skill is selected from the known task-family label. The experiment does not evaluate errors or cost from discovering that skill in a real conversation. Separating the catalog, selected instructions and supporting resources is consistent with [Xu and Yan's survey](https://arxiv.org/html/2602.12430v4); our experiment measures only this specific payload variation.

## Choosing a subagent architecture

The recommendation is a **master with optional delegation**: preserve direct execution and create workers when sufficiently separable work can repay planning and integration. The master discovers catalog metadata; each worker receives relevant skills and task references, with additional resources available on request.

One delegation level and two concurrent workers provide an initial implementation scope, not proven optimal values. The runtime should manage dependencies, cancellation, permissions and conflicting writes. Unresolved decisions are escalated to the coordinator.

This adaptive policy and reduced production context **are hypotheses not yet evaluated**. No universally best architecture is established: on these short tasks, the single agent was the most economical option; among the multi-agent patterns, reflexive coordination used the fewest tokens on average and parallel coordination had the lowest mean latency.

## Scope and materials

This is an exploratory preprint without peer review. The sample is small and synthetic, with one model and short contexts; it does not evaluate terminal use, browsing, multi-file coding, long-running autonomy or RAM. Latency depends on the provider and network. Further work requires held-out real tasks, more models and adaptive-delegation comparisons at matched budgets.

- [Full paper in English](/investigacion/documentos/{SLUG}-v1-en.pdf).
- [Artículo completo en español](/investigacion/documentos/{SLUG}-v1-es.pdf).
- [Code, LaTeX sources, tasks and every trace]({ASSETS}/source-and-data.zip).
- [Workbook with chart data]({ASSETS}/benchmark-data.xlsx).
- [Summary CSV]({ASSETS}/summary.csv) and [per-run results CSV]({ASSETS}/runs.csv).
- [SQL-format sensitivity]({ASSETS}/format-sensitivity.csv) and [download checksums]({ASSETS}/SHA256SUMS.txt).

The bundle preserves the frozen local protocol, code hashes, randomized order, visible responses, times and tokens. Credentials and private reasoning are excluded.

## Review sources

Dates below indicate first submission to arXiv; each link identifies the consulted version. Scores from different papers were not pooled, and simulators or qualitative proposals were not treated as equivalent executed experiments.
"""

sources = [s for s in json.loads((ROOT / "sources.json").read_text()) if s["kind"] == "arxiv"]
for language, body in [("es", es), ("en", en)]:
    body += "\n"
    for source in sources:
        body += f"- [{source['title']}]({source['url']}) — {source['first_submitted']}.\n"
    (ROOT / "paper" / f"page.{language}.md").write_text(body)
print("Wrote complete ES/EN paper-page bodies; nothing was published by this script.")
