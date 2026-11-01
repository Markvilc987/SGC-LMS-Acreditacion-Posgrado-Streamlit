import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from database import (
    init_db,
    authenticate_user,
    get_all_users,
    get_all_programs,
    get_program_by_id,
    get_all_programs_benchmark,
    get_program_summary,
    get_all_standards_for_program,
    update_standard_evaluation,
    save_uploaded_evidence,
    get_standard_evidence_files,
    delete_evidence_file,
    get_lms_academic_data
)
from auditor_ia import consultar_auditor_sgc, get_api_key

# Configuración de página institucional UCV
st.set_page_config(
    page_title="SGC-Posgrado UCV | Escuela de Posgrado Universidad César Vallejo",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Base de Datos
init_db()

# Estado de sesión
if "user" not in st.session_state:
    st.session_state.user = None

# Estilos CSS ejecutivos con identidad institucional UCV (Azul Marino y Rojo Vallejo)
st.markdown("""
<style>
    .sgc-header {
        background: linear-gradient(135deg, #0B2545 0%, #132E59 50%, #8B0000 100%);
        border-radius: 12px;
        padding: 24px 28px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 6px 18px rgba(11, 37, 69, 0.2);
        border-bottom: 4px solid #C8102E;
    }
    .sgc-badge-ucv {
        background-color: #C8102E;
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 6px;
    }
    .sgc-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .sgc-sub {
        font-size: 1.02rem;
        opacity: 0.95;
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
        font-size: 2.1rem;
        font-weight: 800;
        color: #0B2545;
    }
    .kpi-text {
        font-size: 0.82rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        margin-top: 4px;
    }
    .criterio-card {
        background-color: #F8FAFC;
        border-left: 4px solid #0B2545;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }
    .badge-admin {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 700;
        border: 1px solid #FCD34D;
    }
    .badge-responsable {
        background-color: #EEF2FF;
        color: #1E3A8A;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 700;
        border: 1px solid #C7D2FE;
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
    <span class="sgc-badge-ucv">UNIVERSIDAD CÉSAR VALLEJO • ESCUELA DE POSGRADO</span>
    <div class="sgc-title">🏛️ SGC-Posgrado | Sistema de Acreditación y Evidencias Digitales LMS</div>
    <div class="sgc-sub">Modelo Oficial SINEACE / SUNEDU: <strong>4 Dimensiones • 12 Factores • 34 Estándares de Calidad Universitaria</strong></div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# GESTIÓN DE AUTENTICACIÓN Y BARRA LATERAL
# ==========================================

all_programs = get_all_programs()
prog_map = {p["id"]: p for p in all_programs}

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/diploma.png", width=70)
    st.title("Control de Acceso")
    st.divider()

    user = st.session_state.user
    if user:
        role_label = "ADMINISTRADOR GENERAL" if user["role"] == "admin" else "RESPONSABLE DE PROGRAMA"
        role_cls = "badge-admin" if user["role"] == "admin" else "badge-responsable"
        st.markdown(f"**Usuario:** {user['avatar']} {user['full_name']}")
        st.markdown(f"<span class='{role_cls}'>{role_label}</span>", unsafe_allow_html=True)
        st.caption(f"Cargo: {user.get('cargo', 'Comité SGC')}")

        if user["role"] == "responsable" and user.get("programa_nombre"):
            st.info(f"📌 **Programa Asignado:**\n\n{user['programa_nombre']}")
        st.divider()

        # Si es Admin, puede seleccionar qué programa inspeccionar
        if user["role"] == "admin":
            st.subheader("🎯 Vista de Programa:")
            admin_prog_opts = {p["id"]: f"{p['codigo']} - {p['nombre']}" for p in all_programs}
            sel_prog_id = st.selectbox("Seleccionar Programa a Inspeccionar:", options=list(admin_prog_opts.keys()), format_func=lambda x: admin_prog_opts[x])
        else:
            sel_prog_id = user["programa_id"]

        st.divider()
        # Gestión de API Key
        api_key = get_api_key()
        if not api_key:
            c_key = st.text_input("🔑 Clave Gemini API (Auditor IA):", type="password")
            if c_key:
                st.session_state.custom_api_key = c_key
                st.success("API Key configurada.")
                st.rerun()

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        st.info("👋 Por favor inicia sesión para acceder al sistema.")


# ==========================================
# PANTALLA DE INICIO DE SESIÓN (SI NO ESTÁ LOGUEADO)
# ==========================================

if not st.session_state.user:
    st.markdown("## 🔐 Inicio de Sesión Institucional | Escuela de Posgrado UCV")
    st.write("Bienvenido al Sistema de Gestión de la Calidad y Acreditación de Posgrado de la Universidad César Vallejo. Selecciona tu perfil o ingresa tus credenciales:")

    col_l1, col_l2 = st.columns([1, 1.3])

    with col_l1:
        st.subheader("🔑 Ingreso con Credenciales Institucionales")
        log_u = st.text_input("Usuario UCV:", key="in_u", placeholder="Ej. jvilchez, admin_ucv")
        log_p = st.text_input("Contraseña:", type="password", key="in_p")
        if st.button("Iniciar Sesión", type="primary", use_container_width=True):
            auth = authenticate_user(log_u.strip(), log_p.strip())
            if auth:
                st.session_state.user = auth
                st.success(f"¡Bienvenido, {auth['full_name']}!")
                st.rerun()
            else:
                st.error("Credenciales incorrectas. (Prueba con usuario y contraseña demo: clave123)")

        st.info("💡 **Credencial de prueba global:** Todas las cuentas demo utilizan la contraseña: `clave123`")

    with col_l2:
        st.subheader("⚡ Acceso Rápido Demostrativo (1 Clic)")
        st.caption("Prueba los diferentes perfiles institucionales de la Escuela de Posgrado UCV:")

        # Botón Director de Calidad UCV
        if st.button("🏛️ Director Aseguramiento de la Calidad UCV (Dr. Carlos Mendoza Dávila)", type="secondary", use_container_width=True):
            st.session_state.user = authenticate_user("admin_ucv", "clave123")
            st.rerun()

        st.markdown("---")
        st.markdown("**Responsables y Coordinadores de Programa UCV:**")

        st.markdown("🎓 **Doctorados UCV:**")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            if st.button("👨‍🏫 Dr. Juan Marcos Vilchez-Canchari\n(Doc. Gestión Pública)", use_container_width=True):
                st.session_state.user = authenticate_user("jvilchez", "clave123")
                st.rerun()
            if st.button("👩‍🏫 Dra. Elena Vargas Morales\n(Doc. Educación)", use_container_width=True):
                st.session_state.user = authenticate_user("evargas", "clave123")
                st.rerun()
        with d_col2:
            if st.button("👨‍💼 Dr. Roberto Sánchez Romero\n(Doc. Administración)", use_container_width=True):
                st.session_state.user = authenticate_user("rsanchez", "clave123")
                st.rerun()
            if st.button("👨‍⚖️ Dr. Alberto Benavides Ruiz\n(Doc. Derecho)", use_container_width=True):
                st.session_state.user = authenticate_user("abenavides", "clave123")
                st.rerun()

        st.markdown("📚 **Maestrías UCV:**")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            if st.button("👨‍💼 Mag. Carlos Mendoza Dávila\n(Mtr. Gestión Pública)", use_container_width=True):
                st.session_state.user = authenticate_user("cmendoza", "clave123")
                st.rerun()
            if st.button("💼 Mag. Ricardo Paredes Campos\n(Maestría MBA UCV)", use_container_width=True):
                st.session_state.user = authenticate_user("rparedes", "clave123")
                st.rerun()
        with m_col2:
            if st.button("👩‍🏫 Dra. Patricia Morales Soto\n(Mtr. Docencia Univ.)", use_container_width=True):
                st.session_state.user = authenticate_user("pmorales", "clave123")
                st.rerun()
            if st.button("👩‍⚕️ Dra. Lucía Alarcón Medina\n(Mtr. Salud Pública)", use_container_width=True):
                st.session_state.user = authenticate_user("lalarcon", "clave123")
                st.rerun()

    st.stop()


# ==========================================
# VISTA DINÁMICA SEGÚN ROL (ADMIN vs RESPONSABLE)
# ==========================================

active_prog = prog_map.get(sel_prog_id, all_programs[0])
kpis, dimensiones_res, factores_res = get_program_summary(active_prog["id"])
promedio_global = round(kpis.get("promedio_global", 0.0) or 0.0, 1)


# --------------------------------------------------------------------------
# CASO 1: VISTA DEL ADMINISTRADOR GENERAL
# --------------------------------------------------------------------------
if user["role"] == "admin":
    st.markdown(f"### 👨‍💼 Panel del Administrador General | Supervisando: **{active_prog['nombre']}** (`{active_prog['codigo']}`)")

    tab_global, tab_dash, tab_audit_matriz, tab_users, tab_ia = st.tabs([
        "🌐 Tablero Multiprograma (Benchmark Institucional)",
        "📊 Dashboard y Radar SGC del Programa",
        "📋 Auditoría de Evidencias y Estándares (34)",
        "👥 Directorio de Responsables",
        "🤖 Auditor Virtual de Acreditación (IA)"
    ])

    # 1. Tablero Global Multiprograma
    with tab_global:
        st.subheader("🌐 Comparativa Institucional de Programas de Posgrado")
        st.write("Monitoreo ejecutivo del grado de avance y madurez para la acreditación en todos los programas de la Escuela de Posgrado:")

        benchmark_data = get_all_programs_benchmark()
        df_bench = pd.DataFrame(benchmark_data)

        # Gráfico de barras comparativo institucional
        fig_bench = px.bar(
            df_bench,
            x="codigo",
            y="promedio_global",
            color="promedio_global",
            color_continuous_scale="Blues",
            labels={"codigo": "Programa", "promedio_global": "Madurez SGC (%)"},
            text=df_bench["promedio_global"].apply(lambda v: f"{v:.1f}%")
        )
        fig_bench.add_hline(y=80, line_dash="dash", line_color="#DC2626", annotation_text="Meta Acreditación (80%)")
        fig_bench.update_layout(height=340, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_bench, use_container_width=True)

        # Tabla consolidada
        st.markdown("#### 📋 Matriz Consolidada de Acreditación por Programa")
        df_display_bench = df_bench[[
            "codigo", "nombre", "nivel", "director", "promedio_global",
            "plenamente", "parcial", "en_proceso", "no_cumple", "total_archivos_evidencia"
        ]].copy()
        df_display_bench.columns = [
            "Código", "Programa de Posgrado", "Nivel", "Director / Responsable", "% Madurez",
            "Cumple Pleno", "Parcial", "En Proceso", "No Cumple", "Archivos Subidos"
        ]
        df_display_bench["% Madurez"] = df_display_bench["% Madurez"].apply(lambda v: f"{v:.1f}%")
        st.dataframe(df_display_bench, use_container_width=True, hide_index=True)

    # 2. Dashboard y Radar del Programa
    with tab_dash:
        # KPIs del programa seleccionado
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='kpi-box'><div class='kpi-number'>{promedio_global}%</div><div class='kpi-text'>Madurez SGC Global</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='kpi-box'><div class='kpi-number' style='color:#059669;'>{kpis.get('plenamente', 0)} / 34</div><div class='kpi-text'>Cumplen Plenamente</div></div>", unsafe_allow_html=True)
        with col3:
            parc_proc = (kpis.get('parcial', 0) or 0) + (kpis.get('en_proceso', 0) or 0)
            st.markdown(f"<div class='kpi-box'><div class='kpi-number' style='color:#2563EB;'>{parc_proc} / 34</div><div class='kpi-text'>En Proceso / Parcial</div></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='kpi-box'><div class='kpi-number' style='color:#DC2626;'>{kpis.get('no_cumple', 0)} / 34</div><div class='kpi-text'>Brechas Críticas (No Cumple)</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c_radar, c_factores = st.columns([1, 1.1])

        with c_radar:
            st.subheader("🎯 Radar de Madurez por Dimensión")
            df_dim = pd.DataFrame(dimensiones_res)
            cats = df_dim["nombre"].tolist()
            vals = df_dim["promedio"].tolist()
            cats_c = cats + [cats[0]]
            vals_c = vals + [vals[0]]

            fig_r = go.Figure()
            fig_r.add_trace(go.Scatterpolar(
                r=vals_c, theta=cats_c, fill='toself',
                fillcolor='rgba(30, 58, 138, 0.25)', line=dict(color='#1E3A8A', width=3),
                name='Alcanzado (%)'
            ))
            fig_r.add_trace(go.Scatterpolar(
                r=[80] * len(cats_c), theta=cats_c,
                line=dict(color='#DC2626', width=2, dash='dot'), name='Umbral (80%)'
            ))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, margin=dict(t=20, b=20, l=30, r=30))
            st.plotly_chart(fig_r, use_container_width=True)

        with c_factores:
            st.subheader("📊 Cumplimiento por los 12 Factores")
            df_f = pd.DataFrame(factores_res)
            df_f["color"] = df_f["promedio"].apply(lambda p: "#059669" if p >= 80 else ("#2563EB" if p >= 60 else ("#EAB308" if p >= 40 else "#DC2626")))
            fig_f = go.Figure(go.Bar(
                x=df_f["promedio"], y=df_f["codigo"] + ": " + df_f["nombre"],
                orientation='h', marker=dict(color=df_f["color"]),
                text=df_f["promedio"].apply(lambda v: f"{v:.1f}%"), textposition='outside'
            ))
            fig_f.add_vline(x=80, line_dash="dash", line_color="#DC2626", annotation_text="Meta 80%")
            fig_f.update_layout(xaxis=dict(range=[0, 105]), yaxis=dict(autorange="reversed"), height=350, margin=dict(t=10, b=10, l=10, r=20))
            st.plotly_chart(fig_f, use_container_width=True)

        st.divider()
        st.subheader("🚦 Semáforo de los 34 Estándares")
        stds = get_all_standards_for_program(active_prog["id"])
        c_cols = st.columns(6)
        for idx, s in enumerate(stds):
            target = c_cols[idx % 6]
            b_cls = "badge-cumple" if s["estado_cumplimiento"] == "Cumple Plenamente" else (
                "badge-parcial" if s["estado_cumplimiento"] == "Cumple Parcial" else (
                    "badge-proceso" if s["estado_cumplimiento"] == "En Proceso" else "badge-nocumple"
                )
            )
            with target:
                st.markdown(f"""
                <div style="background:white; border:1px solid #E2E8F0; border-radius:8px; padding:10px; margin-bottom:12px; text-align:center;">
                    <strong style="color:#1E3A8A;">{s['estandar_codigo']}</strong><br>
                    <small style="display:block; height:34px; overflow:hidden;">{s['titulo']}</small>
                    <span class="{b_cls}">{s['porcentaje']}%</span>
                </div>
                """, unsafe_allow_html=True)

    # 3. Auditoría de Evidencias (Admin)
    with tab_audit_matriz:
        st.subheader("📋 Auditoría de Evidencias y Autoevaluación")
        st.caption("Revisa los archivos subidos por el responsable del programa y sus justificaciones técnicas.")

        all_stds_admin = get_all_standards_for_program(active_prog["id"])
        for est in all_stds_admin:
            with st.expander(f"{est['estandar_codigo']}: {est['titulo']} | Estado: {est['estado_cumplimiento']} ({est['porcentaje']}%) | Archivos: {est['total_archivos']}"):
                st.markdown(f"**📌 Criterio Oficial de Posgrado:** {est['criterio_posgrado']}")
                st.markdown(f"**Justificación del Responsable:** {est['justificacion'] or '_Sin justificación registrada_'}")
                st.markdown(f"**Evidencias descritas:** {est['evidencias_texto'] or '_Sin evidencias textuales_'}")
                st.markdown(f"**Plan de Mejora:** {est['plan_mejora'] or '_Sin plan de mejora_'}")
                st.markdown(f"**Responsable Operativo:** `{est['responsable']}`")

                # Archivos físicos de evidencia cargados
                files = get_standard_evidence_files(active_prog["id"], est["estandar_id"])
                if files:
                    st.markdown("📂 **Archivos de Evidencia Adjuntos:**")
                    for f in files:
                        st.markdown(f"- 📄 `{f['nombre_archivo']}` ({round(f['tamanio_bytes']/1024, 1)} KB) - Subido por: **{f['subido_por']}** el _{f['fecha_subida']}_")
                else:
                    st.caption("⚠️ No se han subido archivos de evidencia para este estándar.")

    # 4. Directorio de Responsables
    with tab_users:
        st.subheader("👥 Directorio de Responsables de Programa y Comités")
        users_list = get_all_users()
        df_u = pd.DataFrame(users_list)
        st.dataframe(df_u[["avatar", "full_name", "username", "role", "cargo", "programa_nombre", "email"]], use_container_width=True, hide_index=True)

    # 5. Auditor IA
    with tab_ia:
        st.subheader("🤖 Consultoría con el Auditor Virtual IA (Gemini 3.5 Flash)")
        std_all_ia = get_all_standards_for_program(active_prog["id"])
        std_map_ia = {s["estandar_id"]: f"{s['estandar_codigo']} - {s['titulo']}" for s in std_all_ia}
        sel_s = st.selectbox("Selecciona Estándar a Consultar:", options=list(std_map_ia.keys()), format_func=lambda x: std_map_ia[x])
        s_obj = next(s for s in std_all_ia if s["estandar_id"] == sel_s)

        q_ia = st.text_area("Consulta de Auditoría para el Estándar seleccionado:", value="¿Qué 3 evidencias documentales indispensables solicitarás en la visita externa para este estándar?")
        if st.button("Consultar Auditor Virtual", type="primary"):
            with st.spinner("Analizando con el Auditor IA..."):
                ctx_ia = {
                    "codigo": s_obj["estandar_codigo"], "titulo": s_obj["titulo"],
                    "dimension": s_obj["dimension_nombre"], "factor": s_obj["factor_nombre"],
                    "criterio": s_obj["criterio_posgrado"], "estado": s_obj["estado_cumplimiento"],
                    "porcentaje": s_obj["porcentaje"], "justificacion": s_obj["justificacion"],
                    "evidencias": s_obj["evidencias_texto"]
                }
                res_ia = consultar_auditor_sgc(q_ia, ctx_ia)
                st.markdown(res_ia)


# --------------------------------------------------------------------------
# CASO 2: VISTA DEL RESPONSABLE DE PROGRAMA
# --------------------------------------------------------------------------
else:
    st.markdown(f"### 👨‍🏫 Panel del Responsable | Programa: **{active_prog['nombre']}** (`{active_prog['codigo']}`)")

    tab_eval_resp, tab_dash_resp, tab_lms_resp, tab_ia_resp, tab_rep_resp = st.tabs([
        "📋 Mi Matriz de Autoevaluación y Subida de Evidencias (34)",
        "📊 Dashboard y Radar SGC de Mi Programa",
        "🎓 Articulación Académica LMS",
        "🤖 Auditor Virtual de Acreditación (IA)",
        "📄 Mi Informe de Autoevaluación"
    ])

    # 1. Matriz de Autoevaluación y Subida de Archivos
    with tab_eval_resp:
        st.subheader("📋 Autoevaluación y Carga de Evidencias del Programa")
        st.caption("Actualiza el estado de los 34 estándares y sube los documentos sustentatorios (resoluciones, actas, sílabos, reportes Turnitin).")

        standards = get_all_standards_for_program(active_prog["id"])

        for est in standards:
            num = est["numero"]
            b_style = "badge-cumple" if est["estado_cumplimiento"] == "Cumple Plenamente" else (
                "badge-parcial" if est["estado_cumplimiento"] == "Cumple Parcial" else (
                    "badge-proceso" if est["estado_cumplimiento"] == "En Proceso" else "badge-nocumple"
                )
            )

            with st.expander(f"{est['estandar_codigo']}: {est['titulo']} | {est['estado_cumplimiento']} ({est['porcentaje']}%) | Archivos: {est['total_archivos']}"):
                st.markdown(f"""
                <div class="criterio-card">
                    <strong>📌 Criterio Oficial de Posgrado:</strong><br>
                    {est['criterio_posgrado']}
                </div>
                """, unsafe_allow_html=True)

                # Formulario de texto
                with st.form(f"form_resp_{num}"):
                    c1, c2, c3 = st.columns([1.2, 1, 1.2])
                    with c1:
                        new_est = st.selectbox(
                            "Estado de Cumplimiento:",
                            ["Cumple Plenamente", "Cumple Parcial", "En Proceso", "No Cumple"],
                            index=["Cumple Plenamente", "Cumple Parcial", "En Proceso", "No Cumple"].index(est["estado_cumplimiento"])
                        )
                    with c2:
                        new_p = st.slider("Porcentaje de Avance (%):", 0.0, 100.0, float(est["porcentaje"]), step=5.0)
                    with c3:
                        new_r = st.text_input("Responsable:", value=est["responsable"] or user["full_name"])

                    new_j = st.text_area("Justificación Técnica de Cumplimiento:", value=est["justificacion"], height=80)
                    new_et = st.text_area("Descripción de Evidencias / Enlaces:", value=est["evidencias_texto"], height=60)
                    new_pl = st.text_area("Plan de Mejora (si no cumple 100%):", value=est["plan_mejora"], height=60)

                    if st.form_submit_button("💾 Guardar Datos del Estándar", type="primary"):
                        update_standard_evaluation(active_prog["id"], est["estandar_id"], new_est, new_p, new_j, new_et, new_pl, new_r)
                        st.success("¡Datos guardados!")
                        st.rerun()

                st.markdown("---")
                # Subida de Archivos de Evidencia
                st.markdown(f"#### 📂 Archivos de Evidencia Digital para {est['estandar_codigo']}")
                uploaded_evid = st.file_uploader(
                    f"Subir evidencia para {est['estandar_codigo']} (PDF, DOCX, ZIP, PNG):",
                    type=["pdf", "docx", "xlsx", "zip", "png", "jpg"],
                    key=f"file_up_{num}"
                )
                if uploaded_evid is not None:
                    if st.button(f"📤 Confirmar Subida de '{uploaded_evid.name}'", key=f"btn_up_{num}"):
                        save_uploaded_evidence(active_prog["id"], est["estandar_id"], uploaded_evid, user["full_name"])
                        st.success(f"¡Archivo '{uploaded_evid.name}' subido y registrado exitosamente!")
                        st.rerun()

                # Lista de archivos ya subidos
                cur_files = get_standard_evidence_files(active_prog["id"], est["estandar_id"])
                if cur_files:
                    st.write("**Evidencias ya registradas:**")
                    for cf in cur_files:
                        fc_col1, fc_col2 = st.columns([4, 1])
                        with fc_col1:
                            st.markdown(f"📄 `{cf['nombre_archivo']}` ({round(cf['tamanio_bytes']/1024, 1)} KB) - Subido por **{cf['subido_por']}** ({cf['fecha_subida']})")
                        with fc_col2:
                            if st.button("🗑️ Eliminar", key=f"del_{cf['id']}"):
                                delete_evidence_file(cf["id"])
                                st.warning("Archivo eliminado.")
                                st.rerun()
                else:
                    st.caption("Aún no se han subido archivos de evidencia para este estándar.")

    # 2. Dashboard del Programa
    with tab_dash_resp:
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(f"<div class='kpi-box'><div class='kpi-number'>{promedio_global}%</div><div class='kpi-text'>Madurez SGC</div></div>", unsafe_allow_html=True)
        with r2:
            st.markdown(f"<div class='kpi-box'><div class='kpi-number' style='color:#059669;'>{kpis.get('plenamente', 0)} / 34</div><div class='kpi-text'>Cumplen Plenamente</div></div>", unsafe_allow_html=True)
        with r3:
            par_p = (kpis.get('parcial', 0) or 0) + (kpis.get('en_proceso', 0) or 0)
            st.markdown(f"<div class='kpi-box'><div class='kpi-number' style='color:#2563EB;'>{par_p} / 34</div><div class='kpi-text'>En Proceso / Parcial</div></div>", unsafe_allow_html=True)
        with r4:
            st.markdown(f"<div class='kpi-box'><div class='kpi-number' style='color:#DC2626;'>{kpis.get('no_cumple', 0)} / 34</div><div class='kpi-text'>Brechas Críticas</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_r_p, col_f_p = st.columns([1, 1.1])
        with col_r_p:
            st.subheader("🎯 Radar de Madurez por Dimensión")
            df_dim_p = pd.DataFrame(dimensiones_res)
            c_p = df_dim_p["nombre"].tolist()
            v_p = df_dim_p["promedio"].tolist()
            c_p_c = c_p + [c_p[0]]
            v_p_c = v_p + [v_p[0]]

            fig_rp = go.Figure()
            fig_rp.add_trace(go.Scatterpolar(r=v_p_c, theta=c_p_c, fill='toself', fillcolor='rgba(30, 58, 138, 0.25)', line=dict(color='#1E3A8A', width=3), name='Avance (%)'))
            fig_rp.add_trace(go.Scatterpolar(r=[80]*len(c_p_c), theta=c_p_c, line=dict(color='#DC2626', width=2, dash='dot'), name='Meta (80%)'))
            fig_rp.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=340, margin=dict(t=20, b=20, l=30, r=30))
            st.plotly_chart(fig_rp, use_container_width=True)

        with col_f_p:
            st.subheader("📊 Cumplimiento de los 12 Factores")
            df_fp = pd.DataFrame(factores_res)
            df_fp["color"] = df_fp["promedio"].apply(lambda p: "#059669" if p >= 80 else ("#2563EB" if p >= 60 else ("#EAB308" if p >= 40 else "#DC2626")))
            fig_fp = go.Figure(go.Bar(
                x=df_fp["promedio"], y=df_fp["codigo"] + ": " + df_fp["nombre"],
                orientation='h', marker=dict(color=df_fp["color"]),
                text=df_fp["promedio"].apply(lambda v: f"{v:.1f}%"), textposition='outside'
            ))
            fig_fp.add_vline(x=80, line_dash="dash", line_color="#DC2626", annotation_text="Meta 80%")
            fig_fp.update_layout(xaxis=dict(range=[0, 105]), yaxis=dict(autorange="reversed"), height=340, margin=dict(t=10, b=10, l=10, r=20))
            st.plotly_chart(fig_fp, use_container_width=True)

    # 3. Articulación LMS
    with tab_lms_resp:
        st.subheader("🎓 Articulación Académica del Programa en el LMS")
        c_data, t_data, d_data = get_lms_academic_data(active_prog["id"])

        sl1, sl2, sl3 = st.tabs(["📚 Cursos y Sílabos", "🔬 Tesis y Similitud Turnitin", "👨‍🏫 Plana Docente"])
        with sl1:
            df_c_r = pd.DataFrame(c_data)
            if not df_c_r.empty:
                st.dataframe(df_c_r[["codigo", "nombre", "ciclo", "creditos", "docente_nombre", "silabo_url"]], use_container_width=True, hide_index=True)
            else:
                st.info("Sin cursos.")
        with sl2:
            df_t_r = pd.DataFrame(t_data)
            if not df_t_r.empty:
                df_t_r["alerta"] = df_t_r["similitud_turnitin"].apply(lambda x: "🟢 Aceptable (≤20% CEI-UCV)" if x <= 20 else "🔴 Alerta (>20%)")
                st.dataframe(df_t_r[["estudiante_nombre", "titulo_tesis", "asesor_nombre", "porcentaje_avance", "similitud_turnitin", "alerta"]], use_container_width=True, hide_index=True)
            else:
                st.info("Sin proyectos de tesis.")
        with sl3:
            df_d_r = pd.DataFrame(d_data)
            if not df_d_r.empty:
                st.dataframe(df_d_r[["nombre", "grado_academico", "categoria_docente", "nivel_renacyt", "articulos_scopus_wos"]], use_container_width=True, hide_index=True)
            else:
                st.info("Sin docentes.")

    # 4. Auditor IA
    with tab_ia_resp:
        st.subheader("🤖 Consultoría con el Auditor Virtual IA (Gemini 3.5 Flash)")
        st_resp_list = get_all_standards_for_program(active_prog["id"])
        st_map_resp = {s["estandar_id"]: f"{s['estandar_codigo']} - {s['titulo']}" for s in st_resp_list}
        sel_s_r = st.selectbox("Selecciona Estándar a Consultar:", options=list(st_map_resp.keys()), format_func=lambda x: st_map_resp[x], key="sel_s_resp")
        s_obj_r = next(s for s in st_resp_list if s["estandar_id"] == sel_s_r)

        q_r = st.text_area("Consulta al Auditor Virtual:", value="Formula un Plan de Mejora SMART para cerrar la brecha de este estándar.", key="q_resp")
        if st.button("Consultar Auditor Virtual", type="primary", key="btn_ia_resp"):
            with st.spinner("Analizando con el Auditor IA..."):
                ctx_r = {
                    "codigo": s_obj_r["estandar_codigo"], "titulo": s_obj_r["titulo"],
                    "dimension": s_obj_r["dimension_nombre"], "factor": s_obj_r["factor_nombre"],
                    "criterio": s_obj_r["criterio_posgrado"], "estado": s_obj_r["estado_cumplimiento"],
                    "porcentaje": s_obj_r["porcentaje"], "justificacion": s_obj_r["justificacion"],
                    "evidencias": s_obj_r["evidencias_texto"]
                }
                res_r = consultar_auditor_sgc(q_r, ctx_r)
                st.markdown(res_r)

    # 5. Informe del Programa
    with tab_rep_resp:
        st.subheader("📄 Informe de Autoevaluación del Programa")
        st.write(f"Programa: **{active_prog['nombre']}** | Periodo: **{active_prog['periodo_acreditacion']}**")
        st.markdown(f"* **Madurez SGC Alcanzada:** **{promedio_global}%**")
        st.markdown(f"* **Estándares Plenamente Cumplidos:** **{kpis.get('plenamente', 0)} de 34**")

        st_all_rep = get_all_standards_for_program(active_prog["id"])
        df_rep_p = pd.DataFrame(st_all_rep)
        df_pl_p = df_rep_p[df_rep_p["plan_mejora"].str.len() > 5][["estandar_codigo", "titulo", "estado_cumplimiento", "porcentaje", "plan_mejora", "responsable"]]
        df_pl_p.columns = ["Código", "Estándar", "Estado Actual", "% Avance", "Plan de Acción de Mejora", "Responsable"]
        st.dataframe(df_pl_p, use_container_width=True, hide_index=True)
