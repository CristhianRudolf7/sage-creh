# Pre-evaluation implementation note

After development and policy selection, the first final-run invocation stopped
before creating an output directory or making any API call. Its equality guard
compared Python SQL fixture tuples with historical JSON lists. The guard was
corrected to compare JSON-normalized structures, and a regression test added.
No task values, prompts, routing, budgets, grading or policy choice changed.
Development retains its own exact frozen source. The final manifest records the
corrected runner and additional test. No final evaluation observation existed
when this correction was made.

La primera invocación final se detuvo antes de crear evidencia o llamar a la API:
comparaba tuplas Python de fixtures con listas JSON. Se normalizó solo esa
comparación y se añadió una prueba. No cambiaron tareas, prompts, enrutamiento,
presupuestos, evaluador ni elección de política. Desarrollo conserva su código
congelado y la evaluación registra el código corregido en su propio manifiesto.
