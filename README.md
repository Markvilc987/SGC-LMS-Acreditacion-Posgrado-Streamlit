# 🏛️ SGC-Posgrado UCV: Sistema de Gestión de la Calidad y Acreditación LMS
### Universidad César Vallejo (UCV) • Escuela de Posgrado

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Modelo SINEACE / SUNEDU](https://img.shields.io/badge/Modelo-4%20Dim%20%7C%2012%20Fac%20%7C%2034%20Est-0B2545.svg)](https://www.sineace.gob.pe)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-3.5%20Flash-4285F4.svg?logo=google&logoColor=white)](https://aistudio.google.com)
[![UCV Posgrado](https://img.shields.io/badge/Institución-UCV%20Posgrado-C8102E.svg)](https://ucv.edu.pe/posgrado)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Plataforma integral de **Gestión de la Calidad, Acreditación y Articulación LMS para la Escuela de Posgrado de la Universidad César Vallejo (UCV)**, cubriendo sus programas oficiales de **Doctorado y Maestría** bajo el modelo oficial de **4 Dimensiones, 12 Factores y 34 Estándares de SINEACE / SUNEDU**.

Cuenta con arquitectura de control de acceso basado en roles (**RBAC**):
1. **🏛️ Director de Aseguramiento de la Calidad UCV (Administrador):** Supervisa el **Tablero Multiprograma (Benchmark Institucional)**, monitorea en tiempo real los 34 estándares de cada posgrado, valida evidencias documentales y audita el cumplimiento normativo.
2. **👨‍🏫 Responsables y Coordinadores de Programa:** Cada maestría y doctorado de la UCV cuenta con su propio usuario asignado para autoevaluar los 34 estándares, **subir archivos digitales de evidencia** (resoluciones rectorales, actas de comité, sílabos, reportes de similitud Turnitin ≤20% aprobados por el CEI-UCV) y formular planes de mejora SMART.

---

## 🔑 Directorio de Usuarios y Credenciales Institucionales UCV

La plataforma incluye botones de **Acceso Rápido Demostrativo con 1 Clic** y permite el ingreso directo con las siguientes cuentas:

> **Contraseña global de demostración:** `clave123`

| Rol | Usuario | Contraseña | Autoridad / Coordinador Asignado | Programa Oficial UCV |
| :--- | :--- | :--- | :--- | :--- |
| **🏛️ Admin General** | `admin_ucv` | `clave123` | **Dr. Carlos Mendoza Dávila**<br>_Director de Aseguramiento de la Calidad UCV_ | **Escuela de Posgrado UCV** (Dashboard Global de todos los programas) |
| **👨‍🏫 Responsable** | `jvilchez` | `clave123` | **Dr. Juan Marcos Vilchez-Canchari**<br>_Investigador RENACYT Nivel I_ | **Doctorado en Gestión Pública y Gobernabilidad** (`DOC-GPG-UCV`) |
| **👩‍🏫 Responsable** | `evargas` | `clave123` | **Dra. Elena Vargas Morales** | **Doctorado en Educación** (`DOC-EDU-UCV`) |
| **👨‍💼 Responsable** | `rsanchez` | `clave123` | **Dr. Roberto Sánchez Romero** | **Doctorado en Administración** (`DOC-ADM-UCV`) |
| **👨‍⚖️ Responsable** | `abenavides` | `clave123` | **Dr. Alberto Benavides Ruiz** | **Doctorado en Derecho** (`DOC-DER-UCV`) |
| **👨‍💼 Responsable** | `cmendoza` | `clave123` | **Mag. Carlos Mendoza Dávila** | **Maestría en Gestión Pública** (`MAE-GP-UCV`) |
| **💼 Responsable** | `rparedes` | `clave123` | **Mag. Ricardo Paredes Campos** | **Maestría en Administración de Negocios - MBA** (`MAE-MBA-UCV`) |
| **👩‍🏫 Responsable** | `pmorales` | `clave123` | **Dra. Patricia Morales Soto** | **Maestría en Docencia Universitaria** (`MAE-MDU-UCV`) |
| **👩‍⚕️ Responsable** | `lalarcon` | `clave123` | **Dra. Lucía Alarcón Medina** | **Maestría en Salud Pública** (`MAE-MSP-UCV`) |

---

## 🏛️ Estructura del Modelo de Calidad Implementado (SINEACE / SUNEDU)

* **Dimensión 1: Gestión Estratégica (Factores 1 al 3 | Estándares 1 al 8):**
  * *Factor 1:* Planificación del programa de estudios (Est. 1–4)
  * *Factor 2:* Gestión del perfil de egreso (Est. 5–6)
  * *Factor 3:* Aseguramiento de la calidad y planes de mejora (Est. 7–8)
* **Dimensión 2: Formación Integral (Factores 4 al 8 | Estándares 9 al 26):**
  * *Factor 4:* Proceso enseñanza-aprendizaje y movilidad (Est. 9–13)
  * *Factor 5:* Gestión de los docentes y producción científica (Est. 14–17)
  * *Factor 6:* Seguimiento a estudiantes y asesoría de tesis (Est. 18–21)
  * *Factor 7:* Investigación, desarrollo e innovación I+D+i (Est. 22–24)
  * *Factor 8:* Responsabilidad social universitaria y ambiente (Est. 25–26)
* **Dimensión 3: Soporte Institucional (Factores 9 al 11 | Estándares 27 al 32):**
  * *Factor 9:* Servicios de bienestar universitario (Est. 27)
  * *Factor 10:* Infraestructura tecnológica, LMS y bibliotecas científicas (Est. 28–31)
  * *Factor 11:* Recursos humanos y gestión administrativa (Est. 32)
* **Dimensión 4: Resultados (Factor 12 | Estándares 33 al 34):**
  * *Factor 12:* Verificación del perfil de egreso y objetivos educacionales (Est. 33–34)

---

## 🌟 Módulos y Funcionalidades Principales

1. 🌐 **Tablero Multiprograma UCV (Vista Administrador):**
   * Gráfica comparativa de madurez SGC entre los 8 programas de maestría y doctorado de la UCV.
   * Matriz ejecutiva institucional con conteo de estándares cumplidos, en riesgo y archivos de evidencia subidos.
2. 📊 **Dashboard Ejecutivo y Radar SGC (Plotly):**
   * Gráfico Radar polar de las 4 Dimensiones con umbral institucional del 80%.
   * Gráfico de barras horizontales de cumplimiento de los 12 Factores.
   * Semáforo visual en tiempo real de los 34 Estándares.
3. 📋 **Matriz de Autoevaluación y Repositorio de Evidencias Digitales:**
   * Criterio oficial de posgrado textual para cada estándar.
   * **Carga de Archivos Reales:** Soporte para subir PDFs, DOCX, XLSX, imágenes y ZIP con registro de usuario y fecha.
   * Registro y actualización de justificaciones técnicas y planes de mejora SMART.
4. 🎓 **Articulación Académica LMS de Posgrado:**
   * Asignaturas y sílabos por competencias articulados al campus virtual UCV.
   * Monitoreo de tesis doctorales y control de similitud Turnitin conforme a la normativa del Comité de Ética (CEI-UCV, máx. 20%).
   * Directorio docente con categorización RENACYT y publicaciones Scopus/WoS.
5. 🤖 **Auditor Virtual de Acreditación (SGC-AI con Google Gemini 3.5 Flash):**
   * Emite dictámenes técnicos contextualizados en la normativa UCV y SINEACE, sugiere evidencias indispensables y redacta Planes de Mejora SMART.
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

1. Sube este repositorio a tu cuenta de GitHub (`Markvilc987/SGC-LMS-Acreditacion-Posgrado-Streamlit`).
2. Conecta tu repositorio en [share.streamlit.io](https://share.streamlit.io/).
3. Agrega tu clave en **Secrets**:
   ```toml
   GEMINI_API_KEY = "tu_clave_de_google_ai_studio"
   ```
4. Haz clic en **Deploy!**
