import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database import (
    init_db,
    get_connection,
    get_program_summary,
    get_all_standards_for_program,
    update_standard_evaluation,
    get_lms_academic_data
)
from auditor_ia import consultar_auditor_sgc, get_api_key

# Configuración de página institucional
st.set_page_config(
    page_title="SGC-Posgrado | Sistema de Gestión de Calidad y Acreditación LMS",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Base de Datos con las 4 Dimensiones, 12 Factores y 34 Estándares
init_db()

# Estilos CSS ejecutivos y profesionales
st.markdown("""
<style>
    .sgc-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        border-radius: 12px;
        padding: 24px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .sgc-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .sgc-sub {
        font-size: 1.05rem;
        opacity: 0.9;
        margin-top: 6px;
    }
    .kpi-box {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .kpi-number {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
    }
    .kpi-text {
        font-size: 0.85rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        margin-top: 4px;
    }
    .criterio-card {
        background-color: #F8FAFC;
        border-left: 4px solid #1E3A8A;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }
    .badge-cumple {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-parcial {
        background-color: #E1EFFE;
        color: #1E429F;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-proceso {
        background-color: #FEF08A;
        color: #713F12;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .badge-nocumple {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
    }
</style>
<div class="sgc-header">
    <div class="sgc-title">🏛️ SGC-Posgrado | Sistema de Gestión de la Calidad y Acreditación</div>
    <div class="sgc-sub">Modelo Oficial SINEACE / SUNEDU para Maestrías y Doctorados: <strong>4 Dimensiones • 12 Factores • 34 Estándares</strong></div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# BARRA LATERAL (CONFIGURACIÓN INSTITUCIONAL)
# ==========================================

conn = get_connection()
c = conn.cursor()
c.execute("SELECT * FROM sgc_programas ORDER BY id ASC;")
programas = [dict(r) for r in c.fetchall()]
conn.close()

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/diploma.png", width=70)
    st.title("Gestión de Calidad")
    
    prog_options = {p["id"]: f"{p['codigo']} - {p['nombre']}" for p in programas}
    sel_prog_id = st.selectbox("Programa de Posgrado:", options=list(prog_options.keys()), format_func=lambda x: prog_options[x])
    current_prog = next(p for p in programas if p["id"] == sel_prog_id)

    st.markdown(f"**Nivel:** `{current_prog['nivel']}`")
    st.markdown(f"**Director:** {current_prog['director']}")
    st.markdown(f"**Facultad:** {current_prog['facultad']}")
    st.markdown(f"**Periodo:** `{current_prog['periodo_acreditacion']}`")
    st.divider()

    # Gestión de API Key
    api_key = get_api_key()
    if not api_key:
        c_key = st.text_input("🔑 Clave Gemini API (Auditor IA):", type="password")
        if c_key:
            st.session_state.custom_api_key = c_key
            st.success("API Key configurada.")
            st.rerun()

    st.caption("🛡️ **Aseguramiento de Calidad:** Cumple con la Ley Universitaria 30220 y modelos internacionales.")


# ==========================================
# OBTENER DATOS DE EVALUACIÓN DEL PROGRAMA
# ==========================================

kpis, dimensiones_res, factores_res = get_program_summary(sel_prog_id)
promedio_global = round(kpis.get("promedio_global", 0.0) or 0.0, 1)


# ==========================================
# PESTAÑAS PRINCIPALES DEL SISTEMA SGC LMS
# ==========================================

tab_dash, tab_matriz, tab_lms, tab_ia, tab_report = st.tabs([
    "📊 Dashboard Ejecutivo y Radar SGC",
    "📋 Matriz de Autoevaluación (34 Estándares)",
    "🎓 Articulación Académica LMS",
    "🤖 Auditor Virtual de Acreditación (IA)",
    "📄 Informe de Autoevaluación"
])


# ----------------------------------------------------
# 1. PESTAÑA: DASHBOARD EJECUTIVO Y RADAR DE CALIDAD
# ----------------------------------------------------
with tab_dash:
    # 4 Tarjetas KPI
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-number">{promedio_global}%</div>
            <div class="kpi-text">Índice Global de Calidad SGC</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-number" style="color:#059669;">{kpis.get('plenamente', 0)} / 34</div>
            <div class="kpi-text">Cumplimiento Pleno (100%)</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        parcial_proceso = (kpis.get('parcial', 0) or 0) + (kpis.get('en_proceso', 0) or 0)
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-number" style="color:#2563EB;">{parcial_proceso} / 34</div>
            <div class="kpi-text">En Proceso / Parcial</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-number" style="color:#DC2626;">{kpis.get('no_cumple', 0)} / 34</div>
            <div class="kpi-text">Brechas Críticas (No Cumple)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_radar, col_factores = st.columns([1, 1.1])

    # Gráfico Radar de las 4 Dimensiones
    with col_radar:
        st.subheader("🎯 Radar de Madurez por Dimensión")
        df_dim = pd.DataFrame(dimensiones_res)
        
        # Radar Chart en Plotly
        categories = df_dim["nombre"].tolist()
        values = df_dim["promedio"].tolist()
        # Cerrar el polígono
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            fillcolor='rgba(30, 58, 138, 0.25)',
            line=dict(color='#1E3A8A', width=3),
            name='Nivel Alcanzado (%)'
        ))
        # Línea de umbral mínimo de acreditación (80%)
        fig_radar.add_trace(go.Scatterpolar(
            r=[80] * len(categories_closed),
            theta=categories_closed,
            line=dict(color='#DC2626', width=2, dash='dot'),
            name='Umbral Acreditación (80%)'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            margin=dict(t=30, b=30, l=40, r=40),
            height=360,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # Gráfico de Barras de los 12 Factores
    with col_factores:
        st.subheader("📊 Nivel de Cumplimiento por los 12 Factores")
        df_fac = pd.DataFrame(factores_res)
        df_fac["color"] = df_fac["promedio"].apply(lambda p: "#059669" if p >= 80 else ("#2563EB" if p >= 60 else ("#EAB308" if p >= 40 else "#DC2626")))
        
        fig_fac = go.Figure(go.Bar(
            x=df_fac["promedio"],
            y=df_fac["codigo"] + ": " + df_fac["nombre"],
            orientation='h',
            marker=dict(color=df_fac["color"]),
            text=df_fac["promedio"].apply(lambda v: f"{v:.1f}%"),
            textposition='outside'
        ))
        fig_fac.add_vline(x=80, line_width=2, line_dash="dash", line_color="#DC2626", annotation_text="Meta 80%")
        fig_fac.update_layout(
            xaxis=dict(range=[0, 105], title="Porcentaje de Cumplimiento (%)"),
            yaxis=dict(autorange="reversed"),
            margin=dict(t=10, b=10, l=10, r=20),
            height=370
        )
        st.plotly_chart(fig_fac, use_container_width=True)

    st.divider()
    # Semáforo de los 34 Estándares
    st.subheader("🚦 Semáforo de los 34 Estándares del Posgrado")
    all_std = get_all_standards_for_program(sel_prog_id)
    
    cols_sem = st.columns(6)
    for idx, s in enumerate(all_std):
        col_target = cols_sem[idx % 6]
        badge_cls = "badge-cumple" if s["estado_cumplimiento"] == "Cumple Plenamente" else (
            "badge-parcial" if s["estado_cumplimiento"] == "Cumple Parcial" else (
                "badge-proceso" if s["estado_cumplimiento"] == "En Proceso" else "badge-nocumple"
            )
        )
        with col_target:
            st.markdown(f"""
            <div style="background:white; border:1px solid #E2E8F0; border-radius:8px; padding:10px; margin-bottom:12px; text-align:center;">
                <strong style="color:#1E3A8A;">{s['estandar_codigo']}</strong><br>
                <small style="display:block; height:34px; overflow:hidden; text-overflow:ellipsis;">{s['titulo']}</small>
                <span class="{badge_cls}">{s['porcentaje']}%</span>
            </div>
            """, unsafe_allow_html=True)


# ----------------------------------------------------
# 2. PESTAÑA: MATRIZ DE AUTOEVALUACIÓN Y EVIDENCIAS
# ----------------------------------------------------
with tab_matriz:
    st.subheader("📋 Matriz de Autoevaluación Integral de Estándares")
    st.caption("Inspecciona los criterios de posgrado oficiales de cada estándar, carga tus evidencias documentales y actualiza el estado de autoevaluación.")

    # Filtros
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT nombre FROM sgc_dimensiones ORDER BY id ASC;")
    dim_list = ["Todas"] + [r["nombre"] for r in c.fetchall()]
    c.execute("SELECT DISTINCT nombre FROM sgc_factores ORDER BY id ASC;")
    fac_list = ["Todos"] + [r["nombre"] for r in c.fetchall()]
    conn.close()

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        sel_dim_filter = st.selectbox("Filtrar por Dimensión:", dim_list)
    with f_col2:
        sel_fac_filter = st.selectbox("Filtrar por Factor:", fac_list)

    standards_filtered = get_all_standards_for_program(sel_prog_id, sel_dim_filter, sel_fac_filter)
    st.markdown(f"**Mostrando {len(standards_filtered)} estándares seleccionados.**")

    for est in standards_filtered:
        num = est["numero"]
        badge_style = "badge-cumple" if est["estado_cumplimiento"] == "Cumple Plenamente" else (
            "badge-parcial" if est["estado_cumplimiento"] == "Cumple Parcial" else (
                "badge-proceso" if est["estado_cumplimiento"] == "En Proceso" else "badge-nocumple"
            )
        )
        expander_title = f"{est['estandar_codigo']}: {est['titulo']}  |  {est['estado_cumplimiento']} ({est['porcentaje']}%)  |  {est['dimension_nombre']}"

        with st.expander(expander_title, expanded=False):
            st.markdown(f"""
            <div class="criterio-card">
                <strong>📌 Criterio Oficial de Posgrado (SINEACE / SUNEDU):</strong><br>
                {est['criterio_posgrado']}
            </div>
            """, unsafe_allow_html=True)

            with st.form(f"form_estandar_{num}"):
                fc1, fc2, fc3 = st.columns([1.2, 1, 1.2])
                with fc1:
                    new_estado = st.selectbox(
                        "Estado de Cumplimiento:",
                        ["Cumple Plenamente", "Cumple Parcial", "En Proceso", "No Cumple"],
                        index=["Cumple Plenamente", "Cumple Parcial", "En Proceso", "No Cumple"].index(est["estado_cumplimiento"])
                    )
                with fc2:
                    new_pct = st.slider("Porcentaje de Avance (%):", 0.0, 100.0, float(est["porcentaje"]), step=5.0)
                with fc3:
                    new_resp = st.text_input("Responsable / Comité:", value=est["responsable"] or "Comité de Calidad")

                new_just = st.text_area("Justificación Técnica de Cumplimiento:", value=est["justificacion"], height=90)
                new_evid = st.text_area("Evidencias Documentales y Enlaces LMS (Resoluciones, actas, sílabos, reportes):", value=est["evidencias"], height=70)
                new_plan = st.text_area("Plan de Mejora (Acciones para cerrar brechas en este estándar):", value=est["plan_mejora"], height=70)

                btn_save = st.form_submit_button(f"💾 Guardar Evaluación de {est['estandar_codigo']}", type="primary")
                if btn_save:
                    update_standard_evaluation(sel_prog_id, est["estandar_id"], new_estado, new_pct, new_just, new_evid, new_plan, new_resp)
                    st.success(f"¡Estándar {est['estandar_codigo']} actualizado exitosamente!")
                    st.rerun()


# ----------------------------------------------------
# 3. PESTAÑA: ARTICULACIÓN ACADÉMICA LMS
# ----------------------------------------------------
with tab_lms:
    st.subheader("🎓 Articulación entre el LMS y los Estándares de Posgrado")
    st.write("Los estándares 9, 10, 11 (Currículo por competencias), 15 (Plana docente) y 23 (Tesis e investigación) se monitorean en tiempo real a través de los datos de la plataforma académica.")

    sub_lms1, sub_lms2, sub_lms3 = st.tabs([
        "📚 Cursos y Sílabos por Competencias (Est. 9-11)",
        "🔬 Seguimiento de Tesis e I+D+i (Est. 22-24)",
        "👨‍🏫 Plana Docente y RENACYT (Est. 14-17)"
    ])

    cursos_data, tesis_data, docentes_data = get_lms_academic_data(sel_prog_id)

    with sub_lms1:
        st.markdown("#### 📖 Asignaturas y Mapeo de Competencias en el LMS")
        df_c = pd.DataFrame(cursos_data)
        if not df_c.empty:
            st.dataframe(df_c[["codigo", "nombre", "ciclo", "creditos", "docente_nombre", "silabo_url", "enfoque_competencias"]], use_container_width=True, hide_index=True)
        else:
            st.info("No hay asignaturas registradas.")

    with sub_lms2:
        st.markdown("#### 📝 Monitoreo de Tesis Doctorales y Control de Similitud (Turnitin)")
        df_t = pd.DataFrame(tesis_data)
        if not df_t.empty:
            df_t["similitud_alerta"] = df_t["similitud_turnitin"].apply(lambda x: "🟢 Aceptable" if x <= 12 else ("🟡 En Revisión" if x <= 20 else "🔴 Excede Límite"))
            st.dataframe(df_t[["estudiante_nombre", "titulo_tesis", "asesor_nombre", "porcentaje_avance", "similitud_turnitin", "similitud_alerta", "comite_etica_aprobado", "articulo_publicado"]], use_container_width=True, hide_index=True)
        else:
            st.info("No hay proyectos de tesis registrados.")

    with sub_lms3:
        st.markdown("#### 🏅 Calificación Docente y Registro RENACYT (CONCYTEC)")
        df_d = pd.DataFrame(docentes_data)
        if not df_d.empty:
            st.dataframe(df_d[["nombre", "grado_academico", "categoria_docente", "nivel_renacyt", "codigo_orcid", "articulos_scopus_wos"]], use_container_width=True, hide_index=True)
        else:
            st.info("No hay docentes registrados.")


# ----------------------------------------------------
# 4. PESTAÑA: AUDITOR VIRTUAL DE ACREDITACIÓN (IA)
# ----------------------------------------------------
with tab_ia:
    st.subheader("🤖 Auditor Virtual de Acreditación de Posgrado (SGC-AI)")
    st.write("Consulta al auditor inteligente entrenado en el modelo SINEACE / SUNEDU para resolver dudas de auditoría, evaluar la pertinencia de tus evidencias o formular Planes de Mejora SMART.")

    std_all = get_all_standards_for_program(sel_prog_id)
    std_map = {s["estandar_id"]: f"{s['estandar_codigo']} - {s['titulo']} ({s['estado_cumplimiento']})" for s in std_all}

    c_ia1, c_ia2 = st.columns([1, 1.4])
    with c_ia1:
        sel_std_ia = st.selectbox("Selecciona el Estándar a Auditar:", options=list(std_map.keys()), format_func=lambda x: std_map[x])
        std_obj = next(s for s in std_all if s["estandar_id"] == sel_std_ia)

        st.markdown(f"""
        **Factor:** `{std_obj['factor_codigo']}: {std_obj['factor_nombre']}`  
        **Dimensión:** `{std_obj['dimension_codigo']}: {std_obj['dimension_nombre']}`  
        **Criterio Oficial:**  
        _{std_obj['criterio_posgrado']}_
        """)

        pregunta_rapida = st.radio(
            "Opciones rápidas:",
            [
                "¿Qué evidencias documentales indispensables exige este estándar para posgrado?",
                "Formula un Plan de Mejora SMART para cerrar brechas en este estándar.",
                "Escribe una justificación técnica formal de cumplimiento para los pares evaluadores.",
                "Pregunta personalizada"
            ]
        )

        consulta_final = pregunta_rapida
        if pregunta_rapida == "Pregunta personalizada":
            consulta_final = st.text_area("Escribe tu consulta específica para el Auditor:")

        btn_consultar = st.button("🔍 Auditar con IA", type="primary", use_container_width=True)

    with c_ia2:
        st.markdown("#### 📋 Dictamen del Auditor de Calidad:")
        if btn_consultar:
            with st.spinner("El Auditor Virtual está analizando el criterio de posgrado y las evidencias... ⏳"):
                ctx = {
                    "codigo": std_obj["estandar_codigo"],
                    "titulo": std_obj["titulo"],
                    "dimension": std_obj["dimension_nombre"],
                    "factor": std_obj["factor_nombre"],
                    "criterio": std_obj["criterio_posgrado"],
                    "estado": std_obj["estado_cumplimiento"],
                    "porcentaje": std_obj["porcentaje"],
                    "justificacion": std_obj["justificacion"],
                    "evidencias": std_obj["evidencias"]
                }
                dictamen = consultar_auditor_sgc(consulta_final, ctx)
                st.markdown(dictamen)
        else:
            st.info("Selecciona un estándar y haz clic en 'Auditar con IA' para recibir recomendaciones técnicas oficiales.")


# ----------------------------------------------------
# 5. PESTAÑA: INFORME FINAL DE AUTOEVALUACIÓN
# ----------------------------------------------------
with tab_report:
    st.subheader("📄 Informe Ejecutivo de Autoevaluación Institucional")
    st.write(f"Programa: **{current_prog['nombre']}** | Periodo: **{current_prog['periodo_acreditacion']}**")

    st.markdown(f"""
    ### 1. Resumen de Madurez del Sistema de Gestión de Calidad
    * **Índice Global de Calidad Alcanzado:** **{promedio_global}%**
    * **Total de Estándares Plenamente Cumplidos:** **{kpis.get('plenamente', 0)} de 34**
    * **Estándares en Vías de Cumplimiento:** **{parcial_proceso} de 34**
    * **Estándares con Brechas Críticas:** **{kpis.get('no_cumple', 0)} de 34**
    """)

    st.markdown("### 2. Matriz Consolidada de Planes de Mejora Aprobados")
    all_std_report = get_all_standards_for_program(sel_prog_id)
    df_report = pd.DataFrame(all_std_report)
    df_planes = df_report[df_report["plan_mejora"].str.len() > 5][["estandar_codigo", "titulo", "factor_nombre", "estado_cumplimiento", "porcentaje", "plan_mejora", "responsable"]]
    df_planes.columns = ["Código", "Estándar", "Factor", "Estado Actual", "% Avance", "Plan de Acción de Mejora", "Responsable"]

    if not df_planes.empty:
        st.dataframe(df_planes, use_container_width=True, hide_index=True)
    else:
        st.info("No hay planes de mejora registrados actualmente.")

    st.markdown("### 3. Veredicto del Comité de Calidad")
    if promedio_global >= 80.0 and (kpis.get('no_cumple', 0) == 0):
        st.success("🟢 **DICTAMEN FAVORABLE:** El programa cumple satisfactoriamente las condiciones mínimas para solicitar la visita de Pares Evaluadores Externos con fines de Acreditación.")
    else:
        st.warning(f"🟡 **DICTAMEN CONDICIONADO:** El programa se encuentra en {promedio_global}% de avance global. Se requiere ejecutar prioritariamente los planes de mejora de los estándares en estado 'No Cumple' o 'En Proceso' antes de remitir el expediente de acreditación.")
