# Version 2 — SAGE-CREH / ejecución con skills y compuertas

This extension adds a fifth architecture while retaining the original four,
single-agent reference and historical evidence. Research targets subagent
coordination and skill distribution, not a comparison between model families.

Esta extensión añade una quinta arquitectura y conserva los cuatro patrones,
la referencia individual y los datos anteriores. El objetivo es estudiar cómo
coordinar subagentes y repartir skills, no clasificar modelos diferentes.

## Runtime / ejecución

- `architecture.py`: public-interface skill adapter, shape-only gates, independent
  proposals and conditional adjudication; adaptador público, contratos de formato,
  propuestas independientes y arbitraje condicional.
- `run.py`: separate development and paired replication; desarrollo separado y
  réplica emparejada, sin sobrescribir evidencia existente.
- `test_extension.py`: offline routing, trace, isolation and accounting tests;
  pruebas offline, no puntuaciones del modelo.
- `protocol.en.md`, `protocol.es.md`: pre-execution settings and selection rule;
  configuración previa y regla de selección.
- `changes-before-evaluation.md`: serialization guard correction, before any
  final API call; corrección de serialización anterior a la evaluación.

## Reproduce preserved analysis / reproducir análisis conservado

From the study root / desde la raíz del estudio:

```bash
python3 -m unittest discover -s benchmark -v
python3 -m unittest discover -s extension -v
python3 extension/analyze.py
python3 extension/write_results.py
```

`analyze.py` requires completed v2 evidence, exact task identity, frozen hashes,
balanced blocks, recorded order and correct per-call accounting. It writes only
derived analysis. `write_results.py` regenerates numeric bilingual sections,
leaving authored interpretations untouched. Compile both `paper-v2/{es,en}`
articles twice with pdfLaTeX. `verify_pdfs.py` additionally needs PyMuPDF and Pillow.

El analizador exige evidencia v2 completa y auditada; no descarta fallos.
El generador actualiza solo secciones numéricas y no sustituye la interpretación
editorial. Compilar dos veces cada artículo y revisar todas sus páginas.

## New live replication / nueva réplica con API

```bash
python3 extension/run.py --env-file /path/to/authorized.env --output results/new-development --development
python3 extension/run.py --env-file /path/to/authorized.env --output results/new-replication --policy parallel
```

API calls are billable. Only `OPENAI_API_KEY` is read; no credential value is
logged. Use a new output folder. The archived policy is parallel, selected under
the documented rule. A fresh development-based choice must be recorded in a
separate replication copy before its final run. Do not overwrite the archived
policy decision or rename historical outcomes to appear fresh. Analyzer paths
must likewise be adjusted in that separate copy, not by editing frozen evidence.

Las llamadas tienen coste. La clave no se registra. Usar carpetas nuevas y una
copia independiente para decisiones y análisis de otra réplica. No sobrescribir
la decisión original ni presentar los datos conocidos como una prueba a ciegas.

## Evidence / evidencia

- `../results/development-v2/`: all 20 development runs / los 20 intentos.
- `../results/policy-decision-v2.json`: recorded choice before replication /
  elección registrada antes de la réplica.
- `../results/evaluation-v2/`: 216 planned paired runs, raw visible per-call I/O,
  source copies, usage and wall time / ejecuciones, trazas visibles y código.
- `../results/analysis-v2/`: tables, paired intervals, routing transitions and
  bilingual figures / tablas, intervalos, rutas y figuras bilingües.
- `sources-v2.json`: three additional arXiv references / tres fuentes adicionales.
- `../paper-v2/`: bilingual paper sources and PDFs / artículo bilingüe.

The raw responses and strict scores remain unchanged. Normalized SQL is a
separate predefined secondary outcome. No external solver or grader participates
in routing. Frozen-source folders are audit snapshots; the root-level runtime
is the runnable entry point, with the task evidence retained beside it.

Las respuestas crudas y notas estrictas se conservan intactas. SQL normalizado
es una métrica secundaria predefinida. El evaluador no participa en el enrutamiento.
Las copias congeladas sirven para auditoría; ejecutar desde la raíz del estudio.
