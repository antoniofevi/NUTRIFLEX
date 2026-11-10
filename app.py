# -*- coding: utf-8 -*-
"""
NUTRIFLEX - Asistente inteligente de alimentacion (Concepto AB con Traducomida)
Prototipo final de alta fidelidad - Version 2
Diseno del Producto, Proceso y Servicio

Novedades frente a la version anterior:
  * Perfil / "Personalizar mi dieta": meta de calorias, macros, restricciones, gustos y plan de comidas.
  * Todo el motor (Traducomida, filtros, barras) usa los valores REALES del usuario (st.session_state).
  * Cada alternativa muestra su desviacion frente al plan (+120 kcal, -8 g de proteina...).
  * Catalogo ampliado con cafeterias y restaurantes de ciudad.
  * Pago simulado (Pagar y reservar) en el paso 6.
  * Flujo corto: restricciones y gustos ya no se piden en cada imprevisto.

Como ejecutar:  streamlit run app.py   (instrucciones de despliegue al final del archivo)
"""
import copy
import math
import time
from datetime import datetime

import streamlit as st

# ============================================================
# 1) CONFIGURACION INICIAL Y ESTILO (paleta NUTRIFLEX)
# ============================================================
st.set_page_config(page_title="NUTRIFLEX", page_icon="🥗", layout="centered", initial_sidebar_state="collapsed")

CORAL, GRANATE, TINTA = "#EF4B33", "#6D0E00", "#1A1A1A"
BEIGE, SALMON, NARANJA, CREMA = "#FDE6DB", "#FDB28A", "#E7966B", "#FFF6F1"

# El CSS usa marcadores @NOMBRE@ para evitar tener que duplicar llaves dentro de un f-string.
CSS = """
<style>
:root, .stApp {color-scheme: light;}
.stApp {background: linear-gradient(180deg, @BEIGE@ 0%, @BEIGE@ 55%, #FCCFB8 100%); color: @TINTA@;}
header[data-testid="stHeader"] {background: transparent;}
#MainMenu, footer {visibility: hidden;}
.block-container {max-width: 480px; padding: 1rem 1rem 3rem 1rem;}
h1, h2, h3, h4, h5 {color: @GRANATE@ !important; font-weight: 800 !important;}
p, label, span, li {color: @TINTA@;}
[data-testid="stCaptionContainer"] p {color: #8A4A3D !important;}

/* Sin hipervinculos no deseados: anclas de titulos, toolbar y cualquier enlace heredado */
[data-testid="stHeaderActionElements"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], a.anchor, h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {display: none !important;}
.stApp a:not([download]), .stApp a:not([download]):hover {color: inherit !important; text-decoration: none !important; pointer-events: none; cursor: default;}

/* Encabezado */
.nf-hero {position: relative; overflow: hidden; background: @GRANATE@; border-radius: 26px;
    padding: 22px 22px 18px 22px; margin-bottom: 14px; box-shadow: 0 8px 22px rgba(109,14,0,.28);}
.nf-hero:before {content: ""; position: absolute; right: -40px; top: -40px; width: 140px; height: 140px;
    border-radius: 50%; background: @NARANJA@; opacity: .55;}
.nf-hero:after {content: ""; position: absolute; right: 40px; bottom: -50px; width: 110px; height: 110px;
    border-radius: 50%; background: @SALMON@; opacity: .35;}
.nf-logo {position: relative; z-index: 2; font-size: 2.1rem; font-weight: 900; letter-spacing: 2px; color: @CORAL@; line-height: 1;}
.nf-logo span {color: @SALMON@;}
.nf-tag {position: relative; z-index: 2; color: @BEIGE@ !important; font-size: .9rem; margin-top: 6px;}

/* Indicador de pasos */
.nf-steps {display: flex; align-items: center; gap: 6px; margin: 4px 2px 16px 2px;}
.nf-dot {height: 8px; flex: 1; border-radius: 99px; background: @SALMON@;}
.nf-dot.done {background: @GRANATE@;}
.nf-dot.act {background: @CORAL@; flex: 2;}
.nf-steplabel {color: @GRANATE@ !important; font-weight: 700; font-size: .85rem; margin: 0 2px 2px 2px;}

/* Tarjetas */
[class*="st-key-card"], .nf-card {background: @CREMA@; border: 1.5px solid @SALMON@; border-radius: 20px;
    padding: 14px 16px; box-shadow: 0 4px 14px rgba(109,14,0,.10); margin-bottom: 10px;}
/* Alternativa equivalente: borde granate solido. Alternativa que se aleja: borde punteado y mas suave */
[class*="st-key-card_eq"] {border: 2.5px solid @GRANATE@; box-shadow: 0 6px 18px rgba(109,14,0,.18);}
[class*="st-key-card_no"] {border: 1.5px dashed @NARANJA@; background: #FFFAF7; box-shadow: none;}
.nf-card.dark {background: @GRANATE@; border-color: @GRANATE@;}
.nf-card.dark, .nf-card.dark p, .nf-card.dark span, .nf-card.dark div, .nf-card.dark small {color: @BEIGE@;}
.nf-card h4 {margin: 0 0 4px 0;}
.nf-card.dark h4 {color: @SALMON@ !important;}
.nf-row {display: flex; justify-content: space-between; align-items: center; gap: 10px;}
.nf-hora {background: @GRANATE@; color: @BEIGE@ !important; font-weight: 800; font-size: .85rem;
    padding: 4px 12px; border-radius: 99px; white-space: nowrap;}
.nf-comida {font-weight: 800; color: @GRANATE@; font-size: 1.02rem;}
.nf-sub {font-size: .85rem; opacity: .9;}
.nf-chip {display: inline-block; background: @SALMON@; color: @GRANATE@ !important; font-weight: 700;
    font-size: .78rem; padding: 3px 10px; border-radius: 99px; margin: 6px 6px 0 0;}
.nf-chip.out {background: transparent; border: 1.5px solid @NARANJA@;}
.nf-card.dark .nf-chip {background: @NARANJA@; color: @GRANATE@ !important;}
.nf-badge-ok {background: @GRANATE@; color: @BEIGE@ !important; font-size: .75rem; font-weight: 700; padding: 3px 10px; border-radius: 99px;}
.nf-badge-no {border: 1.5px solid @NARANJA@; color: @GRANATE@ !important; font-size: .75rem; font-weight: 700; padding: 2px 10px; border-radius: 99px;}
/* Desviacion respecto al plan: granate = dentro del rango, coral = fuera del rango */
.nf-dev {display: inline-block; font-weight: 800; font-size: .8rem; padding: 3px 11px; border-radius: 99px; margin: 6px 6px 0 0;}
.nf-dev.ok {background: @GRANATE@; color: @BEIGE@ !important;}
.nf-dev.no {background: @CORAL@; color: white !important;}
.nf-why {font-size: .8rem; color: @GRANATE@ !important; margin-top: 6px; font-weight: 600;}
.nf-band {display: inline-block; background: @CORAL@; color: white !important; font-weight: 800;
    font-size: .82rem; padding: 4px 14px; border-radius: 99px; margin: 8px 0 8px 0;}
.nf-total {display: flex; justify-content: space-around; text-align: center;}
.nf-total b {display: block; font-size: 1.5rem; color: @CORAL@;}
.nf-total small {color: @BEIGE@; opacity: .85;}
.nf-bar {height: 10px; border-radius: 99px; background: rgba(253,230,219,.25); margin: 3px 0 10px 0;}
.nf-bar > div {height: 10px; border-radius: 99px; background: @CORAL@;}
.nf-bar.over > div {background: @SALMON@;}
.nf-ticket {border: 2px dashed @SALMON@; border-radius: 14px; padding: 10px; text-align: center; margin-top: 10px;}
.nf-ticket b {font-size: 1.5rem; letter-spacing: 3px; color: @CORAL@;}
.nf-line {display: flex; justify-content: space-between; font-size: .88rem; padding: 4px 0;
    border-bottom: 1px dashed rgba(253,230,219,.3);}
.nf-pay {display: flex; justify-content: space-between; font-weight: 800; font-size: 1.1rem; padding-top: 8px;}

/* Mensaje de exito legible: fondo verde claro, texto verde oscuro */
.nf-ok {background: #DDF2E3; border: 1.5px solid #2E7D4F; border-radius: 14px; padding: 12px 16px; margin-bottom: 10px;
    color: #124A2B !important; font-weight: 600; font-size: .92rem;}
.nf-ok * {color: #124A2B !important;}
/* Aviso informativo/suave: crema con borde coral y texto granate (alto contraste sobre el fondo beige) */
.nf-soft {background: @CREMA@; border: 1.5px solid @CORAL@; border-left: 6px solid @CORAL@; border-radius: 14px;
    padding: 12px 16px; margin-bottom: 10px; color: @GRANATE@ !important; font-weight: 600; font-size: .92rem;}
.nf-soft * {color: @GRANATE@ !important;}

/* Filtros rapidos (pills): inactivo = crema, activo = coral */
button[data-variant="pills"] {border-radius: 99px !important; font-weight: 700; padding: .25rem .8rem;
    border: 1.5px solid @NARANJA@ !important; background: @CREMA@ !important;}
button[data-variant="pills"] *, button[data-variant="pills"] p {color: @GRANATE@ !important;}
button[data-variant="pills"][aria-pressed="true"] {background: @CORAL@ !important; border-color: @CORAL@ !important;}
button[data-variant="pills"][aria-pressed="true"] *, button[data-variant="pills"][aria-pressed="true"] p {color: white !important;}
.nf-hist {padding: 8px 0; border-bottom: 1px dashed @SALMON@;}
.nf-hist:last-child {border-bottom: none;}

/* Toggle: inactivo = gris rosado con borde granate, activo = coral; perilla blanca con borde */
label:has(input[role="switch"]) > div:nth-of-type(1) {background: #D9B8AA !important; border: 2px solid @GRANATE@ !important;
    box-sizing: content-box;}
label:has(input[role="switch"]:checked) > div:nth-of-type(1) {background: @CORAL@ !important;}
label:has(input[role="switch"]) > div:nth-of-type(1) > div {background: #FFFFFF !important; border: 1.5px solid @GRANATE@;
    box-shadow: 0 1px 4px rgba(0,0,0,.35) !important;}
label:has(input[role="switch"]) p {color: @GRANATE@ !important; font-weight: 700;}
[class*="st-key-card_toggle"] {padding: 8px 14px;}

/* Botones */
button[kind="primary"], [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
    background: @CORAL@; border: none; color: white; border-radius: 99px; font-weight: 800;
    padding: .55rem 1rem; box-shadow: 0 4px 12px rgba(239,75,51,.35);}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover, [data-testid="stBaseButton-primaryFormSubmit"]:hover {background: @GRANATE@; color: white;}
button[kind="primary"] p, [data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-primaryFormSubmit"] p {color: white !important;}
button[kind="secondary"], [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"] {
    background: @CREMA@; color: @GRANATE@; border: 1.5px solid @GRANATE@; border-radius: 99px; font-weight: 700;}
button[kind="secondary"]:hover, [data-testid="stBaseButton-secondary"]:hover {background: @GRANATE@; color: @BEIGE@;}
button[kind="secondary"]:hover p, [data-testid="stBaseButton-secondary"]:hover p {color: @BEIGE@ !important;}
button[kind="secondary"] p, [data-testid="stBaseButton-secondary"] p {color: @GRANATE@;}

/* Campos de formulario: fondo claro y texto oscuro aunque el navegador este en modo oscuro */
div[data-baseweb="select"], div[data-baseweb="select"] div,
div[data-baseweb="input"], div[data-baseweb="input"] div,
div[data-baseweb="base-input"], div[data-baseweb="base-input"] div,
div[data-baseweb="textarea"], div[data-baseweb="textarea"] div,
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] input, div[data-testid="stMultiSelect"] input,
div[data-testid="stTimeInput"] input {background-color: @CREMA@ !important; color: @TINTA@ !important;
    -webkit-text-fill-color: @TINTA@ !important; border-color: @SALMON@ !important;}
div[data-baseweb="select"] > div, div[data-baseweb="input"], div[data-baseweb="textarea"] {
    border: 1.5px solid @SALMON@ !important; border-radius: 14px !important;}
div[data-baseweb="select"] span, div[data-baseweb="select"] p {color: @TINTA@ !important; -webkit-text-fill-color: @TINTA@ !important;}
div[data-baseweb="select"] svg {fill: @GRANATE@ !important; color: @GRANATE@ !important;}
input::placeholder, textarea::placeholder {color: #8A4A3D !important; -webkit-text-fill-color: #8A4A3D !important; opacity: 1;}
div[data-baseweb="select"] div[data-baseweb="tag"] {background-color: @GRANATE@ !important; border-radius: 99px !important;}
div[data-baseweb="select"] div[data-baseweb="tag"] * {background-color: transparent !important; color: @BEIGE@ !important;
    -webkit-text-fill-color: @BEIGE@ !important;}
div[data-baseweb="popover"], div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li,
div[data-baseweb="popover"] div {background-color: @CREMA@ !important; color: @TINTA@ !important;}
div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li[aria-selected="true"] {background-color: @SALMON@ !important;}
div[data-testid="stNumberInput"] button {background: @CREMA@ !important; color: @GRANATE@ !important; border-color: @SALMON@ !important;}

/* Deslizadores, radios, toggles, pestanas, expanders, formularios */
div[data-baseweb="slider"] div[role="slider"] {background: @CORAL@ !important; box-shadow: none !important;}
div[data-testid="stSliderThumbValue"], div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"] {color: @GRANATE@ !important; font-weight: 700;}
div[data-testid="stRadio"] label p, div[data-testid="stToggle"] label p {color: @TINTA@ !important;}
button[data-baseweb="tab"] p {color: @GRANATE@ !important; font-weight: 700;}
div[data-baseweb="tab-highlight"] {background-color: @CORAL@ !important;}
div[data-baseweb="tab-border"] {background-color: @SALMON@ !important;}
[data-testid="stExpander"] details {background: @CREMA@; border: 1.5px solid @SALMON@ !important; border-radius: 16px;}
[data-testid="stExpander"] summary p {color: @GRANATE@ !important; font-weight: 700;}
[data-testid="stForm"] {border: none !important; padding: 0 !important;}
[data-testid="stFileUploaderDropzone"] {background: @CREMA@ !important; border: 1.5px dashed @SALMON@;}
[data-testid="stFileUploaderDropzone"] * {color: @TINTA@ !important;}
</style>
"""
for _nombre, _valor in (("CORAL", CORAL), ("GRANATE", GRANATE), ("TINTA", TINTA), ("BEIGE", BEIGE),
                        ("SALMON", SALMON), ("NARANJA", NARANJA), ("CREMA", CREMA)):
    CSS = CSS.replace(f"@{_nombre}@", _valor)
st.markdown(CSS, unsafe_allow_html=True)


def html(bloque):
    """Renderiza HTML sin que Markdown lo confunda con codigo (quita sangrias).
    Escapa '$' para que los precios no se interpreten como formulas LaTeX."""
    st.markdown("".join(linea.strip() for linea in bloque.splitlines()).replace("$", "&#36;"), unsafe_allow_html=True)


# ============================================================
# 2) DATOS DEL PROTOTIPO (perfil de ejemplo y catalogo ampliado)
# ============================================================
def _comida(id_, hora, nombre, plato, prot, carb, gras):
    """Crea una comida del plan; las kcal salen de los macros (4-4-9) redondeadas a 10."""
    return {"id": id_, "hora": hora, "nombre": nombre, "plato": plato, "prot": prot, "carb": carb, "gras": gras,
            "kcal": int(round((4 * prot + 4 * carb + 9 * gras) / 10.0) * 10)}


def perfil_inicial():
    """Perfil de ejemplo (persona activa que cuida sus macros). El usuario lo reemplaza al personalizar."""
    return {
        "configurado": False,
        "nombre": "",
        "meta": {"kcal": 2000, "prot": 140, "carb": 220, "gras": 60},
        "restricciones": [],
        "gustos": ["pollo", "aguacate", "bowls"],
        "presupuesto": 20000,
        "pago": {"metodo": "Tarjeta", "ultimos4": "4242"},
        "plan": [
            _comida("desayuno", "07:00", "Desayuno", "Avena con huevo y fruta", 32, 58, 14),
            _comida("almuerzo", "12:30", "Almuerzo", "Pollo a la plancha, arroz y ensalada", 48, 78, 18),
            _comida("merienda", "16:00", "Merienda", "Yogur griego con granola", 24, 28, 8),
            _comida("cena", "19:30", "Cena", "Pescado, papa y verduras", 40, 52, 20),
        ],
    }


def _alt(id_, nombre, lugar, dist, min_, precio, prot, carb, gras, tipo, ingredientes, contiene, kcal=None):
    """Crea una alternativa del catalogo. 'min' = minutos hasta tenerla lista (incluye el desplazamiento)."""
    if kcal is None:
        kcal = int(round((4 * prot + 4 * carb + 9 * gras) / 10.0) * 10)
    return {"id": id_, "nombre": nombre, "lugar": lugar, "dist": dist, "min": min_, "precio": precio,
            "kcal": kcal, "prot": prot, "carb": carb, "gras": gras, "tipo": tipo,
            "ingredientes": ingredientes, "contiene": contiene}


# 'contiene' son las etiquetas de restriccion que el plato incluye. Lugares y distancias son de ejemplo (ciudad).
ALTERNATIVAS = [
    # ---- Comidas principales ----
    _alt(2, "Bowl de proteína con arroz", "Bowl & Co.", "A 3 min caminando", 8, 16000, 44, 68, 19, "principal",
         "Arroz, pollo desmechado, frijol, maíz, aguacate", ["carne"], kcal=660),
    _alt(4, "Ensalada con pollo y quinua", "Green Garden", "A 5 min caminando", 14, 15000, 40, 50, 22, "principal",
         "Quinua, pollo, espinaca, tomate cherry, semillas", ["frutos secos", "carne"], kcal=590),
    _alt(5, "Almuerzo ejecutivo (pollo, arroz, ensalada)", "Restaurante La Sazón", "A 6 min caminando", 22, 18000, 46, 72, 18, "principal",
         "Pechuga a la plancha, arroz blanco, ensalada mixta", ["carne"], kcal=680),
    _alt(6, "Bowl vegetariano de garbanzos", "Green Garden", "A 5 min caminando", 13, 14000, 32, 78, 16, "principal",
         "Garbanzos, arroz integral, aguacate, tomate, pepino", [], kcal=620),
    _alt(10, "Pechuga a la plancha con quinua y brócoli", "Fit Kitchen", "A 6 min en transporte", 18, 22000, 48, 55, 14, "principal",
         "Pechuga, quinua, brócoli, zanahoria, aceite de oliva", ["carne"]),
    _alt(11, "Poke bowl de salmón", "Poke Bar", "A 8 min en transporte", 24, 27000, 38, 70, 22, "principal",
         "Salmón, arroz de sushi, edamame, aguacate, pepino", ["pescado", "soya"]),
    _alt(12, "Burrito bowl de res y frijol", "Burrito Bowl Co.", "A 5 min en transporte", 16, 24000, 42, 75, 20, "principal",
         "Res desmechada, arroz, frijol negro, maíz, pico de gallo", ["carne"]),
    _alt(13, "Sándwich de pavo y queso", "Deli Central", "A 4 min caminando", 9, 16000, 30, 52, 14, "principal",
         "Pan integral, pechuga de pavo, queso, lechuga, tomate", ["gluten", "lactosa", "carne"]),
    _alt(14, "Almuerzo corriente (res, arroz y lentejas)", "Restaurante Doña Mery", "A 7 min caminando", 26, 15000, 40, 80, 17, "principal",
         "Carne de res, arroz, lentejas, ensalada, plátano", ["carne"]),
    _alt(15, "Wrap vegano de falafel", "Verde Vivo", "A 9 min caminando", 17, 19000, 24, 70, 18, "principal",
         "Tortilla integral, falafel, hummus, pepino, tomate", ["gluten"]),
    _alt(16, "Pasta integral con pollo y vegetales", "Trattoria Express", "A 6 min en transporte", 21, 23000, 42, 82, 16, "principal",
         "Pasta integral, pollo, espinaca, tomate, queso parmesano", ["gluten", "lactosa", "carne"]),
    _alt(17, "Bowl de tofu y vegetales salteados", "Verde Vivo", "A 9 min caminando", 19, 20000, 30, 65, 17, "principal",
         "Tofu, arroz integral, brócoli, zanahoria, salsa de soya", ["soya"]),
    _alt(18, "Arepa con pollo desmechado y aguacate", "Arepas del Barrio", "A 4 min caminando", 7, 12000, 34, 52, 18, "principal",
         "Arepa de maíz, pollo desmechado, aguacate, ensalada", ["carne"]),
    _alt(19, "Bowl de avena, huevo y fruta", "Café Granola", "A 3 min caminando", 8, 10500, 26, 58, 12, "principal",
         "Avena cocida, huevo, banano, fresas, canela", ["huevo", "gluten"]),
    _alt(29, "Wrap de pollo y vegetales", "Wrap Station", "En el centro comercial", 11, 14000, 38, 62, 20, "principal",
         "Tortilla integral, pollo, lechuga, tomate, aguacate", ["gluten", "carne"], kcal=610),
    _alt(30, "Sándwich de atún integral", "Deli Central", "A 4 min caminando", 12, 12500, 36, 55, 18, "principal",
         "Pan integral, atún, tomate, lechuga, mayonesa ligera", ["gluten", "pescado", "huevo"], kcal=560),
    _alt(31, "Salmón a la plancha con arroz y vegetales", "Mar y Brasa", "A 8 min en transporte", 27, 32000, 40, 60, 20, "principal",
         "Salmón, arroz con coco, espárragos, limón", ["pescado"]),
    _alt(32, "Bandeja paisa ligera (res, frijol, arroz, aguacate)", "Fonda Paisa", "A 7 min caminando", 23, 17000, 42, 85, 22, "principal",
         "Carne molida, frijol, arroz, huevo, aguacate, plátano", ["carne", "huevo"]),
    _alt(33, "Pollo asado con papa criolla y ensalada", "Asadero El Fogón", "A 5 min caminando", 15, 17500, 44, 60, 18, "principal",
         "Cuarto de pollo asado, papa criolla, ensalada fresca", ["carne"]),
    _alt(34, "Hamburguesa de res con pan integral y ensalada", "Burger Lab", "En el centro comercial", 17, 21000, 38, 48, 26, "principal",
         "Carne de res, pan integral, queso, tomate, lechuga", ["gluten", "lactosa", "carne"]),
    _alt(35, "Sushi roll variado (12 piezas)", "Sushi Express", "A 6 min en transporte", 20, 26000, 28, 80, 12, "principal",
         "Arroz, salmón, aguacate, queso crema, alga nori", ["pescado", "soya", "lactosa"]),
    _alt(36, "Curry de lentejas con arroz basmati", "Sabores de la India", "A 8 min caminando", 20, 18000, 28, 85, 14, "principal",
         "Lentejas, arroz basmati, espinaca, leche de coco, especias", []),
    _alt(37, "Ensalada César con pollo", "Green Garden", "A 5 min caminando", 11, 16000, 36, 25, 24, "principal",
         "Lechuga, pollo, parmesano, crutones, aderezo césar", ["gluten", "lactosa", "carne", "huevo"]),
    _alt(38, "Wrap de huevo y espinaca", "Café Granola", "A 3 min caminando", 9, 11500, 24, 48, 16, "principal",
         "Tortilla integral, huevo, espinaca, queso, tomate", ["gluten", "huevo", "lactosa"]),
    _alt(39, "Bowl de açaí con granola y proteína", "Frutería Tropical", "A 4 min caminando", 12, 17000, 22, 75, 14, "principal",
         "Açaí, banano, granola, proteína vegetal, coco rallado", ["frutos secos", "gluten"]),
    _alt(40, "Calentado con huevo y arepa", "Fonda Paisa", "A 7 min caminando", 13, 11000, 26, 65, 20, "principal",
         "Calentado de arroz y frijol, huevo frito, arepa", ["huevo"]),
    # ---- Snacks / meriendas ----
    _alt(7, "Yogur griego con fruta y granola", "Café Granola", "A 3 min caminando", 4, 8000, 19, 32, 6, "snack",
         "Yogur griego, fruta, granola", ["lactosa", "gluten", "frutos secos"], kcal=260),
    _alt(8, "Barra de proteína + banano", "Tienda Fit", "A 2 min caminando", 3, 9000, 17, 30, 6, "snack",
         "Barra de proteína, banano", ["lactosa", "frutos secos"], kcal=240),
    _alt(9, "Huevos revueltos con pan integral", "Café Granola", "A 3 min caminando", 11, 9500, 24, 30, 17, "snack",
         "Huevos, pan integral, tomate", ["huevo", "gluten"], kcal=380),
    _alt(21, "Batido de proteína con avena", "Tienda Fit", "A 2 min caminando", 6, 12000, 28, 30, 5, "snack",
         "Proteína whey, leche, avena, banano", ["lactosa"]),
    _alt(22, "Fruta con mantequilla de maní", "Frutería Tropical", "A 4 min caminando", 7, 7000, 9, 30, 12, "snack",
         "Manzana, banano, mantequilla de maní", ["frutos secos"]),
    _alt(27, "Huevos duros (x3) con fruta", "Café Granola", "A 3 min caminando", 5, 6500, 19, 18, 15, "snack",
         "Huevos cocidos, mandarina", ["huevo"]),
    _alt(28, "Pudín de chía con frutas", "Green Garden", "A 5 min caminando", 8, 9500, 10, 28, 11, "snack",
         "Chía, bebida de coco, fresas, miel", []),
    _alt(23, "Hummus con vegetales y pita", "Verde Vivo", "A 9 min caminando", 13, 11000, 12, 38, 12, "snack",
         "Hummus, pita integral, zanahoria, pepino", ["gluten"]),
    _alt(24, "Yogur griego natural con frutos rojos", "Tienda Fit", "A 2 min caminando", 5, 9000, 20, 20, 4, "snack",
         "Yogur griego, frutos rojos, miel", ["lactosa"]),
    _alt(25, "Tostada de aguacate con huevo", "Café del Parque", "A 6 min caminando", 12, 10000, 16, 32, 16, "snack",
         "Pan integral, aguacate, huevo pochado", ["gluten", "huevo"]),
    _alt(42, "Mini sándwich de pollo", "Deli Central", "A 4 min caminando", 6, 8500, 24, 34, 7, "snack",
         "Pan integral, pollo desmechado, lechuga", ["gluten", "carne"]),
    _alt(43, "Smoothie bowl de frutas con proteína vegetal", "Frutería Tropical", "A 4 min caminando", 9, 13000, 20, 40, 6, "snack",
         "Mango, fresas, banano, proteína de arveja, semillas de chía", []),
    _alt(44, "Wrap pequeño de pavo y queso", "Wrap Station", "En el centro comercial", 7, 9000, 20, 30, 9, "snack",
         "Tortilla, pavo, queso, lechuga", ["gluten", "lactosa", "carne"]),
    _alt(45, "Arepa con queso y huevo", "Arepas del Barrio", "A 4 min caminando", 6, 6000, 14, 30, 12, "snack",
         "Arepa de maíz, queso, huevo", ["huevo", "lactosa"]),
    _alt(46, "Frutos secos mixtos y fruta", "Tienda Fit", "A 2 min caminando", 4, 8000, 8, 28, 16, "snack",
         "Almendras, nueces, pasas, manzana", ["frutos secos"]),
    _alt(47, "Ensalada de frutas con yogur", "Frutería Tropical", "A 4 min caminando", 8, 7500, 8, 35, 3, "snack",
         "Fruta picada, yogur natural, miel", ["lactosa"]),
    _alt(48, "Tortilla de claras con tostada integral", "Café del Parque", "A 6 min caminando", 12, 9500, 24, 26, 10, "snack",
         "Claras de huevo, espinaca, pan integral", ["huevo", "gluten"]),
    _alt(49, "Wrap de hummus y vegetales", "Verde Vivo", "A 9 min caminando", 14, 9500, 12, 40, 10, "snack",
         "Tortilla integral, hummus, zanahoria, pepino", ["gluten"]),
]

# Etiquetas de restriccion (valor interno -> texto visible)
RESTRICCIONES = {
    "lactosa": "Lactosa", "gluten": "Gluten", "frutos secos": "Frutos secos y maní", "huevo": "Huevo",
    "pescado": "Pescado", "soya": "Soya", "carne": "Carne y pollo (dieta vegetariana)",
}
GUSTOS_SUGERIDOS = ["pollo", "aguacate", "bowls", "quinua", "arroz", "garbanzos", "huevo", "yogur", "wrap",
                    "sándwich", "ensalada", "pasta", "pescado", "tofu", "avena", "batido"]
TIEMPOS = [5, 10, 15, 30]
MOTIVOS = ["Reunión o compromiso que se extendió", "Trancón o retraso en el transporte", "Olvidé empacar mi comida", "Cambio de plan social o familiar", "Otros"]
METODOS_PAGO = ["Tarjeta", "Nequi", "Daviplata", "Efectivo en el punto"]
FILTROS_RAPIDOS = ["💪 Alta en proteína", "💵 Más barato", "🥦 Vegetariano", "⚡ Listo en ≤ 10 min"]
COMISION_PCT, COMISION_MIN = 0.06, 500  # comision NutriFlex: 6 % del precio (minimo $500), redondeada a $100
NOMBRES_PASOS = ["Inicio", "Emergencia", "Análisis", "Alternativas", "Traducomida", "Reserva y pago", "Confirmación"]
MACROS = [("prot", "Proteína", "g"), ("carb", "Carbohidratos", "g"), ("gras", "Grasas", "g")]


# ============================================================
# 3) FUNCIONES DE AYUDA
# ============================================================
def formato_cop(valor):
    """Convierte un numero a texto tipo $13.000."""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def signo(n):
    """Numero con signo visible: +120, −8, ±0."""
    return "±0" if n == 0 else (f"+{n:.0f}" if n > 0 else f"−{abs(n):.0f}")


def buscar_comida(id_comida):
    return next(c for c in st.session_state.perfil["plan"] if c["id"] == id_comida)


def buscar_alternativa(id_alt):
    return next(a for a in ALTERNATIVAS if a["id"] == id_alt)


def es_equivalente(original, alt):
    """Traducomida: kcal dentro de +-15% y proteina de al menos 85% de la original (valores REALES del usuario)."""
    dif_kcal = abs(alt["kcal"] - original["kcal"]) / max(original["kcal"], 1)
    return dif_kcal <= 0.15 and alt["prot"] >= 0.85 * original["prot"]


def desviacion(original, alt):
    """Diferencia alternativa - plan para kcal y macros."""
    return {k: alt[k] - original[k] for k in ("kcal", "prot", "carb", "gras")}


def motivos_alejamiento(original, alt):
    """Frases cortas que explican exactamente cuanto se aleja una opcion del plan."""
    motivos = []
    minimo, maximo = original["kcal"] * 0.85, original["kcal"] * 1.15
    if alt["kcal"] > maximo:
        motivos.append(f"tiene {alt['kcal'] - original['kcal']} kcal de más")
    elif alt["kcal"] < minimo:
        motivos.append(f"tiene {original['kcal'] - alt['kcal']} kcal de menos")
    if alt["prot"] < 0.85 * original["prot"]:
        motivos.append(f"le faltan {math.ceil(0.85 * original['prot'] - alt['prot'])} g de proteína para equivaler")
    return motivos


def chips_desviacion(original, alt, completo=False):
    """Chips 'vs tu plan' (kcal y proteina; con completo=True tambien carbohidratos y grasas)."""
    d = desviacion(original, alt)
    ok_k = abs(d["kcal"]) / max(original["kcal"], 1) <= 0.15
    ok_p = alt["prot"] >= 0.85 * original["prot"]
    chips = (f'<span class="nf-dev {"ok" if ok_k else "no"}">🔥 {signo(d["kcal"])} kcal</span>'
             f'<span class="nf-dev {"ok" if ok_p else "no"}">💪 {signo(d["prot"])} g proteína</span>')
    if completo:
        chips += (f'<span class="nf-chip out">🍚 {signo(d["carb"])} g carbo</span>'
                  f'<span class="nf-chip out">🥑 {signo(d["gras"])} g grasa</span>')
    return chips


def le_gusta(alt, gustos):
    texto = (alt["nombre"] + " " + alt["ingredientes"]).lower()
    return any(g.lower() in texto for g in gustos)


def alternativas_posibles(original, datos, perfil):
    """Filtra por tiempo, presupuesto, restricciones GUARDADAS. Ordena SIEMPRE de la mas rapida a la mas lenta
    (desempate: equivalentes primero, luego los que le gustan al usuario, luego el precio)."""
    tipo = "snack" if original["kcal"] < 350 else "principal"
    restr, gustos = set(perfil["restricciones"]), perfil["gustos"]
    lista = [
        a for a in ALTERNATIVAS
        if a["tipo"] == tipo
        and a["min"] <= datos["tiempo"]
        and a["precio"] <= datos["presupuesto"]
        and not set(a["contiene"]) & restr
        and (not datos["solo_eq"] or es_equivalente(original, a))
    ]
    return sorted(lista, key=lambda a: (a["min"], not es_equivalente(original, a), not le_gusta(a, gustos), a["precio"]))


def aplicar_filtros(lista, filtros):
    """Filtros rapidos del Paso 4 (se combinan entre si y se aplican sobre el listado ya filtrado por tiempo,
    presupuesto y restricciones). Sin 'Más barato' se conserva el orden por tiempo."""
    if "💪 Alta en proteína" in filtros:      # al menos 25 % de las calorias provienen de proteina
        lista = [a for a in lista if a["prot"] * 4 >= 0.25 * a["kcal"]]
    if "🥦 Vegetariano" in filtros:           # sin carne/pollo (y sin pescado, para ser realmente vegetariano)
        lista = [a for a in lista if not {"carne", "pescado"} & set(a["contiene"])]
    if "⚡ Listo en ≤ 10 min" in filtros:
        lista = [a for a in lista if a["min"] <= 10]
    if "💵 Más barato" in filtros:
        lista = sorted(lista, key=lambda a: (a["precio"], a["min"]))
    return lista


def totales(plan):
    return {k: sum(c[k] for c in plan) for k in ("kcal", "prot", "carb", "gras")}


def barra(etiqueta, valor, meta, unidad):
    """Barra de progreso HTML (valor frente a meta) para tarjetas oscuras."""
    pct = min(100, valor / meta * 100) if meta else 0
    over = " over" if meta and valor > meta * 1.05 else ""
    return (f"<div class='nf-sub'>{etiqueta} · <b>{valor:.0f} / {meta:.0f} {unidad}</b></div>"
            f"<div class='nf-bar{over}'><div style='width:{pct:.0f}%'></div></div>")


def exito(texto):
    """Mensaje de exito con buen contraste (reemplaza a st.success)."""
    html(f'<div class="nf-ok">✅ {texto}</div>')


def aviso_suave(texto):
    """Aviso informativo con buen contraste (reemplaza a st.info)."""
    html(f'<div class="nf-soft">💡 {texto}</div>')


def comision(precio):
    """Comision de servicio NutriFlex: porcentaje del precio, minimo fijo, redondeada a $100."""
    return int(max(COMISION_MIN, round(precio * COMISION_PCT, -2)))


def chips_restricciones(perfil):
    """Resumen compacto de restricciones y gustos guardados."""
    partes = "".join(f'<span class="nf-chip out">🚫 {RESTRICCIONES[r]}</span>' for r in perfil["restricciones"])
    partes += "".join(f'<span class="nf-chip">⭐ {g}</span>' for g in perfil["gustos"][:6])
    return partes or '<span class="nf-sub">Sin restricciones guardadas</span>'


# ---- Navegacion y estado ----
def ir_a(paso):
    st.session_state.paso = paso


def ir_perfil():
    """Abre el perfil recordando de donde venia (para volver al mismo punto del flujo)."""
    st.session_state.volver_a = st.session_state.paso if st.session_state.paso != "perfil" else 1
    st.session_state.paso = "perfil"


def salir_perfil():
    st.session_state.paso = st.session_state.get("volver_a", 1)


def elegir(id_alt):
    st.session_state.alt_id = id_alt
    ir_a(5)


def limpiar_widgets_perfil():
    """Borra el estado de los campos del formulario para que vuelvan a leer el perfil guardado."""
    for clave in [k for k in st.session_state if str(k).startswith("pl_")]:
        del st.session_state[clave]


def restablecer_perfil():
    st.session_state.perfil = perfil_inicial()
    limpiar_widgets_perfil()


def reiniciar():
    """Vuelve al inicio. El PERFIL (plan, restricciones, gustos, pago) se conserva."""
    for clave in ("paso", "datos", "comida_id", "alt_id", "reserva"):
        st.session_state.pop(clave, None)
    for clave in [k for k in st.session_state if str(k).startswith(("em_", "t_"))]:
        del st.session_state[clave]


# ============================================================
# 4) ESTADO DE LA SESION (aqui se "simula" la persistencia)
# ============================================================
# st.session_state vive mientras la pestana del navegador siga abierta. En produccion, 'perfil' se leeria/guardaria
# en una base de datos (p. ej. Supabase/Firestore) con el usuario autenticado.
if "perfil" not in st.session_state:
    st.session_state.perfil = perfil_inicial()
perfil = st.session_state.perfil
if "paso" not in st.session_state:
    st.session_state.paso = 1
if "datos" not in st.session_state:
    # Solo lo que cambia en cada imprevisto. Restricciones y gustos vienen del perfil.
    st.session_state.datos = {"motivo": MOTIVOS[0], "tiempo": 15, "presupuesto": perfil["presupuesto"],
                              "solo_eq": False}
if "comida_id" not in st.session_state:
    st.session_state.comida_id = "almuerzo"
st.session_state.setdefault("historial", [])

# Salvaguardas de navegacion (p. ej. si se recarga a mitad del flujo)
if st.session_state.paso in (5, 6, 7) and "alt_id" not in st.session_state:
    st.session_state.paso = 4
if st.session_state.paso == 7 and "reserva" not in st.session_state:
    st.session_state.paso = 6
if st.session_state.comida_id not in [c["id"] for c in perfil["plan"]]:
    st.session_state.comida_id = perfil["plan"][0]["id"]

# ONBOARDING OBLIGATORIO: mientras el perfil no este configurado, la unica pantalla accesible es la de personalizacion.
# Al guardar por primera vez, perfil["configurado"] pasa a True y salir_perfil() lleva al Paso 1.
onboarding = not perfil["configurado"]
if onboarding:
    st.session_state.paso = "perfil"
    st.session_state.volver_a = 1

paso = st.session_state.paso
datos = st.session_state.datos

# ============================================================
# 5) ENCABEZADO NUTRIFLEX E INDICADOR DE PASOS
# ============================================================
html("""
<div class="nf-hero">
  <div class="nf-logo">NUTRI<span>FLEX</span></div>
  <div class="nf-tag">Tu plan de alimentación, flexible cuando la rutina cambia 🥗</div>
</div>
""")
if paso == "perfil":
    html(f'<div class="nf-steplabel">{"Bienvenido · Configuración inicial" if onboarding else "Mi perfil y dieta"}</div>')
else:
    puntos = "".join(
        f'<div class="nf-dot {"done" if n < paso else "act" if n == paso else ""}"></div>' for n in range(1, 8)
    )
    html(f'<div class="nf-steplabel">Paso {paso} de 7 · {NOMBRES_PASOS[paso - 1]}</div><div class="nf-steps">{puntos}</div>')

# ============================================================
# 6) PERFIL - PERSONALIZAR MI DIETA
# ============================================================
if paso == "perfil":
    meta = perfil["meta"]
    if onboarding:
        st.subheader("👋 ¡Bienvenido a NUTRIFLEX!")
        html("""
        <div class="nf-card dark">
          <h4>Antes de empezar, personaliza tu dieta</h4>
          <div class="nf-sub">Así las recomendaciones serán realmente tuyas. Te dejamos un plan de ejemplo como punto de partida: ajústalo o déjalo como está. Solo lo haces una vez.</div>
        </div>
        """)
    else:
        st.subheader("⚙️ Personaliza tu dieta")
        st.caption("Configúralo una sola vez: cuando tengas un imprevisto, NUTRIFLEX ya sabrá tus metas, restricciones y gustos.")

    modo = st.radio("Quiero definir mis macros en:", ["Gramos", "Porcentaje de calorías"], horizontal=True, key="pf_modo")

    # --- Formulario: nada se guarda hasta pulsar "Guardar" (evita reruns por cada tecla) ---
    with st.form("form_perfil", border=False):
        tab_metas, tab_rest, tab_plan = st.tabs(["🎯 Metas", "🚫 Restricciones y gustos", "🍽️ Mi plan"])

        with tab_metas:
            nombre = st.text_input("¿Cómo te llamas? (opcional)", value=perfil["nombre"], placeholder="Ej.: Antonio")
            kcal_meta = st.number_input("Meta diaria de calorías (kcal)", 1000, 6000, int(meta["kcal"]), step=50)
            c1, c2, c3 = st.columns(3)
            if modo == "Gramos":
                nuevos = {
                    "prot": c1.number_input("Proteína (g)", 0, 500, int(meta["prot"]), step=5),
                    "carb": c2.number_input("Carbo (g)", 0, 800, int(meta["carb"]), step=5),
                    "gras": c3.number_input("Grasas (g)", 0, 300, int(meta["gras"]), step=5),
                }
            else:
                nuevos = {
                    "prot": c1.number_input("Proteína (%)", 0, 100, round(meta["prot"] * 4 / meta["kcal"] * 100), step=5),
                    "carb": c2.number_input("Carbo (%)", 0, 100, round(meta["carb"] * 4 / meta["kcal"] * 100), step=5),
                    "gras": c3.number_input("Grasas (%)", 0, 100, round(meta["gras"] * 9 / meta["kcal"] * 100), step=5),
                }
            st.caption("Referencia: proteína y carbohidratos aportan 4 kcal por gramo; las grasas, 9 kcal.")

        with tab_rest:
            restricciones = st.multiselect(
                "Alergias o alimentos que no puedes consumir", list(RESTRICCIONES), default=perfil["restricciones"],
                format_func=lambda r: RESTRICCIONES[r], placeholder="Elige las que apliquen")
            extras = [g for g in perfil["gustos"] if g not in GUSTOS_SUGERIDOS]
            gustos = st.multiselect("Gustos y preferencias", GUSTOS_SUGERIDOS,
                                    default=[g for g in perfil["gustos"] if g in GUSTOS_SUGERIDOS], placeholder="Elige tus favoritos")
            otros = st.text_input("Otros gustos (separados por coma)", value=", ".join(extras), placeholder="Ej.: salmón, arepa, mango")
            st.caption("Estas preferencias se usan en cada imprevisto: nunca tendrás que escribirlas de nuevo.")

        with tab_plan:
            st.caption("Edita tu plan de hoy: Traducomida usará exactamente estos valores para calcular equivalencias.")
            plan_nuevo = []
            for c in perfil["plan"]:
                p = f"pl_{c['id']}_"
                with st.expander(f"{c['hora']} · {c['nombre']} — {c['plato']}"):
                    plato = st.text_input("Plato", value=c["plato"], key=p + "plato")
                    hora = st.time_input("Hora", value=datetime.strptime(c["hora"], "%H:%M").time(), key=p + "hora")
                    k1, k2 = st.columns(2)
                    kcal = k1.number_input("Calorías (kcal)", 50, 2500, int(c["kcal"]), step=10, key=p + "kcal")
                    prot = k2.number_input("Proteína (g)", 0, 250, int(c["prot"]), key=p + "prot")
                    k3, k4 = st.columns(2)
                    carb = k3.number_input("Carbohidratos (g)", 0, 400, int(c["carb"]), key=p + "carb")
                    gras = k4.number_input("Grasas (g)", 0, 200, int(c["gras"]), key=p + "gras")
                plan_nuevo.append({"id": c["id"], "nombre": c["nombre"], "plato": plato.strip() or c["plato"],
                                   "hora": hora.strftime("%H:%M"), "kcal": int(kcal), "prot": int(prot),
                                   "carb": int(carb), "gras": int(gras)})

        guardar = st.form_submit_button("Guardar y empezar ✔" if onboarding else "Guardar mi dieta ✔", type="primary", width="stretch")

    if guardar:
        if modo == "Gramos":
            macros_g = {k: int(v) for k, v in nuevos.items()}
        elif abs(sum(nuevos.values()) - 100) > 1:
            macros_g = None
            st.error(f"Los porcentajes suman {sum(nuevos.values())}%. Ajústalos para que lleguen a 100% y guardamos.")
        else:
            macros_g = {"prot": round(kcal_meta * nuevos["prot"] / 100 / 4), "carb": round(kcal_meta * nuevos["carb"] / 100 / 4),
                        "gras": round(kcal_meta * nuevos["gras"] / 100 / 9)}
        if macros_g is not None:
            lista_gustos = list(gustos) + [g.strip().lower() for g in otros.split(",") if g.strip()]
            perfil.update({
                "configurado": True, "nombre": nombre.strip(),
                "meta": {"kcal": int(kcal_meta), **macros_g},
                "restricciones": list(restricciones),
                "gustos": list(dict.fromkeys(lista_gustos)),
                "plan": sorted(plan_nuevo, key=lambda c: c["hora"]),
            })
            kcal_macros = 4 * macros_g["prot"] + 4 * macros_g["carb"] + 9 * macros_g["gras"]
            if abs(kcal_macros - kcal_meta) / kcal_meta > 0.10:
                st.session_state.aviso = (f"Tus macros suman {kcal_macros} kcal y tu meta es {int(kcal_meta)} kcal. "
                                          "Puedes dejarlo así o ajustarlo cuando quieras en tu perfil.")
            else:
                st.session_state.aviso = "¡Listo! Guardamos tu dieta. Tu botón de imprevisto ya la usa."
            limpiar_widgets_perfil()
            salir_perfil()
            st.rerun()

    if not onboarding:  # en la configuracion inicial no hay a donde volver
        st.button("← Volver sin cambiar nada", width="stretch", on_click=salir_perfil)
        st.button("↺ Restablecer datos de ejemplo", width="stretch", on_click=restablecer_perfil)

# ============================================================
# 7) PASO 1 - INICIO: PLAN DE ALIMENTACION Y ACCESO RAPIDO AL IMPREVISTO
# ============================================================
elif paso == 1:
    aviso = st.session_state.pop("aviso", None)
    if aviso:
        exito(aviso)
    plan, meta = perfil["plan"], perfil["meta"]
    tot = totales(plan)

    if perfil["nombre"]:
        html(f'<div class="nf-comida" style="margin:0 2px 8px 2px">Hola, {perfil["nombre"]} 👋</div>')

    # CTA principal arriba: en un imprevisto la persona va con prisa
    st.button("🚨 Tuve un imprevisto", type="primary", width="stretch", on_click=ir_a, args=(2,))
    st.button("⚙️ Editar mi perfil y plan", width="stretch", on_click=ir_perfil)

    html(f"""
    <div class="nf-card dark" style="margin-top:12px">
      <h4>Tu plan de hoy</h4>
      <div class="nf-total">
        <div><b>{len(plan)}</b><small>comidas</small></div>
        <div><b>{tot['kcal']}</b><small>kcal</small></div>
        <div><b>{tot['prot']} g</b><small>proteína</small></div>
      </div>
      <div style="margin-top:12px">
        {barra('Calorías', tot['kcal'], meta['kcal'], 'kcal')}
        {barra('Proteína', tot['prot'], meta['prot'], 'g')}
        {barra('Carbohidratos', tot['carb'], meta['carb'], 'g')}
        {barra('Grasas', tot['gras'], meta['gras'], 'g')}
      </div>
    </div>
    """)
    html(f'<div class="nf-card"><div class="nf-sub"><b>Tus restricciones y gustos</b> (ya guardados)</div>{chips_restricciones(perfil)}</div>')
    for c in plan:
        html(f"""
        <div class="nf-card">
          <div class="nf-row"><span class="nf-comida">{c['nombre']}</span><span class="nf-hora">{c['hora']}</span></div>
          <div class="nf-sub">{c['plato']}</div>
          <span class="nf-chip">🔥 {c['kcal']} kcal</span><span class="nf-chip">💪 {c['prot']} g proteína</span>
          <span class="nf-chip out">🍚 {c['carb']} g</span><span class="nf-chip out">🥑 {c['gras']} g</span>
        </div>
        """)
    # Historial de imprevistos resueltos (solo sesion actual)
    historial = st.session_state.historial
    if historial:
        filas = "".join(
            f"""<div class="nf-hist"><div class="nf-comida" style="font-size:.95rem">{h['comida']} → {h['alt']}</div>
            <div class="nf-sub">Era: {h['plato']} · 📍 {h['lugar']}</div>
            <span class="nf-chip">🔥 {signo(h['dkcal'])} kcal</span><span class="nf-chip">💪 {signo(h['dprot'])} g</span></div>"""
            for h in reversed(historial[-3:])
        )
        html(f"""
        <div class="nf-card">
          <h4>✅ Imprevistos resueltos</h4>
          <div class="nf-sub">Has resuelto <b>{len(historial)}</b> imprevisto(s) en esta sesión, sin perder el rumbo.</div>
          {filas}
        </div>
        """)
    else:
        st.caption("Aún no has resuelto ningún imprevisto en esta sesión.")

# ============================================================
# 8) PASO 2 - BOTON DE EMERGENCIA
# ============================================================
elif paso == 2:
    html("""
    <div class="nf-card dark">
      <h4>No pasa nada, podemos ajustar tu plan 💚</h4>
      <div class="nf-sub">Un cambio de rutina no es un incumplimiento. Dinos qué comida no podrás tomar y buscamos una alternativa.</div>
    </div>
    """)
    opciones = {c["id"]: f"{c['hora']} · {c['nombre']} — {c['plato']}" for c in perfil["plan"]}
    st.session_state.setdefault("em_comida", st.session_state.comida_id)
    st.session_state.comida_id = st.radio("¿Qué comida se ve afectada?", list(opciones), format_func=lambda k: opciones[k], key="em_comida")
    col1, col2 = st.columns(2)
    col1.button("← Volver", width="stretch", on_click=ir_a, args=(1,))
    col2.button("Continuar →", type="primary", width="stretch", on_click=ir_a, args=(3,))

# ============================================================
# 9) PASO 3 - ANALISIS DE SITUACION (solo lo que cambia hoy)
# ============================================================
elif paso == 3:
    st.subheader("Cuéntanos tu situación")
    html(f'<div class="nf-card"><div class="nf-sub"><b>✓ Ya tenemos tus restricciones y gustos</b></div>{chips_restricciones(perfil)}</div>')
    st.button("✏️ Editar restricciones y gustos", width="stretch", on_click=ir_perfil)

    # Los widgets usan 'key' + setdefault para conservar su valor al ir y volver entre pasos
    for k, v in (("em_motivo", datos["motivo"]), ("em_tiempo", datos["tiempo"]), ("em_presupuesto", datos["presupuesto"])):
        st.session_state.setdefault(k, v)
    datos["motivo"] = st.selectbox("¿Qué pasó?", MOTIVOS, key="em_motivo")
    datos["tiempo"] = st.select_slider("Tiempo disponible para comer (min)", options=TIEMPOS, key="em_tiempo")
    datos["presupuesto"] = st.slider("Presupuesto máximo", 5000, 40000, step=1000, format="$%d", key="em_presupuesto")

    def guardar_y_buscar():
        perfil["presupuesto"] = datos["presupuesto"]  # recordamos el presupuesto para la proxima vez
        ir_a(4)

    col1, col2 = st.columns(2)
    col1.button("← Volver", width="stretch", on_click=ir_a, args=(2,))
    col2.button("Ver alternativas →", type="primary", width="stretch", on_click=guardar_y_buscar)

# ============================================================
# 10) PASO 4 - ALTERNATIVAS (por tiempo, con desviacion frente al plan)
# ============================================================
elif paso == 4:
    original = buscar_comida(st.session_state.comida_id)
    html(f"""
    <div class="nf-card dark">
      <h4>Alternativas para tu {original['nombre'].lower()}</h4>
      <div class="nf-sub">Reemplazan: {original['plato']}</div>
      <span class="nf-chip">🔥 {original['kcal']} kcal</span><span class="nf-chip">💪 {original['prot']} g</span>
      <span class="nf-chip">⏱️ {datos['tiempo']} min</span><span class="nf-chip">💵 hasta {formato_cop(datos['presupuesto'])}</span>
    </div>
    """)
    # Filtros rapidos: pills multiseleccion (se combinan). El valor se conserva en datos["filtros"].
    datos.setdefault("filtros", [])
    st.session_state.setdefault("t_filtros", datos["filtros"])
    datos["filtros"] = st.pills("Filtros rápidos", FILTROS_RAPIDOS, selection_mode="multi", key="t_filtros",
                                label_visibility="collapsed") or []
    st.session_state.setdefault("t_eq", datos["solo_eq"])
    with st.container(key="card_toggle"):
        datos["solo_eq"] = st.toggle("✓ Mostrar solo equivalentes", key="t_eq")

    base = alternativas_posibles(original, datos, perfil)
    posibles = aplicar_filtros(base, datos["filtros"])
    barato = "💵 Más barato" in datos["filtros"]
    n_eq = sum(es_equivalente(original, a) for a in posibles)
    if not base:
        st.warning("No encontramos opciones con esas condiciones, y eso es normal en días apretados. "
                   "Prueba con un poco más de tiempo o de presupuesto.")
    elif not posibles:
        aviso_suave("Ninguna opción cumple todos los filtros activos. Quita alguno para ver más alternativas.")
    else:
        orden = "de la más barata a la más cara" if barato else "de la más rápida a la más lenta"
        activos = f" · filtros: {len(datos['filtros'])}" if datos["filtros"] else ""
        st.caption(f"{len(posibles)} opciones · {n_eq} equivalentes a tu plan · {orden}{activos}")
    html('<div class="nf-sub"><span class="nf-badge-ok">✓ Equivalente</span> = dentro de tu rango &nbsp;·&nbsp; '
         '<span class="nf-badge-no">Se aleja</span> = te mostramos cuánto</div>')

    etiquetas = {5: "Listas en 5 min o menos", 10: "Listas en 6 a 10 min", 15: "Listas en 11 a 15 min", 30: "Listas en 16 a 30 min"}
    if barato:  # con "Más barato" se muestra una sola lista ordenada por precio
        grupos = [("💵 Ordenadas por precio", posibles)]
    else:       # orden principal: por tiempo, en franjas
        grupos = [(f"⏱️ {etiquetas[hi]}", [a for a in posibles if lo < a["min"] <= hi])
                  for lo, hi in [(0, 5), (5, 10), (10, 15), (15, 30)]]
    for titulo, grupo in grupos:
        if not grupo:
            continue
        html(f'<span class="nf-band">{titulo}</span>')
        for a in grupo:
            eq = es_equivalente(original, a)
            estrella = " ⭐" if le_gusta(a, perfil["gustos"]) else ""
            insignia = '<span class="nf-badge-ok">✓ Equivalente</span>' if eq else '<span class="nf-badge-no">Se aleja del plan</span>'
            porque = "" if eq else f'<div class="nf-why">Se aleja porque {" y ".join(motivos_alejamiento(original, a))}.</div>'
            with st.container(key=f"card_{'eq' if eq else 'no'}_{a['id']}"):
                html(f"""
                <div class="nf-row"><span class="nf-comida">{a['nombre']}{estrella}</span>{insignia}</div>
                <div class="nf-sub">📍 {a['lugar']} · {a['dist']}</div>
                <span class="nf-chip">⏱️ {a['min']} min</span><span class="nf-chip">💵 {formato_cop(a['precio'])}</span>
                <span class="nf-chip">🔥 {a['kcal']} kcal</span><span class="nf-chip">💪 {a['prot']} g</span>
                <div class="nf-sub" style="margin-top:8px">Frente a tu plan:</div>
                {chips_desviacion(original, a)}
                {porque}
                """)
                st.button("Elegir esta opción", key=f"elegir_{a['id']}", type="primary" if eq else "secondary",
                          width="stretch", on_click=elegir, args=(a["id"],))
    st.button("← Cambiar mi situación", width="stretch", on_click=ir_a, args=(3,))

# ============================================================
# 11) PASO 5 - TRADUCOMIDA: REEMPLAZO NUTRICIONALMENTE EQUIVALENTE
# ============================================================
elif paso == 5:
    original = buscar_comida(st.session_state.comida_id)
    alt = buscar_alternativa(st.session_state.alt_id)
    st.subheader("🔄 Traducomida")
    st.caption("Traducimos tu comida planeada a una alternativa equivalente")
    d = desviacion(original, alt)
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
          <span class="nf-chip">🔥 {alt['kcal']} kcal ({signo(d['kcal'])})</span><span class="nf-chip">💪 {alt['prot']} g ({signo(d['prot'])})</span>
        </div>
        """)
    # Detalle de desviacion con los 4 nutrientes
    filas = "".join(
        f"<div class='nf-line'><span>{n}</span><span>{original[k]} → <b>{alt[k]}</b> {u} ({signo(d[k])})</span></div>"
        for k, n, u in [("kcal", "Calorías", "kcal")] + [(k, n, u) for k, n, u in MACROS]
    )
    html(f'<div class="nf-card dark"><h4>Diferencia frente a tu plan</h4>{filas}</div>')

    if es_equivalente(original, alt):
        exito("¡Buena elección! Mantiene tus calorías y tu proteína dentro del rango de tu plan.")
    else:
        st.warning(f"Se aleja un poco de tu plan: {' y '.join(motivos_alejamiento(original, alt))}. "
                   "Puedes elegirla igual, un día flexible no es un fallo, o mirar opciones más cercanas.")

    otras = [a for a in alternativas_posibles(original, datos, perfil) if es_equivalente(original, a) and a["id"] != alt["id"]]
    if otras:
        st.markdown("##### Otras opciones equivalentes")
        for a in otras:
            with st.container(key=f"card_eq_otra_{a['id']}"):
                html(f"""
                <span class="nf-comida">{a['nombre']}</span>
                <div class="nf-sub">📍 {a['lugar']} · {a['dist']} · ⏱️ {a['min']} min · 💵 {formato_cop(a['precio'])}</div>
                {chips_desviacion(original, a)}
                """)
                st.button("Cambiar por esta", key=f"cambiar_{a['id']}", width="stretch",
                          on_click=lambda i=a["id"]: st.session_state.update(alt_id=i))
    col1, col2 = st.columns(2)
    col1.button("← Alternativas", width="stretch", on_click=ir_a, args=(4,))
    col2.button("Reservar →", type="primary", width="stretch", on_click=ir_a, args=(6,))

# ============================================================
# 12) PASO 6 - RESERVA ANTICIPADA + PAGO SIMULADO
# ============================================================
elif paso == 6:
    alt = buscar_alternativa(st.session_state.alt_id)
    st.subheader("Reserva y paga tu comida")
    html(f"""
    <div class="nf-card dark">
      <h4>{alt['nombre']}</h4>
      <div class="nf-sub">📍 {alt['lugar']} · {alt['dist']}</div>
      <div class="nf-sub">🥕 {alt['ingredientes']}</div>
      <span class="nf-chip">⏱️ lista en {alt['min']} min</span>
    </div>
    """)
    horas = sorted({alt["min"], *[m for m in (10, 15, 20, 30, 45, 60) if m > alt["min"]]})
    espera = st.selectbox("¿En cuántos minutos la recoges?", horas, format_func=lambda m: f"En {m} min")
    nota = st.text_input("Nota para el punto de venta (opcional)", placeholder="Ej.: sin aguacate")

    html('<div class="nf-comida" style="margin:6px 0 2px 0">Pago</div>')
    pago_prev = perfil["pago"]
    metodo = st.radio("Método de pago", METODOS_PAGO, horizontal=True,
                      index=METODOS_PAGO.index(pago_prev["metodo"]) if pago_prev["metodo"] in METODOS_PAGO else 0)
    referencia = metodo  # Nequi, Daviplata y Efectivo en el punto: solo se elige el metodo
    if metodo == "Tarjeta":
        numero = st.text_input("Número de tarjeta", value="4242 4242 4242 4242")
        c1, c2 = st.columns(2)
        c1.text_input("Vence", value="12/29")
        c2.text_input("CVV", value="123", type="password")
        digitos = "".join(ch for ch in numero if ch.isdigit())
        referencia = f"Tarjeta •••• {digitos[-4:]}" if len(digitos) >= 12 else None
    fee = comision(alt["precio"])
    total = alt["precio"] + fee
    html(f"""
    <div class="nf-card dark">
      <div class="nf-line"><span>{alt['nombre']}</span><span>{formato_cop(alt['precio'])}</span></div>
      <div class="nf-line"><span>Comisión NutriFlex</span><span>{formato_cop(fee)}</span></div>
      <div class="nf-pay"><span>Total a pagar</span><span style="color:{SALMON}">{formato_cop(total)}</span></div>
    </div>
    """)

    col1, col2 = st.columns(2)
    col1.button("← Volver", width="stretch", on_click=ir_a, args=(5,))
    if col2.button("Pagar y reservar 🔒", type="primary", width="stretch"):
        if referencia is None:
            st.error("Revisa los datos de pago: parece que falta algún número. No se ha cobrado nada.")
        else:
            with st.spinner("Procesando tu pago seguro..."):
                time.sleep(1.3)  # simula la latencia de la pasarela de pagos
            perfil["pago"] = {"metodo": metodo, "ultimos4": referencia[-4:] if metodo == "Tarjeta" else ""}
            st.session_state.reserva = {
                "espera": espera, "nota": nota, "pago": referencia, "total": total, "comision": fee,
                "codigo": f"NF-{alt['id']:02d}{espera:02d}", "recibo": f"TX{int(time.time()) % 100000:05d}",
            }
            original = buscar_comida(st.session_state.comida_id)
            st.session_state.historial.append({
                "comida": original["nombre"], "plato": original["plato"], "alt": alt["nombre"], "lugar": alt["lugar"],
                "total": total, "dkcal": alt["kcal"] - original["kcal"], "dprot": alt["prot"] - original["prot"],
            })
            ir_a(7)
            st.rerun()

# ============================================================
# 13) PASO 7 - CONFIRMACION
# ============================================================
else:
    alt = buscar_alternativa(st.session_state.alt_id)
    reserva = st.session_state.reserva
    original = buscar_comida(st.session_state.comida_id)
    meta = perfil["meta"]
    efectivo = reserva["pago"] == "Efectivo en el punto"
    nota = f"<div class='nf-sub'>📝 {reserva['nota']}</div>" if reserva["nota"] else ""
    barras = "".join(
        f"<div class='nf-sub'>{n} · <b>{v} g</b></div><div class='nf-bar'><div style='width:{min(100, v / tope * 100):.0f}%'></div></div>"
        for n, v, tope in [("Proteína", alt["prot"], 60), ("Carbohidratos", alt["carb"], 100), ("Grasas", alt["gras"], 40)]
    )
    # Dia completo tras el cambio: total del plan - comida original + alternativa
    tot = totales(perfil["plan"])
    dia = {k: tot[k] - original[k] + alt[k] for k in tot}
    html(f"""
    <div class="nf-card dark">
      <h4>🎉 {"¡Reserva confirmada!" if efectivo else "¡Reserva confirmada y pagada!"}</h4>
      <div class="nf-comida" style="color:{BEIGE}">{alt['nombre']}</div>
      <div class="nf-sub">📍 {alt['lugar']} · 🕒 recógela en {reserva['espera']} min</div>
      <div class="nf-sub">{"💵 Pagas " + formato_cop(reserva['total']) + " en el punto" if efectivo else "💳 " + formato_cop(reserva['total']) + " · " + reserva['pago']} · recibo {reserva['recibo']}</div>
      {nota}
      <div class="nf-ticket">Código de reserva<br><b>{reserva['codigo']}</b></div>
    </div>
    <div class="nf-card dark">
      <h4>Información nutricional</h4>
      <div class="nf-total"><div><b>{alt['kcal']}</b><small>kcal</small></div></div>
      {barras}
      {chips_desviacion(original, alt)}
      <div class="nf-sub" style="margin-top:8px">Reemplaza tu {original['nombre'].lower()} planeado ({original['kcal']} kcal · {original['prot']} g de proteína).</div>
    </div>
    <div class="nf-card dark">
      <h4>Tu día sigue en marcha 💚</h4>
      {barra('Calorías del día', dia['kcal'], meta['kcal'], 'kcal')}
      {barra('Proteína del día', dia['prot'], meta['prot'], 'g')}
      <div class="nf-sub">Un imprevisto no cambia tu objetivo: ya ajustamos tu plan de hoy.</div>
    </div>
    """)
    st.button("Volver al inicio", type="primary", width="stretch", on_click=reiniciar)

# ============================================================
# 14) COMO EJECUTAR Y DESPLEGAR
# ============================================================
# EJECUTAR EN LOCAL
#   1. Instala Python 3.9+ y luego:   pip install -r requirements.txt     (solo necesita streamlit>=1.50)
#   2. Desde la carpeta del proyecto: streamlit run app.py
#   3. Abre http://localhost:8501 y, en el navegador, activa la vista de movil (F12 -> Ctrl+Shift+M).
#
# DESPLEGAR (gratis)
#   * Streamlit Community Cloud: sube app.py, requirements.txt y .streamlit/config.toml a un repositorio de GitHub,
#     entra a share.streamlit.io, elige el repositorio y "app.py" como archivo principal. Listo.
#   * Hugging Face Spaces: crea un Space con SDK "Streamlit" y sube los mismos archivos.
#
# NOTAS
#   * Persistencia: el perfil vive en st.session_state (por sesion). Para persistencia real, conecta una base de
#     datos en las funciones donde se asigna st.session_state.perfil (inicio del archivo y al guardar el perfil).
#   * El pago es 100% simulado: no se envia ni se guarda ningun dato de pago.
#   * .streamlit/config.toml fija el tema claro para que los colores se vean igual en cualquier dispositivo.