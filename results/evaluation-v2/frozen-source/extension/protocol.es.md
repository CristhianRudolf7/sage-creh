# Extensión v2: SAGE-CREH y coordinación con selección de skills

Escrito antes del desarrollo y de la réplica con API. Es un protocolo local
previo a la ejecución, no un prerregistro con sello de tiempo independiente.

## Pregunta y alcance

¿Puede la delegación selectiva conservar el cumplimiento y reducir tokens
agregados y tiempo frente a coordinación secuencial, paralela, jerárquica y
reflexiva? SAGE-CREH significa ejecución con selección de skills y compuertas.
Es una composición local nueva, no una reivindicación de haber inventado el
enrutamiento adaptativo o el consenso. No se presupone un ganador universal;
se busca un equilibrio de Pareto entre cumplimiento, tokens y tiempo.

## Arquitectura propuesta

Un adaptador determinista identifica seis interfaces cerradas por la estructura
JSON PÚBLICA y entrega a cada trabajador el skill pertinente sin modificar sus
instrucciones, omitiendo el catálogo de diez descripciones. No usa identificadores,
respuestas de referencia ni fixtures SQL para decidir. No es recuperación
semántica aprendida. Todos reciben los datos públicos completos originales.

Se desarrollan dos políticas. Serial: un proponente y un verificador solo ante
riesgo estructural público, dudas concretas o incumplimiento del contrato de salida.
Paralela: ante riesgo, dos resolutores completos e independientes simultáneos;
si sus candidatos válidos coinciden, se acepta sin integrador; si no, un árbitro.
Con riesgo bajo, un proponente y revisión únicamente por dudas o formato inválido.
El riesgo se fija para grafos de al menos ocho nodos y algún nodo con dos o más
predecesores, o selección de al menos diez elementos con incompatibilidades y
prerrequisitos. La compuerta valida claves y tipos, no exactitud ni restricciones.
La propuesta interna contiene candidato y dudas. La respuesta final conserva el
sobre answer original; los prompts nuevos explicitan el anidamiento SQL.
No se usan solucionadores externos, herramientas, feedback del evaluador,
deliberación privada ni respuestas cacheadas. Serial: máximo dos llamadas;
paralela: máximo tres, con dos simultáneas.

## Desarrollo y elección (excluidos de la evaluación)

Diez instancias nuevas: dos de contabilidad, agenda, dependencias, selección y
memoria; semillas 1501 + 100*índice_familia + variante. Una repetición por política:
20 ejecuciones. Los contratos SQL se prueban offline; no hay desarrollo SQL vivo.
Elegir por mayor número de aciertos estrictos; desempatar por menos tokens medios
agregados y luego menor tiempo medio. Guardar intentos, costes y decisión antes
de la réplica final. No presentar los resultados elegidos durante desarrollo
como evidencia a ciegas. Cualquier desarrollo adicional debe registrarse,
usar otra carpeta y terminar antes de congelar el código final.

## Réplica emparejada y controles

Repetir EXACTAMENTE las doce tareas, referencias y fixtures SQL originales dos
veces en nueve condiciones: single, sequential, parallel, hierarchical,
reflexive, hierarchical_all_skills, sage, sage_single y sage_all_skills.
Son 216 ejecuciones, 24 por condición; semilla de orden 20260914. Aleatorizar
bloques tarea x repetición y después condiciones dentro del bloque. Una condición
a la vez, máximo dos llamadas simultáneas dentro de ella. Mantener implementación
y prompts originales en los controles. Modelo gpt-5.6-luna, esfuerzo low, máximo
1536 tokens de salida por llamada, JSON-object, sin streaming, store=false, los
mismos timeouts y cero reintentos. No modificar código, prompts, tareas ni
evaluador una vez iniciada la evaluación. Congelar copias y hashes antes de cada
fase y comprobarlos al finalizar. Fallos de autorización/cuota detienen la fase
y conservan la evidencia parcial.

El par jerarquía/todos los skills aísla la carga de cuerpos de instrucciones.
sage_single conserva proponente y payload nuevos pero nunca delega; compararlo
con sage permite medir la coordinación añadida. sage_all_skills conserva política
y prompts nuevos, cargando los diez cuerpos intactos; compararlo con sage mide la
selección de instrucciones. Frente a las arquitecturas originales cambian prompts
y exposición al catálogo además de topología: no interpretar como un efecto puro
de topología. El número real de llamadas es un resultado, no un presupuesto
oculto diferente por llamada.

## Métricas, incertidumbre y límites

Primarias: cumplimiento estricto completo, tokens observados de entrada+salida y
tiempo monotónico desde el inicio hasta la última respuesta, incluida coordinación
y trazas locales, excluida calificación. Secundarias: llamadas, desgloses de tokens,
rutas y familias. Caché ya pertenece a entrada y razonamiento a salida: no sumarlos
dos veces. Registrar errores y contabilidad incompleta; no estimar uso ausente.

Predefinir cumplimiento SQL normalizado como métrica secundaria: solo si answer
es una cadena, envolver esa MISMA cadena en {sql:...} y ejecutar el MISMO evaluador.
No editar consultas, recalcular respuestas ni reparar la métrica primaria. Así se
separa la sensibilidad de formato conocida en v1 de una mejora de razonamiento.
Usar 10000 remuestreos bootstrap emparejados por doce conglomerados de tarea,
conservando ambas repeticiones y condiciones juntas, para diferencias y razones
de tokens. Intervalos exploratorios: doce tareas y efectos techo no establecen
igualdad, significancia, fiabilidad ni superioridad general por ausencia de fallos.

Los resultados v1 se conocían al diseñar. Reutilizar esas tareas es una réplica
emparejada informada por desarrollo, NO una evaluación a ciegas ni prueba de
generalización. Semillas nuevas reducen ajuste directo, no el conocimiento de
familias y benchmark. Conservar v1 separado; no mezclar tandas para latencia ni
sustituir controles nuevos por datos viejos. Publicar costes de desarrollo aparte,
entradas/salidas visibles, código, manifiesto, métricas estrictas/normalizadas y
ablaciones. No publicar claves de API ni razonamiento privado.
