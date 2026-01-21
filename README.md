# DAA_Actividad3_GA_Music  
Generación automática de melodías mediante Algoritmos Genéticos

## Introducción
Este proyecto aborda la generación automática de melodías musicales utilizando Algoritmos Genéticos, explorando cómo los principios de evolución, selección y mutación pueden aplicarse a un dominio creativo como la música, donde no existe una solución óptima única ni criterios de evaluación estrictamente formales.

A diferencia de los problemas clásicos de optimización, la calidad musical de una melodía no puede evaluarse de forma exacta, sino que depende de criterios heurísticos relacionados con la armonía, el ritmo y la coherencia melódica. Esta característica convierte a la música en un dominio especialmente adecuado para el uso de Algoritmos Genéticos, ya que permiten explorar grandes espacios de búsqueda y mejorar progresivamente soluciones a partir de evaluaciones aproximadas.

El objetivo del proyecto no es generar música aleatoria, sino diseñar e implementar un sistema evolutivo capaz de optimizar melodías musicales a lo largo de generaciones según criterios musicales definidos, demostrando de forma práctica el funcionamiento completo de un algoritmo genético aplicado a un problema real y creativo.


---

## Idea y objetivo del proyecto
La idea principal del proyecto es aplicar un algoritmo genético completo a la generación automática de melodías musicales, utilizando la evolución artificial para mejorar progresivamente la calidad de las soluciones generadas. El sistema parte de melodías completamente aleatorias y las optimiza mediante los operadores clásicos de selección, cruce y mutación, guiado por una función fitness diseñada específicamente para evaluar criterios musicales.

Para ello, se modelan conceptos musicales como notas, silencios, ritmo, armonía y repetición dentro de una representación genética manipulable por el algoritmo. Además, se incorporan parámetros configurables que permiten ajustar la función fitness antes de cada ejecución, facilitando un enfoque experimental e iterativo en el que el usuario puede explorar distintos estilos musicales sin modificar el código.

---

## Objetivos del proyecto
El objetivo principal es diseñar e implementar un algoritmo genético funcional capaz de generar melodías musicales coherentes en formato MIDI, optimizando progresivamente su calidad según criterios musicales definidos.

De forma específica, el proyecto persigue:
- Implementar un algoritmo genético completo con representación genética, población inicial, función fitness, operadores genéticos y criterio de parada.
- Definir una representación genética capaz de modelar tanto el contenido melódico como el ritmo de una pieza musical.
- Diseñar una función fitness musical que combine penalizaciones duras y puntuaciones suaves basadas en criterios armónicos, rítmicos y melódicos.
- Analizar la evolución de las soluciones a lo largo de las generaciones mediante métricas objetivas y validación auditiva.
- Permitir la modificación del estilo musical mediante parámetros ajustables por el usuario.

---

## Algoritmos Genéticos y modelado musical

### Representación genética de la melodía
Cada individuo del algoritmo genético representa una melodía completa codificada como una lista de enteros que constituye su cromosoma. Cada gen puede representar:
- Una nota MIDI (valor entero ≥ 0)
- Un silencio (REST)
- Una prolongación de la nota anterior (HOLD)

La longitud del cromosoma es fija y viene determinada por el número de compases y subdivisiones, lo que permite modelar de forma explícita la estructura rítmica y garantizar la compatibilidad entre individuos durante el cruce.

### Población inicial
La población inicial se genera de forma completamente aleatoria, asignando probabilísticamente notas, silencios o prolongaciones dentro de un rango musical definido. Esta alta diversidad inicial es fundamental para una exploración eficaz del espacio de búsqueda.

### Función fitness musical
La evaluación de las melodías se realiza mediante una función fitness musical que combina:
- Penalizaciones duras para descartar soluciones inválidas o musicalmente pobres.
- Puntuaciones suaves basadas en criterios como consonancia armónica, pertenencia a la escala, suavidad melódica, ritmo y síncopa, repetición de motivos y contorno melódico global.

Este enfoque guía el proceso evolutivo hacia soluciones coherentes sin imponer reglas deterministas rígidas.

### Operadores genéticos
La selección se realiza mediante selección por torneo, favoreciendo a los individuos con mayor fitness sin perder diversidad.  
El cruce intercambia bloques completos de compases entre dos melodías parentales, respetando la estructura musical.  
La mutación introduce variación aleatoria y se implementa de forma adaptativa, aumentando su probabilidad en fases de estancamiento y reduciéndola cuando hay mejoras.

---

## Estrategias avanzadas anti-estancamiento
Para evitar la convergencia prematura, el sistema incorpora:
- Reinyección periódica de diversidad sustituyendo individuos de bajo fitness.
- Mutación adaptativa ajustada dinámicamente según el progreso del algoritmo.
- Catástrofe controlada, que reinicia parcialmente la población manteniendo una élite.

Estas estrategias mejoran la estabilidad evolutiva y aumentan la probabilidad de encontrar melodías de mayor calidad.

---

## Resultados y análisis experimental

### Metodología
Se realizaron tres ejecuciones independientes (Run A, B y C) manteniendo constantes la entrada musical (C mayor, tempo 120, misma progresión de acordes) y los parámetros estructurales del algoritmo genético.  
La única variación entre ejecuciones fue la configuración de los pesos de la función fitness.

En cada ejecución se registraron:
- Un fichero CSV con métricas por generación.
- El MIDI final generado.
- Ficheros auxiliares con genes y parámetros utilizados.

### Configuración de los runs

| Run | Consonancia | Suavidad | Síncopa | Repetición | Aire |
|----|------------|----------|---------|------------|------|
| A | 55 | 55 | 45 | 55 | 45 |
| B | 80 | 80 | 30 | 55 | 40 |
| C | 50 | 50 | 80 | 40 | 75 |

### Resumen de salida

| Run | Fitness final | Notes | Rest | Hold |
|----|--------------|-------|------|------|
| A | 195.155 | 33 | 10 | 21 |
| B | 198.409 | 33 | 11 | 20 |
| C | 210.743 | 34 | 13 | 17 |

El fitness final es una puntuación relativa que refleja la adecuación de la melodía a los criterios musicales definidos, no una medida musical absoluta ni un valor con máximo teórico fijo.

---

## Conclusión
El proyecto demuestra que los algoritmos genéticos pueden aplicarse con éxito a un dominio creativo y no determinista como la música. A partir de una población inicial aleatoria, el sistema es capaz de mejorar progresivamente la calidad de las melodías mediante selección, cruce y mutación, guiado por una función fitness musical flexible.

Los resultados experimentales muestran un comportamiento coherente con la teoría de los algoritmos genéticos, combinando fases de mejora rápida con periodos de estancamiento. Las estrategias avanzadas anti-estancamiento han sido clave para evitar la convergencia prematura y permitir la exploración de nuevas regiones del espacio de búsqueda.

En conjunto, el proyecto cumple los objetivos propuestos y constituye una base sólida para futuras ampliaciones, como la incorporación de polifonía, evaluación con usuarios o aprendizaje automático híbrido.
