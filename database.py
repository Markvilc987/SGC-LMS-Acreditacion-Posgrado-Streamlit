"""
database.py
Base de datos SQLite del Sistema de Gestión de la Calidad (SGC) y LMS de Posgrado.
Implementa el modelo oficial de 4 Dimensiones, 12 Factores y 34 Estándares para
la autoevaluación, aseguramiento de la calidad y acreditación de Maestrías y Doctorados.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "sgc_posgrado.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # 1. TABLAS ESTRUCTURALES DEL MODELO DE CALIDAD (SGC / SINEACE / SUNEDU)
    c.execute("""
    CREATE TABLE IF NOT EXISTS sgc_dimensiones (
        id INTEGER PRIMARY KEY,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        descripcion TEXT
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS sgc_factores (
        id INTEGER PRIMARY KEY,
        dimension_id INTEGER NOT NULL REFERENCES sgc_dimensiones(id) ON DELETE CASCADE,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS sgc_estandares (
        id INTEGER PRIMARY KEY,
        factor_id INTEGER NOT NULL REFERENCES sgc_factores(id) ON DELETE CASCADE,
        numero INTEGER NOT NULL UNIQUE,
        codigo TEXT NOT NULL UNIQUE,
        titulo TEXT NOT NULL,
        criterio_posgrado TEXT NOT NULL,
        peso_ponderado REAL DEFAULT 1.00
    );
    """)

    # 2. TABLAS OPERATIVAS DEL PROGRAMA DE POSGRADO Y AUTOEVALUACIÓN
    c.execute("""
    CREATE TABLE IF NOT EXISTS sgc_programas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        nivel TEXT NOT NULL CHECK(nivel IN ('Maestría', 'Doctorado')),
        facultad TEXT NOT NULL,
        director TEXT NOT NULL,
        mision TEXT DEFAULT '',
        vision TEXT DEFAULT '',
        periodo_acreditacion TEXT DEFAULT '2026-I',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS sgc_autoevaluaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        programa_id INTEGER NOT NULL REFERENCES sgc_programas(id) ON DELETE CASCADE,
        estandar_id INTEGER NOT NULL REFERENCES sgc_estandares(id) ON DELETE CASCADE,
        estado_cumplimiento TEXT DEFAULT 'En Proceso' CHECK(estado_cumplimiento IN ('No Cumple', 'En Proceso', 'Cumple Parcial', 'Cumple Plenamente')),
        porcentaje REAL DEFAULT 50.0,
        justificacion TEXT DEFAULT '',
        evidencias TEXT DEFAULT '',
        plan_mejora TEXT DEFAULT '',
        responsable TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(programa_id, estandar_id)
    );
    """)

    # 3. TABLAS DE ARTICULACIÓN LMS DE POSGRADO
    c.execute("""
    CREATE TABLE IF NOT EXISTS lms_cursos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        programa_id INTEGER NOT NULL REFERENCES sgc_programas(id) ON DELETE CASCADE,
        codigo TEXT NOT NULL,
        nombre TEXT NOT NULL,
        ciclo TEXT NOT NULL,
        creditos INTEGER NOT NULL,
        docente_nombre TEXT NOT NULL,
        silabo_url TEXT DEFAULT '',
        enfoque_competencias TEXT DEFAULT 'Implementado en LMS'
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS lms_tesis_seguimiento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        programa_id INTEGER NOT NULL REFERENCES sgc_programas(id) ON DELETE CASCADE,
        estudiante_nombre TEXT NOT NULL,
        titulo_tesis TEXT NOT NULL,
        linea_investigacion TEXT NOT NULL,
        asesor_nombre TEXT NOT NULL,
        porcentaje_avance REAL DEFAULT 30.0,
        similitud_turnitin REAL DEFAULT 12.0,
        comite_etica_aprobado INTEGER DEFAULT 1,
        articulo_publicado INTEGER DEFAULT 0
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS lms_docentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        programa_id INTEGER NOT NULL REFERENCES sgc_programas(id) ON DELETE CASCADE,
        nombre TEXT NOT NULL,
        grado_academico TEXT NOT NULL,
        categoria_docente TEXT NOT NULL,
        es_renacyt INTEGER DEFAULT 1,
        nivel_renacyt TEXT DEFAULT 'Nivel III',
        codigo_orcid TEXT DEFAULT '',
        articulos_scopus_wos INTEGER DEFAULT 5
    );
    """)

    conn.commit()

    # Poblar dimensiones, factores y estándares si están vacías
    c.execute("SELECT COUNT(*) as cnt FROM sgc_dimensiones")
    if c.fetchone()["cnt"] == 0:
        seed_sgc_framework(conn)

    # Poblar programa de posgrado demo y autoevaluación inicial si está vacía
    c.execute("SELECT COUNT(*) as cnt FROM sgc_programas")
    if c.fetchone()["cnt"] == 0:
        seed_demo_program(conn)

    conn.close()


def seed_sgc_framework(conn):
    c = conn.cursor()

    # 1. Dimensiones
    dimensiones = [
        (1, 'DIM-01', 'Gestión Estratégica', 'Evalúa cómo se planifica y conduce el programa de posgrado usando información para la mejora continua.'),
        (2, 'DIM-02', 'Formación Integral', 'Eje central que evalúa enseñanza-aprendizaje, gestión docente, seguimiento estudiantil, I+D+i y RSU.'),
        (3, 'DIM-03', 'Soporte Institucional', 'Evalúa la gestión de recursos, infraestructura tecnológica, bibliotecas científicas y bienestar.'),
        (4, 'DIM-04', 'Resultados', 'Verificación del logro de competencias del perfil de graduado y cumplimiento de objetivos educacionales.')
    ]
    c.executemany("INSERT INTO sgc_dimensiones (id, codigo, nombre, descripcion) VALUES (?, ?, ?, ?);", dimensiones)

    # 2. Factores
    factores = [
        (1, 1, 'FAC-01', 'Planificación del programa de estudios'),
        (2, 1, 'FAC-02', 'Gestión del perfil de egreso'),
        (3, 1, 'FAC-03', 'Aseguramiento de la calidad'),
        (4, 2, 'FAC-04', 'Proceso enseñanza-aprendizaje'),
        (5, 2, 'FAC-05', 'Gestión de los docentes'),
        (6, 2, 'FAC-06', 'Seguimiento a estudiantes'),
        (7, 2, 'FAC-07', 'Investigación, desarrollo tecnológico e innovación'),
        (8, 2, 'FAC-08', 'Responsabilidad social universitaria'),
        (9, 3, 'FAC-09', 'Servicios de bienestar'),
        (10, 3, 'FAC-10', 'Infraestructura y soporte'),
        (11, 3, 'FAC-11', 'Recursos humanos'),
        (12, 4, 'FAC-12', 'Verificación del perfil de egreso')
    ]
    c.executemany("INSERT INTO sgc_factores (id, dimension_id, codigo, nombre) VALUES (?, ?, ?, ?);", factores)

    # 3. Estándares
    estandares = [
        # Factor 1
        (1, 1, 1, 'EST-01', 'Propósitos articulados', 'Los propósitos de la maestría/doctorado están definidos y alineados con la misión institucional.'),
        (2, 1, 2, 'EST-02', 'Participación de los grupos de interés', 'Mecanismos activos con comités consultivos y empleadores para asegurar la pertinencia de la oferta de posgrado.'),
        (3, 1, 3, 'EST-03', 'Revisión periódica y participativa de las políticas y objetivos', 'Revisión periódica que permite reorientar metas, planes de acción y recursos del programa.'),
        (4, 1, 4, 'EST-04', 'Sostenibilidad', 'Gestión eficiente del presupuesto y recursos financieros que garantizan la continuidad del posgrado.'),
        # Factor 2
        (5, 2, 5, 'EST-05', 'Pertinencia del perfil de egreso', 'El perfil de graduado considera demandas científicas, profesionales y expectativas de grupos de interés.'),
        (6, 2, 6, 'EST-06', 'Revisión del perfil de egreso', 'Revisión periódica (máximo cada 3 años) del perfil del graduado de maestría o doctorado.'),
        # Factor 3
        (7, 3, 7, 'EST-07', 'Sistema de gestión de la calidad (SGC)', 'El programa cuenta con un SGC implementado y eficaz para la mejora continua.'),
        (8, 3, 8, 'EST-08', 'Planes de mejora', 'Se definen, implementan y monitorean planes de mejora con base en autoevaluaciones y auditorías.'),
        # Factor 4
        (9, 4, 9, 'EST-09', 'Plan de estudios', 'Asegura una formación actualizada, flexible y acorde al nivel de maestría o doctorado.'),
        (10, 4, 10, 'EST-10', 'Características del plan de estudios', 'Organización curricular, créditos, sílabos estandarizados y distribución de horas académicas y de investigación.'),
        (11, 4, 11, 'EST-11', 'Enfoque por competencias', 'Garantiza que el proceso de enseñanza-aprendizaje y las rúbricas en el LMS desarrollen las competencias.'),
        (12, 4, 12, 'EST-12', 'Articulación con I+D+i y responsabilidad social', 'El proceso formativo articula las asignaturas con líneas de investigación y transferencia a la sociedad.'),
        (13, 4, 13, 'EST-13', 'Movilidad', 'Mecanismos de movilidad nacional e internacional para estudiantes y docentes de posgrado.'),
        # Factor 5
        (14, 5, 14, 'EST-14', 'Selección, evaluación, capacitación y perfeccionamiento', 'Procesos transparentes de selección y evaluación 360° del desempeño docente en posgrado.'),
        (15, 5, 15, 'EST-15', 'Plana docente adecuada', 'Docentes con grado igual o superior al programa que dictan, experiencia profesional y registro RENACYT.'),
        (16, 5, 16, 'EST-16', 'Reconocimiento de las actividades de labor docente', 'Reconocimiento e incentivos a la producción científica, asesoría de tesis y buenas prácticas pedagógicas.'),
        (17, 5, 17, 'EST-17', 'Plan de desarrollo académico del docente', 'Ejecución de programas de capacitación continua en investigación y uso del LMS.'),
        # Factor 6
        (18, 6, 18, 'EST-18', 'Admisión al programa de estudios', 'Proceso de admisión riguroso que evalúa competencias previas e investigación.'),
        (19, 6, 19, 'EST-19', 'Nivelación de ingresantes', 'Programas de inducción o nivelación en metodología científica y herramientas digitales.'),
        (20, 6, 20, 'EST-20', 'Seguimiento al desempeño de los estudiantes', 'Sistema de tutoría y alertas tempranas para asegurar la permanencia y avance en tesis.'),
        (21, 6, 21, 'EST-21', 'Actividades extracurriculares', 'Seminarios internacionales, coloquios doctorales y talleres de escritura científica.'),
        # Factor 7
        (22, 7, 22, 'EST-22', 'Gestión y calidad de la I+D+i realizada por docentes', 'Vigilancia ética, originalidad y rigor científico en proyectos de investigación docente.'),
        (23, 7, 23, 'EST-23', 'Investigación para la obtención del grado', 'Asegura el rigor científico, asesoría calificada, comité de ética y control de similitud en tesis de grado.'),
        (24, 7, 24, 'EST-24', 'Publicaciones de los resultados de I+D+i', 'Fomento y registro de artículos publicados en revistas indizadas (Scopus, WoS, SciELO) y patentes.'),
        # Factor 8
        (25, 8, 25, 'EST-25', 'Responsabilidad social', 'Acciones de transferencia de conocimiento e impacto en el entorno vinculadas al posgrado.'),
        (26, 8, 26, 'EST-26', 'Implementación de políticas ambientales', 'Cumplimiento de estándares de ecoeficiencia y sostenibilidad ambiental.'),
        # Factor 9
        (27, 9, 27, 'EST-27', 'Bienestar', 'Acceso de los estudiantes y docentes de posgrado a servicios de bienestar y soporte.'),
        # Factor 10
        (28, 10, 28, 'EST-28', 'Equipamiento y uso de la infraestructura', 'Infraestructura física y tecnológica (LMS, software estadístico/cualitativo) adecuada para el posgrado.'),
        (29, 10, 29, 'EST-29', 'Mantenimiento de la infraestructura', 'Programa de mantenimiento preventivo y actualización de servidores, plataformas y laboratorios.'),
        (30, 10, 30, 'EST-30', 'Sistema de información y comunicación', 'Sistema auditable que gestiona información académica, administrativa y de calidad en tiempo real.'),
        (31, 10, 31, 'EST-31', 'Centros de información y referencia', 'Acceso a bibliotecas virtuales, bases de datos científicas de alto impacto y repositorio institucional.'),
        # Factor 11
        (32, 11, 32, 'EST-32', 'Recursos humanos para la gestión del programa', 'Personal directivo, coordinador y administrativo calificado para la gestión de posgrado.'),
        # Factor 12
        (33, 12, 33, 'EST-33', 'Logro de competencias', 'Evaluación y verificación de que los maestrandos/doctorandos alcanzan las competencias al graduarse.'),
        (34, 12, 34, 'EST-34', 'Seguimiento a egresados y objetivos educacionales', 'Monitoreo de la inserción laboral, impacto profesional y logro de objetivos educacionales de los graduados.')
    ]
    c.executemany("""
    INSERT INTO sgc_estandares (id, factor_id, numero, codigo, titulo, criterio_posgrado)
    VALUES (?, ?, ?, ?, ?, ?);
    """, estandares)

    conn.commit()


def seed_demo_program(conn):
    c = conn.cursor()

    # 1. Programa de Doctorado Demo
    c.execute("""
    INSERT INTO sgc_programas (codigo, nombre, nivel, facultad, director, mision, vision, periodo_acreditacion)
    VALUES ('DOC-GPG', 'Doctorado en Gestión Pública y Gobernabilidad', 'Doctorado', 'Escuela de Posgrado', 'Dr. Juan Marcos Vilchez-Canchari', 
            'Formar investigadores de alto nivel capaces de generar conocimiento científico para transformar las políticas públicas.',
            'Ser un programa doctoral líder en Latinoamérica por su rigor científico e impacto social.', '2026-I');
    """)
    prog_id = c.lastrowid

    # 2. Inicializar los 34 estándares con valores realistas de autoevaluación
    c.execute("SELECT id, numero FROM sgc_estandares ORDER BY numero ASC;")
    estandares = c.fetchall()

    eval_data = []
    for est in estandares:
        num = est["numero"]
        # Asignar estados realistas para tener un semáforo variado
        if num in [1, 2, 7, 9, 10, 15, 23, 28, 30, 31]:
            estado = "Cumple Plenamente"
            pct = 100.0
            just = f"El programa cuenta con evidencia documental completa, resoluciones de consejo y procesos digitalizados en el LMS para el Estándar {num}."
            evid = f"Resolución Decanal N° 142-2025; Actas de Comité Consultivo; Reporte LMS 2026."
            plan = "Mantenimiento del estándar y auditoría semestral."
        elif num in [4, 5, 11, 14, 16, 20, 22, 24, 33]:
            estado = "Cumple Parcial"
            pct = 75.0
            just = f"Existe implementación del 75% en las asignaturas y plataformas, con auditorías internas en curso para el Estándar {num}."
            evid = f"Sílabos por competencias; Registro de Asesorías en Plataforma; Reporte Turnitin."
            plan = f"Capacitar al 100% de la plana docente en el nuevo módulo de evaluación de competencias del LMS."
        elif num in [3, 6, 8, 12, 13, 17, 19, 21, 25, 27, 32]:
            estado = "En Proceso"
            pct = 45.0
            just = f"Se ha formulado la política y directiva interna, encontrándose en fase de recolección de evidencias para el Estándar {num}."
            evid = f"Proyecto de Directiva 2026; Encuestas de satisfacción a maestrandos."
            plan = f"Ejecutar el plan de acción aprobado en el Comité de Calidad antes de julio 2026."
        else: # 18, 26, 29, 34
            estado = "No Cumple"
            pct = 15.0
            just = f"Brecha identificada en la última autoevaluación institucional respecto al criterio de posgrado del Estándar {num}."
            evid = f"Informe de Auditoría Interna N° 03-2025-SGC."
            plan = f"Implementar el sistema de trazabilidad de graduados y seguimiento de impacto laboral."

        eval_data.append((prog_id, est["id"], estado, pct, just, evid, plan, "Comité de Calidad de Posgrado"))

    c.executemany("""
    INSERT INTO sgc_autoevaluaciones (programa_id, estandar_id, estado_cumplimiento, porcentaje, justificacion, evidencias, plan_mejora, responsable)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, eval_data)

    # 3. Cursos de Posgrado vinculados al LMS
    cursos = [
        (prog_id, 'DOC-101', 'Epistemología y Diseño de la Investigación Científica', 'Ciclo I', 5, 'Dr. Roberto Sánchez', 'https://lms.posgrado.edu.pe/cursos/doc101'),
        (prog_id, 'DOC-102', 'Políticas Públicas y Teoría del Estado', 'Ciclo I', 4, 'Dra. Elena Vargas', 'https://lms.posgrado.edu.pe/cursos/doc102'),
        (prog_id, 'DOC-201', 'Seminario de Tesis I (Modelado Estadístico y Econometría)', 'Ciclo II', 6, 'Dr. Juan Marcos Vilchez', 'https://lms.posgrado.edu.pe/cursos/doc201'),
        (prog_id, 'DOC-301', 'Seminario de Tesis II (Redacción de Artículo Scopus/WoS)', 'Ciclo III', 6, 'Dr. Alberto Benavides', 'https://lms.posgrado.edu.pe/cursos/doc301'),
        (prog_id, 'DOC-401', 'Seminario de Tesis III (Defensa y Sustentación Doctoral)', 'Ciclo IV', 8, 'Dr. Juan Marcos Vilchez', 'https://lms.posgrado.edu.pe/cursos/doc401')
    ]
    c.executemany("""
    INSERT INTO lms_cursos (programa_id, codigo, nombre, ciclo, creditos, docente_nombre, silabo_url)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, cursos)

    # 4. Seguimiento de Tesis
    tesistas = [
        (prog_id, 'Mag. Carlos Paredes', 'Modelo de Inteligencia Artificial para la Gestión de Contrataciones Estatales', 'Gestión Pública y Tecnología', 'Dr. Juan Marcos Vilchez', 85.0, 8.5, 1, 1),
        (prog_id, 'Mag. Patricia Morales', 'Impacto del Canon Minero en la Eficiencia del Gasto Social Municipal', 'Finanzas Públicas y Descentralización', 'Dr. Alberto Benavides', 70.0, 11.2, 1, 0),
        (prog_id, 'Mag. Daniel Vega', 'Gobernanza Digital y Reducción de la Burocracia en Gobiernos Regionales', 'Políticas Públicas', 'Dra. Elena Vargas', 45.0, 14.0, 1, 0),
        (prog_id, 'Mag. Lucía Alarcón', 'Eficiencia Hospitalaria Comparada en Redes de Salud Pública', 'Gestión en Salud Pública', 'Dr. Juan Marcos Vilchez', 95.0, 6.0, 1, 1)
    ]
    c.executemany("""
    INSERT INTO lms_tesis_seguimiento (programa_id, estudiante_nombre, titulo_tesis, linea_investigacion, asesor_nombre, porcentaje_avance, similitud_turnitin, comite_etica_aprobado, articulo_publicado)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, tesistas)

    # 5. Docentes RENACYT
    docentes = [
        (prog_id, 'Dr. Juan Marcos Vilchez-Canchari', 'Doctor en Ingeniería / PhD', 'Principal', 1, 'Nivel I (Distinguido)', '0000-0002-1825-0097', 18),
        (prog_id, 'Dr. Alberto Benavides', 'Doctor en Economía', 'Principal', 1, 'Nivel II', '0000-0003-4122-9012', 12),
        (prog_id, 'Dra. Elena Vargas', 'Doctora en Ciencias Políticas', 'Asociada', 1, 'Nivel III', '0000-0001-8841-5523', 8),
        (prog_id, 'Dr. Roberto Sánchez', 'Doctor en Filosofía y Epistemología', 'Principal', 1, 'Nivel IV', '0000-0002-7711-3091', 6)
    ]
    c.executemany("""
    INSERT INTO lms_docentes (programa_id, nombre, grado_academico, categoria_docente, es_renacyt, nivel_renacyt, codigo_orcid, articulos_scopus_wos)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, docentes)

    conn.commit()


# ==========================================
# CONSULTAS PARA EL DASHBOARD DE ACREDITACIÓN
# ==========================================

def get_program_summary(prog_id):
    conn = get_connection()
    c = conn.cursor()

    # Promedio global ponderado
    c.execute("""
    SELECT 
        AVG(a.porcentaje) as promedio_global,
        SUM(CASE WHEN a.estado_cumplimiento = 'Cumple Plenamente' THEN 1 ELSE 0 END) as plenamente,
        SUM(CASE WHEN a.estado_cumplimiento = 'Cumple Parcial' THEN 1 ELSE 0 END) as parcial,
        SUM(CASE WHEN a.estado_cumplimiento = 'En Proceso' THEN 1 ELSE 0 END) as en_proceso,
        SUM(CASE WHEN a.estado_cumplimiento = 'No Cumple' THEN 1 ELSE 0 END) as no_cumple
    FROM sgc_autoevaluaciones a
    WHERE a.programa_id = ?;
    """, (prog_id,))
    kpis = dict(c.fetchone())

    # Promedio por dimensión (4 dimensiones)
    c.execute("""
    SELECT 
        d.id, d.codigo, d.nombre, AVG(a.porcentaje) as promedio,
        COUNT(e.id) as total_estandares
    FROM sgc_dimensiones d
    JOIN sgc_factores f ON d.id = f.dimension_id
    JOIN sgc_estandares e ON f.id = e.factor_id
    LEFT JOIN sgc_autoevaluaciones a ON e.id = a.estandar_id AND a.programa_id = ?
    GROUP BY d.id
    ORDER BY d.id ASC;
    """, (prog_id,))
    dimensiones_res = [dict(r) for r in c.fetchall()]

    # Promedio por factor (12 factores)
    c.execute("""
    SELECT 
        f.id, f.codigo, f.nombre, d.nombre as dimension_nombre, AVG(a.porcentaje) as promedio,
        COUNT(e.id) as total_estandares
    FROM sgc_factores f
    JOIN sgc_dimensiones d ON f.dimension_id = d.id
    JOIN sgc_estandares e ON f.id = e.factor_id
    LEFT JOIN sgc_autoevaluaciones a ON e.id = a.estandar_id AND a.programa_id = ?
    GROUP BY f.id
    ORDER BY f.id ASC;
    """, (prog_id,))
    factores_res = [dict(r) for r in c.fetchall()]

    conn.close()
    return kpis, dimensiones_res, factores_res


def get_all_standards_for_program(prog_id, filter_dimension=None, filter_factor=None):
    conn = get_connection()
    c = conn.cursor()

    query = """
    SELECT 
        e.id as estandar_id, e.numero, e.codigo as estandar_codigo, e.titulo, e.criterio_posgrado,
        f.codigo as factor_codigo, f.nombre as factor_nombre,
        d.codigo as dimension_codigo, d.nombre as dimension_nombre,
        COALESCE(a.estado_cumplimiento, 'No Cumple') as estado_cumplimiento,
        COALESCE(a.porcentaje, 0.0) as porcentaje,
        COALESCE(a.justificacion, '') as justificacion,
        COALESCE(a.evidencias, '') as evidencias,
        COALESCE(a.plan_mejora, '') as plan_mejora,
        COALESCE(a.responsable, '') as responsable
    FROM sgc_estandares e
    JOIN sgc_factores f ON e.factor_id = f.id
    JOIN sgc_dimensiones d ON f.dimension_id = d.id
    LEFT JOIN sgc_autoevaluaciones a ON e.id = a.estandar_id AND a.programa_id = ?
    WHERE 1=1
    """
    params = [prog_id]

    if filter_dimension and filter_dimension != "Todas":
        query += " AND d.nombre = ?"
        params.append(filter_dimension)
    if filter_factor and filter_factor != "Todos":
        query += " AND f.nombre = ?"
        params.append(filter_factor)

    query += " ORDER BY e.numero ASC;"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def update_standard_evaluation(prog_id, estandar_id, estado, pct, just, evid, plan, resp):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO sgc_autoevaluaciones (programa_id, estandar_id, estado_cumplimiento, porcentaje, justificacion, evidencias, plan_mejora, responsable, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(programa_id, estandar_id) DO UPDATE SET
        estado_cumplimiento = excluded.estado_cumplimiento,
        porcentaje = excluded.porcentaje,
        justificacion = excluded.justificacion,
        evidencias = excluded.evidencias,
        plan_mejora = excluded.plan_mejora,
        responsable = excluded.responsable,
        updated_at = CURRENT_TIMESTAMP;
    """, (prog_id, estandar_id, estado, pct, just, evid, plan, resp))
    conn.commit()
    conn.close()


def get_lms_academic_data(prog_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM lms_cursos WHERE programa_id = ? ORDER BY ciclo ASC;", (prog_id,))
    cursos = [dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM lms_tesis_seguimiento WHERE programa_id = ? ORDER BY porcentaje_avance DESC;", (prog_id,))
    tesis = [dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM lms_docentes WHERE programa_id = ? ORDER BY articulos_scopus_wos DESC;", (prog_id,))
    docentes = [dict(r) for r in c.fetchall()]

    conn.close()
    return cursos, tesis, docentes
