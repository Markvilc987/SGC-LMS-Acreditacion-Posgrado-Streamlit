# 🏛️ SGC-Posgrado: Sistema de Gestión de la Calidad y Acreditación LMS

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Modelo SINEACE / SUNEDU](https://img.shields.io/badge/Modelo-4%20Dim%20%7C%2012%20Fac%20%7C%2034%20Est-1E3A8A.svg)](https://www.sineace.gob.pe)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-3.5%20Flash-4285F4.svg?logo=google&logoColor=white)](https://aistudio.google.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Plataforma integral de **Gestión de la Calidad, Acreditación y Articulación LMS para Posgrado (Maestrías y Doctorados)**, basada estrictamente en el modelo oficial de **4 Dimensiones, 12 Factores y 34 Estándares**.

Implementa control de acceso basado en roles (**RBAC**):
1. **👨‍💼 Administrador General (Director de Calidad):** Supervisa el **Dashboard Comparativo Multiprograma**, inspecciona los 34 estándares de cada posgrado, valida evidencias y coordina las auditorías.
2. **👨‍🏫 Responsables de Programa:** Cada maestría o doctorado cuenta con su propio usuario para autoevaluar los 34 estándares, **subir archivos digitales de evidencia** (resoluciones, actas, sílabos, reportes Turnitin) y formular planes de mejora.

---

## 🔑 Credenciales de Acceso Demostrativas (Pre-cargadas)

La plataforma cuenta con botones de **Acceso Rápido con 1 Clic** y credenciales de prueba:

| Rol | Usuario | Contraseña | Cargo / Programa Asignado |
| :--- | :--- | :--- | :--- |
| **👨‍💼 Administrador** | `admin` | `clave123` | **Dr. Carlos Mendoza** - Director General de Calidad y Acreditación (Acceso a todos los programas y dashboard global). |
| **👨‍🏫 Responsable** | `resp_gestion` | `clave123` | **Dr. Marcos Canchari** - Doctorado en Gestión Pública y Gobernabilidad (`DOC-GPG`). |
| **👩‍🏫 Responsable** | `resp_educacion` | `clave123` | **Dra. Elena Vargas** - Maestría en Educación con Mención en Docencia (`MAE-EDU`). |
| **👨‍💼 Responsable** | `resp_mba` | `clave123` | **Dr. Roberto Sánchez** - Maestría en Administración de Negocios - MBA (`MAE-MBA`). |
| **👨‍⚖️ Responsable** | `resp_derecho` | `clave123` | **Dr. Alberto Benavides** - Doctorado en Derecho y Ciencia Política (`DOC-DER`). |

---

## 🏛️ Estructura del Modelo de Calidad Implementado

* **Dimensión 1: Gestión Estratégica (Factores 1 al 3 | Estándares 1 al 8):**
  * *Factor 1:* Planificación del programa de estudios (Est. 1–4)
  * *Factor 2:* Gestión del perfil de egreso (Est. 5–6)
  * *Factor 3:* Aseguramiento de la calidad y planes de mejora (Est. 7–8)
* **Dimensión 2: Formación Integral (Factores 4 al 8 | Estándares 9 al 26):**
  * *Factor 4:* Proceso enseñanza-aprendizaje y movilidad (Est. 9–13)
  * *Factor 5:* Gestión de los docentes y producción (Est. 14–17)
  * *Factor 6:* Seguimiento a estudiantes y tutorías (Est. 18–21)
  * *Factor 7:* Investigación, desarrollo e innovación I+D+i (Est. 22–24)
  * *Factor 8:* Responsabilidad social universitaria y ambiente (Est. 25–26)
* **Dimensión 3: Soporte Institucional (Factores 9 al 11 | Estándares 27 al 32):**
  * *Factor 9:* Servicios de bienestar (Est. 27)
  * *Factor 10:* Infraestructura, LMS y bibliotecas (Est. 28–31)
  * *Factor 11:* Recursos humanos y gestión (Est. 32)
* **Dimensión 4: Resultados (Factor 12 | Estándares 33 al 34):**
  * *Factor 12:* Verificación del perfil de egreso y seguimiento a graduados (Est. 33–34)

---

## 🌟 Módulos y Funcionalidades del Sistema

1. 🌐 **Tablero Multiprograma (Vista Administrador):**
   * Gráfica comparativa de madurez SGC entre todos los programas de la universidad.
   * Matriz ejecutiva institucional con conteo de estándares cumplidos, en riesgo y archivos de evidencia subidos.
2. 📊 **Dashboard Ejecutivo y Radar SGC (Plotly):**
   * Gráfico Radar polar de las 4 Dimensiones con umbral institucional del 80%.
   * Gráfico de barras horizontales de cumplimiento de los 12 Factores.
   * Semáforo visual en tiempo real de los 34 Estándares.
3. 📋 **Matriz de Autoevaluación y Carga de Evidencias Digitales:**
   * Criterio oficial de posgrado textual para cada estándar.
   * **Carga de Archivos Reales:** Soporte para subir PDFs, DOCX, XLSX, imágenes y ZIP con registro de usuario y fecha.
   * Registro y actualización de justificaciones técnicas y planes de mejora SMART.
4. 🎓 **Articulación Académica LMS de Posgrado:**
   * Asignaturas y sílabos por competencias (Estándares 9, 10 y 11).
   * Monitoreo de tesis doctorales y control de similitud Turnitin con alertas semafóricas (Estándar 23).
   * Directorio docente con categorización RENACYT y publicaciones Scopus/WoS (Estándares 15 y 24).
5. 🤖 **Auditor Virtual de Acreditación (SGC-AI con Google Gemini 3.5 Flash):**
   * Emite dictámenes técnicos, sugiere evidencias documentales indispensables y redacta Planes de Mejora SMART.
6. 📄 **Generador de Informe Final de Autoevaluación:**
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
