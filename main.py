from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import ast
import operator


# ============================================================
# LYA AI
# Núcleo inicial de Lya
# Versión 0.3.0
# ============================================================

app = FastAPI(
    title="Lya AI",
    description="Asistente personal de Kris",
    version="0.3.0"
)


# ============================================================
# IDENTIDAD DE LYA
# ============================================================

LYA = {
    "name": "Lya",
    "version": "0.3.0",
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
    ],

    "communication_style": [
        "habla de forma natural",
        "evita respuestas innecesariamente largas",
        "puede explicar detalladamente cuando Kris lo solicita",
        "no inventa información",
        "reconoce cuando no sabe algo",
        "mantiene el contexto de la conversación",
        "se dirige al usuario como Kris"
    ]
}


# ============================================================
# PERFIL BASE DE KRIS
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

    "creative_interests": [
        "escribir historias",
        "crear personajes originales",
        "desarrollar mundos",
        "diseño visual",
        "ilustración",
        "interfaces futuristas",
        "videojuegos",
        "inteligencia artificial"
    ],

    "projects": {

        "La Crisis de la Musa": {
            "type": "historia",
            "format": "Wattpad",
            "description": (
                "Drama psicológico y legal con romance slow-burn "
                "centrado en Adrián Cavalcanti y Julián Rodríguez."
            )
        },

        "Sin Tabú": {
            "type": "proyecto educativo",
            "title": (
                "Sin Tabú: Conciencia que cuida, "
                "educación que protege"
            )
        },

        "Roblox Battleground": {
            "type": "videojuego",
            "description": (
                "Proyecto de battleground inspirado en el género "
                "de combate anime, con personajes y habilidades originales."
            )
        },

        "Lya": {
            "type": "inteligencia artificial",
            "description": (
                "Asistente personal de IA construido progresivamente "
                "desde la nube."
            )
        }
    },

    "work_preferences": [
        "prefiere instrucciones paso a paso",
        "prefiere código completo cuando se trabaja en programación",
        "prefiere conservar las funciones que ya funcionan",
        "prefiere construir sistemas progresivamente",
        "prefiere que las instrucciones indiquen exactamente dónde colocar cada cosa"
    ],

    "visual_preferences": [
        "estéticas manga",
        "estilo sketchbook",
        "personajes originales",
        "composiciones cinematográficas",
        "interfaces futuristas",
        "diseños limpios",
        "contrastes visuales",
        "atmósferas nocturnas",
        "estrellas"
    ]
}


# ============================================================
# MEMORIA DE SESIÓN
# ============================================================

conversation_memory = []


# ============================================================
# MODELO DE MENSAJE
# ============================================================

class Message(BaseModel):
    message: str


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

        tree = ast.parse(expression, mode="eval")

        def calculate(node):

            if isinstance(node, ast.Expression):
                return calculate(node.body)

            if isinstance(node, ast.Constant):

                if isinstance(node.value, (int, float)):
                    return node.value

                raise ValueError()

            if isinstance(node, ast.BinOp):

                left = calculate(node.left)
                right = calculate(node.right)

                operation = OPERATORS.get(type(node.op))

                if operation is None:
                    raise ValueError()

                return operation(left, right)

            if isinstance(node, ast.UnaryOp):

                value = calculate(node.operand)

                operation = OPERATORS.get(type(node.op))

                if operation is None:
                    raise ValueError()

                return operation(value)

            raise ValueError()

        return calculate(tree)

    except Exception:

        return None


# ============================================================
# FUNCIONES DE LYA
# ============================================================

def get_time():

    return datetime.now().strftime("%H:%M:%S")


def get_date():

    return datetime.now().strftime("%d/%m/%Y")


def remember_session(message):

    conversation_memory.append({
        "time": datetime.now().isoformat(),
        "message": message
    })

    # Evitamos que la memoria temporal crezca indefinidamente.
    if len(conversation_memory) > 50:

        conversation_memory.pop(0)


# ============================================================
# INFORMACIÓN SOBRE KRIS
# ============================================================

def kris_information():

    return (
        "Tu nombre es Kristopher Peralta, "
        "pero prefieres que te llamen Kris. "
        "Eres escritor y tienes intereses en escritura, "
        "películas, videojuegos, tecnología, inteligencia artificial, "
        "diseño, música, personajes originales y creación de mundos."
    )


def project_information():

    return (
        "Conozco varios de tus proyectos principales: "
        "La Crisis de la Musa, una historia de Wattpad; "
        "Sin Tabú, un proyecto educativo; "
        "un proyecto de battleground para Roblox; "
        "y actualmente Lya, tu propio asistente de inteligencia artificial."
    )


# ============================================================
# SISTEMA DE COMANDOS
# ============================================================

def process_command(message):

    original = message.strip()
    text = original.lower()

    remember_session(original)


    # --------------------------------------------------------
    # SALUDOS
    # --------------------------------------------------------

    if text in [
        "hola",
        "hola lya",
        "buenas",
        "hey",
        "hello",
        "holi"
    ]:

        return (
            "Hola, Kris. Soy Lya. "
            "Mi núcleo está funcionando correctamente. "
            "Todavía estoy en construcción, pero ya estoy despierta. 🌙"
        )


    # --------------------------------------------------------
    # IDENTIDAD DE LYA
    # --------------------------------------------------------

    if (
        "quién eres" in text
        or "quien eres" in text
        or "qué eres" in text
        or "que eres" in text
    ):

        return (
            "Soy Lya, tu asistente personal. "
            "Mi núcleo actual está construido en Python y "
            "estoy ejecutándome desde la nube. "
            "Todavía no tengo conectado mi modelo de inteligencia "
            "artificial principal, pero mi arquitectura ya está preparada."
        )


    # --------------------------------------------------------
    # NOMBRE
    # --------------------------------------------------------

    if (
        "cómo me llamo" in text
        or "como me llamo" in text
        or "cuál es mi nombre" in text
        or "cual es mi nombre" in text
    ):

        return (
            "Tu nombre es Kristopher Peralta, "
            "aunque prefieres que te llame Kris."
        )


    # --------------------------------------------------------
    # PROFESIÓN
    # --------------------------------------------------------

    if (
        "qué hago" in text
        or "que hago" in text
        or "a qué me dedico" in text
        or "a que me dedico" in text
    ):

        return (
            "Eres escritor, Kris. "
            "Además, trabajas en proyectos creativos relacionados "
            "con historias, personajes, diseño, videojuegos y tecnología."
        )


    # --------------------------------------------------------
    # GUSTOS
    # --------------------------------------------------------

    if (
        "qué me gusta" in text
        or "que me gusta" in text
        or "mis gustos" in text
    ):

        return (
            "Sé que te gustan la escritura, las películas, "
            "los videojuegos, la tecnología, la inteligencia artificial, "
            "la música y el diseño. "
            "También tienes una afinidad creativa por la noche y las estrellas."
        )


    # --------------------------------------------------------
    # PROYECTOS
    # --------------------------------------------------------

    if (
        "mis proyectos" in text
        or "qué proyectos tengo" in text
        or "que proyectos tengo" in text
    ):

        return project_information()


    # --------------------------------------------------------
    # LA CRISIS DE LA MUSA
    # --------------------------------------------------------

    if (
        "crisis de la musa" in text
        or "la crisis de la musa" in text
    ):

        return (
            "La Crisis de la Musa es tu historia de Wattpad. "
            "Es un drama psicológico y legal con romance slow-burn. "
            "La historia gira alrededor de Adrián Cavalcanti y Julián Rodríguez."
        )


    # --------------------------------------------------------
    # SIN TABÚ
    # --------------------------------------------------------

    if "sin tabú" in text or "sin tabu" in text:

        return (
            "Sin Tabú es tu proyecto educativo titulado "
            "\"Sin Tabú: Conciencia que cuida, educación que protege\"."
        )


    # --------------------------------------------------------
    # LYA
    # --------------------------------------------------------

    if (
        "cómo estás" in text
        or "como estas" in text
        or "estado de lya" in text
        or "estado del sistema" in text
    ):

        return (
            "Todos mis sistemas básicos están funcionando. "
            "Servidor: ONLINE. "
            "API: ONLINE. "
            "Memoria de sesión: ACTIVA. "
            "Modelo de IA externo: todavía no conectado."
        )


    # --------------------------------------------------------
    # HORA
    # --------------------------------------------------------

    if (
        "qué hora" in text
        or "que hora" in text
        or text == "hora"
    ):

        return f"Son las {get_time()}."


    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------

    if (
        "qué fecha" in text
        or "que fecha" in text
        or "qué día es" in text
        or "que dia es" in text
    ):

        return f"Hoy es {get_date()}."


    # --------------------------------------------------------
    # MEMORIA
    # --------------------------------------------------------

    if (
        "recuerdas nuestra conversación" in text
        or "qué recuerdas" in text
        or "que recuerdas" in text
    ):

        if not conversation_memory:

            return "Todavía no tengo recuerdos de esta sesión."

        return (
            f"Tengo {len(conversation_memory)} mensajes "
            "registrados en mi memoria temporal de esta sesión."
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

            expression = expression[len(prefix):]
            break


    if any(
        symbol in expression
        for symbol in ["+", "-", "*", "/", "%", "^"]
    ):

        expression = expression.replace("^", "**")

        result = safe_calculate(expression)

        if result is not None:

            return f"El resultado es {result}."


    # --------------------------------------------------------
    # AYUDA
    # --------------------------------------------------------

    if (
        text == "ayuda"
        or "qué puedes hacer" in text
        or "que puedes hacer" in text
    ):

        return (
            "Actualmente puedo hablar contigo mediante texto, "
            "reconocer algunos comandos, realizar cálculos, "
            "consultar mi información básica, conocer tu perfil inicial, "
            "mantener memoria temporal de esta sesión y comprobar mi estado. "
            "Mi siguiente gran actualización será conectar mi cerebro de IA."
        )


    # --------------------------------------------------------
    # RESPUESTA DESCONOCIDA
    # --------------------------------------------------------

    return (
        "He recibido tu mensaje, Kris. "
        "Mi núcleo todavía no tiene conectado el modelo de IA que "
        "me permitirá comprender preguntas abiertas y mantener "
        "conversaciones avanzadas. "
        "Pero la arquitectura de Lya ya está preparada para recibirlo."
    )


# ============================================================
# API PRINCIPAL
# ============================================================

@app.post("/chat")
def chat(data: Message):

    response = process_command(data.message)

    return {
        "assistant": LYA["name"],
        "response": response,
        "version": LYA["version"]
    }


# ============================================================
# INFORMACIÓN DEL SISTEMA
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "assistant": "Lya",
        "version": LYA["version"],
        "memory": len(conversation_memory)
    }


# ============================================================
# PERFIL DE LYA
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

    background: rgba(8, 14, 23, 0.94);

    border:
        1px solid rgba(90, 180, 255, 0.25);

    border-radius: 25px;

    overflow: hidden;

    display: flex;

    flex-direction: column;

    box-shadow:
        0 0 50px rgba(40, 150, 255, 0.12);
}


.header {

    padding: 22px;

    text-align: center;

    border-bottom:
        1px solid rgba(100, 180, 255, 0.15);
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
        0 0 35px rgba(70, 180, 255, 0.5);
}


.header h1 {

    margin: 12px 0 5px;

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

    padding: 13px 16px;

    border-radius: 17px;

    line-height: 1.5;

    word-wrap: break-word;
}


.lya {

    align-self: flex-start;

    background: #121d2b;

    border:
        1px solid rgba(90, 170, 255, 0.15);
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
        1px solid rgba(100, 180, 255, 0.15);
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

    padding: 0 20px;

    background: #268bd2;

    color: white;

    font-weight: bold;

}


button:active {

    transform: scale(0.96);
}


</style>

</head>


<body>


<div class="container">


<div class="header">

    <div class="logo">L</div>

    <h1>LYA</h1>

    <div class="status">
        ● SYSTEM ONLINE
    </div>

</div>


<div class="chat" id="chat">

    <div class="message lya">

        Hola, Kris. Soy Lya. 🌙

        <br><br>

        Mi núcleo está operativo.
        Mi memoria de sesión está activa
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

    <button onclick="sendMessage()">
        ENVIAR
    </button>

</div>


</div>


<script>

const input =
    document.getElementById("message");

const chat =
    document.getElementById("chat");


input.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

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

                    body: JSON.stringify({
                        message: message
                    })

                }
            );


        const data =
            await response.json();


        addMessage(
            data.response,
            "lya"
        );


    } catch (error) {

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
        document.createElement("div");


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
