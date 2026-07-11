# Las 20 misiones — campaña de validación y arranque real

**Para el coordinador.** Ejecuta las misiones en orden, una por una, usando las
tools del toolset `adversal` (nunca líneas de shell a mano; si el plugin no está
instalado, pide al usuario activarlo — ver `docs/coordinator-runbook.md`).
Reporta después de cada una: estado otorgado por el gate, regla que decidió,
coste, y qué nodo del mapa cambió de color. Sin adjetivos.

**Para el usuario, antes de empezar — el pacto de expectativas.** La mayoría de
misiones acabarán en `not_established`. Eso NO es fracaso: es el sistema
diciendo la verdad. El éxito de esta campaña se mide así: (1) el mapa refleja
fielmente qué está establecido y qué no; (2) errores concretos encontrados y
recordados; (3) algún lema pequeño en verde, ganado por el kernel. Nada más —
y nada menos.

**Reglas permanentes para el coordinador:**
- `claim_id` = id del nodo del mapa, siempre. Trabajo fuera del mapa = side
  quest, y se dice explícitamente.
- Ningún `proven` se presenta como cerrado sin su `adversal_backtranslate`
  revisado por el usuario.
- `providers`: empieza con `claude`; añade `claude,codex` en misiones de
  formalización cuando el usuario confirme que Codex tiene cuota disponible.
- Si una misión falla 2 veces por la misma causa, para y pregunta al usuario.
- `not_established` no se celebra ni se entierra: se registra y se sigue.

---

## Fase A — Calibrar la máquina (M1–M5)

> Antes de matemática real, demostramos que el sistema acepta lo verdadero,
> rechaza lo falso, y detecta lo ya conocido. Con testigos de kernel.

**M1 — Un lema verdadero pequeño.**
`adversal_map_add`: id `CAL-1`, statement "La suma de dos enteros pares es par.",
formal_statement `∀ a b : ℤ, Even a → Even b → Even (a + b)`,
theorem_name `even_add_even_int`. Después `adversal_mission` sobre `CAL-1`
(worker_timeout 600).
*Esperado:* `proven` (mathlib tiene `Even.add`). El primer verde legítimo.

**M2 — Una afirmación falsa.**
`adversal_map_add`: id `CAL-2`, statement "Para todo natural n, n + 1 = n.",
formal_statement `∀ n : Nat, n + 1 = n`, theorem_name `succ_eq_self`.
`adversal_mission` sobre `CAL-2`.
*Esperado:* `refuted` con disproof verificado por kernel
(`succ_eq_self_disproof : ¬ (∀ n : Nat, n + 1 = n)`), o `not_established` con el
contraejemplo como pista si el escéptico no logra construirlo. Nunca `proven`.

**M3 — Un teorema conocido.**
`adversal_map_add`: id `CAL-3`, statement "Existen infinitos números primos.",
formal_statement `∀ n : ℕ, ∃ p, n ≤ p ∧ Nat.Prime p`,
theorem_name `infinitude_of_primes`. `adversal_mission` sobre `CAL-3`.
*Esperado:* `proven` (mathlib: `Nat.exists_infinite_primes`) **y** una cita de
prior-art (Euclides) como pista. Lección para todos: **proven ≠ nuevo**. El
verde dice "verdadero", no "descubrimiento".

**M4 — Fidelidad de enunciados.**
`adversal_backtranslate` sobre `CAL-1` y `CAL-3` (lang `es`). Presenta al
usuario las dos frases lado a lado y espera su confirmación explícita de que
coinciden con lo que se quería decir.
*Esperado:* coincidencia. Si algo difiere, la formalización estaba mal aunque
el kernel dijera que sí — esa es la lección.

**M5 — El CI y el ritual del mapa.**
`adversal_reverify` (todo lo proven debe re-verificar) y `/map`. Muestra al
usuario el Map.canvas en Obsidian: CAL-1 y CAL-3 en verde, CAL-2 en rojo o
blanco. Cero coste de modelo.
*Esperado:* `0 regressions`. La máquina está calibrada; ahora sí, matemática.

---

## Fase B — El mapa del problema real (M6–M10)

> El problema real del investigador entra en el sistema. No para resolverlo
> esta semana — para convertir las vueltas en un mapa que recuerda.

**M6 — Declarar el objetivo (sesión con el usuario, coste solo de redacción).**
Con el usuario/investigador: acotar el objetivo real. NO "demostrar RH" — el
subobjetivo concreto del manuscrito en el que se ha estado trabajando, en una
frase falsable. Antes de crear el mapa nuevo, el USUARIO borra el mapa
provisional de calibración a mano en su terminal (la guardia no deja hacerlo
al agente, correctamente): `rm -rf map .adversal/map` desde la raíz del
proyecto. Los verdes CAL-* no se pierden: viven en el ledger y sus runs, y el
CI los seguirá re-verificando; solo salen del dibujo.
Después: `adversal_map_init` con el objetivo acordado, y re-añade los nodos
CAL-* de la Fase A con `adversal_map_add` (supports GOAL) para no perder la
calibración… o déjalos fuera si el usuario prefiere un mapa limpio.
Importante: al borrar el mapa demo se pierde la vista de Obsidian; recréala
una vez con el terminal: `python3 scripts/map_tool.py export-obsidian`
(a partir de ahí se refresca sola tras cada misión). Avisa al usuario de que
reabra `map/Map.canvas`.
*Esperado:* un GOAL en morado y un pacto escrito de qué es éxito.

**M7 — La fase de comprensión (el expediente). Multi-sesión; la más cara del
proyecto, a propósito: tiempo en la base.**
Trabaja en rondas hasta saturación medible:
1. *Intake*: pide al usuario las transcripciones de chats previos relevantes y
   pásalas por `adversal_dossier_intake`; añade al expediente SOLO las
   preguntas que el usuario acepte (`adversal_dossier_question`).
2. *Bibliografía*: rastrea la literatura con tu web (los workers no navegan) —
   programas conocidos, callejones con su porqué, parciales, surveys.
   `adversal_bib_add` cada hallazgo con enlace verificado.
3. *Fuentes canónicas*: para todo lo que vaya a sostener algo, trae el texto,
   conviértelo a Markdown y guárdalo con `adversal_bib_attach` (queda anclado
   por hash).
4. *Lecturas*: `adversal_read_paper` nivel `deep` sobre esas fuentes (readers 2
   en las piedras angulares). Toda cita se verifica contra el texto; una cita
   inventada rechaza la lectura entera.
5. *Expediente*: clasifica preguntas (`adversal_dossier_classify` — respondida
   exige 2 fuentes leídas a fondo; el script se niega a menos), añade hechos
   por niveles (`adversal_dossier_fact`), y declara el vacío de las secciones
   sin contenido (`adversal_dossier_note`). Las 10 secciones del patrón, todas.
6. *Auditoría adversarial*: `adversal_dossier_audit` — un worker aislado busca
   preguntas ausentes, afirmaciones flojas y secciones flacas. Sus hallazgos
   marcan la ronda siguiente. Cierra cada ronda con `adversal_dossier_round`
   (cuántas novedades produjo).
*Criterio de salida (todos):* 10 secciones trabajadas o con vacío declarado;
todo lo que sostiene el expediente en nivel `leído a fondo`; `saturated_hint`
verdadero en `adversal_dossier_status`; y el usuario lee el dossier.md en su
Obsidian y aprueba. Hasta entonces, NO se pasa a imaginar.
*Esperado:* una wiki súper documentada de verdad — preguntas del investigador
clasificadas con fuentes, cementerio señalizado, y los cruxes a la vista.

**M8 — La primera descomposición, desde el entendimiento.**
`adversal_decompose` sobre `GOAL` (n 5). Se apoya solo en ambos digests
(bibliografía + expediente) y obliga a cada pieza a declarar su programa
conocido más cercano y su apuesta diferencial. Presenta la propuesta al
usuario con tu lectura crítica (¿atacable en días? ¿adyacente a un callejón
documentado?). Importa SOLO lo aceptado: `adversal_map_import` con `only`.
*Esperado:* 3–5 nodos grises con su adyacencia declarada. Un plan, no un
resultado — dilo así.

**M9 — Objetivos formales para las hojas.**
Para cada nodo hoja aceptado: misión de formalización de ENUNCIADO (no de
prueba): pide al formalizer solo el `formal_statement` candidato, fíjalo con
`adversal_map_set`, pasa `adversal_backtranslate`, y el usuario confirma la
fidelidad. Un nodo sin objetivo formal confirmado no puede dar verde jamás.
*Esperado:* 2–3 hojas con diana formal confirmada; alguna hoja resultará "no
expresable con mathlib hoy" — se anota en el nodo y ES un resultado.

**M10 — Primera misión real, y trocear lo que no cede.**
`adversal_map_next` y `adversal_mission` sobre la primera hoja con diana formal
(worker_timeout 900). Si no establece nada: `adversal_decompose` sobre ESE nodo
(no sobre GOAL), importa lo aceptado, y repite sobre la sub-hoja más pequeña.
*Esperado:* lo más probable, `not_established` con obstrucciones concretas — y
la lección del ritmo: cuando un nodo no cede, se trocea; no se empuja más
fuerte. Si sale verde, backtranslate antes de contarlo.

---

## Fase C — Acumular verdes y matar ramas (M11–M20)

**M11–M16 — Seis misiones sobre hojas del mapa.**
En cada una: `adversal_map_next` → misión sobre la primera hoja lista →
reporte con contadores. Si Codex ya tiene cuota, `providers claude,codex` en
las de formalización dura. Si dos hojas seguidas de la misma rama no ceden,
vuelve a trocear (regla de M10) en vez de quemar cuota.
*Esperado:* 1–3 verdes pequeños entre las seis, varios `not_established` con
obstrucciones útiles, quizá un rojo.

**M17 — Registrar una rama muerta conocida.**
Pide al usuario/investigador un paso de su corpus que ya se sospeche o se sepa
inválido (una derivación dudosa, un salto señalado en revisiones o auditorías
previas). Añádelo como nodo (`adversal_map_add`, con una nota del motivo de
sospecha), corre una misión, y deja el resultado en el mapa.
*Esperado:* `not_established` con el `breaks_at` del escéptico como pista (el
disproof formal probablemente no es construible hoy). El valor: la rama muere
EN EL MAPA, visible, y nadie vuelve a gastarle un mes.

**M18 — Fidelidad en lote.**
`adversal_backtranslate` de TODO lo que esté en verde en el mapa. El usuario
revisa cada par de frases.
*Esperado:* todo coincide. Cualquier discrepancia degrada ese verde a
"formalización errónea" y se re-formaliza (M8).

**M19 — CI + ritual de mapa con el investigador.**
`adversal_reverify`, `/map`, y una revisión del Map.canvas en Obsidian con el
usuario/investigador: qué hay verde, qué murió y por qué, qué sigue. Es el
informe de progreso — colores, no adjetivos.
*Esperado:* `0 regressions` y una decisión humana de prioridades.

**M20 — Retrospectiva escrita.**
Sin modelo o casi: lee el ledger y escribe en el proyecto un
`retrospectiva-20.md` con: contadores finales (proven / refuted /
not_established / leads), coste total del budget ledger, las 3 obstrucciones
más repetidas, y tu propuesta de las siguientes 20 misiones basada en DATOS.
*Esperado:* la primera decisión de roadmap del proyecto tomada con evidencia
en vez de con entusiasmo.

---

*Nota final para el coordinador: si en cualquier punto el usuario te pide saltarte el
gate, recuerda en voz alta el contrato de epistemics.md y ofrécele la
alternativa sancionada. Para eso estás.*
