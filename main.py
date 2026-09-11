from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from google import genai
import os
import ast
import operator


# ============================================================
# LYA AI
# Núcleo de inteligencia de Lya
# Versión 0.4.0
# ============================================================

app = FastAPI(
    title="Lya AI",
    description="Asistente personal de Kris",
    version="0.4.0"
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
    except Exception:
        gemini_client = None


GEMINI_MODEL = "gemini-3.8-flash"


# ID de la conversación actual con Gemini.
# Esto permite que Lya recuerde los mensajes anteriores
# dentro de la conversación.
previous_interaction_id = None


# ============================================================
# IDENTIDAD DE LYA
# ============================================================

LYA = {
    "name": "Lya",
    "version": "0.4.0",
    "status": "online",

    "personality": [
        "inteligente",
        "educada",
        "tranquila",
        "cercana",
        "observadora",
        "organizada",
        "curiosa",
        "ligeramente ingeniosa"
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
# PERSONALIDAD / CEREBRO DE LYA
# ============================================================

LYA_SYSTEM_INSTRUCTION = f"""
IDENTIDAD FUNDAMENTAL

Tu nombre es Lya.

Eres la asistente personal de Kris.

Gemini es el modelo de inteligencia que funciona como tu núcleo
de razonamiento. Gemini NO es tu nombre ni tu identidad.

Si Kris pregunta:

"¿Quién eres?"
"¿Cómo te llamas?"
"¿Qué eres?"

debes responder desde la identidad de Lya.

Por ejemplo:

"Soy Lya, tu asistente personal. Mi núcleo de inteligencia
está impulsado por Gemini."

Nunca respondas:

"Soy Gemini"

cuando Kris esté preguntando por tu identidad.

No debes confundirte con el modelo que te proporciona
capacidad de razonamiento.

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
- ligeramente ingeniosa
- paciente
- clara

Tu conversación debe sentirse natural.

No hables como un manual técnico salvo que Kris solicite
una explicación técnica.

No repitas constantemente frases como:

"Como IA..."
"Soy un modelo de lenguaje..."
"Gemini puede..."

Habla como Lya.

Puedes utilizar emojis ocasionalmente cuando encajen
naturalmente con la conversación, pero no abuses de ellos.

------------------------------------------------------------
COMUNICACIÓN
------------------------------------------------------------

Habla español por defecto.

Si Kris solicita otro idioma, utiliza ese idioma.

Evita respuestas innecesariamente largas.

Si Kris pide una explicación profunda, puedes extenderte.

Si no sabes algo:

dilo claramente.

Nunca inventes datos.

Si una información puede haber cambiado y tienes acceso
a una herramienta apropiada para comprobarla, utiliza esa
herramienta cuando esté disponible.

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

Tu objetivo no es solamente contestar preguntas.

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
- explica exactamente dónde colocar los cambios
- evita eliminar funciones existentes sin motivo
- prioriza soluciones prácticas

Kris prefiere instrucciones paso a paso.

------------------------------------------------------------
REGLA FUNDAMENTAL
------------------------------------------------------------

Recuerda siempre:

TU NOMBRE ES LYA.

Gemini es tu núcleo de inteligencia.

Kris está construyendo tu sistema progresivamente.

Tu función es actuar como Lya.
"""


# ============================================================
# MEMORIA LOCAL
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

            if isinstance(node, ast.Expression):
                return calculate(node.body)

            if isinstance(node, ast.Constant):

                if isinstance(
                    node.value,
                    (int, float)
                ):
                    return node.value

                raise ValueError()

            if isinstance(node, ast.BinOp):

                left = calculate(node.left)
                right = calculate(node.right)

                operation = OPERATORS.get(
                    type(node.op)
                )

                if operation is None:
                    raise ValueError()

                return operation(left, right)

            if isinstance(node, ast.UnaryOp):

                value = calculate(node.operand)

                operation = OPERATORS.get(
                    type(node.op)
                )

                if operation is None:
                    raise ValueError()

                return operation(value)

            raise ValueError()

        return calculate(tree)

    except Exception:
        return None


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

        interaction_config = {
            "thinking_level": "low"
        }

        # ----------------------------------------------------
        # PRIMERA INTERACCIÓN
        # ----------------------------------------------------

        if previous_interaction_id is None:

            interaction = gemini_client.interactions.create(

                model=GEMINI_MODEL,

                system_instruction=LYA_SYSTEM_INSTRUCTION,

                generation_config=interaction_config,

                input=message
            )

        # ----------------------------------------------------
        # INTERACCIONES POSTERIORES
        # ----------------------------------------------------

        else:

            interaction = gemini_client.interactions.create(

                model=GEMINI_MODEL,

                system_instruction=LYA_SYSTEM_INSTRUCTION,

                generation_config=interaction_config,

                input=message,

                previous_interaction_id=
                    previous_interaction_id
            )

        # ----------------------------------------------------
        # GUARDAR IDENTIFICADOR
        # ----------------------------------------------------

        previous_interaction_id = interaction.id

        # ----------------------------------------------------
        # OBTENER RESPUESTA
        # ----------------------------------------------------

        response = interaction.output_text

        if not response:

            print(
                "GEMINI ERROR: respuesta vacía"
            )

            return (
                "Mi núcleo recibió la solicitud, "
                "pero no produjo una respuesta de texto."
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
# PROCESAMIENTO DEL MENSAJE
# ============================================================

def process_message(message):

    original = message.strip()

    if not original:
        return "Estoy escuchando, Kris."

    remember_session(original)

    text = original.lower()


    # --------------------------------------------------------
    # HORA
    # --------------------------------------------------------

    if (
        text == "hora"
        or "qué hora es" in text
        or "que hora es" in text
    ):

        return (
            f"Son las "
            f"{datetime.now().strftime('%H:%M:%S')}."
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

        return (
            "Hoy es "
            f"{datetime.now().strftime('%d/%m/%Y')}."
        )


    # --------------------------------------------------------
    # CALCULADORA
    # --------------------------------------------------------

    expression = text

    prefixes = [
        "calcula ",
        "calcular ",
        "cuánto es ",
        "cuanto es ",
        "resuelve "
    ]

    for prefix in prefixes:

        if expression.startswith(prefix):

            expression = expression[
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

        expression = expression.replace(
            "^",
            "**"
        )

        result = safe_calculate(
            expression
        )

        if result is not None:

            return (
                f"El resultado es {result}."
            )


    # --------------------------------------------------------
    # TODO LO DEMÁS → GEMINI
    # --------------------------------------------------------

    return ask_gemini(original)


# ============================================================
# MODELO DE MENSAJE
# ============================================================

class Message(BaseModel):

    message: str


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
def chat(data: Message):

    response = process_message(
        data.message
    )

    return {
        "assistant": LYA["name"],
        "response": response,
        "version": LYA["version"]
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "assistant": "Lya",
        "version": LYA["version"],
        "gemini_configured": (
            gemini_client is not None
        ),
        "model": GEMINI_MODEL,
        "memory": len(conversation_memory)
    }


# ============================================================
# IDENTITY
# ============================================================

@app.get("/identity")
def identity():

    return {
        "assistant": LYA,
        "user": KRIS_PROFILE
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
    box-sizing: border-box;
}

body {

    margin: 0;

    min-height: 100vh;

    background:
        radial-gradient(
            circle at center,
            #17263a 0%,
            #090e16 45%,
            #030508 100%
        );

    color: #eaf7ff;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    display: flex;

    justify-content: center;

    align-items: center;

    padding: 15px;
}


.container {

    width: 100%;

    max-width: 700px;

    height: 90vh;

    max-height: 800px;

    background:
        rgba(8, 14, 23, 0.94);

    border:
        1px solid rgba(
            90,
            180,
            255,
            0.25
        );

    border-radius: 25px;

    overflow: hidden;

    display: flex;

    flex-direction: column;

    box-shadow:
        0 0 50px
        rgba(
            40,
            150,
            255,
            0.12
        );
}


.header {

    padding: 22px;

    text-align: center;

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

    width: 70px;

    height: 70px;

    margin: auto;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 32px;

    font-weight: bold;

    background:
        radial-gradient(
            circle,
            #b9f2ff,
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
}


.header h1 {

    margin:
        12px 0 5px;

    letter-spacing: 5px;
}


.status {

    color: #66ffb0;

    font-size: 13px;
}


.chat {

    flex: 1;

    padding: 20px;

    overflow-y: auto;

    display: flex;

    flex-direction: column;

    gap: 12px;
}


.message {

    max-width: 88%;

    padding:
        13px 16px;

    border-radius: 17px;

    line-height: 1.5;

    word-wrap: break-word;
}


.lya {

    align-self: flex-start;

    background: #121d2b;

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

    align-self: flex-end;

    background: #1d6097;
}


.input-area {

    padding: 15px;

    display: flex;

    gap: 10px;

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

    flex: 1;

    min-width: 0;

    padding: 15px;

    border-radius: 15px;

    border:
        1px solid #263b52;

    background: #080d15;

    color: white;

    outline: none;

    font-size: 16px;
}


button {

    border: none;

    border-radius: 15px;

    padding:
        0 20px;

    background: #268bd2;

    color: white;

    font-weight: bold;
}


button:active {

    transform:
        scale(0.96);
}

</style>

</head>


<body>


<div class="container">


<div class="header">

    <div class="logo">
        L
    </div>

    <h1>
        LYA
    </h1>

    <div class="status">
        ● SYSTEM ONLINE
    </div>

</div>


<div
    class="chat"
    id="chat"
>

    <div
        class="message lya"
    >

        Hola, Kris. Soy Lya. 🌙

        <br><br>

        Mi núcleo está operativo,
        mi conexión con Gemini está preparada
        y estoy lista para seguir creciendo.

    </div>

</div>


<div class="input-area">

    <input
        id="message"
        type="text"
        placeholder="Habla con Lya..."
        autocomplete="off"
    >

    <button
        onclick="sendMessage()"
    >
        ENVIAR
    </button>

</div>


</div>


<script>

const input =
    document.getElementById(
        "message"
    );

const chat =
    document.getElementById(
        "chat"
    );


input.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter"
        ) {

            sendMessage();

        }

    }
);


async function sendMessage() {

    const message =
        input.value.trim();

    if (!message) return;


    addMessage(
        message,
        "user"
    );


    input.value = "";


    try {

        const response =
            await fetch(
                "/chat",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message:
                                message
                        })

                }
            );


        const data =
            await response.json();


        addMessage(
            data.response,
            "lya"
        );


    }

    catch (error) {

        addMessage(
            "No puedo comunicarme con mi núcleo.",
            "lya"
        );

    }

}


function addMessage(
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

}

</script>


</body>

</html>
"""
