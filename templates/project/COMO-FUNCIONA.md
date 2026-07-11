# Cómo funciona este sistema, explicado desde cero

*(Documento para el investigador y su equipo. El coordinador puede releerlo
cuando haga falta re-explicar el sistema.)*

## El problema que venimos a resolver

Trabajar matemáticas difíciles con IAs tiene una trampa: **te dicen que sí a
todo**. Que vas bien, que casi está, que es brillante. Y pasar la respuesta de
una IA a otra no lo arregla — todas leyeron los mismos libros y todas quieren
agradar. Si no eres matemático, no puedes distinguir un avance real de humo
bien redactado. Resultado: meses dando vueltas sin saber si hay algo.

## La idea central, en una frase

**Ninguna opinión de ninguna IA cuenta como verdad. Solo cuenta lo que
verifica una máquina que no sabe adular: Lean.**

Lean es un programa (usado por los mejores matemáticos del mundo) que
comprueba demostraciones paso a paso, como una calculadora: o la prueba
compila, o no. No se le puede convencer, impresionar ni dar pena. A eso lo
llamamos **el gate** (la puerta): nada se declara "demostrado" sin pasar por
ella.

## Las piezas

1. **El coordinador (Hermes).** El secretario. Habla contigo, organiza el
   trabajo, lanza a los trabajadores, te informa. **Nunca decide qué es
   verdad** — tiene prohibido (por software, no por promesa) escribir en los
   registros de resultados.
2. **El council (los trabajadores).** Varias IAs, cada una con un papel fijo y
   **aisladas entre sí** (no ven el trabajo de las otras, para que no se
   contagien errores):
   - El **formalizador**: traduce la afirmación a Lean e intenta demostrarla.
   - El **auditor**: busca si eso ya estaba descubierto en la literatura.
   - El **escéptico**: intenta romperla. Tiene prohibido halagar.
3. **El motor de veredictos.** Un programa normal y corriente (sin IA) que
   aplica las reglas: ¿compiló la prueba en Lean? → `proven`. ¿Compiló una
   desprueba? → `refuted`. ¿Nada de eso? → `not_established` (no establecido),
   que es la respuesta honesta por defecto. Los halagos se cuentan y se tiran.
4. **El ledger (el libro de actas).** Cada veredicto se apunta en un registro
   que solo se puede añadir, nunca reescribir. Es la memoria oficial.
5. **El mapa.** El tablero visual (en Obsidian): el objetivo arriba, las
   piezas necesarias debajo, cada una con un color. **Los colores salen solo
   del libro de actas** — nadie, ni el coordinador, puede pintar un nodo de
   verde a mano. El mapa responde a la pregunta "¿esto que probamos acerca al
   objetivo?" mirando su posición: si está en el árbol del objetivo, suma.
6. **Las misiones.** La unidad de trabajo: una afirmación concreta y acotada
   que se somete al proceso completo.

## Antes de imaginar: la fase de comprensión

Con el objetivo declarado, el sistema no se lanza a proponer: primero se
estudia el problema en serio. El coordinador trae los papers a la wiki (copias
canónicas, ancladas por hash), lectores aislados los leen de verdad — cada
conclusión anclada a una cita textual que una máquina comprueba contra el
documento; una cita inventada tumba la lectura entera — y todo se organiza en
el **expediente**: las preguntas del investigador clasificadas (respondida /
parcial / abierta / aún-no-precisa), los hechos por niveles (establecido solo
con dos fuentes leídas a fondo), los callejones documentados con su porqué, y
lo que los expertos dicen que falta. Un auditor adversarial busca lo que se
quedó fuera, y la fase termina cuando las rondas dejan de aportar — medido,
no sentido. Solo entonces se imagina: desde el entendimiento, no desde la nada.

## Qué pasa, paso a paso, en una misión

1. **Las afirmaciones no las inventa el humano — las propone la máquina.**
   El investigador declara el objetivo en lenguaje normal ("quiero atacar X
   por esta clase de vía"). La ideación y la descomposición generan candidatos
   concretos en su idioma, y el investigador **elige** cuáles se persiguen.
   Cada elegido se añade como nodo gris del mapa.
2. El coordinador lanza la misión. Cada trabajador recibe **solo el
   enunciado** — sin contexto, sin saber de quién es, sin ver a los demás.
3. El formalizador escribe la prueba en Lean. El auditor busca si es
   conocido. El escéptico busca el fallo (y si dice "es falso", tiene que
   construir una desprueba que Lean acepte — su palabra no vale).
4. El motor de veredictos ejecuta Lean de verdad y aplica las reglas. Ni
   votos, ni promedios, ni entusiasmo: kernel o nada.
5. El veredicto se apunta en el libro de actas y **el nodo del mapa cambia de
   color solo**: verde probado, rojo refutado, gris sin establecer.
6. **Retro-traducción** (el paso anti-trampa): otra IA que *nunca vio la
   frase original* traduce el Lean de vuelta al idioma del investigador, y un
   HUMANO compara las dos frases. Así evitamos el engaño más peligroso: que
   "verificado" signifique *otra cosa* distinta de lo que se quiso decir.
7. De vez en cuando, el **CI matemático** re-comprueba todo lo verde. Si algo
   deja de compilar, el mapa lo marca con ⚠ y deja de contar como probado.

## Los colores del mapa

- 🟢 verde = probado por Lean · 🔴 rojo = refutado por Lean
- ⚪ gris = sin intentar o sin establecer · 🟡 amarillo = conjetura razonada
- 🟠 naranja = disputa o regresión · 🟣 morado = el objetivo

## Qué es "éxito" aquí (el pacto)

La mayoría de misiones terminarán en "no establecido". **Eso no es fracaso:
es el sistema diciendo la verdad.** El éxito es: (1) saber en todo momento
qué está de verdad demostrado y qué no; (2) que los errores se encuentren y
queden apuntados para no repetirlos; (3) acumular lemas verdes pequeños que
alimentan el objetivo. Lo que este sistema promete no es resolver el problema
— es **que nunca más te mientan sobre cuánto llevas resuelto**.

## Cómo empezar

Con el bootstrap terminado (todos los checks en verde), dile al coordinador:
**"Lee MISIONES.md y ejecuta la M1."** Las misiones M1–M5 calibran la máquina;
la M6 es la reunión donde tu objetivo real entra en el sistema.
