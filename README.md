# 🏛️ SGC-Posgrado: Sistema de Gestión de la Calidad y Acreditación LMS

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Modelo SINEACE / SUNEDU](https://img.shields.io/badge/Modelo-4%20Dim%20%7C%2012%20Fac%20%7C%2034%20Est-1E3A8A.svg)](https://www.sineace.gob.pe)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-3.5%20Flash-4285F4.svg?logo=google&logoColor=white)](https://aistudio.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Plataforma integral de **Gestión de la Calidad y Articulación LMS para Programas de Posgrado (Maestrías y Doctorados)**, basada estrictamente en el modelo oficial de acreditación universitaria de **4 Dimensiones, 12 Factores y 34 Estándares**.

---

## 🏛️ Estructura del Modelo Oficial de Calidad

* **Dimensión 1: Gestión Estratégica (Factores 1 a 3 | Estándares 1 a 8):**
  * *Factor 1:* Planificación del programa de estudios (Est. 1–4)
  * *Factor 2:* Gestión del perfil de egreso (Est. 5–6)
  * *Factor 3:* Aseguramiento de la calidad y planes de mejora (Est. 7–8)
* **Dimensión 2: Formación Integral (Factores 4 a 8 | Estándares 9 a 26):**
  * *Factor 4:* Proceso enseñanza-aprendizaje y movilidad (Est. 9–13)
  * *Factor 5:* Gestión de los docentes y producción (Est. 14–17)
  * *Factor 6:* Seguimiento a estudiantes y tutorías (Est. 18–21)
  * *Factor 7:* Investigación, desarrollo e innovación I+D+i (Est. 22–24)
  * *Factor 8:* Responsabilidad social universitaria y ambiente (Est. 25–26)
* **Dimensión 3: Soporte Institucional (Factores 9 a 11 | Estándares 27 a 32):**
  * *Factor 9:* Servicios de bienestar (Est. 27)
  * *Factor 10:* Infraestructura, LMS y bibliotecas (Est. 28–31)
  * *Factor 11:* Recursos humanos y gestión (Est. 32)
* **Dimensión 4: Resultados (Factor 12 | Estándares 33 a 34):**
  * *Factor 12:* Verificación del perfil de egreso y seguimiento a graduados (Est. 33–34)

---

## 🌟 Módulos y Funcionalidades del Sistema

1. 📊 **Dashboard Ejecutivo y Radar de Calidad (Plotly):**
   * Gráfica Radar polar de las 4 Dimensiones con umbral institucional del 80%.
   * Gráfica de barras horizontales de cumplimiento de los 12 Factores.
   * Semáforo visual en tiempo real de los 34 Estándares.
2. 📋 **Matriz de Autoevaluación y Carga de Evidencias:**
   * Criterio oficial de posgrado textual para cada estándar.
   * Registro y actualización de justificaciones técnicas, enlaces de evidencias (resoluciones, sílabos, actas) y planes de mejora.
3. 🎓 **Articulación Académica LMS:**
   * Cursos y sílabos por competencias.
   * Seguimiento de tesis doctorales, avance porcentual y control de similitud Turnitin (Estándar 23).
   * Plana docente con categorización RENACYT / CONCYTEC y producción en Scopus/WoS (Estándares 15 y 24).
4. 🤖 **Auditor Virtual de Acreditación (SGC-AI con Google Gemini 3.5 Flash):**
   * Emite dictámenes técnicos, sugiere evidencias documentales indispensables y redacta Planes de Mejora SMART.
5. 📄 **Generador de Informe Final de Autoevaluación:**
   * Reporte consolidado con matriz de planes de mejora para auditorías externas de pares evaluadores.

---

## 💻 Ejecución Local

```bash
cd 09_SGC_LMS_Acreditacion_Posgrado_Streamlit
pip install -r requirements.txt
streamlit run app.py --server.port 8503
```

---

## 🚀 Despliegue en Streamlit Community Cloud (Gratuito)

1. Sube este repositorio a tu cuenta de GitHub.
2. Conecta tu repositorio en [share.streamlit.io](https://share.streamlit.io/).
3. Agrega tu clave en **Secrets**:
   ```toml
   GEMINI_API_KEY = "tu_clave_de_google_ai_studio"
   ```
4. Haz clic en **Deploy!**
