"""
database.py
Base de datos SQLite del Sistema de Gestión de la Calidad (SGC) y LMS de Posgrado.
Soporta:
  1. 4 Dimensiones, 12 Factores y 34 Estándares (SINEACE / SUNEDU)
  2. Múltiples Programas de Posgrado (Doctorados y Maestrías)
  3. Control de Acceso por Roles (RBAC):
     - Administrador General: Vista global de todos los programas, métricas comparativas y gestión.
     - Responsables de Programa: Acceso específico a su programa para autoevaluar y subir evidencias.
  4. Repositorio de Evidencias Digitales con subida y almacenamiento de archivos.
"""

import sqlite3
import hashlib
import os
import shutil
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "sgc_posgrado.db")
EVIDENCIAS_DIR = os.path.join(os.path.dirname(__file__), "evidencias")
os.makedirs(EVIDENCIAS_DIR, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def hash_password(password: str) -> str:
    salt = "SGC_Posgrado_Salt_2026_Secure"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # 1. TABLAS ESTRUCTURALES DEL MODELO DE CALIDAD (4 DIMENSIONES, 12 FACTORES, 34 ESTÁNDARES)
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

    # 2. TABLA DE PROGRAMAS DE POSGRADO
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

    # 3. TABLA DE USUARIOS Y ROLES (ADMINISTRADOR vs. RESPONSABLES DE PROGRAMA)
    c.execute("""
    CREATE TABLE IF NOT EXISTS sgc_usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'responsable')),
        programa_id INTEGER REFERENCES sgc_programas(id) ON DELETE SET NULL,
        email TEXT DEFAULT '',
        cargo TEXT DEFAULT '',
        avatar TEXT DEFAULT '👤',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. TABLA DE AUTOEVALUACIÓN POR PROGRAMA Y ESTÁNDAR
    c.execute("""
    CREATE TABLE IF NOT EXISTS sgc_autoevaluaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        programa_id INTEGER NOT NULL REFERENCES sgc_programas(id) ON DELETE CASCADE,
        estandar_id INTEGER NOT NULL REFERENCES sgc_estandares(id) ON DELETE CASCADE,
        estado_cumplimiento TEXT DEFAULT 'En Proceso' CHECK(estado_cumplimiento IN ('No Cumple', 'En Proceso', 'Cumple Parcial', 'Cumple Plenamente')),
        porcentaje REAL DEFAULT 50.0,
        justificacion TEXT DEFAULT '',
        evidencias_texto TEXT DEFAULT '',
        plan_mejora TEXT DEFAULT '',
        responsable TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(programa_id, estandar_id)
    );
    """)

    # 5. TABLA DE ARCHIVOS DE EVIDENCIAS SUBIDOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS sgc_evidencias_archivos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        programa_id INTEGER NOT NULL REFERENCES sgc_programas(id) ON DELETE CASCADE,
        estandar_id INTEGER NOT NULL REFERENCES sgc_estandares(id) ON DELETE CASCADE,
        nombre_archivo TEXT NOT NULL,
        ruta_archivo TEXT NOT NULL,
        tamanio_bytes INTEGER DEFAULT 0,
        subido_por TEXT NOT NULL,
        fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. TABLAS DE ARTICULACIÓN LMS DE POSGRADO
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

    # Poblar el marco SGC si está vacío
    c.execute("SELECT COUNT(*) as cnt FROM sgc_dimensiones")
    if c.fetchone()["cnt"] == 0:
        seed_sgc_framework(conn)

    # Poblar programas y usuarios si están vacíos
    c.execute("SELECT COUNT(*) as cnt FROM sgc_programas")
    if c.fetchone()["cnt"] == 0:
        seed_multi_programs_and_users(conn)

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


def seed_multi_programs_and_users(conn):
    c = conn.cursor()
    pwd = hash_password("clave123")

    # 1. Crear Programas Oficiales de Posgrado de la Universidad César Vallejo (UCV)
    programas = [
        ('DOC-GPG-UCV', 'Doctorado en Gestión Pública y Gobernabilidad', 'Doctorado', 'Escuela de Posgrado UCV', 'Dr. Juan Marcos Vilchez-Canchari', '2026-I'),
        ('DOC-EDU-UCV', 'Doctorado en Educación', 'Doctorado', 'Escuela de Posgrado UCV', 'Dra. Elena Vargas Morales', '2026-I'),
        ('DOC-ADM-UCV', 'Doctorado en Administración', 'Doctorado', 'Escuela de Posgrado UCV', 'Dr. Roberto Sánchez Romero', '2026-I'),
        ('DOC-DER-UCV', 'Doctorado en Derecho', 'Doctorado', 'Escuela de Posgrado UCV', 'Dr. Alberto Benavides Ruiz', '2026-I'),
        ('MAE-GP-UCV', 'Maestría en Gestión Pública', 'Maestría', 'Escuela de Posgrado UCV', 'Mag. Carlos Mendoza Dávila', '2026-I'),
        ('MAE-MBA-UCV', 'Maestría en Administración de Negocios - MBA', 'Maestría', 'Escuela de Posgrado UCV', 'Mag. Ricardo Paredes Campos', '2026-I'),
        ('MAE-MDU-UCV', 'Maestría en Docencia Universitaria', 'Maestría', 'Escuela de Posgrado UCV', 'Dra. Patricia Morales Soto', '2026-I'),
        ('MAE-MSP-UCV', 'Maestría en Salud Pública', 'Maestría', 'Escuela de Posgrado UCV', 'Dra. Lucía Alarcón Medina', '2026-I')
    ]

    prog_ids = {}
    for cod, nom, niv, fac, dir_nom, per in programas:
        c.execute("""
        INSERT INTO sgc_programas (codigo, nombre, nivel, facultad, director, periodo_acreditacion)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (cod, nom, niv, fac, dir_nom, per))
        prog_ids[cod] = c.lastrowid

    # 2. Crear Usuarios UCV (Administrador General de Calidad UCV + Responsables por Programa)
    # Admin General UCV
    c.execute("""
    INSERT INTO sgc_usuarios (username, password_hash, full_name, role, programa_id, email, cargo, avatar)
    VALUES ('admin_ucv', ?, 'Dr. Carlos Mendoza Dávila', 'admin', NULL, 'calidad.posgrado@ucv.edu.pe', 'Director de Aseguramiento de la Calidad - Escuela de Posgrado UCV', '🏛️');
    """, (pwd,))

    # Responsables de Programa UCV
    responsables = [
        ('jvilchez', pwd, 'Dr. Juan Marcos Vilchez-Canchari', 'responsable', prog_ids['DOC-GPG-UCV'], 'jvilchezca@ucv.edu.pe', 'Coordinador del Doctorado en Gestión Pública y Gobernabilidad', '👨‍🏫'),
        ('evargas', pwd, 'Dra. Elena Vargas Morales', 'responsable', prog_ids['DOC-EDU-UCV'], 'evargasm@ucvvirtual.edu.pe', 'Coordinadora del Doctorado en Educación', '👩‍🏫'),
        ('rsanchez', pwd, 'Dr. Roberto Sánchez Romero', 'responsable', prog_ids['DOC-ADM-UCV'], 'rsanchezr@ucvvirtual.edu.pe', 'Coordinador del Doctorado en Administración', '👨‍💼'),
        ('abenavides', pwd, 'Dr. Alberto Benavides Ruiz', 'responsable', prog_ids['DOC-DER-UCV'], 'abenavidesr@ucvvirtual.edu.pe', 'Coordinador del Doctorado en Derecho', '👨‍⚖️'),
        ('cmendoza', pwd, 'Mag. Carlos Mendoza Dávila', 'responsable', prog_ids['MAE-GP-UCV'], 'cmendozad@ucvvirtual.edu.pe', 'Coordinador de la Maestría en Gestión Pública', '👨‍💼'),
        ('rparedes', pwd, 'Mag. Ricardo Paredes Campos', 'responsable', prog_ids['MAE-MBA-UCV'], 'rparedesc@ucvvirtual.edu.pe', 'Director de la Maestría MBA UCV', '💼'),
        ('pmorales', pwd, 'Dra. Patricia Morales Soto', 'responsable', prog_ids['MAE-MDU-UCV'], 'pmoraless@ucvvirtual.edu.pe', 'Coordinadora de la Maestría en Docencia Universitaria', '👩‍🏫'),
        ('lalarcon', pwd, 'Dra. Lucía Alarcón Medina', 'responsable', prog_ids['MAE-MSP-UCV'], 'lalarconm@ucvvirtual.edu.pe', 'Coordinadora de la Maestría en Salud Pública', '👩‍⚕️')
    ]

    c.executemany("""
    INSERT INTO sgc_usuarios (username, password_hash, full_name, role, programa_id, email, cargo, avatar)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, responsables)

    # 3. Inicializar autoevaluaciones para cada uno de los 4 programas
    c.execute("SELECT id, numero FROM sgc_estandares ORDER BY numero ASC;")
    estandares = c.fetchall()

    for cod, p_id in prog_ids.items():
        eval_data = []
        for est in estandares:
            num = est["numero"]
            # Variaciones en los datos para que cada programa tenga métricas distintas
            if (num + p_id) % 4 == 0:
                estado = "Cumple Plenamente"
                pct = 100.0
                just = f"Evidencias auditadas y aprobadas por el Comité de Calidad del programa {cod}."
                plan = "Mantenimiento preventivo de evidencias."
            elif (num + p_id) % 3 == 0:
                estado = "Cumple Parcial"
                pct = 75.0
                just = f"En proceso de implementación curricular en el LMS para el programa {cod}."
                plan = "Completar la recolección de actas y encuestas de satisfacción."
            elif (num + p_id) % 2 == 0:
                estado = "En Proceso"
                pct = 45.0
                just = f"Elaboración de informe de línea de base en desarrollo."
                plan = "Alinear sílabos y rúbricas al modelo de competencias de posgrado."
            else:
                estado = "No Cumple"
                pct = 20.0
                just = f"Brecha identificada en la auditoría inicial de autoevaluación."
                plan = "Aprobar directiva interna y designar responsable operativo."

            eval_data.append((
                p_id, est["id"], estado, pct, just,
                f"Resolución N° 0{num}-2025-{cod}; Acta SGC-2026",
                plan,
                "Comité de Calidad del Programa"
            ))

        c.executemany("""
        INSERT INTO sgc_autoevaluaciones (programa_id, estandar_id, estado_cumplimiento, porcentaje, justificacion, evidencias_texto, plan_mejora, responsable)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, eval_data)

        # Cursos de ejemplo alineados a la malla curricular de Posgrado UCV
        c.execute("""
        INSERT INTO lms_cursos (programa_id, codigo, nombre, ciclo, creditos, docente_nombre, silabo_url)
        VALUES (?, 'POS-101', 'Metodología y Diseño de la Investigación Científica', 'Ciclo I', 5, 'Dr. Juan Marcos Vilchez-Canchari', 'https://campusvirtual.ucv.edu.pe/cursos/pos101');
        """, (p_id,))
        c.execute("""
        INSERT INTO lms_cursos (programa_id, codigo, nombre, ciclo, creditos, docente_nombre, silabo_url)
        VALUES (?, 'POS-201', 'Seminario de Tesis I (Modelado y Análisis de Datos)', 'Ciclo II', 6, 'Dr. Investigador RENACYT UCV', 'https://campusvirtual.ucv.edu.pe/cursos/pos201');
        """, (p_id,))
        c.execute("""
        INSERT INTO lms_cursos (programa_id, codigo, nombre, ciclo, creditos, docente_nombre, silabo_url)
        VALUES (?, 'POS-301', 'Seminario de Tesis II (Redacción de Artículo Scopus/WoS)', 'Ciclo III', 6, 'Dr. Docente Renacyt UCV', 'https://campusvirtual.ucv.edu.pe/cursos/pos301');
        """, (p_id,))

        # Tesis de ejemplo con política de integridad académica UCV (Turnitin CEI-UCV)
        c.execute("""
        INSERT INTO lms_tesis_seguimiento (programa_id, estudiante_nombre, titulo_tesis, linea_investigacion, asesor_nombre, porcentaje_avance, similitud_turnitin, comite_etica_aprobado, articulo_publicado)
        VALUES (?, 'Mag. Tesista Doctoral UCV', 'Modernización de la Gestión Pública y Eficiencia del Gasto Social en el Perú', 'Gestión Pública y Políticas Sociales', 'Dr. Juan Marcos Vilchez-Canchari', 85.0, 8.5, 1, 1);
        """, (p_id,))

        # Docente RENACYT UCV
        c.execute("""
        INSERT INTO lms_docentes (programa_id, nombre, grado_academico, categoria_docente, es_renacyt, nivel_renacyt, codigo_orcid, articulos_scopus_wos)
        VALUES (?, 'Dr. Juan Marcos Vilchez-Canchari', 'Doctor en Ingeniería / PhD', 'Principal', 1, 'Nivel I (Distinguido)', '0000-0002-1825-0097', 18);
        """, (p_id,))

    conn.commit()


# ==========================================
# GESTIÓN DE USUARIOS Y AUTENTICACIÓN
# ==========================================

def authenticate_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    pwd_hash = hash_password(password)
    c.execute("""
    SELECT u.*, p.nombre as programa_nombre, p.codigo as programa_codigo
    FROM sgc_usuarios u
    LEFT JOIN sgc_programas p ON u.programa_id = p.id
    WHERE u.username = ? AND u.password_hash = ?;
    """, (username, pwd_hash))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None


def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT u.id, u.username, u.full_name, u.role, u.email, u.cargo, u.avatar, p.nombre as programa_nombre
    FROM sgc_usuarios u
    LEFT JOIN sgc_programas p ON u.programa_id = p.id
    ORDER BY u.role ASC, u.full_name ASC;
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ==========================================
# GESTIÓN DE PROGRAMAS
# ==========================================

def get_all_programs():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM sgc_programas ORDER BY nivel DESC, nombre ASC;")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_program_by_id(prog_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM sgc_programas WHERE id = ?;", (prog_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_programs_benchmark():
    """Calcula métricas agregadas de todos los programas para el Dashboard del Administrador."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT 
        p.id, p.codigo, p.nombre, p.nivel, p.director,
        AVG(a.porcentaje) as promedio_global,
        SUM(CASE WHEN a.estado_cumplimiento = 'Cumple Plenamente' THEN 1 ELSE 0 END) as plenamente,
        SUM(CASE WHEN a.estado_cumplimiento = 'Cumple Parcial' THEN 1 ELSE 0 END) as parcial,
        SUM(CASE WHEN a.estado_cumplimiento = 'En Proceso' THEN 1 ELSE 0 END) as en_proceso,
        SUM(CASE WHEN a.estado_cumplimiento = 'No Cumple' THEN 1 ELSE 0 END) as no_cumple,
        COUNT(ev.id) as total_archivos_evidencia
    FROM sgc_programas p
    LEFT JOIN sgc_autoevaluaciones a ON p.id = a.programa_id
    LEFT JOIN sgc_evidencias_archivos ev ON p.id = ev.programa_id
    GROUP BY p.id
    ORDER BY promedio_global DESC;
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


# ==========================================
# AUTOEVALUACIÓN Y EVIDENCIAS DIGITALES
# ==========================================

def get_program_summary(prog_id):
    conn = get_connection()
    c = conn.cursor()

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

    # Promedio por dimensión
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

    # Promedio por factor
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
        COALESCE(a.evidencias_texto, '') as evidencias_texto,
        COALESCE(a.plan_mejora, '') as plan_mejora,
        COALESCE(a.responsable, '') as responsable,
        (SELECT COUNT(*) FROM sgc_evidencias_archivos ev WHERE ev.programa_id = ? AND ev.estandar_id = e.id) as total_archivos
    FROM sgc_estandares e
    JOIN sgc_factores f ON e.factor_id = f.id
    JOIN sgc_dimensiones d ON f.dimension_id = d.id
    LEFT JOIN sgc_autoevaluaciones a ON e.id = a.estandar_id AND a.programa_id = ?
    WHERE 1=1
    """
    params = [prog_id, prog_id]

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


def update_standard_evaluation(prog_id, estandar_id, estado, pct, just, evid_texto, plan, resp):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO sgc_autoevaluaciones (programa_id, estandar_id, estado_cumplimiento, porcentaje, justificacion, evidencias_texto, plan_mejora, responsable, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(programa_id, estandar_id) DO UPDATE SET
        estado_cumplimiento = excluded.estado_cumplimiento,
        porcentaje = excluded.porcentaje,
        justificacion = excluded.justificacion,
        evidencias_texto = excluded.evidencias_texto,
        plan_mejora = excluded.plan_mejora,
        responsable = excluded.responsable,
        updated_at = CURRENT_TIMESTAMP;
    """, (prog_id, estandar_id, estado, pct, just, evid_texto, plan, resp))
    conn.commit()
    conn.close()


def save_uploaded_evidence(prog_id, estandar_id, uploaded_file, uploader_name):
    """Guarda un archivo físico de evidencia en disco y lo registra en la base de datos."""
    prog_dir = os.path.join(EVIDENCIAS_DIR, f"prog_{prog_id}", f"est_{estandar_id}")
    os.makedirs(prog_dir, exist_ok=True)

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = f"{timestamp_str}_{uploaded_file.name.replace(' ', '_')}"
    file_path = os.path.join(prog_dir, clean_name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO sgc_evidencias_archivos (programa_id, estandar_id, nombre_archivo, ruta_archivo, tamanio_bytes, subido_por)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (prog_id, estandar_id, uploaded_file.name, file_path, uploaded_file.size, uploader_name))
    conn.commit()
    conn.close()
    return True


def get_standard_evidence_files(prog_id, estandar_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT id, nombre_archivo, ruta_archivo, tamanio_bytes, subido_por, fecha_subida
    FROM sgc_evidencias_archivos
    WHERE programa_id = ? AND estandar_id = ?
    ORDER BY fecha_subida DESC;
    """, (prog_id, estandar_id))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def delete_evidence_file(file_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT ruta_archivo FROM sgc_evidencias_archivos WHERE id = ?;", (file_id,))
    row = c.fetchone()
    if row and os.path.exists(row["ruta_archivo"]):
        try:
            os.remove(row["ruta_archivo"])
        except Exception:
            pass
    c.execute("DELETE FROM sgc_evidencias_archivos WHERE id = ?;", (file_id,))
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
