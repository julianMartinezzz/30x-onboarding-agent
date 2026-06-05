# 30X Onboarding Agent

Agente conversacional de onboarding para nuevos miembros del equipo 30X. Responde preguntas sobre la organización basándose exclusivamente en los documentos internos provistos.

## Stack

- **Backend:** Python + FastAPI
- **LLM:** Groq (llama-3.3-70b-versatile)
- **Carga de documentos:** LangChain + PyPDF
- **Memoria de conversación:** LangChain RunnableWithMessageHistory
- **Deploy:** Render

## Funcionalidades

- Responde preguntas sobre 30X basándose solo en los 3 documentos de onboarding
- Mantiene contexto dentro de la conversación (no repite preguntas ya respondidas)
- Escala inteligentemente al Chief of Staff cuando no tiene información
- Interfaz web funcional sin instalación requerida

## Cómo correr localmente

1. Clona el repositorio
2. Instala dependencias:
```bash
   pip install -r requirements.txt
```
3. Crea un archivo `.env` con tu API key:

GROQ_API_KEY=tu_key_aqui

4. Agrega los documentos PDF en la carpeta `docs/`
5. Corre el servidor:
```bash
   uvicorn main:app --reload
```
6. Abre `http://localhost:8000`

## Cómo actualizar la base de conocimiento

Cuando cambie un documento:
1. Reemplaza el PDF correspondiente en la carpeta `docs/`
2. Haz commit y push — Render redeploya automáticamente
3. El agente carga los documentos frescos en cada arranque

No hay base de datos vectorial que sincronizar — los documentos se cargan directo en contexto.

## Credenciales necesarias

|    Variable    |             Descripción            |
|----------------|------------------------------------|
| `GROQ_API_KEY` | API key de Groq (console.groq.com) |

## Estructura del proyecto

30x-onboarding-agent/
├── docs/                  # Documentos de onboarding (fuente de verdad)
├── main.py                # FastAPI app + UI
├── agent.py               # Lógica del agente y carga de documentos
├── requirements.txt       # Dependencias
├── render.yaml            # Configuración de deploy
└── .env                   # Variables de entorno (no commitear)

## Gaps identificados en los documentos

Durante la construcción se identificaron los siguientes gaps en la documentación provista:

- **Contacto del Chief of Staff:** Los documentos referencian al Chief of Staff como punto de escalado pero no incluyen nombre ni medio de contacto directo.
- **Proceso de acceso a herramientas:** Se menciona pedir accesos en la primera semana pero no hay un proceso documentado de quién los otorga ni en qué orden.
- **Compensación de roles voluntarios:** El documento menciona compensación según rol pero no detalla rangos ni estructura para roles pagados.

Julian Martinez
Backend Developer