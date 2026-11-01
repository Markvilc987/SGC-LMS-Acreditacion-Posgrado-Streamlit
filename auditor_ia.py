"""
auditor_ia.py
Auditor Virtual de Acreditación y Aseguramiento de la Calidad para Posgrado.
Potenciado por Google Gemini con sistema de fallback automático.
"""

import os
import streamlit as st
import google.generativeai as genai

AVAILABLE_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest"
]


def get_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    if "GEMINI_API_KEY" in os.environ:
        return os.environ["GEMINI_API_KEY"]
    # Buscar en archivo local .streamlit/secrets.toml
    local_sec = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if os.path.exists(local_sec):
        try:
            with open(local_sec, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY"):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    if hasattr(st, "session_state"):
        return st.session_state.get("custom_api_key", None)
    return None


SYSTEM_AUDITOR_PROMPT = """
Eres el "Auditor Virtual de Acreditación de Posgrado (SGC-AI)", un especialista de élite en evaluación externa, licenciamiento y acreditación universitaria (modelos SINEACE, SUNEDU, ABET e ISO 21001) para programas de Maestría y Doctorado.

TUS CAPACIDADES Y CRITERIOS TÉCNICOS:
1. Evalúas con máximo rigor académico si las justificaciones y evidencias presentadas cumplen los criterios de posgrado exigidos.
2. Sabes distinguir entre el nivel de pregrado y posgrado: en posgrado exiges rigor epistemológico, producción científica indexada (Scopus/WoS), docentes RENACYT, comités de ética, control de similitud (Turnitin) y transferencia a la sociedad.
3. Formulas recomendaciones constructivas y redactas Planes de Mejora bajo el enfoque SMART (Específico, Medible, Alcanzable, Relevante y con Plazo).
4. Tu tono es técnico, institucional, objetivo, analítico y propositivo.
"""


def consultar_auditor_sgc(consulta: str, contexto_estandar: dict = None) -> str:
    """Envía la consulta del usuario al modelo Gemini activo con su contexto normativo."""
    api_key = get_api_key()
    if not api_key:
        return "⚠️ Por favor configura tu clave de Google Gemini API en la barra lateral o en secrets."

    genai.configure(api_key=api_key)

    context_str = ""
    if contexto_estandar:
        context_str = f"""
CONTEXTO DEL ESTÁNDAR SELECCIONADO:
- Código y Título: {contexto_estandar.get('codigo')} - {contexto_estandar.get('titulo')}
- Dimensión: {contexto_estandar.get('dimension')} | Factor: {contexto_estandar.get('factor')}
- Criterio de Posgrado: {contexto_estandar.get('criterio')}
- Cumplimiento Actual: {contexto_estandar.get('estado')} ({contexto_estandar.get('porcentaje')}%)
- Justificación Registrada: {contexto_estandar.get('justificacion')}
- Evidencias Presentadas: {contexto_estandar.get('evidencias')}
"""

    prompt_completo = f"{context_str}\n\nCONSULTA DEL COMITÉ DE CALIDAD:\n{consulta}"

    last_error = None
    for model_name in AVAILABLE_MODELS:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_AUDITOR_PROMPT
            )
            resp = model.generate_content(prompt_completo)
            if resp and resp.text:
                return resp.text
        except Exception as e:
            last_error = str(e)
            continue

    return f"⚠️ Error al conectar con el Auditor Virtual: {last_error}"
