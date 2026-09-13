"""Render verified numeric results to bilingual LaTeX/Markdown; no model calls."""
import csv
import json
from pathlib import Path

from analyze import LABELS, ORDER

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/analysis-v2'


def table(rows, lang, tex=True):
    labels = dict(zip(ORDER, LABELS[lang]))
    headers = ['Configuración','Estricto','SQL norm.','Tokens','s/tarea','Llamadas'] if lang=='es' else ['Configuration','Strict','SQL norm.','Tokens','s/task','Calls']
    cells = [[labels[r['condition']], f"{r['successes']}/24", f"{r['normalized_successes']}/24", f"{r['mean_tokens']:,.0f}",f"{r['mean_seconds']:.2f}", str(r['calls'])] for r in rows]
    if tex:
        return '\\begin{center}\\small\n\\setlength{\\tabcolsep}{4pt}\n\\begin{tabularx}{\\linewidth}{@{}Xrrrrr@{}}\n\\toprule '+ ' & '.join(headers) + ' \\\\ \\midrule\n' + '\n'.join(' & '.join(row)+' \\\\' for row in cells) + '\n\\bottomrule\n\\end{tabularx}\\end{center}\n'
    return '| ' + ' | '.join(headers) + ' |\n| --- | ---: | ---: | ---: | ---: | ---: |\n' + '\n'.join('| ' + ' | '.join(row)+' |' for row in cells)


def main():
    data = json.loads((OUT / 'summary.json').read_text())
    assert data['run_count'] == 216 and data['source_hashes_verified']
    rows = data['summary']; lookup = {r['condition']:r for r in rows}; sage = lookup['sage']
    historical = json.loads((ROOT / 'results/analysis/summary.json').read_text())
    development = data['policy_decision']
    transitions = list(csv.DictReader((OUT / 'routing.csv').open()))
    for lang in ['es','en']:
        destination = ROOT / 'paper-v2' / lang
        es = lang=='es'
        if es:
            abstract = (f"Proponemos SAGE-CREH, una quinta arquitectura que combina selección de skills, vía directa, resolutores independientes y arbitraje condicional. "
                        f"Una revisión focalizada de doce papers de arXiv fundamenta el diseño. Tras 20 ejecuciones de desarrollo separadas, se realizaron {data['run_count']} ejecuciones reales "
                        f"con el mismo modelo y las doce tareas originales, dos repeticiones y nueve condiciones: cuatro arquitecturas, un agente único, SAGE y tres controles de ablación. "
                        f"La réplica consumió {data['total_tokens']:,} tokens en {data['calls']} llamadas. SAGE obtuvo {sage['successes']}/24 aciertos estrictos y "
                        f"{sage['normalized_successes']}/24 tras normalizar únicamente el envoltorio SQL, con {sage['mean_tokens']:,.0f} tokens y {sage['mean_seconds']:.2f} segundos medios por tarea. "
                        "Se separan coordinación, carga de instrucciones y formato de salida mediante controles explícitos. La muestra es pequeña, sintética y conocida durante el diseño; "
                        "la comparación es una réplica informada por desarrollo, no evidencia de superioridad universal ni de generalización a ciegas.")
        else:
            abstract = (f"We propose SAGE-CREH, a fifth architecture combining skill selection, a direct path, independent solvers and conditional adjudication. "
                        f"A focused review of twelve arXiv papers informs the design. After 20 separate development runs, {data['run_count']} live runs used "
                        f"the same model and twelve original tasks, two repetitions and nine conditions: four architectures, a single agent, SAGE and three ablation controls. "
                        f"Replication consumed {data['total_tokens']:,} tokens in {data['calls']} calls. SAGE achieved {sage['successes']}/24 strict successes and "
                        f"{sage['normalized_successes']}/24 after normalizing only the SQL envelope, averaging {sage['mean_tokens']:,.0f} tokens and {sage['mean_seconds']:.2f} seconds per task. "
                        "Explicit controls distinguish coordination, instruction loading and output format. The sample is small, synthetic and known during design; "
                        "this is a development-informed replication, not evidence of universal superiority or blind generalization.")
        (destination / 'abstract.tex').write_text('\\ArticleAbstract{'+abstract+'}\n')
        content = ['\\section{' + ('Resultados de la réplica v2' if es else 'Version-2 replication results')+'}']
        content.append((f"Las {data['run_count']} ejecuciones completaron {data['calls']} llamadas y {data['total_tokens']:,} tokens. Se registraron {data['errors']} errores de infraestructura o protocolo. "
                        f"La contabilidad de todas las llamadas fue {'completa' if data['accounting_complete'] else 'incompleta'}; los tokens no se estimaron. " if es else
                        f"The {data['run_count']} runs completed {data['calls']} calls and {data['total_tokens']:,} tokens, with {data['errors']} infrastructure or protocol errors. "
                        f"Call accounting was {'complete' if data['accounting_complete'] else 'incomplete'}; tokens were not estimated. "))
        content.append('\\subsection{'+('Comparación principal: mismas tareas y modelo' if es else 'Main comparison: same tasks and model')+'}')
        content.append(table(rows[:6], lang))
        content.append(('Cada fila contiene 24 ejecuciones. Tokens y segundos son medias por tarea; llamadas es el total por condición. SQL norm. es una métrica secundaria de formato, no una reparación de respuestas.' if es else
                        'Each row contains 24 runs. Tokens and seconds are per-task means; calls are the condition total. SQL norm. is a secondary format metric, not answer repair.'))
        content.append('\\begin{center}\\includegraphics[width=\\linewidth]{../../results/analysis-v2/comparison-'+lang+'.pdf}\\end{center}')
        content.append(('Barras de cumplimiento estricto y marcas de SQL normalizado. Intervalos percentiles por tarea del 95\\%; no prueban una clasificación general de arquitecturas.' if es else
                        'Strict-completion bars and normalized-SQL diamonds. Task-cluster 95\\% percentile intervals do not establish a general architecture ranking.'))
        content.append('\\subsection{'+('Cumplimiento por familia de tareas' if es else 'Completion by task family')+'}')
        details = list(csv.DictReader((OUT/'by-task.csv').open()))
        families = ['ledger','schedule','dependencies','selection','memory','sql']
        family_labels = ['Registros','Calendario','Dependencias','Selección','Memoria','SQL'] if es else ['Ledger','Calendar','Dependencies','Selection','Memory','SQL']
        column_labels = ['Familia','Único','Sec.','Par.','Jer.','Refl.','SAGE'] if es else ['Family','Single','Seq.','Par.','Hier.','Refl.','SAGE']
        family_rows = []
        for family,label in zip(families,family_labels):
            cells = [label]
            for condition in ORDER[:6]:
                group = [r for r in details if r['family']==family and r['condition']==condition]
                cells.append(str(sum(int(r['strict']) for r in group))+' / '+str(sum(int(r['normalized']) for r in group)))
            family_rows.append(cells)
        content.append('\\begin{center}\\small\\begin{tabularx}{\\linewidth}{@{}Xrrrrrr@{}}\\toprule\n'+' & '.join(column_labels)+' \\\\ \\midrule\n'+'\n'.join(' & '.join(r)+' \\\\' for r in family_rows)+'\n\\bottomrule\\end{tabularx}\\end{center}')
        content.append(('Cada celda: aciertos estrictos / aciertos con SQL normalizado, ambos sobre cuatro ejecuciones de la familia (dos tareas por dos repeticiones). Fuera de SQL son la misma métrica.' if es else
                        'Each cell: strict successes / normalized-SQL successes, both out of four family runs (two tasks times two repetitions). Outside SQL the metrics are identical.'))
        content.append('\\subsection{'+('Controles de skills y delegación' if es else 'Skill-loading and delegation controls')+'}')
        content.append(table([lookup[c] for c in ['hierarchical','hierarchical_all_skills','sage','sage_single','sage_all_skills']],lang))
        if es:
            content.append('SAGE sin delegación conserva el proponente y las instrucciones de SAGE, eliminando solo el segundo resolutor y la revisión. SAGE con diez skills conserva la política, cambiando la carga de instrucciones. Los controles originales incluyen un catálogo de descripciones que SAGE no recibe; no atribuir toda diferencia a la topología.')
        else:
            content.append('SAGE without delegation retains its proposer and instructions, removing only the second solver and review. SAGE with ten skills retains the policy and changes instruction loading. Original controls include a description catalog absent from SAGE; do not attribute every difference to topology.')
        content.append('\\subsection{'+('Diferencias emparejadas de consumo y tiempo' if es else 'Paired token and time differences')+'}')
        headers = ['Comparación','Cambio tokens (\\%)','IC 95\\%','Diferencia s','IC 95\\%'] if es else ['Comparison','Token change (\\%)','95\\% CI','Seconds difference','95\\% CI']
        lines = []
        labels = dict(zip(ORDER,LABELS[lang]))
        for b in ['single','sequential','parallel','hierarchical','reflexive','sage_single','sage_all_skills']:
            token = next(c for c in data['comparisons'] if c['a']=='sage' and c['b']==b and c['metric']=='token_change_percent')
            seconds = next(c for c in data['comparisons'] if c['a']=='sage' and c['b']==b and c['metric']=='seconds')
            lines.append([labels[b],f"{token['difference']:+.1f}",f"[{token['ci_low']:.1f}, {token['ci_high']:.1f}]",f"{seconds['difference']:+.2f}",f"[{seconds['ci_low']:.2f}, {seconds['ci_high']:.2f}]"])
        content.append('\\begin{center}\\footnotesize\\setlength{\\tabcolsep}{3pt}\\begin{tabularx}{\\linewidth}{@{}Xrrrr@{}}\\toprule\n'+' & '.join(headers)+' \\\\ \\midrule\n'+'\n'.join(' & '.join(r)+' \\\\' for r in lines)+'\n\\bottomrule\\end{tabularx}\\end{center}')
        content.append(('En cada fila: SAGE menos la configuración indicada; el cambio porcentual de tokens es 100(SAGE/control $-1$). Valores negativos favorecen menor consumo o tiempo de SAGE. Intervalos exploratorios de 10000 remuestreos emparejados por tarea.' if es else
                        'Each row is SAGE minus the indicated configuration; token percentage change is 100(SAGE/control $-1$). Negative values favor lower SAGE consumption or time. Exploratory intervals use 10000 paired task-cluster draws.'))
        content.append('\\subsection{'+('Rutas ejecutadas y efecto de las revisiones' if es else 'Executed routes and revision outcomes')+'}')
        paths = {'direct':('Directa','Direct'), 'parallel_agreement':('Acuerdo paralelo','Parallel agreement'), 'parallel_adjudication':('Arbitraje paralelo','Parallel adjudication'), 'selective_review':('Revisión selectiva','Selective review'),'error':('Error','Error')}
        for condition in ['sage','sage_single','sage_all_skills']:
            group = [r for r in transitions if r['condition']==condition]
            counts = []
            for key, names in paths.items():
                number = sum(r['path']==key for r in group)
                if number: counts.append(f"{names[0 if es else 1]}: {number}")
            corrected = sum(r['corrected']=='True' for r in group)
            regressed = sum(r['regressed']=='True' for r in group)
            content.append(labels[condition]+'. '+ '; '.join(counts)+'. '+
                           (f"Frente al primer candidato: {corrected} correcciones y {regressed} regresiones de acierto estricto." if es else
                            f"Relative to the first candidate: {corrected} corrections and {regressed} regressions in strict completion."))
        content.append(('Esta inspección usa el evaluador después de terminar las ejecuciones; nunca alimentó la política de enrutamiento. Una corrección puede ser de formato. Se conserva el detalle por ejecución.' if es else
                        'This inspection uses the evaluator after execution and never fed the routing policy. A correction may concern formatting. Per-run details are retained.'))
        content.append('\\subsection{'+('Desarrollo: resultados excluidos de la réplica' if es else 'Development: excluded from replication')+'}')
        for candidate in development['candidates']:
            name = ('Serial' if candidate['condition']=='sage_serial' else ('Paralela' if es else 'Parallel'))
            content.append(f"{name}: {candidate['successes']}/{candidate['runs']}; {candidate['mean_tokens']:,.1f} "+('tokens y ' if es else 'tokens and ')+f"{candidate['mean_seconds']:.2f} "+('segundos medios.' if es else 'mean seconds.'))
        content.append((f"Se eligió la política paralela por mayor cumplimiento, según la regla previa. Desarrollo consumió {development['development_tokens']:,} tokens en {development['development_calls']} llamadas y {development['development_runs']} ejecuciones. Este coste no se oculta en la réplica ni se suma a sus medias." if es else
                        f"The parallel policy was selected for higher completion under the prior rule. Development used {development['development_tokens']:,} tokens in {development['development_calls']} calls and {development['development_runs']} runs. This cost is reported separately and excluded from replication means."))
        content.append(('El único acierto que separó a los candidatos ocurrió en DEV22, de calendario: ambas políticas usaron la misma vía directa, sin riesgo ni revisión. La diferencia puede deberse a variación de generación y no demuestra una ventaja causal del paralelismo. Se conserva la elección conforme a la regla previa, sin reinterpretarla como prueba de superioridad.' if es else
                        'The sole success separating candidates occurred on calendar task DEV22: both policies used the same direct path, without risk or review. Generation variability can explain this difference; it does not establish a causal advantage of parallelism. Selection is retained under the prior rule, not reinterpreted as proof of superiority.'))
        (destination / 'results.tex').write_text('\n\n'.join(content)+'\n')
        history = '\\clearpage\n\\section*{'+('Apéndice: resultados históricos v1' if es else 'Appendix: historical v1 results')+'}\n'
        history += (f"La tanda anterior incluyó {historical['run_count']} ejecuciones, {historical['calls']} llamadas y {historical['total_tokens']:,} tokens, conservados sin cambios. Su normalización SQL fue post hoc; en v2 se predefinió como secundaria. No se mezclan tandas.\n" if es else
                    f"The earlier wave contained {historical['run_count']} runs, {historical['calls']} calls and {historical['total_tokens']:,} tokens, preserved unchanged. SQL normalization was post hoc in v1 and predefined as secondary in v2. Waves are not pooled.\n")
        history += table(historical['summary'],lang)
        history += '\n\\subsection*{'+('Cómo reproducir y auditar los materiales' if es else 'Reproducing and auditing the materials')+'}\n'
        history += ('El archivo público incluye código, datos y fuentes editables de ambas versiones. Descomprimirlo y trabajar desde su raíz, con las dependencias de \\texttt{requirements.txt} instaladas en un entorno aislado. Para verificar y regenerar los resultados de la tanda conservada, sin llamar a la API:\n' if es else
                    'The public archive contains code, data and editable sources for both versions. Extract it and work from its root, installing \\texttt{requirements.txt} dependencies in an isolated environment. To verify and regenerate the preserved wave without calling the API:\n')
        history += r'''\begin{verbatim}
python3 -m unittest discover -s benchmark -v
python3 -m unittest discover -s extension -v
python3 extension/analyze.py
python3 extension/write_results.py
python3 extension/write_web.py
\end{verbatim}
'''
        history += ('Las pruebas offline no generan puntuaciones del modelo. El analizador comprueba las 216 ejecuciones, identidad de tareas, orden, copias congeladas, instrucciones cargadas y consumo por llamada. El generador escribe las secciones numéricas; las conclusiones editoriales se conservan aparte. Compilar dos veces cada \\texttt{article.tex} desde \\texttt{paper-v2/es} y \\texttt{paper-v2/en} con pdfLaTeX.\n\nUna nueva réplica real requiere una clave autorizada y tiene coste de API. Utilizar siempre otra carpeta de salida y seguir \\texttt{extension/README.md}; no sobrescribir la decisión de política ni las trazas publicadas. El modelo es un alias: una réplica posterior no garantiza respuestas o tiempos idénticos.\n\nLa integridad del paquete v2 se comprueba con \\texttt{ARTIFACTS-v2.sha256}; los archivos descargables tienen además un manifiesto \\texttt{SHA256SUMS.txt}. Las trazas registran datos públicos sintéticos, respuestas visibles y uso informado, nunca encabezados de autorización.\n' if es else
                    'Offline tests do not produce model scores. The analyzer checks all 216 runs, task identity, order, frozen copies, loaded instructions and per-call usage. The generator writes numeric sections; authored conclusions remain separate. Compile each \\texttt{article.tex} twice from \\texttt{paper-v2/es} and \\texttt{paper-v2/en} using pdfLaTeX.\n\nA new live replication requires an authorized key and incurs API cost. Always use a new output directory and follow \\texttt{extension/README.md}; do not overwrite the policy decision or published traces. The model is an alias, so later replication does not guarantee identical answers or time.\n\nPackage v2 integrity can be checked with \\texttt{ARTIFACTS-v2.sha256}; downloadable files additionally have a \\texttt{SHA256SUMS.txt} manifest. Traces contain synthetic public inputs, visible responses and reported usage, never authorization headers.\n')
        (destination / 'historical.tex').write_text(history)
        (OUT / f'main-table-{lang}.md').write_text(table(rows[:6],lang,False)+'\n')
        (OUT / f'ablation-table-{lang}.md').write_text(table([lookup[c] for c in ['hierarchical','hierarchical_all_skills','sage','sage_single','sage_all_skills']],lang,False)+'\n')
    print('Generated verified bilingual numeric sections; author conclusions before compiling.')


if __name__ == '__main__': main()
