"""Insert observed results into both manuscripts without duplicating numbers.

Run only after analyze.py has audited the complete evaluation.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "results/analysis/summary.json").read_text())
rows = data["summary"]
single, sequential, parallel, hierarchical, reflexive, full = rows
ablation = data["ablation"]
labels = {
    "en": ["Single agent", "Sequential", "Parallel", "Hierarchical", "Reflexive", "Hierarchical + all skills"],
    "es": ["Agente único", "Secuencial", "Paralela", "Jerárquica", "Reflexiva", "Jerárquica + todos los skills"],
}


def integer(value):
    return f"{int(value):,}".replace(",", r"\,")


def decimal(value, digits=1):
    return f"{value:.{digits}f}"


def interval(low, high, digits=1):
    return "[" + decimal(low, digits) + "; " + decimal(high, digits) + "]"


def table(language):
    lines = [r"\begin{table}[htbp]", r"\centering\small", r"\setlength{\tabcolsep}{4pt}",
             r"\begin{tabular}{@{}lrrrrr@{}}", r"\toprule"]
    lines.append((r"\textbf{Condition} & \textbf{Strict} & \textbf{SQL norm.} & \textbf{Tokens/run} & \textbf{Mean s} & \textbf{Median s}\\"
                  if language == "en" else
                  r"\textbf{Configuración} & \textbf{Estricto} & \textbf{SQL norm.} & \textbf{Tokens/ej.} & \textbf{Media s} & \textbf{Mediana s}\\"))
    lines.append(r"\midrule")
    for i, row in enumerate(rows):
        if i == 5:
            lines.append(r"\midrule")
        lines.append(f"{labels[language][i]} & {row['successes']}/24 & {row['normalized_successes']}/24 & {integer(round(row['mean_tokens']))} & {decimal(row['mean_seconds'],2)} & {decimal(row['median_seconds'],2)}" + r"\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    lines.append(r"\caption{" + (
        "Observed results. Strict is the frozen primary score. SQL norm. is the explicitly post-hoc wrapper sensitivity; query text is unchanged. The separated last row is the skill-loading ablation."
        if language == "en" else
        "Resultados observados. Estricto es el criterio principal fijado. SQL norm. es la sensibilidad posterior al envoltorio; no cambia el texto de la consulta. La última fila separada corresponde a la carga de skills."
    ) + "}")
    lines += [r"\label{tab:results}", r"\end{table}"]
    return "\n".join(lines)


def efficiency_table(language):
    lines = [r"\begin{table}[htbp]", r"\centering\small", r"\setlength{\tabcolsep}{4pt}",
             r"\begin{tabular}{@{}lrrrr@{}}", r"\toprule"]
    lines.append((r"\textbf{Condition} & \textbf{Total tokens} & \textbf{Calls} & \textbf{Success/100k tok.} & \textbf{Success/min}\\"
                  if language == "en" else r"\textbf{Configuración} & \textbf{Tokens totales} & \textbf{Llamadas} & \textbf{Aciertos/100k tok.} & \textbf{Aciertos/min}\\"))
    lines.append(r"\midrule")
    for i, row in enumerate(rows):
        if i == 5:
            lines.append(r"\midrule")
        lines.append(f"{labels[language][i]} & {integer(row['total_tokens'])} & {row['calls']} & {decimal(row['successes_per_100k_tokens'],2)} & {decimal(row['successes_per_minute'],2)}" + r"\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\caption{" + (
        "Resource efficiency using primary strict successes and all attempts. Accumulated successes/minute is not saturated-server throughput."
        if language == "en" else
        "Eficiencia con aciertos estrictos y todos los intentos. Aciertos por minuto acumulado no equivale a capacidad de un servidor saturado."
    ) + "}", r"\label{tab:efficiency}", r"\end{table}"]
    return "\n".join(lines)


def interval_table(language):
    lines = [r"\begin{table}[htbp]", r"\centering\small", r"\setlength{\tabcolsep}{4pt}",
             r"\begin{tabular}{@{}lrrr@{}}", r"\toprule"]
    lines.append((r"\textbf{Condition} & \textbf{Success \%} & \textbf{Mean tokens} & \textbf{Mean seconds}\\"
                  if language == "en" else r"\textbf{Configuración} & \textbf{Éxito \%} & \textbf{Tokens medios} & \textbf{Segundos medios}\\"))
    lines.append(r"\midrule")
    for i, row in enumerate(rows):
        lines.append(labels[language][i] + " & " + interval(row['success_ci_low'],row['success_ci_high']) + " & " + interval(row['tokens_ci_low'],row['tokens_ci_high'],0) + " & " + interval(row['seconds_ci_low'],row['seconds_ci_high'],2) + r"\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\caption{" + (
        "Descriptive 95\\% task-cluster bootstrap intervals for the primary metric, mean total tokens and mean wall time. Twelve task ids are the resampling units."
        if language == "en" else
        "Intervalos descriptivos del 95\\% por bootstrap de tareas para éxito principal, tokens medios y tiempo medio. Se remuestrean doce identificadores de tarea."
    ) + "}", r"\label{tab:intervals}", r"\end{table}"]
    return "\n".join(lines)


def figure(language, stem, caption, name):
    return (r"\begin{figure}[htbp]" + "\n" + r"\centering" + "\n" +
            r"\includegraphics[width=\linewidth]{../../results/analysis/" + stem + "-" + language + ".pdf}\n" +
            r"\caption{" + caption + "}\n" + r"\label{" + name + "}\n" + r"\end{figure}")


for language in ["en", "es"]:
    primary_min = min(r["successes"] for r in rows[1:5])
    primary_max = max(r["successes"] for r in rows[1:5])
    normalized_total = data["normalized_successes"]
    strict_total = sum(r["successes"] for r in rows)
    if language == "en":
        abstract = (
            "We review nine arXiv papers first submitted in 2026 and execute a small comparison of sequential, parallel, hierarchical and reflexive subagent management, with a single-agent baseline and a skill-loading ablation. "
            f"Twelve synthetic tasks, two repetitions and six conditions produce 144 live runs and {data['calls']} model calls using GPT-5.6 Luna with low reasoning effort. "
            f"The single agent completes {single['successes']}/24 strict tasks with {integer(round(single['mean_tokens']))} tokens and {decimal(single['mean_seconds'],2)} seconds per run on average; the four team configurations complete {primary_min}--{primary_max}/24. "
            f"A post-hoc SQL-wrapper sensitivity changes total completions from {strict_total}/144 to {normalized_total}/144 without changing query text. "
            f"Loading all skills increases hierarchical mean tokens by {decimal(ablation['token_increase_percent'])}\\%. "
            "These exploratory results quantify overhead on short, fully supplied tasks and do not establish a universal best architecture or long-running autonomy."
        )
        lead = (r"\section{Results}" + "\n" +
            f"All 144 planned evaluation runs completed. The trace audit reconciles {data['calls']} model calls and {integer(data['total_tokens'])} provider-reported tokens, including the 24-run skill ablation. "
            f"There were {data['errors']} infrastructure or protocol execution errors; usage accounting is complete in every run. The six development-pilot runs are excluded. "
            "The preserved manifest and final hashes match, and the recorded order matches the frozen schedule.\n\n" +
            f"Evaluation ran on 13 September 2026 from {data['evaluation_start'][11:19]} to {data['evaluation_end'][11:19]} UTC. "
            "This is an observed same-day API experiment, not a latency forecast for other accounts or deployments.\n\n")
        sensitivity = (r"\subsection{Format compliance and solution quality}" + "\n" +
            "During evaluation, visible SQL answers exposed a distinction between a correct-looking query and the requested nested result shape. The primary grader was left unchanged. An explicitly post-hoc sensitivity wraps an existing raw string under answer as an object with a sql field, then executes the identical query against the same three fixtures. "
            "No SQL text, numeric answer, prompt or trial is repaired or repeated.\n\n" +
            f"This normalization applies to {data['sql_wrapper_normalizations']} recorded outputs. It changes whole-task completions from {strict_total}/144 to {normalized_total}/144 across the six conditions. "
            "The strict column measures delivered schema compliance as well as correctness; the normalized column diagnoses how much of the observed failure is attributable to that wrapper. It is not a second prespecified endpoint or proof that every generated query is correct outside these fixtures.\n\n"
            "The two remaining failures are T05, repetition 2, under the single and parallel conditions. Both return a correct makespan of 38 but start H at 10 instead of 18 and K at 21 instead of 29. H depends on C finishing, and K depends on H finishing. This is a dependency-propagation error, not a JSON-wrapper error; checking only the final makespan would miss it.\n\n")
        skill_text = (r"\subsection{Selected skills versus the complete catalog}" + "\n" +
            f"The hierarchical condition uses {integer(round(hierarchical['mean_tokens']))} tokens per run on average with one selected skill, compared with {integer(round(full['mean_tokens']))} when all ten bodies are loaded. "
            f"The paired mean difference is {integer(round(ablation['mean_token_difference']))} tokens, with a 95\\% interval {interval(*ablation['token_difference_ci'],0)}. "
            f"The increase is {decimal(ablation['token_increase_percent'])}\\%, interval {interval(*ablation['token_increase_percent_ci'])}\\%.\n\n" +
            f"Strict success changes from {hierarchical['successes']}/24 to {full['successes']}/24; under the wrapper sensitivity it changes from {hierarchical['normalized_successes']}/24 to {full['normalized_successes']}/24. "
            f"The mean latency difference, all minus selected, is {decimal(ablation['mean_second_difference'],2)} seconds, interval {interval(*ablation['seconds_difference_ci'],2)}. "
            "This is a payload ablation with the correct family supplied in advance. It does not measure catalog-search errors or their token cost.\n\n")
        diagnostic = (r"\subsection{Costs and uncertainty}" + "\n" +
            f"The reflexive workflow executes {data['role_counts'].get('reflexive:revise',0)} revision calls across its 24 runs; a critic can add cost even when no revision follows. "
            f"Provider-reported cached input totals {integer(sum(r['cached_input_tokens'] for r in rows))} tokens, and reported reasoning totals {integer(sum(r['reasoning_tokens'] for r in rows))}. These are subsets, not additional tokens. "
            "Tables~\\ref{tab:efficiency} and~\\ref{tab:intervals} retain failed attempts and reflect the small number of independent task instances. Point rankings alone should not be interpreted as statistically established general superiority.\n\n")
        takeaway = (
            f"On these short tasks, the single-agent reference spends {integer(round(single['mean_tokens']))} tokens per run, while the least token-intensive team configuration spends {integer(round(min(r['mean_tokens'] for r in rows[1:5])))}. "
            f"Their strict completion counts must be read alongside Table~\\ref{{tab:results}} and the SQL sensitivity. "
            "The actionable lesson is to preserve direct execution while evaluating delegation where parallel work or context separation can repay the extra calls. This is a workload-specific recommendation, not a rejection of subagents.\n"
        )
        caption_comparison = "Measured primary success, total tokens and elapsed time. Whiskers are descriptive 95\\% task-cluster intervals. All-skills loading is shown separately. Figure generated from the released data."
        caption_family = "Strict successes by task family. Each cell represents four runs, not four independent task instances. The SQL sensitivity is reported separately in Table~\\ref{tab:results}."
    else:
        abstract = (
            "Se revisan nueve papers de arXiv publicados inicialmente en 2026 y se comparan gestión secuencial, paralela, jerárquica y reflexiva, con un agente único de referencia y una variante de carga de skills. "
            f"Doce tareas sintéticas, dos repeticiones y seis configuraciones producen 144 ejecuciones reales y {data['calls']} llamadas a GPT-5.6 Luna con pensamiento bajo. "
            f"El agente único completa {single['successes']}/24 tareas estrictas con {integer(round(single['mean_tokens']))} tokens y {decimal(single['mean_seconds'],2)} segundos medios; las cuatro configuraciones de equipo completan {primary_min}--{primary_max}/24. "
            f"Una sensibilidad posterior al envoltorio SQL cambia los aciertos totales de {strict_total}/144 a {normalized_total}/144 sin alterar las consultas. "
            f"Cargar todos los skills aumenta los tokens medios jerárquicos un {decimal(ablation['token_increase_percent'])}\\%. "
            "Son resultados exploratorios sobre tareas cortas con datos completos; no establecen una arquitectura universalmente mejor ni autonomía prolongada."
        )
        lead = (r"\section{Resultados}" + "\n" +
            f"Terminaron las 144 ejecuciones previstas. La auditoría reconcilia {data['calls']} llamadas y {integer(data['total_tokens'])} tokens informados por el proveedor, incluidas las 24 ejecuciones de carga de skills. "
            f"Hubo {data['errors']} errores de infraestructura o ejecución del protocolo; todas las ejecuciones tienen consumo completo. Se excluyen las seis del piloto. "
            "Los hashes iniciales y finales coinciden y el orden registrado corresponde al plan fijado.\n\n" +
            f"Se evaluó el 13 de septiembre de 2026 entre {data['evaluation_start'][11:19]} y {data['evaluation_end'][11:19]} UTC. "
            "Son tiempos observados ese día contra la API, no una previsión para otras cuentas o despliegues.\n\n")
        sensitivity = (r"\subsection{Cumplimiento de formato y calidad de la solución}" + "\n" +
            "Durante la evaluación, las respuestas SQL mostraron una diferencia entre una consulta aparentemente correcta y la estructura anidada solicitada. Se conservó el evaluador principal. Una sensibilidad explícitamente posterior envuelve una cadena existente dentro de answer en un objeto con campo sql y ejecuta la misma consulta contra las tres bases. "
            "No se corrige ni repite texto SQL, respuesta numérica, prompt o intento.\n\n" +
            f"La normalización se aplica a {data['sql_wrapper_normalizations']} salidas registradas y cambia los aciertos completos de {strict_total}/144 a {normalized_total}/144 entre las seis configuraciones. "
            "La columna estricta mide también cumplimiento del formato entregado; la normalizada diagnostica cuánto fallo se atribuye al envoltorio. No es otro objetivo prefijado ni prueba de que todas las consultas funcionen fuera de estas bases.\n\n"
            "Los dos fallos restantes corresponden a T05, repetición 2, en las configuraciones individual y paralela. Ambas entregan la duración total correcta de 38, pero inician H en 10 en vez de 18 y K en 21 en vez de 29. H depende de que termine C y K de que termine H. Es un error al propagar dependencias, no de envoltorio JSON; comprobar solo la duración final lo ocultaría.\n\n")
        skill_text = (r"\subsection{Skills seleccionados frente al catálogo completo}" + "\n" +
            f"La configuración jerárquica consume {integer(round(hierarchical['mean_tokens']))} tokens medios con un skill seleccionado y {integer(round(full['mean_tokens']))} al cargar los diez cuerpos. "
            f"La diferencia media pareada es {integer(round(ablation['mean_token_difference']))} tokens, con intervalo del 95\\% {interval(*ablation['token_difference_ci'],0)}. "
            f"El incremento es {decimal(ablation['token_increase_percent'])}\\%, intervalo {interval(*ablation['token_increase_percent_ci'])}\\%.\n\n" +
            f"El éxito estricto pasa de {hierarchical['successes']}/24 a {full['successes']}/24; con la sensibilidad de envoltorio pasa de {hierarchical['normalized_successes']}/24 a {full['normalized_successes']}/24. "
            f"La diferencia media de latencia, todos menos seleccionado, es {decimal(ablation['mean_second_difference'],2)} segundos, intervalo {interval(*ablation['seconds_difference_ci'],2)}. "
            "Es una comparación de carga con el grupo correcto conocido de antemano; no mide errores de búsqueda de skills ni su coste.\n\n")
        diagnostic = (r"\subsection{Costes e incertidumbre}" + "\n" +
            f"El flujo reflexivo ejecuta {data['role_counts'].get('reflexive:revise',0)} llamadas de revisión en 24 ejecuciones; un crítico puede añadir coste aunque no haya revisión posterior. "
            f"La API informa {integer(sum(r['cached_input_tokens'] for r in rows))} tokens de entrada cacheada y {integer(sum(r['reasoning_tokens'] for r in rows))} de razonamiento. Son subconjuntos, no tokens adicionales. "
            "Las tablas~\\ref{tab:efficiency} y~\\ref{tab:intervals} conservan intentos fallidos y reflejan el pequeño número de instancias independientes. Un orden puntual no establece superioridad general estadística.\n\n")
        takeaway = (
            f"En estas tareas cortas, la referencia individual consume {integer(round(single['mean_tokens']))} tokens medios, frente a {integer(round(min(r['mean_tokens'] for r in rows[1:5])))} de la configuración de equipo que menos tokens utiliza. "
            "Sus aciertos estrictos deben interpretarse junto a la tabla~\\ref{tab:results} y la sensibilidad SQL. "
            "La recomendación práctica es conservar ejecución directa y evaluar delegación cuando el trabajo paralelo o separar contexto puedan compensar las llamadas adicionales. Es una recomendación para esta carga, no un rechazo de los subagentes.\n"
        )
        caption_comparison = "Éxito principal, tokens totales y tiempo transcurrido medidos. Las líneas muestran intervalos descriptivos del 95\\% por tarea. La carga de todos los skills se distingue del resto. Figura generada con los datos entregados."
        caption_family = "Aciertos estrictos por grupo. Cada celda corresponde a cuatro ejecuciones, no cuatro instancias independientes. La sensibilidad SQL figura por separado en la tabla~\\ref{tab:results}."
    (ROOT / "paper" / language / "abstract.tex").write_text(r"\ArticleAbstract{" + abstract + "}\n")
    (ROOT / "paper" / language / "takeaway.tex").write_text(takeaway)
    result_text = lead + table(language) + "\n\n" + sensitivity
    result_text += figure(language, "comparison", caption_comparison, "fig:comparison") + "\n\n"
    result_text += skill_text + diagnostic + efficiency_table(language) + "\n\n"
    result_text += figure(language, "families", caption_family, "fig:families") + "\n\n" + interval_table(language)
    # Ordinary Python text used escaped backslashes for ref; normalize to LaTeX.
    result_text = result_text.replace(r"\\ref", r"\ref")
    (ROOT / "paper" / language / "results.tex").write_text(result_text + "\n")
    takeaway_path = ROOT / "paper" / language / "takeaway.tex"
    takeaway_path.write_text(takeaway_path.read_text().replace(r"\\ref", r"\ref"))
print("Wrote observed results and complete abstracts in English and Spanish.")
