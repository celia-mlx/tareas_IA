# Reporte — Encadenamiento en la biblioteca

**1. ¿Por qué `Becario(Ana)` sale hacia adelante y no hacia atrás?**
El encadenamiento hacia adelante está dirigido por los datos: en cada ronda
dispara toda regla cuyas premisas ya son hechos y sigue hasta el punto fijo,
sin mirar la consulta. `Estudiante(Ana)` y `TieneCredencial(Ana)` cumplen
`R_beca`, así que `Becario(Ana)` se deriva en la ronda 1 aunque no sirva
para probar `AccesoNoche(Ana)`. El encadenamiento hacia atrás está dirigido
por la meta: solo abre reglas cuya cabeza unifica con la meta actual. Ninguna
meta de la prueba es `Becario(_)`, así que `R_beca` nunca se abre y el átomo
nunca se deriva (la traza no menciona `R_beca`, ni a Luis ni a Marta).

**2. ¿Por qué hacia atrás prueba `R_miembro_est` al buscar `Miembro(Marta)`
si Marta es profesora?**
El algoritmo no sabe de antemano qué regla va a servir. Para la meta
`Miembro(Marta)` no hay un hecho que unifique, así que prueba las reglas en
el orden de la tabla. La cabeza de `R_miembro_est` (`Miembro(x)`) unifica con
la meta, por lo que la abre y busca su primera premisa, `Estudiante(Marta)`.
Esa meta falla (no hay hecho ni regla que la derive), se corta ese camino y
solo entonces prueba `R_miembro_prof`, que se cumple con el hecho
`Profesor(Marta)`. En un empate gana la primera regla de la tabla; por eso
el camino de Marta pasa primero por la regla de estudiante y falla.

**3. Con `TieneCredencial(Luis)` añadido, ¿qué cambia en `AccesoNoche(Luis)`?**
Comprobado con `python main.py --extra "TieneCredencial(Luis)"`. Hacia
adelante, a los cinco átomos nuevos de antes se suman tres relativos a Luis:
`Miembro(Luis)` (por `R_miembro_est`), `Becario(Luis)` (por `R_beca`) y
`AccesoNoche(Luis)` (por `R_acceso`, en la ronda 2). Quedan así, en este
orden: `Miembro(Ana)`, `Miembro(Luis)`, `Miembro(Marta)`, `Becario(Ana)`,
`Becario(Luis)`, `AccesoNoche(Ana)`, `AccesoNoche(Luis)`,
`AccesoNoche(Marta)`. La consulta **queda probada** con ambos algoritmos.
Hacia atrás la prueba usa `R_acceso` y `R_miembro_est` con los hechos
`Estudiante(Luis)`, `TieneCredencial(Luis)` y `HorarioNocturno(Hoy)`, y
sigue sin derivar `Becario(Luis)`.
