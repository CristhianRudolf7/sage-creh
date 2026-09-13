# Investigación de orquestación de subagentes

[English](README.md)

## Versión actual: 2.0 — SAGE-CREH

El estudio incorpora una quinta arquitectura enfocada en coordinación selectiva
de subagentes y reparto de skills. [extension/README.md](extension/README.md)
documenta implementación, protocolos y reproducción; `paper-v2/` contiene
las dos ediciones actualizadas del artículo.

La nueva réplica emparejada incluye 216 ejecuciones, 510 llamadas y 707.090 tokens
observados sobre las doce tareas originales exactas. Desarrollo suma aparte
20 ejecuciones, 28 llamadas y 32.351 tokens, excluidos de las medias de la réplica.
Se repitieron las cuatro arquitecturas, el agente único y el control original de
carga de skills; se añadieron SAGE, SAGE sin delegación y SAGE con diez skills.

SAGE obtuvo 23/24 aciertos estrictos con 1.765 tokens y 7,34 segundos medios.
Consumió un 30,2%–61,1% menos tokens que los cuatro equipos originales, pero no
gana bajo todos los criterios: SQL normalizado da 24/24 a secuencial/reflexiva y
23/24 a SAGE/agente único, con menor consumo del agente único. Las tareas ya se
conocían al diseñar; no es una prueba a ciegas. Se conservan todos los intentos
y fallos. Tres referencias nuevas amplían a doce el corpus de arXiv.

Las entradas científicas, ejecutor y resultados v1 no cambiaron. La introducción
v2 de este README es una actualización editorial. `ARTIFACTS.sha256` describe la
fotografía histórica v1, incluido su README original, disponible en el ZIP v1
preservado; no describe el directorio ampliado. El paquete v2 incluye su propio
`ARTIFACTS-v2.sha256` actualizado.

## Documentación histórica de la versión 1

Estudio exploratorio de CREH Labs sobre arquitecturas de coordinación de subagentes. Compara cuatro patrones acotados con subagentes, un agente único y una variante de carga de skills mediante llamadas reales a `gpt-5.6-luna` con pensamiento bajo. La bibliografía incluye nueve papers de arXiv publicados inicialmente en 2026.

Esta carpeta contiene un arnés de investigación independiente y sus evidencias registradas. El benchmark contiene 12 tareas sintéticas distintas, dos repeticiones y seis configuraciones: 144 ejecuciones de evaluación más un piloto separado de seis ejecuciones. No es un resultado de SWE-bench, Terminal-Bench ni autonomía en producción.

## Contenido

- `benchmark/`: tareas, skills procedurales, evaluadores objetivos, prompts de roles y ejecución real.
- `protocol.en.md` / `protocol.es.md`: configuración experimental fijada antes de la evaluación, con enmiendas editoriales documentadas.
- `results/pilot/`: evidencia de desarrollo excluida de las métricas publicadas.
- `results/evaluation/`: manifiesto ordenado, hashes, tareas, trazas y resultados.
- `analysis/`: auditoría, agregación, bootstrap, hoja de cálculo y gráficos.
- `results/analysis/`: tablas JSON/CSV/XLSX y figuras generadas.
- `sources.json`: fechas, versiones, enlaces y alcance de las fuentes.
- `paper/es/` / `paper/en/`: fuentes LaTeX completas y PDF compilados.

## Reproducción

Utilizar Python 3.13 o una versión compatible e instalar `requirements.txt` en un entorno aislado. Desde esta carpeta:

```bash
python3 -m unittest discover -s benchmark -v
python3 benchmark/runner.py --pilot --output results/new-pilot
python3 benchmark/runner.py --output results/new-evaluation
```

Definir una clave autorizada en `OPENAI_API_KEY`, o pasar `--env-file /ruta/a/autorizado.env`. El ejecutor solo lee esa clave. Las llamadas a la API tienen coste; no se imprime la credencial ni se guardan encabezados de autorización. Las carpetas de salida deben ser nuevas. El alias del modelo puede cambiar: repetir el estudio no garantiza respuestas o tiempos idénticos.

Para regenerar el análisis publicado a partir de su evaluación preservada:

```bash
python3 analysis/analyze.py
```

El análisis valida hashes, orden, bloques completos y tokens por llamada. Exige que termine la evaluación y no descarta resultados desfavorables. Para analizar otra carpeta se cambia únicamente la ruta de entrada del analizador en una copia de reproducción, conservando la evidencia original.

Cada PDF se compila dos veces con pdfLaTeX desde su carpeta de idioma, o con el script de CREH Labs `build_article.py` si está instalado. Las fuentes utilizan el isotipo y estilo originales, A4, cuerpos completos traducidos y el pie de autor obligatorio. Primero debe generarse el análisis para disponer de las figuras.

## Interpretación

La métrica principal exige completar toda la tarea. Se cuentan todas las llamadas, incluida supervisión, crítica, entradas repetidas y generaciones fallidas con consumo informado. Caché y razonamiento son partes ya incluidas en el total. Los intervalos usan bootstrap pareado por tarea conservando ambas repeticiones. La latencia es tiempo transcurrido, no suma de solicitudes solapadas. Aciertos por minuto expresa eficiencia acumulada de ejecuciones secuenciales, no capacidad bajo carga.

El benchmark, los datos y el artículo se entregan para revisión pública. Los papers citados pertenecen a sus autores y no se redistribuyen completos. Las trazas públicas contienen datos sintéticos y respuestas visibles, sin razonamiento privado ni conversaciones personales. Este preprint no ha pasado revisión por pares.

## Enmienda editorial

`editorial-amendments.json` registra los hashes originales y actuales de los dos protocolos tras un cambio exclusivo de enfoque editorial. Los manifiestos históricos, tareas, prompts, evaluadores y resultados no se modificaron. El análisis valida los hashes del benchmark y las enmiendas documentadas de los protocolos.
