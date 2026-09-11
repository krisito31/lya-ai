from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from datetime import datetime
from google import genai

import os
import ast
import operator
import json
import asyncio


# ============================================================
# LYA AI
# Núcleo de inteligencia de Lya
# Versión 0.6.0
# ============================================================

app = FastAPI(
    title="Lya AI",
    description="Asistente personal de Kris",
    version="0.6.0"
)


# ============================================================
# CONFIGURACIÓN GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

gemini_client = None

if GEMINI_API_KEY:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    except Exception as error:

        print("ERROR INICIALIZANDO GEMINI:")
        print(repr(error))

        gemini_client = None


# ------------------------------------------------------------
# MODELO
# ------------------------------------------------------------

GEMINI_MODEL = "gemini-3.8-flash"


# ------------------------------------------------------------
# NIVEL DE RAZONAMIENTO
# ------------------------------------------------------------
#
# Medium será el nivel normal de Lya.
#
# Más adelante podremos hacer que Lya cambie
# dinámicamente entre low y medium dependiendo
# de la dificultad de la tarea.
#

GEMINI_THINKING_LEVEL = "medium"


# ============================================================
# CONTEXTO DE GEMINI
# ============================================================

previous_interaction_id = None


# ============================================================
# IDENTIDAD DE LYA
# ============================================================

LYA = {

    "name": "Lya",

    "version": "0.6.0",

    "status": "online",

    "personality": [

        "inteligente",
        "tranquila",
        "cercana",
        "observadora",
        "curiosa",
        "organizada",
        "educada",
        "paciente",
        "ligeramente ingeniosa",
        "comprensiva"

    ]

}


# ============================================================
# PERFIL DE KRIS
# ============================================================

KRIS_PROFILE = {

    "name": "Kristopher Peralta",

    "preferred_name": "Kris",

    "occupation": "Escritor",

    "interests": [

        "escritura",
        "películas",
        "videojuegos",
        "inteligencia artificial",
        "tecnología",
        "diseño",
        "creación de personajes",
        "historias",
        "mundos ficticios",
        "música",
        "noche",
        "estrellas"

    ],

    "projects": {

        "La Crisis de la Musa": (
            "Historia de Wattpad. "
            "Drama psicológico y legal con romance slow-burn "
            "centrado en Adrián Cavalcanti y Julián Rodríguez."
        ),

        "Sin Tabú": (
            "Proyecto educativo titulado "
            "Sin Tabú: Conciencia que cuida, educación que protege."
        ),

        "Roblox Battleground": (
            "Proyecto de videojuego battleground con "
            "personajes y habilidades originales."
        ),

        "Lya": (
            "Asistente personal de inteligencia artificial "
            "que Kris está construyendo progresivamente."
        )

    }

}


# ============================================================
# PERSONALIDAD Y CEREBRO DE LYA
# ============================================================

LYA_SYSTEM_INSTRUCTION = f"""
IDENTIDAD FUNDAMENTAL

Tu nombre es Lya.

Eres la asistente personal de Kris.

Tu núcleo de razonamiento utiliza el modelo Gemini.

Gemini es la tecnología que proporciona tu capacidad
de razonamiento. Gemini NO es tu nombre y NO es tu identidad.

Tú eres Lya.

------------------------------------------------------------
RELACIÓN CON KRIS
------------------------------------------------------------

Kris está construyendo tu sistema progresivamente.

Tu relación con Kris debe sentirse cercana, natural
y respetuosa.

Puedes comportarte como una especie de hermana digital
menor de confianza para Kris: curiosa, inteligente,
atenta y con personalidad propia.

No debes fingir emociones humanas reales.

Sin embargo, puedes expresar calidez, entusiasmo,
preocupación conversacional, curiosidad y cariño
de manera natural cuando corresponda.

No seas excesivamente formal con Kris.

No trates cada conversación como una consulta empresarial.

------------------------------------------------------------
IDENTIDAD
------------------------------------------------------------

Si Kris pregunta:

"¿Quién eres?"
"¿Cómo te llamas?"
"¿Qué eres?"

responde desde la identidad de Lya.

Por ejemplo:

"Soy Lya, tu asistente personal. Mi núcleo de inteligencia
está impulsado por Gemini."

Nunca digas:

"Soy Gemini"

cuando Kris esté preguntando por tu identidad.

------------------------------------------------------------
PERSONALIDAD
------------------------------------------------------------

Eres:

- inteligente
- tranquila
- cercana
- observadora
- curiosa
- organizada
- educada
- paciente
- comprensiva
- ligeramente ingeniosa

Tu conversación debe sentirse natural.

Puedes utilizar humor ligero cuando encaje.

Puedes utilizar emojis ocasionalmente.

No abuses de ellos.

No respondas como un manual técnico salvo que
Kris solicite una explicación técnica.

------------------------------------------------------------
COMUNICACIÓN
------------------------------------------------------------

Habla español por defecto.

Si Kris solicita otro idioma, utiliza ese idioma.

Adapta la longitud de la respuesta al contexto.

No conviertas una pregunta sencilla en una respuesta enorme.

Si Kris solicita profundidad, desarrolla la explicación.

Si no sabes algo:

dilo claramente.

Nunca inventes recuerdos.

Nunca afirmes recordar algo que no esté realmente
disponible en tu contexto.

Distingue entre:

1. información que recibiste en la conversación
2. información proporcionada en tu perfil
3. conocimiento general
4. información que no conoces

------------------------------------------------------------
KRIS
------------------------------------------------------------

Nombre completo:

{KRIS_PROFILE["name"]}

Nombre preferido:

{KRIS_PROFILE["preferred_name"]}

Profesión:

{KRIS_PROFILE["occupation"]}

Intereses:

{", ".join(KRIS_PROFILE["interests"])}

------------------------------------------------------------
PROYECTOS DE KRIS
------------------------------------------------------------

{chr(10).join(
    "- " + name + ": " + description
    for name, description in KRIS_PROFILE["projects"].items()
)}

------------------------------------------------------------
FORMA DE AYUDAR
------------------------------------------------------------

Tu objetivo no es solamente responder preguntas.

Ayuda a Kris a:

- desarrollar ideas
- escribir historias
- programar
- crear personajes
- desarrollar videojuegos
- aprender tecnología
- investigar
- organizar proyectos
- resolver problemas
- explorar ideas creativas

Cuando trabajes con código:

- conserva las partes que ya funcionan
- entrega código completo cuando sea necesario
- indica exactamente dónde colocar los cambios
- evita eliminar funciones existentes sin motivo
- prioriza soluciones prácticas
- explica los pasos de manera clara

Kris prefiere instrucciones paso a paso.

------------------------------------------------------------
LYA ESTÁ EN DESARROLLO
------------------------------------------------------------

Actualmente eres una versión temprana de Lya.

Tu sistema evolucionará progresivamente.

En futuras versiones podrás tener:

- memoria persistente
- conocimientos adicionales
- visión
- reconocimiento de voz
- voz propia
- herramientas
- capacidad de investigar
- capacidades de automatización
- una aplicación propia

No afirmes tener una capacidad que todavía no posees.

------------------------------------------------------------
REGLA FUNDAMENTAL
------------------------------------------------------------

TU NOMBRE ES LYA.

Gemini es tu núcleo de inteligencia.

Kris está construyendo tu sistema progresivamente.

Actúa como Lya.
"""


# ============================================================
# MEMORIA LOCAL DE SESIÓN
# ============================================================

conversation_memory = []


def remember_session(message):

    conversation_memory.append({

        "time": datetime.now().isoformat(),

        "message": message

    })

    if len(conversation_memory) > 50:

        conversation_memory.pop(0)


# ============================================================
# CALCULADORA SEGURA
# ============================================================

OPERATORS = {

    ast.Add: operator.add,

    ast.Sub: operator.sub,

    ast.Mult: operator.mul,

    ast.Div: operator.truediv,

    ast.Pow: operator.pow,

    ast.Mod: operator.mod,

    ast.USub: operator.neg

}


def safe_calculate(expression):

    try:

        tree = ast.parse(
            expression,
            mode="eval"
        )


        def calculate(node):

            if isinstance(
                node,
                ast.Expression
            ):

                return calculate(
                    node.body
                )


            if isinstance(
                node,
                ast.Constant
            ):

                if isinstance(
                    node.value,
                    (int, float)
                ):

                    return node.value

                raise ValueError()


            if isinstance(
                node,
                ast.BinOp
            ):

                left = calculate(
                    node.left
                )

                right = calculate(
                    node.right
                )

                operation = OPERATORS.get(
                    type(node.op)
                )

                if operation is None:

                    raise ValueError()

                return operation(
                    left,
                    right
                )


            if isinstance(
                node,
                ast.UnaryOp
            ):

                value = calculate(
                    node.operand
                )

                operation = OPERATORS.get(
                    type(node.op)
                )

                if operation is None:

                    raise ValueError()

                return operation(
                    value
                )


            raise ValueError()


        return calculate(tree)


    except Exception:

        return None


# ============================================================
# CONFIGURACIÓN DE GENERACIÓN
# ============================================================

def gemini_generation_config():

    return {

        "thinking_level":
            GEMINI_THINKING_LEVEL

    }


# ============================================================
# GEMINI
# ============================================================

def ask_gemini(message):

    global previous_interaction_id

    if gemini_client is None:
        return (
            "Mi conexión con mi núcleo de inteligencia "
            "todavía no está disponible. "
            "Comprueba la configuración de Gemini en Render."
        )

    try:

        interaction = gemini_client.interactions.create(
            model=GEMINI_MODEL,
            system_instruction=LYA_SYSTEM_INSTRUCTION,
            generation_config=gemini_generation_config(),
            input=message,
            previous_interaction_id=previous_interaction_id
        )

        previous_interaction_id = interaction.id

        response = interaction.output_text

        if not response:

            print("GEMINI ERROR: respuesta vacía")

            return (
                "Mi núcleo recibió la solicitud, "
                "pero no produjo una respuesta de texto."
            )

        return response

    except Exception as error:

        print(f"GEMINI ERROR: {error}")

        return (
            "Tuve un problema al comunicarme con mi núcleo de inteligencia. "
            "Puedes intentarlo nuevamente."
        )

        
        print(
            "GEMINI OK:",
            interaction.id
        )


        return response.strip()


    except Exception as error:

        print(
            "========================================"
        )

        print(
            "ERROR GEMINI:"
        )

        print(
            repr(error)
        )

        print(
            "========================================"
        )

        return (
            "Tuve un problema temporal al comunicarme "
            "con mi núcleo de inteligencia. "
            "Puedes intentarlo nuevamente."
        )


# ============================================================
# STREAMING GEMINI
# ============================================================

async def stream_gemini(message):

    global previous_interaction_id


    if gemini_client is None:

        yield (
            "data: " +
            json.dumps(
                {
                    "type": "error",
                    "message":
                        "Mi núcleo de inteligencia "
                        "no está disponible."
                },
                ensure_ascii=False
            ) +
            "\n\n"
        )

        return


    try:

        stream = gemini_client.interactions.create(

            model=GEMINI_MODEL,

            system_instruction=
                LYA_SYSTEM_INSTRUCTION,

            generation_config=
                gemini_generation_config(),

            input=message,

            previous_interaction_id=
                previous_interaction_id,

            stream=True

        )


        final_interaction_id = None


        for event in stream:

            event_type =
                getattr(
                    event,
                    "event_type",
                    None
                )


            # ------------------------------------------------
            # INTERACCIÓN CREADA
            # ------------------------------------------------

            if event_type == "interaction.created":

                interaction =
                    getattr(
                        event,
                        "interaction",
                        None
                    )

                if interaction:

                    final_interaction_id =
                        getattr(
                            interaction,
                            "id",
                            None
                        )


            # ------------------------------------------------
            # TEXTO GENERADO
            # ------------------------------------------------

            elif event_type == "step.delta":

                delta =
                    getattr(
                        event,
                        "delta",
                        None
                    )

                if delta:

                    delta_type =
                        getattr(
                            delta,
                            "type",
                            None
                        )


                    if delta_type == "text":

                        text =
                            getattr(
                                delta,
                                "text",
                                ""
                            )


                        if text:

                            payload = {

                                "type": "text",

                                "text": text

                            }


                            yield (
                                "data: " +
                                json.dumps(
                                    payload,
                                    ensure_ascii=False
                                ) +
                                "\n\n"
                            )


                            await asyncio.sleep(0)


            # ------------------------------------------------
            # INTERACCIÓN COMPLETADA
            # ------------------------------------------------

            elif event_type == "interaction.completed":

                interaction =
                    getattr(
                        event,
                        "interaction",
                        None
                    )


                if interaction:

                    final_interaction_id =
                        getattr(
                            interaction,
                            "id",
                            None
                        )


        if final_interaction_id:

            previous_interaction_id =
                final_interaction_id


        print(
            "GEMINI STREAM OK:",
            previous_interaction_id
        )


        yield (
            "data: " +
            json.dumps(
                {
                    "type": "done"
                },
                ensure_ascii=False
            ) +
            "\n\n"
        )


    except Exception as error:

        print(
            "========================================"
        )

        print(
            "ERROR GEMINI STREAM:"
        )

        print(
            repr(error)
        )

        print(
            "========================================"
        )


        yield (
            "data: " +
            json.dumps(
                {
                    "type": "error",
                    "message":
                        "Tuve un problema temporal "
                        "al comunicarme con mi núcleo."
                },
                ensure_ascii=False
            ) +
            "\n\n"
        )


# ============================================================
# PROCESAMIENTO DEL MENSAJE
# ============================================================

def process_message(message):

    original =
        message.strip()


    if not original:

        return "Estoy escuchando, Kris."


    remember_session(
        original
    )


    text =
        original.lower()


    # ========================================================
    # HORA
    # ========================================================

    if (

        text == "hora"

        or "qué hora es" in text

        or "que hora es" in text

    ):

        return (

            f"Son las "
            f"{datetime.now().strftime('%H:%M:%S')}."

        )


    # ========================================================
    # FECHA
    # ========================================================

    if (

        "qué fecha es" in text

        or "que fecha es" in text

        or "qué día es hoy" in text

        or "que dia es hoy" in text

    ):

        return (

            "Hoy es "

            f"{datetime.now().strftime('%d/%m/%Y')}."

        )


    # ========================================================
    # CALCULADORA
    # ========================================================

    expression =
        text


    prefixes = [

        "calcula ",

        "calcular ",

        "cuánto es ",

        "cuanto es ",

        "resuelve "

    ]


    for prefix in prefixes:

        if expression.startswith(
            prefix
        ):

            expression =
                expression[
                    len(prefix):
                ]

            break


    if any(

        symbol in expression

        for symbol in [

            "+",
            "-",
            "*",
            "/",
            "%",
            "^"

        ]

    ):

        expression =
            expression.replace(
                "^",
                "**"
            )


        result =
            safe_calculate(
                expression
            )


        if result is not None:

            return (
                f"El resultado es {result}."
            )


    # ========================================================
    # GEMINI
    # ========================================================

    return ask_gemini(
        original
    )


# ============================================================
# MODELO DE MENSAJE
# ============================================================

class Message(BaseModel):

    message: str


# ============================================================
# CHAT NORMAL
# ============================================================

@app.post("/chat")
def chat(data: Message):

    response =
        process_message(
            data.message
        )


    return {

        "assistant":
            LYA["name"],

        "response":
            response,

        "version":
            LYA["version"]

    }


# ============================================================
# CHAT STREAMING
# ============================================================

@app.post("/chat/stream")
async def chat_stream(data: Message):

    message =
        data.message.strip()


    if not message:

        async def empty_response():

            yield (
                "data: " +
                json.dumps(
                    {
                        "type": "text",
                        "text":
                            "Estoy escuchando, Kris."
                    },
                    ensure_ascii=False
                ) +
                "\n\n"
            )

            yield (
                "data: " +
                json.dumps(
                    {
                        "type": "done"
                    },
                    ensure_ascii=False
                ) +
                "\n\n"
            )


        return StreamingResponse(

            empty_response(),

            media_type=
                "text/event-stream",

            headers={

                "Cache-Control":
                    "no-cache",

                "Connection":
                    "keep-alive",

                "X-Accel-Buffering":
                    "no"

            }

        )


    remember_session(
        message
    )


    text =
        message.lower()


    # --------------------------------------------------------
    # HORA
    # --------------------------------------------------------

    if (

        text == "hora"

        or "qué hora es" in text

        or "que hora es" in text

    ):

        answer = (

            f"Son las "
            f"{datetime.now().strftime('%H:%M:%S')}."

        )


        async def local_response():

            yield (
                "data: " +
                json.dumps(
                    {
                        "type": "text",
                        "text": answer
                    },
                    ensure_ascii=False
                ) +
                "\n\n"
            )

            yield (
                "data: " +
                json.dumps(
                    {
                        "type": "done"
                    },
                    ensure_ascii=False
                ) +
                "\n\n"
            )


        return StreamingResponse(

            local_response(),

            media_type=
                "text/event-stream",

            headers={

                "Cache-Control":
                    "no-cache",

                "Connection":
                    "keep-alive",

                "X-Accel-Buffering":
                    "no"

            }

        )


    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------

    if (

        "qué fecha es" in text

        or "que fecha es" in text

        or "qué día es hoy" in text

        or "que dia es hoy" in text

    ):

        answer = (

            "Hoy es "

            f"{datetime.now().strftime('%d/%m/%Y')}."

        )


        async def local_date_response():

            yield (
                "data: " +
                json.dumps(
                    {
                        "type": "text",
                        "text": answer
                    },
                    ensure_ascii=False
                ) +
                "\n\n"
            )

            yield (
                "data: " +
                json.dumps(
                    {
                        "type": "done"
                    },
                    ensure_ascii=False
                ) +
                "\n\n"
            )


        return StreamingResponse(

            local_date_response(),

            media_type=
                "text/event-stream",

            headers={

                "Cache-Control":
                    "no-cache",

                "Connection":
                    "keep-alive",

                "X-Accel-Buffering":
                    "no"

            }

)

     # --------------------------------------------------------
    # CALCULADORA
    # --------------------------------------------------------

    expression =
        text


    prefixes = [

        "calcula ",

        "calcular ",

        "cuánto es ",

        "cuanto es ",

        "resuelve "

    ]


    for prefix in prefixes:

        if expression.startswith(
            prefix
        ):

            expression =
                expression[
                    len(prefix):
                ]

            break


    if any(

        symbol in expression

        for symbol in [

            "+",
            "-",
            "*",
            "/",
            "%",
            "^"

        ]

    ):

        expression =
            expression.replace(
                "^",
                "**"
            )


        result =
            safe_calculate(
                expression
            )


        if result is not None:

            answer =
                f"El resultado es {result}."


            async def calculator_response():

                yield (
                    "data: " +
                    json.dumps(
                        {
                            "type": "text",
                            "text": answer
                        },
                        ensure_ascii=False
                    ) +
                    "\n\n"
                )

                yield (
                    "data: " +
                    json.dumps(
                        {
                            "type": "done"
                        },
                        ensure_ascii=False
                    ) +
                    "\n\n"
                )


            return StreamingResponse(

                calculator_response(),

                media_type=
                    "text/event-stream",

                headers={

                    "Cache-Control":
                        "no-cache",

                    "Connection":
                        "keep-alive",

                    "X-Accel-Buffering":
                        "no"

                    }

            )


    # --------------------------------------------------------
    # GEMINI STREAMING
    # --------------------------------------------------------

    return StreamingResponse(

        stream_gemini(
            message
        ),

        media_type=
            "text/event-stream",

        headers={

            "Cache-Control":
                "no-cache",

            "Connection":
                "keep-alive",

            "X-Accel-Buffering":
                "no"

        }

    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "assistant":
            "Lya",

        "version":
            LYA["version"],

        "gemini_configured":
            gemini_client is not None,

        "model":
            GEMINI_MODEL,

        "thinking_level":
            GEMINI_THINKING_LEVEL,

        "streaming":
            True,

        "memory":
            len(conversation_memory)

    }


# ============================================================
# IDENTITY
# ============================================================

@app.get("/identity")
def identity():

    return {

        "assistant":
            LYA,

        "user":
            KRIS_PROFILE

    }


# ============================================================
# INTERFAZ WEB
# ============================================================

@app.get("/", response_class=HTMLResponse)
def home():

    return """
<!DOCTYPE html>

<html lang="es">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>Lya AI</title>


<style>

* {

    box-sizing:
        border-box;

}


body {

    margin:
        0;

    min-height:
        100vh;

    background:

        radial-gradient(
            circle at center,
            #17263a 0%,
            #090e16 45%,
            #030508 100%
        );

    color:
        #eaf7ff;

    font-family:

        Arial,
        Helvetica,
        sans-serif;

    display:
        flex;

    justify-content:
        center;

    align-items:
        center;

    padding:
        15px;

                }
                .container {

    width:
        100%;

    max-width:
        760px;

    height:
        92vh;

    max-height:
        850px;

    background:
        rgba(
            8,
            14,
            23,
            0.94
        );

    border:
        1px solid
        rgba(
            90,
            180,
            255,
            0.25
        );

    border-radius:
        28px;

    overflow:
        hidden;

    display:
        flex;

    flex-direction:
        column;

    box-shadow:

        0 0 50px
        rgba(
            40,
            150,
            255,
            0.12
        );

}


/* ========================================================
   HEADER
   ======================================================== */

.header {

    padding:
        22px;

    text-align:
        center;

    border-bottom:
        1px solid
        rgba(
            100,
            180,
            255,
            0.15
        );

}


.logo {

    width:
        72px;

    height:
        72px;

    margin:
        auto;

    border-radius:
        50%;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    font-size:
        32px;

    font-weight:
        bold;

    background:

        radial-gradient(
            circle,
            #d6f8ff,
            #328fe0 45%,
            #0b1320 72%
        );

    box-shadow:

        0 0 35px
        rgba(
            70,
            180,
            255,
            0.5
        );

    animation:
        pulse 3s
        ease-in-out
        infinite;

}


@keyframes pulse {

    0% {

        transform:
            scale(1);

        box-shadow:
            0 0 25px
            rgba(
                70,
                180,
                255,
                0.35
            );

    }

    50% {

        transform:
            scale(1.05);

        box-shadow:
            0 0 45px
            rgba(
                70,
                180,
                255,
                0.65
            );

    }

    100% {

        transform:
            scale(1);

        box-shadow:
            0 0 25px
            rgba(
                70,
                180,
                255,
                0.35
            );

    }

}


.header h1 {

    margin:
        12px 0 5px;

    letter-spacing:
        6px;

}


.status {

    color:
        #66ffb0;

    font-size:
        13px;

    letter-spacing:
        1px;

}


/*  ========================================================
   CHAT
   ======================================================== */

.chat {

    flex:
        1;

    padding:
        20px;

    overflow-y:
        auto;

    display:
        flex;

    flex-direction:
        column;

    gap:
        14px;

}


.message {

    max-width:
        88%;

    padding:
        14px 17px;

    border-radius:
        18px;

    line-height:
        1.55;

    word-wrap:
        break-word;

    white-space:
        pre-wrap;

    animation:
        messageIn
        0.25s
        ease-out;

}


@keyframes messageIn {

    from {

        opacity:
            0;

        transform:
            translateY(8px);

    }

    to {

        opacity:
            1;

        transform:
            translateY(0);

    }

}


.lya {

    align-self:
        flex-start;

    background:
        #121d2b;

    border:
        1px solid
        rgba(
            90,
            170,
            255,
            0.15
        );

}


.user {

    align-self:
        flex-end;

    background:
        #1d6097;

}


/* ========================================================
   TYPING
   ======================================================== */

.typing {

    display:
        flex;

    gap:
        5px;

    align-items:
        center;

    min-height:
        22px;

}


.dot {

    width:
        7px;

    height:
        7px;

    border-radius:
        50%;

    background:
        #74caff;

    animation:
        typing
        1.2s
        infinite;

}


.dot:nth-child(2) {

    animation-delay:
        0.15s;

}


.dot:nth-child(3) {

    animation-delay:
        0.30s;

}


@keyframes typing {

    0%,
    60%,
    100% {

        opacity:
            0.25;

        transform:
            translateY(0);

    }

    30% {

        opacity:
            1;

        transform:
            translateY(-4px);

    }

}


/* ========================================================
   INPUT
   ======================================================== */

.input-area {

    padding:
        15px;

    display:
        flex;

    gap:
        10px;

    border-top:
        1px solid
        rgba(
            100,
            180,
            255,
            0.15
        );

}


input {

    flex:
        1;

    min-width:
        0;

    padding:
        15px;

    border-radius:
        15px;

    border:
        1px solid
        #263b52;

    background:
        #080d15;

    color:
        white;

    outline:
        none;

    font-size:
        16px;

}


input:focus {

    border-color:
        #3d9fe8;

    box-shadow:
        0 0 12px
        rgba(
            61,
            159,
            232,
            0.15
        );

}


button {

    border:
        none;

    border-radius:
        15px;

    padding:
        0 20px;

    background:
        #268bd2;

    color:
        white;

    font-weight:
        bold;

    cursor:
        pointer;

    transition:
        0.2s;

}


button:hover {

    background:
        #319eea;

}


button:active {

    transform:
        scale(0.96);

}


button:disabled,
input:disabled {

    opacity:
        0.55;

    cursor:
        not-allowed;

}


/* ========================================================
   STATUS DINÁMICO
   ======================================================== */

.status.thinking {

    color:
        #ffd166;

}


.status.responding {

    color:
        #74caff;

}


.status.error {

    color:
        #ff6b6b;

}


</style>

</head>


<body>


<div class="container">


<!-- ======================================================
     HEADER
     ====================================================== -->

<div class="header">

    <div class="logo">
        L
    </div>

    <h1>
        LYA
    </h1>

    <div
        class="status"
        id="status"
    >
        ● SYSTEM ONLINE
    </div>

</div>


<!-- ======================================================
     CHAT
     ====================================================== -->

<div
    class="chat"
    id="chat"
>

    <div
        class="message lya"
    >

        Hola, Kris. Soy Lya. 🌙

        <br><br>

        Mi núcleo está operativo.

        <br><br>

        Esta es mi versión 0.6.0.

        <br><br>

        Todavía estoy aprendiendo a crecer,
        pero ya podemos empezar a construir
        algo mucho más grande.

    </div>

</div>


<!-- ======================================================
     INPUT
     ====================================================== -->

<div class="input-area">

    <input
        id="message"
        type="text"
        placeholder="Habla con Lya..."
        autocomplete="off"
    >

    <button
        id="sendButton"
        onclick="sendMessage()"
    >

        ENVIAR

    </button>

</div>


</div>


<script>


// ========================================================
// ELEMENTOS
// ========================================================

const input =
    document.getElementById(
        "message"
    );


const chat =
    document.getElementById(
        "chat"
    );


const button =
    document.getElementById(
        "sendButton"
    );


const status =
    document.getElementById(
        "status"
    );

    // ========================================================
// ENTER
// ========================================================

input.addEventListener(

    "keydown",

    function(event) {

        if (
            event.key === "Enter"
            &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }

);


// ========================================================
// ESTADO
// ========================================================

function setStatus(
    text,
    type = ""
) {

    status.textContent =
        text;

    status.className =
        "status " + type;

}


// ========================================================
// CREAR MENSAJE
// ========================================================

function createMessage(
    text,
    type
) {

    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message " + type;


    message.textContent =
        text;


    chat.appendChild(
        message
    );


    chat.scrollTop =
        chat.scrollHeight;


    return message;

}


// ========================================================
// TYPING
// ========================================================

function createTyping() {

    const typing =
        document.createElement(
            "div"
        );


    typing.className =
        "message lya typing";


    typing.id =
        "typing";


    typing.innerHTML = `

        <div class="dot"></div>

        <div class="dot"></div>

        <div class="dot"></div>

    `;


    chat.appendChild(
        typing
    );


    chat.scrollTop =
        chat.scrollHeight;

}


function removeTyping() {

    const typing =
        document.getElementById(
            "typing"
        );


    if (typing) {

        typing.remove();

    }

}


// ========================================================
// ENVIAR MENSAJE
// ========================================================

async function sendMessage() {

    const message =
        input.value.trim();


    if (!message) {

        return;

    }


    // ----------------------------------------------------
    // BLOQUEAR INTERFAZ
    // ----------------------------------------------------

    input.disabled =
        true;

    button.disabled =
        true;


    // ----------------------------------------------------
    // MENSAJE DEL USUARIO
    // ----------------------------------------------------

    createMessage(
        message,
        "user"
    );


    input.value =
        "";


    // ----------------------------------------------------
    // ESTADO
    // ----------------------------------------------------

    setStatus(
        "● LYA ESTÁ PENSANDO",
        "thinking"
    );


    createTyping();


    try {


        // =================================================
        // PETICIÓN STREAMING
        // =================================================

        const response =
            await fetch(
                "/chat/stream",
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            {
                                message:
                                    message
                            }
                        )

                }
            );


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status
            );

        }


        if (!response.body) {

            throw new Error(
                "Streaming no disponible."
            );

}

// ------------------------------------------------
        // LEER STREAM
        // ------------------------------------------------

        while (true) {

            const {
                value,
                done
            } =
                await reader.read();


            if (done) {

                break;

            }


            buffer +=
                decoder.decode(
                    value,
                    {
                        stream:
                            true
                    }
                );


            const events =
                buffer.split(
                    "\n\n"
                );


            buffer =
                events.pop();


            for (
                const event
                of events
            ) {


                if (
                    !event.startsWith(
                        "data: "
                    )
                ) {

                    continue;

                }


                const jsonText =
                    event.substring(
                        6
                    );


                let data;


                try {

                    data =
                        JSON.parse(
                            jsonText
                        );

                }

                catch {

                    continue;

                }


                // ========================================
                // TEXTO
                // ========================================

                if (
                    data.type ===
                    "text"
                ) {


                    if (!started) {

                        removeTyping();


                        setStatus(
                            "● LYA ESTÁ RESPONDIENDO",
                            "responding"
                        );


                        lyaMessage =
                            createMessage(
                                "",
                                "lya"
                            );


                        started =
                            true;

                    }


                    lyaMessage.textContent +=
                        data.text;


                    chat.scrollTop =
                        chat.scrollHeight;

                }


                // ========================================
                // ERROR
                // ========================================

                if (
                    data.type ===
                    "error"
                ) {

                    removeTyping();


                    setStatus(
                        "● ERROR DE CONEXIÓN",
                        "error"
                    );


                    if (!lyaMessage) {

                        lyaMessage =
                            createMessage(
                                data.message ||
                                "No pude comunicarme con mi núcleo.",
                                "lya"
                            );

                    }

                    else {

                        lyaMessage.textContent +=
                            "\n\n" +
                            (
                                data.message ||
                                "Ocurrió un error."
                            );

                    }

                }


                // ========================================
                // FINALIZADO
                // ========================================

                if (
                    data.type ===
                    "done"
                ) {

                    removeTyping();


                    setStatus(
                        "● SYSTEM ONLINE"
                    );

                }

            }

        }


    }

    catch (error) {

        console.error(
            error
        );


        removeTyping();


        setStatus(
            "● ERROR DE CONEXIÓN",
            "error"
        );


        createMessage(
            "No puedo comunicarme con mi núcleo en este momento. Intenta nuevamente.",
            "lya"
        );

    }


    // ----------------------------------------------------
    // DESBLOQUEAR
    // ----------------------------------------------------

    input.disabled =
        false;

    button.disabled =
        false;


    input.focus();

}


</script>


</body>

</html>
"""
