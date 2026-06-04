from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from agent import load_vectorstore, build_chain

app = FastAPI()
vectorstore = load_vectorstore()
chain = build_chain(vectorstore)

class Message(BaseModel):
    message: str
    session_id: str = "default"

@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>30X — Agente de Onboarding</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #f5f5f5; display: flex; flex-direction: column; height: 100vh; }
        header { background: #000; color: #fff; padding: 16px 24px; font-size: 16px; font-weight: 600; }
        header span { color: #aaa; font-weight: 400; font-size: 14px; margin-left: 12px; }
        #chat { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
        .msg { max-width: 75%; padding: 12px 16px; border-radius: 12px; font-size: 14px; line-height: 1.6; }
        .user { background: #000; color: #fff; align-self: flex-end; border-radius: 12px 12px 2px 12px; }
        .bot { background: #fff; color: #111; align-self: flex-start; border-radius: 12px 12px 12px 2px; border: 1px solid #e0e0e0; }
        .typing { color: #999; font-size: 13px; align-self: flex-start; padding: 8px 0; }
        #form { display: flex; gap: 10px; padding: 16px 24px; background: #fff; border-top: 1px solid #e0e0e0; }
        #input { flex: 1; padding: 12px 16px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
        #input:focus { border-color: #000; }
        button { background: #000; color: #fff; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; }
        button:hover { background: #333; }
    </style>
</head>
<body>
    <header>30X Onboarding Agent <span>Pregúntame lo que necesites saber sobre la organización</span></header>
    <div id="chat">
        <div class="msg bot">¡Hola! Soy el agente de onboarding de 30X. Estoy aquí para ayudarte a conocer la organización, el equipo, las herramientas y cómo funciona todo. ¿Qué quieres saber?</div>
    </div>
    <div id="form">
        <input id="input" type="text" placeholder="Escribe tu pregunta..." autofocus />
        <button onclick="send()">Enviar</button>
    </div>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');

        input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });

        async function send() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';

            chat.innerHTML += `<div class="msg user">${text}</div>`;
            chat.innerHTML += `<div class="typing" id="typing">Escribiendo...</div>`;
            chat.scrollTop = chat.scrollHeight;

            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const data = await res.json();

            document.getElementById('typing')?.remove();
            chat.innerHTML += `<div class="msg bot">${data.response}</div>`;
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.post("/chat")
def chat(msg: Message):
    result = chain.invoke(
        {"question": msg.message},
        config={"configurable": {"session_id": msg.session_id}}
    )
    return {"response": result}