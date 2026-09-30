# -*- coding: utf-8 -*-
"""
NUTRIFLEX - Asistente inteligente de alimentacion (Concepto AB con Traducomida)
Diseno del Producto, Proceso y Servicio - Universidad de La Sabana
Como ejecutar:  streamlit run app.py
"""
import streamlit as st

# ============================================================
# 1) CONFIGURACION INICIAL Y ESTILO (paleta NUTRIFLEX)
# ============================================================
st.set_page_config(page_title="NUTRIFLEX", page_icon="🥗", layout="centered")

CORAL, GRANATE, TINTA = "#EF4B33", "#6D0E00", "#1A1A1A"
BEIGE, SALMON, NARANJA = "#FDE6DB", "#FDB28A", "#E7966B"

st.markdown(
    f"""
    <style>
    :root, .stApp {{color-scheme: light;}}
    .stApp {{background: linear-gradient(180deg, {BEIGE} 0%, {BEIGE} 55%, #FCCFB8 100%); color: {TINTA};}}
    header[data-testid="stHeader"] {{background: transparent;}}
    #MainMenu, footer {{visibility: hidden;}}
    .block-container {{max-width: 480px; padding: 1rem 1rem 3rem 1rem;}}
    h1, h2, h3, h4, h5 {{color: {GRANATE} !important; font-weight: 800 !important;}}
    p, label, span, li {{color: {TINTA};}}

    /* Encabezado */
    .nf-hero {{position: relative; overflow: hidden; background: {GRANATE}; border-radius: 26px;
        padding: 22px 22px 18px 22px; margin-bottom: 14px; box-shadow: 0 8px 22px rgba(109,14,0,.28);}}
    .nf-hero:before {{content: ""; position: absolute; right: -40px; top: -40px; width: 140px; height: 140px;
        border-radius: 50%; background: {NARANJA}; opacity: .55;}}
    .nf-hero:after {{content: ""; position: absolute; right: 40px; bottom: -50px; width: 110px; height: 110px;
        border-radius: 50%; background: {SALMON}; opacity: .35;}}
    .nf-logo {{position: relative; z-index: 2; font-size: 2.1rem; font-weight: 900; letter-spacing: 2px; color: {CORAL};
        line-height: 1;}}
    .nf-logo span {{color: {SALMON};}}
    .nf-tag {{position: relative; z-index: 2; color: {BEIGE}; font-size: .9rem; margin-top: 6px;}}

    /* Indicador de pasos */
    .nf-steps {{display: flex; align-items: center; gap: 6px; margin: 4px 2px 16px 2px;}}
    .nf-dot {{height: 8px; flex: 1; border-radius: 99px; background: {SALMON};}}
    .nf-dot.done {{background: {GRANATE};}}
    .nf-dot.act {{background: {CORAL}; flex: 2;}}
    .nf-steplabel {{color: {GRANATE}; font-weight: 700; font-size: .85rem; margin: 0 2px 2px 2px;}}

    /* Tarjetas */
    [class*="st-key-card"], .nf-card {{background: #FFF6F1; border: 1.5px solid {SALMON}; border-radius: 20px;
        padding: 14px 16px; box-shadow: 0 4px 14px rgba(109,14,0,.10); margin-bottom: 10px;}}
    .nf-card.dark {{background: {GRANATE}; border-color: {GRANATE};}}
    .nf-card.dark, .nf-card.dark p, .nf-card.dark span, .nf-card.dark div {{color: {BEIGE};}}
    .nf-card h4 {{margin: 0 0 4px 0;}}
    .nf-card.dark h4 {{color: {SALMON} !important;}}
    .nf-row {{display: flex; justify-content: space-between; align-items: center; gap: 10px;}}
    .nf-hora {{background: {GRANATE}; color: {BEIGE} !important; font-weight: 800; font-size: .85rem;
        padding: 4px 12px; border-radius: 99px; white-space: nowrap;}}
    .nf-comida {{font-weight: 800; color: {GRANATE}; font-size: 1.02rem;}}
    .nf-sub {{font-size: .85rem; opacity: .85;}}
    .nf-chip {{display: inline-block; background: {SALMON}; color: {GRANATE} !important; font-weight: 700;
        font-size: .78rem; padding: 3px 10px; border-radius: 99px; margin: 6px 6px 0 0;}}
    .nf-chip.out {{background: transparent; border: 1.5px solid {NARANJA};}}
    .nf-card.dark .nf-chip {{background: {NARANJA}; color: {GRANATE} !important;}}
    .nf-badge-ok {{background: {GRANATE}; color: {BEIGE} !important; font-size: .75rem; font-weight: 700;
        padding: 3px 10px; border-radius: 99px;}}
    .nf-badge-no {{border: 1.5px solid {NARANJA}; color: {GRANATE} !important; font-size: .75rem; font-weight: 700;
        padding: 2px 10px; border-radius: 99px;}}
    .nf-band {{display: inline-block; background: {CORAL}; color: white !important; font-weight: 800;
        font-size: .82rem; padding: 4px 14px; border-radius: 99px; margin: 8px 0 8px 0;}}
    .nf-total {{display: flex; justify-content: space-around; text-align: center;}}
    .nf-total b {{display: block; font-size: 1.5rem; color: {CORAL};}}
    .nf-total small {{color: {BEIGE}; opacity: .85;}}
    .nf-bar {{height: 10px; border-radius: 99px; background: rgba(253,230,219,.25); margin: 3px 0 10px 0;}}
    .nf-bar > div {{height: 10px; border-radius: 99px; background: {CORAL};}}
    .nf-ticket {{border: 2px dashed {SALMON}; border-radius: 14px; padding: 10px; text-align: center; margin-top: 10px;}}
    .nf-ticket b {{font-size: 1.5rem; letter-spacing: 3px; color: {CORAL};}}

    /* Botones */
    button[kind="primary"], [data-testid="stBaseButton-primary"] {{background: {CORAL}; border: none; color: white;
        border-radius: 99px; font-weight: 800; padding: .55rem 1rem; box-shadow: 0 4px 12px rgba(239,75,51,.35);}}
    button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {{background: {GRANATE}; color: white;}}
    button[kind="secondary"], [data-testid="stBaseButton-secondary"] {{background: #FFF6F1; color: {GRANATE};
        border: 1.5px solid {GRANATE}; border-radius: 99px; font-weight: 700;}}
    button[kind="secondary"]:hover, [data-testid="stBaseButton-secondary"]:hover {{background: {GRANATE}; color: {BEIGE};}}
    /* Campos de formulario: fondo claro y texto oscuro (aunque el navegador este en modo oscuro) */
    div[data-baseweb="select"] > div, div[data-baseweb="input"], div[data-baseweb="base-input"],
    div[data-baseweb="textarea"] {{background: #FFF6F1 !important; border: 1.5px solid {SALMON} !important;
        border-radius: 14px !important;}}
    div[data-baseweb="select"] *, div[data-baseweb="input"] *, input, textarea {{color: {TINTA} !important;
        -webkit-text-fill-color: {TINTA} !important; background-color: transparent !important;}}
    div[data-baseweb="select"] svg {{fill: {GRANATE} !important;}}
    input::placeholder, textarea::placeholder {{color: #6D0E0099 !important; -webkit-text-fill-color: #6D0E0099 !important;}}
    div[data-baseweb="tag"] {{background: {GRANATE} !important; border-radius: 99px !important;}}
    div[data-baseweb="tag"] * {{color: {BEIGE} !important; -webkit-text-fill-color: {BEIGE} !important;}}
    div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li {{background: #FFF6F1 !important; color: {TINTA} !important;}}
    div[data-baseweb="popover"] li:hover {{background: {SALMON} !important;}}
    /* Deslizadores y opciones de radio */
    div[data-baseweb="slider"] div[role="slider"] {{background: {CORAL} !important; box-shadow: none !important;}}
    div[data-testid="stSliderThumbValue"], div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"] {{color: {GRANATE} !important; font-weight: 700;}}
    div[data-testid="stRadio"] label p {{color: {TINTA} !important;}}
    </style>
    """,
    unsafe_allow_html=True,
)


def html(bloque):
    """Renderiza HTML sin que Markdown lo confunda con codigo (quita sangrias)."""
    st.markdown("".join(linea.strip() for linea in bloque.splitlines()), unsafe_allow_html=True)


# ============================================================
# 2) DATOS DEL PROTOTIPO (plan y catalogo de alternativas)
# ============================================================
# Plan de alimentacion del usuario: hora, nombre, kcal, proteina (g)
PLAN = [
    {"id": "desayuno", "hora": "07:00", "nombre": "Desayuno", "plato": "Avena con huevo y fruta", "kcal": 450, "prot": 28},
    {"id": "almuerzo", "hora": "12:30", "nombre": "Almuerzo", "plato": "Pollo a la plancha, arroz y ensalada", "kcal": 650, "prot": 45},
    {"id": "merienda", "hora": "16:00", "nombre": "Merienda", "plato": "Yogur griego con granola", "kcal": 250, "prot": 18},
    {"id": "cena", "hora": "19:30", "nombre": "Cena", "plato": "Pescado, papa y verduras", "kcal": 550, "prot": 40},
]

# Alternativas: tiempo hasta tenerla lista (min), precio (COP), macros y restricciones que CONTIENE
ALTERNATIVAS = [
    {"id": 1, "nombre": "Wrap de pollo y vegetales", "lugar": "Punto móvil del campus", "min": 5, "precio": 13000,
     "kcal": 610, "prot": 38, "carb": 62, "gras": 20, "tipo": "principal",
     "ingredientes": "Tortilla integral, pollo, lechuga, tomate, aguacate", "contiene": ["gluten"]},
    {"id": 2, "nombre": "Bowl de proteína con arroz", "lugar": "Cafetería central", "min": 10, "precio": 16000,
     "kcal": 660, "prot": 44, "carb": 68, "gras": 19, "tipo": "principal",
     "ingredientes": "Arroz, pollo desmechado, frijol, maíz, aguacate", "contiene": []},
    {"id": 3, "nombre": "Sándwich de atún integral", "lugar": "Punto móvil del campus", "min": 5, "precio": 11000,
     "kcal": 560, "prot": 36, "carb": 55, "gras": 18, "tipo": "principal",
     "ingredientes": "Pan integral, atún, tomate, lechuga, mayonesa ligera", "contiene": ["gluten", "pescado", "huevo"]},
    {"id": 4, "nombre": "Ensalada con pollo y quinua", "lugar": "Cafetería central", "min": 15, "precio": 15000,
     "kcal": 590, "prot": 40, "carb": 50, "gras": 22, "tipo": "principal",
     "ingredientes": "Quinua, pollo, espinaca, tomate cherry, semillas", "contiene": ["frutos secos"]},
    {"id": 5, "nombre": "Almuerzo ejecutivo (pollo, arroz, ensalada)", "lugar": "Restaurante cercano", "min": 25, "precio": 18000,
     "kcal": 680, "prot": 46, "carb": 72, "gras": 18, "tipo": "principal",
     "ingredientes": "Pechuga a la plancha, arroz blanco, ensalada mixta", "contiene": []},
    {"id": 6, "nombre": "Bowl vegetariano de garbanzos", "lugar": "Cafetería central", "min": 15, "precio": 14000,
     "kcal": 620, "prot": 32, "carb": 78, "gras": 16, "tipo": "principal",
     "ingredientes": "Garbanzos, arroz integral, aguacate, tomate, pepino", "contiene": []},
    {"id": 7, "nombre": "Yogur griego con fruta y granola", "lugar": "Kiosco del edificio", "min": 5, "precio": 8000,
     "kcal": 260, "prot": 19, "carb": 32, "gras": 6, "tipo": "snack",
     "ingredientes": "Yogur griego, fruta, granola", "contiene": ["lactosa", "gluten", "frutos secos"]},
    {"id": 8, "nombre": "Barra de proteína + banano", "lugar": "Kiosco del edificio", "min": 5, "precio": 9000,
     "kcal": 240, "prot": 17, "carb": 30, "gras": 6, "tipo": "snack",
     "ingredientes": "Barra de proteína, banano", "contiene": ["lactosa", "frutos secos"]},
    {"id": 9, "nombre": "Huevos revueltos con pan integral", "lugar": "Cafetería central", "min": 10, "precio": 9500,
     "kcal": 380, "prot": 24, "carb": 30, "gras": 17, "tipo": "snack",
     "ingredientes": "Huevos, pan integral, tomate", "contiene": ["huevo", "gluten"]},
]

RESTRICCIONES = ["lactosa", "gluten", "frutos secos", "huevo", "pescado"]
TIEMPOS = [5, 10, 15, 30]
MOTIVOS = ["Clase o reunión que se extendió", "Trancón o retraso en el transporte", "Olvidé empacar mi comida", "Cambio de plan social o familiar"]


# ============================================================
# 3) FUNCIONES DE AYUDA
# ============================================================
def formato_cop(valor):
    """Convierte un numero a texto tipo $13.000."""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def buscar_comida(id_comida):
    return next(c for c in PLAN if c["id"] == id_comida)


def buscar_alternativa(id_alt):
    return next(a for a in ALTERNATIVAS if a["id"] == id_alt)


def es_equivalente(original, alt):
    """Traducomida: kcal dentro de +-15% y proteina de al menos 85% de la original."""
    dif_kcal = abs(alt["kcal"] - original["kcal"]) / original["kcal"]
    return dif_kcal <= 0.15 and alt["prot"] >= 0.85 * original["prot"]


def alternativas_posibles(original, datos):
    """Filtra por tiempo, presupuesto y restricciones. Ordena de la mas rapida a la mas lenta."""
    tipo = "snack" if original["kcal"] < 350 else "principal"
    lista = [
        a for a in ALTERNATIVAS
        if a["tipo"] == tipo
        and a["min"] <= datos["tiempo"]
        and a["precio"] <= datos["presupuesto"]
        and not set(a["contiene"]) & set(datos["restricciones"])
    ]
    return sorted(lista, key=lambda a: (a["min"], a["precio"]))


def ir_a(paso):
    st.session_state.paso = paso


def elegir(id_alt):
    st.session_state.alt_id = id_alt
    ir_a(5)


def reiniciar():
    for clave in ("paso", "datos", "comida_id", "alt_id", "reserva"):
        st.session_state.pop(clave, None)


# ============================================================
# 4) ESTADO DE LA SESION
# ============================================================
if "paso" not in st.session_state:
    st.session_state.paso = 1
if "datos" not in st.session_state:
    st.session_state.datos = {"motivo": MOTIVOS[0], "tiempo": 15, "presupuesto": 20000, "restricciones": [], "gustos": ""}
if "comida_id" not in st.session_state:
    st.session_state.comida_id = "almuerzo"

paso = st.session_state.paso
datos = st.session_state.datos
NOMBRES_PASOS = ["Inicio", "Emergencia", "Análisis", "Alternativas", "Traducomida", "Reserva", "Confirmación"]

# ============================================================
# 5) ENCABEZADO NUTRIFLEX E INDICADOR DE PASOS
# ============================================================
html("""
<div class="nf-hero">
  <div class="nf-logo">NUTRI<span>FLEX</span></div>
  <div class="nf-tag">Tu plan de alimentación, flexible cuando la rutina cambia 🥗</div>
</div>
""")
puntos = "".join(
    f'<div class="nf-dot {"done" if n < paso else "act" if n == paso else ""}"></div>' for n in range(1, 8)
)
html(f'<div class="nf-steplabel">Paso {paso} de 7 · {NOMBRES_PASOS[paso - 1]}</div><div class="nf-steps">{puntos}</div>')

# ============================================================
# 6) PASO 1 - INICIO: PLAN DE ALIMENTACION
# ============================================================
if paso == 1:
    total_kcal = sum(c["kcal"] for c in PLAN)
    total_prot = sum(c["prot"] for c in PLAN)
    html(f"""
    <div class="nf-card dark">
      <h4>Tu plan de hoy</h4>
      <div class="nf-total">
        <div><b>{len(PLAN)}</b><small>comidas</small></div>
        <div><b>{total_kcal}</b><small>kcal</small></div>
        <div><b>{total_prot} g</b><small>proteína</small></div>
      </div>
    </div>
    """)
    for c in PLAN:
        html(f"""
        <div class="nf-card">
          <div class="nf-row"><span class="nf-comida">{c['nombre']}</span><span class="nf-hora">{c['hora']}</span></div>
          <div class="nf-sub">{c['plato']}</div>
          <span class="nf-chip">🔥 {c['kcal']} kcal</span><span class="nf-chip">💪 {c['prot']} g proteína</span>
        </div>
        """)
    st.button("🚨 Tuve un imprevisto", type="primary", width="stretch", on_click=ir_a, args=(2,))

# ============================================================
# 7) PASO 2 - BOTON DE EMERGENCIA
# ============================================================
elif paso == 2:
    html("""
    <div class="nf-card dark">
      <h4>No pasa nada, podemos ajustar tu plan 💚</h4>
      <div class="nf-sub">Un cambio de rutina no es un incumplimiento. Dinos qué comida no podrás tomar y buscamos una alternativa.</div>
    </div>
    """)
    opciones = {c["id"]: f"{c['hora']} · {c['nombre']} — {c['plato']}" for c in PLAN}
    st.session_state.comida_id = st.radio(
        "¿Qué comida se ve afectada?", list(opciones.keys()),
        format_func=lambda k: opciones[k], index=list(opciones.keys()).index(st.session_state.comida_id),
    )
    col1, col2 = st.columns(2)
    col1.button("← Volver", width="stretch", on_click=ir_a, args=(1,))
    col2.button("Continuar →", type="primary", width="stretch", on_click=ir_a, args=(3,))

# ============================================================
# 8) PASO 3 - ANALISIS DE SITUACION
# ============================================================
elif paso == 3:
    st.subheader("Cuéntanos tu situación")
    motivo = st.selectbox("¿Qué pasó?", MOTIVOS, index=MOTIVOS.index(datos["motivo"]))
    tiempo = st.select_slider("Tiempo disponible para comer (min)", options=TIEMPOS, value=datos["tiempo"])
    presupuesto = st.slider("Presupuesto máximo", 5000, 30000, datos["presupuesto"], step=1000, format="$%d")
    restricciones = st.multiselect("Alergias o alimentos que no puedes consumir", RESTRICCIONES, default=datos["restricciones"])
    gustos = st.text_input("Gustos personales (opcional)", value=datos["gustos"], placeholder="Ej.: pollo, aguacate, bowls")

    def guardar_y_buscar():
        st.session_state.datos = {
            "motivo": motivo, "tiempo": tiempo, "presupuesto": presupuesto,
            "restricciones": restricciones, "gustos": gustos,
        }
        ir_a(4)

    col1, col2 = st.columns(2)
    col1.button("← Volver", width="stretch", on_click=ir_a, args=(2,))
    col2.button("Ver alternativas →", type="primary", width="stretch", on_click=guardar_y_buscar)

# ============================================================
# 9) PASO 4 - ALTERNATIVAS SEGUN EL TIEMPO DISPONIBLE
# ============================================================
elif paso == 4:
    original = buscar_comida(st.session_state.comida_id)
    posibles = alternativas_posibles(original, datos)
    html(f"""
    <div class="nf-card dark">
      <h4>Alternativas para tu {original['nombre'].lower()}</h4>
      <div class="nf-sub">Reemplazan: {original['plato']}</div>
      <span class="nf-chip">🔥 {original['kcal']} kcal</span><span class="nf-chip">💪 {original['prot']} g</span>
      <span class="nf-chip">⏱️ {datos['tiempo']} min</span><span class="nf-chip">💵 hasta {formato_cop(datos['presupuesto'])}</span>
    </div>
    """)
    if not posibles:
        st.warning("No encontramos opciones con esas condiciones. Prueba con más tiempo, más presupuesto o menos restricciones.")
    gustos = [g.strip().lower() for g in datos["gustos"].split(",") if g.strip()]
    for lo, hi in [(0, 5), (5, 10), (10, 15), (15, 30)]:
        grupo = [a for a in posibles if lo < a["min"] <= hi]
        if not grupo:
            continue
        html(f'<span class="nf-band">⏱️ Listas en {"menos de 5" if hi == 5 else "hasta " + str(hi)} min</span>')
        for a in grupo:
            gusta = any(g in (a["nombre"] + a["ingredientes"]).lower() for g in gustos)
            insignia = '<span class="nf-badge-ok">✓ Equivalente</span>' if es_equivalente(original, a) else '<span class="nf-badge-no">Se aleja del plan</span>'
            estrella = " ⭐" if gusta else ""
            with st.container(key=f"card_alt_{a['id']}"):
                html(f"""
                <div class="nf-row"><span class="nf-comida">{a['nombre']}{estrella}</span></div>
                <div class="nf-sub">📍 {a['lugar']}</div>
                <span class="nf-chip">⏱️ {a['min']} min</span><span class="nf-chip">💵 {formato_cop(a['precio'])}</span>
                <span class="nf-chip">🔥 {a['kcal']} kcal</span><span class="nf-chip">💪 {a['prot']} g</span>
                <div style="margin-top:8px">{insignia}</div>
                """)
                st.button("Elegir esta opción", key=f"elegir_{a['id']}", type="primary", width="stretch",
                          on_click=elegir, args=(a["id"],))
    st.button("← Cambiar mi situación", width="stretch", on_click=ir_a, args=(3,))

# ============================================================
# 10) PASO 5 - TRADUCOMIDA: REEMPLAZO NUTRICIONALMENTE EQUIVALENTE
# ============================================================
elif paso == 5:
    original = buscar_comida(st.session_state.comida_id)
    alt = buscar_alternativa(st.session_state.alt_id)
    st.subheader("🔄 Traducomida")
    st.caption("Traducimos tu comida planeada a una alternativa equivalente")
    d_kcal, d_prot = alt["kcal"] - original["kcal"], alt["prot"] - original["prot"]
    col1, col2 = st.columns(2)
    with col1:
        html(f"""
        <div class="nf-card">
          <div class="nf-sub"><b>TU PLAN</b></div>
          <div class="nf-comida">{original['plato']}</div>
          <span class="nf-chip">🔥 {original['kcal']} kcal</span><span class="nf-chip">💪 {original['prot']} g</span>
        </div>
        """)
    with col2:
        html(f"""
        <div class="nf-card dark">
          <div class="nf-sub"><b>ALTERNATIVA</b></div>
          <div class="nf-comida" style="color:{SALMON}">{alt['nombre']}</div>
          <span class="nf-chip">🔥 {alt['kcal']} kcal ({d_kcal:+d})</span><span class="nf-chip">💪 {alt['prot']} g ({d_prot:+d})</span>
        </div>
        """)
    if es_equivalente(original, alt):
        st.success("Esta opción mantiene tus calorías y tu proteína dentro del rango de tu plan.")
    else:
        st.warning("Esta opción se aleja de tu plan. Mira otras equivalentes abajo.")

    otras = [a for a in alternativas_posibles(original, datos) if es_equivalente(original, a) and a["id"] != alt["id"]]
    if otras:
        st.markdown("##### Otras opciones equivalentes")
        for a in otras:
            with st.container(key=f"card_otra_{a['id']}"):
                html(f"""
                <span class="nf-comida">{a['nombre']}</span>
                <div class="nf-sub">📍 {a['lugar']} · ⏱️ {a['min']} min · 💵 {formato_cop(a['precio'])}</div>
                <span class="nf-chip">🔥 {a['kcal']} kcal</span><span class="nf-chip">💪 {a['prot']} g</span>
                """)
                st.button("Cambiar por esta", key=f"cambiar_{a['id']}", width="stretch",
                          on_click=lambda i=a["id"]: st.session_state.update(alt_id=i))
    col1, col2 = st.columns(2)
    col1.button("← Alternativas", width="stretch", on_click=ir_a, args=(4,))
    col2.button("Reservar →", type="primary", width="stretch", on_click=ir_a, args=(6,))

# ============================================================
# 11) PASO 6 - RESERVA ANTICIPADA
# ============================================================
elif paso == 6:
    alt = buscar_alternativa(st.session_state.alt_id)
    st.subheader("Reserva tu comida")
    html(f"""
    <div class="nf-card dark">
      <h4>{alt['nombre']}</h4>
      <div class="nf-sub">📍 {alt['lugar']}</div>
      <div class="nf-sub">🥕 {alt['ingredientes']}</div>
      <span class="nf-chip">💵 {formato_cop(alt['precio'])}</span><span class="nf-chip">⏱️ lista en {alt['min']} min</span>
    </div>
    """)
    horas = [m for m in TIEMPOS if m >= alt["min"]] + [45]
    espera = st.selectbox("¿En cuántos minutos la recoges?", horas, format_func=lambda m: f"En {m} min")
    nota = st.text_input("Nota para el punto de venta (opcional)", placeholder="Ej.: sin aguacate")

    def confirmar():
        st.session_state.reserva = {"espera": espera, "nota": nota, "codigo": f"NF-{alt['id']:02d}{espera:02d}"}
        ir_a(7)

    col1, col2 = st.columns(2)
    col1.button("← Volver", width="stretch", on_click=ir_a, args=(5,))
    col2.button("Confirmar reserva ✔", type="primary", width="stretch", on_click=confirmar)

# ============================================================
# 12) PASO 7 - CONFIRMACION
# ============================================================
else:
    alt = buscar_alternativa(st.session_state.alt_id)
    reserva = st.session_state.reserva
    original = buscar_comida(st.session_state.comida_id)
    nota = f"<div class='nf-sub'>📝 {reserva['nota']}</div>" if reserva["nota"] else ""
    barras = "".join(
        f"<div class='nf-sub'>{n} · <b>{v} g</b></div><div class='nf-bar'><div style='width:{min(100, v / tope * 100):.0f}%'></div></div>"
        for n, v, tope in [("Proteína", alt["prot"], 60), ("Carbohidratos", alt["carb"], 100), ("Grasas", alt["gras"], 40)]
    )
    html(f"""
    <div class="nf-card dark">
      <h4>🎉 ¡Reserva confirmada!</h4>
      <div class="nf-comida" style="color:{BEIGE}">{alt['nombre']}</div>
      <div class="nf-sub">📍 {alt['lugar']} · 🕒 recógela en {reserva['espera']} min · 💵 {formato_cop(alt['precio'])}</div>
      {nota}
      <div class="nf-ticket">Código de reserva<br><b>{reserva['codigo']}</b></div>
    </div>
    <div class="nf-card dark">
      <h4>Información nutricional</h4>
      <div class="nf-total"><div><b>{alt['kcal']}</b><small>kcal</small></div></div>
      {barras}
      <div class="nf-sub">Reemplaza tu {original['nombre'].lower()} planeado ({original['kcal']} kcal · {original['prot']} g de proteína). Tu plan sigue en marcha.</div>
    </div>
    """)
    st.button("Volver al inicio", type="primary", width="stretch", on_click=reiniciar)
