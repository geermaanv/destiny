# Comparación de modelos de IA (OpenRouter) para explicaciones y rompehielos

Generado por `apps/api/scripts/compare_llm_models.py` el 2026-10-12, con los mismos prompts que usa la app (spec X1) y 3 casos sintéticos (pareja, amistad, trabajo). Precios de la API pública de OpenRouter.

| Modelo | USD cada 1000 textos | Segundos promedio | Errores |
|---|---|---|---|
| `qwen/qwen3.7-flash` | 0.0179 | 1.6 | 0 |
| `mistralai/mistral-small-3.2-24b-instruct` | 0.0514 | 2.7 | 0 |
| `openai/gpt-5-nano` | 0.0000 | None | 6 |
| `google/gemini-2.5-flash-lite` | 0.0595 | 1.3 | 0 |
| `anthropic/claude-haiku-5.5` | 0.1162 | 1.7 | 0 |
| `deepseek/deepseek-v3.2` | 0.1509 | 2.7 | 0 |

## `qwen/qwen3.7-flash`

- **Pareja · Explicación** (2.1 s): Lo que más los une es el compromiso, con un nivel medio que les da la base para construir algo estable. Tienen que trabajar en la atracción, ya que está baja y requiere esfuerzo para encender esa chispa inicial entre ustedes.
- **Pareja · Rompehielos** (1.6 s): Vimos que tienen un potencial lindo para construir algo estable y duradero juntos. ¿Qué buscan cuando pensás en ese compromiso a futuro?
- **Amistad · Explicación** (1.3 s): La química y el cariño son altísimos, así que se llevan muy bien. Pero la comunicación está baja, lo que pueden trabajar para entendernos mejor y evitar malentendidos.
- **Amistad · Rompehielos** (1.4 s): Nos une una conexión emocional muy fuerte y sincera, así que cuéntame, ¿qué es lo primero que te viene a la mente cuando pensás en este vínculo?
- **Trabajo · Explicación** (1.6 s): Lo que más los une es la comunicación, con un nivel alto que facilita el entendimiento mutuo. Sin embargo, tienen que trabajar en el compromiso, ya que está bajo y les cuesta construir algo estable juntos.
- **Trabajo · Rompehielos** (1.5 s): Vemos que tienen una conexión mental increíble, así que vamos a aprovechar esa onda para charlar. ¿Qué tema les sale más fácil de conversar cuando empiezan a hablar?

## `mistralai/mistral-small-3.2-24b-instruct`

- **Pareja · Explicación** (3.4 s): Lo que más los une es su compromiso medio: ambos buscan construir algo estable. Para fortalecer su vínculo, tendrán que trabajar en su baja atracción, encontrando formas de conectarse más profundamente y encender esa chispa.
- **Pareja · Rompehielos** (2.2 s): Qué bueno que los dos busquen algo estable, ¿no? ¿Vos también sentís que la comunicación es clave para construir algo fuerte?
- **Amistad · Explicación** (2.4 s): Los une una profunda conexión emocional, llena de cariño y complicidad. Para fortalecer su amistad, tendrán que trabajar en mejorar la comunicación, ya que les cuesta entender cómo se expresan mutuamente.
- **Amistad · Rompehielos** (1.1 s): Tenemos un feeling especial desde el primer momento, como si ya nos conociéramos. ¿Qué crees que nos une tan fuerte?
- **Trabajo · Explicación** (4.3 s): En esta relación laboral, lo que más los une es su excelente comunicación. Se entienden rápido, se complementan y fluye la información con facilidad. Sin embargo, tendrán que trabajar en el compromiso, ya que les costará un poco alinear sus objetivos a largo plazo y mantener la constancia en proyectos conjuntos.
- **Trabajo · Rompehielos** (2.7 s): Nos encanta cómo fluye la comunicación entre nosotros, parece que ya nos conocemos de antes. ¿Qué opinas de esta conexión tan instantánea?

## `openai/gpt-5-nano`

- **Pareja · Explicación** (0.1 s): ⚠️ HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cannot be disabled.","code":400,"metadata":{"provider_name":null}}}
- **Pareja · Rompehielos** (0.1 s): ⚠️ HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cannot be disabled.","code":400,"metadata":{"provider_name":null}}}
- **Amistad · Explicación** (0.1 s): ⚠️ HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cannot be disabled.","code":400,"metadata":{"provider_name":null}}}
- **Amistad · Rompehielos** (0.1 s): ⚠️ HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cannot be disabled.","code":400,"metadata":{"provider_name":null}}}
- **Trabajo · Explicación** (0.1 s): ⚠️ HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cannot be disabled.","code":400,"metadata":{"provider_name":null}}}
- **Trabajo · Rompehielos** (0.1 s): ⚠️ HTTP 400: {"error":{"message":"Reasoning is mandatory for this endpoint and cannot be disabled.","code":400,"metadata":{"provider_name":null}}}

## `google/gemini-2.5-flash-lite`

- **Pareja · Explicación** (0.9 s): Lo que más los une es el deseo de construir algo sólido y duradero, buscando seguridad y estabilidad juntos. Sin embargo, la chispa y la conexión profunda son un área a desarrollar, necesitando avivar la pasión y la atracción mutua para que la relación florezca.
- **Pareja · Rompehielos** (1.1 s): ¡Qué copado! Vemos que lo que más nos une es la idea de construir algo lindo y estable juntos, como que el universo nos está guiando por ahí. ¿Qué es lo que más buscás en una relación a largo plazo?
- **Amistad · Explicación** (1.1 s): Hay un montón de afecto y buena onda entre ustedes, eso los acerca un montón. Para que la amistad funcione de verdad, van a tener que ponerle pilas a la forma en que se comunican y se entienden.
- **Amistad · Rompehielos** (2.1 s): ¡Che, qué copado que conectamos! Se nota que nos une un montón el afecto y las ganas de construir algo copado, ¿no? ¿Qué es lo que más te gusta de sentirte cerca de la gente?
- **Trabajo · Explicación** (0.9 s): Lo que más los une es una comunicación fluida y un entendimiento mutuo que facilita el trabajo en equipo. Sin embargo, para que el vínculo sea duradero, van a tener que aprender a comprometerse y a construir un proyecto en común a largo plazo.
- **Trabajo · Rompehielos** (1.9 s): ¡Qué copado que tengamos esta conexión tan fluida para charlar! ¿Qué es lo que más te gusta de poder expresarte libremente?

## `anthropic/claude-haiku-5.5`

- **Pareja · Explicación** (2.0 s): Lo que más los une es el compromiso: ambos tienen una base de ganas de construir algo estable y de cuidar un proyecto en común, con un nivel medio que da para avanzar con paciencia. Lo que tienen que trabajar es la atracción: la química entre los dos está en un nivel bajo, así que conviene darle espacio a lo que enciende el vínculo, sin esperar que aparezca sola.
- **Pareja · Rompehielos** (1.5 s): Nos une la idea de construir algo que dure, y me gusta que eso ya esté en el centro de esta conexión. ¿Qué es lo primero que te imaginás cuando pensás en un proyecto de pareja que sea sólido de verdad?
- **Amistad · Explicación** (1.7 s): Entre ustedes hay un afecto que se nota: la conexión emocional es lo que más los une, y eso les da una base cálida para sostener la amistad. Lo que van a tener que trabajar es la comunicación, porque hablar de frente y decirse las cosas a tiempo no les sale tan natural, así que conviene ser más explícitos con lo que sienten y necesitan.
- **Amistad · Rompehielos** (1.6 s): Nos cruzamos en Destiny y ya siento que tenemos cosas para contarnos, así que arranquemos por lo que más nos une: ¿qué es lo que más te hace sentir en casa cuando estás con alguien de confianza?
- **Trabajo · Explicación** (1.8 s): Lo que más los une es la comunicación: se entienden bien al hablar, se escuchan y se les hace fácil explicar las ideas, algo muy valioso en un vínculo de trabajo. Lo que tienen que trabajar es el compromiso: construir algo estable a largo plazo les va a costar más que lo demás, así que conviene aclarar desde el principio los objetivos, los tiempos y quién hace qué.
- **Trabajo · Rompehielos** (1.6 s): Qué bueno que nos conectó Destiny, parece que nos entendemos bastante bien al hablar, así que arranquemos por ahí: ¿qué es lo que más te gusta charlar cuando conocés a alguien nuevo?

## `deepseek/deepseek-v3.2`

- **Pareja · Explicación** (1.1 s): Lo que más los une es el deseo de compromiso, aunque tienen que trabajar la atracción porque está baja. Su comunicación fluye bien, pero falta conectar más en lo afectivo para fortalecer el vínculo como pareja.
- **Pareja · Rompehielos** (1.2 s): Uf, mirá todo lo que hay para construir juntos... ¿qué proyecto te gustaría empezar?
- **Amistad · Explicación** (3.2 s): Los une un afecto profundo y sincero, con mucha química y ganas de construir algo estable. El desafío está en la comunicación: a veces les cuesta expresarse con claridad o entenderse, y eso puede generar roces si no le ponen palabras a lo que sienten.
- **Amistad · Rompehielos** (6.3 s): Che, mirá, justo estaba pensando que tenemos una conexión re linda y eso es lo más copado. ¿Qué te parece si hoy charlamos un toque más para conocernos mejor?
- **Trabajo · Explicación** (2.3 s): Lo que más los une es la comunicación, que es alta: se entienden bien para trabajar juntos y coordinar. Lo que tienen que trabajar es el compromiso, que es bajo: les cuesta alinear sus objetivos a largo plazo o mantener la constancia en proyectos compartidos.
- **Trabajo · Rompehielos** (1.9 s): Viendo que tenemos muy buena comunicación, ¿qué proyecto te gustaría que empecemos a charlar para coordinar mejor?
