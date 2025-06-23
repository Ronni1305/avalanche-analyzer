import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Initialisierung der Session State ---
def initialize_state():
    st.session_state.setdefault('ns_value', 0)
    st.session_state.setdefault('temp_value', 0)
    st.session_state.setdefault('stunden_value', 0)
    st.session_state.setdefault('setzung_visible', False)
    for frage in fragen_definitions:
        st.session_state.setdefault(f"radio_{frage}", "")

fragen_definitions = {
    "Neuschneemenge (24h)": {
        "": 0,
        "1: > 40 cm / Tag": 4,
        "2: 20–40 cm / Tag": 2.5,
        "3: < 20 cm / Tag": 2
    },
    "Regenmenge": {
        "": 0,
        "1: starker Regen (> 5 mm)": 4,
        "2: leichter Regen (< 5 mm)": 2.5,
        "3: kein Regen": 3
    },
    "Erwärmung": {
        "": 0,
        "1: > 4 °C Erwärmung": 3.5,
        "2: bis 4 °C Erwärmung": 2,
        "3: kalt oder keine Erwärmung": 3
    },
    "Schneedecken-Stabilität": {
        "": 0,
        "1: Altschnee mitgerissen": 4,
        "2: nicht tragfähiger Harschdeckel": 2.5,
        "3: tragfähiger Harschdeckel oder keine Schwachschicht": 1
    },
    "Verbindung zur Altschneedecke": {
        "": 0,
        "1: schlecht (kaltes Einschneien)": 3,
        "2: Beginn bei 0–2 °C": 2,
        "3: gut (Regen, dann Temperaturabfall)": 1
    },
    "Wind/Verfrachtung": {
        "": 0,
        "1: starker Wind (> 40 km/h)": 3,
        "2: mäßiger Wind (< 40 km/h)": 2,
        "3: kein/wenig Wind": 1
    },
    "Exposition/Sonneneinstrahlung": {
        "": 0,
        "1: starke Sonneneinstrahlung": 3.5,
        "2: mäßige Sonneneinstrahlung": 2.5,
        "3: kaum oder keine Sonneneinstrahlung": 2
    },
    "SSD (vSSD)": {
        "": 0,
        "1: schlechte Struktur (große Kristalle, weiche Schicht, dünn)": 4,
        "2: teils kritische Schwachschichten": 2.5,
        "3: stabile Struktur (kleine Kristalle, fest, dick)": 2
    },
    "Hangneigung / Exposition": {
        "": 0,
        "1: > 35° und ungünstige Exposition": 4,
        "2: 30–35° oder teils ungünstig": 2,
        "3: < 30° oder günstige Exposition": 1
    },
    "Setzung des Neuschnees": {
        "Zur Eingabe öffnen": None
    }
}

def berechne_setzung_excel(ns_val, temp_val, stunden_val):
    if stunden_val <= 0:
        return "", 0
    ln_teil = math.log(min(stunden_val, 72) + 1)
    setzungsgrad = min(100, ((0.4 * (temp_val + 5) * ln_teil) / 8) * 100)
    if setzungsgrad < 20:
        return ("1: (fast) keine Setzung", 3.5) if ns_val > 30 else ("2: mäßige Setzung", 2)
    elif setzungsgrad < 40:
        return ("1: (fast) keine Setzung", 3.5) if ns_val > 50 else ("2: mäßige Setzung", 2)
    else:
        return ("2: mäßige Setzung", 2) if ns_val > 80 else ("3: starke Setzung", 3.5)

# --- App Start ---
st.set_page_config(layout="wide")
st.title("Selbstauslösung von Neuschnee-Lawinen")
initialize_state()
punkte = []
auswahl_typen = []
faktor_namen = []

# --- Fragenformular ---
with st.form("lawinen_form_main"):
    show_setzung_panel = False

    for frage, optionen in fragen_definitions.items():
        if frage == "Setzung des Neuschnees":
            if st.form_submit_button("➕ Setzung des Neuschnees eingeben"):
                show_setzung_panel = True
            continue

        auswahl = st.radio(
            frage,
            list(optionen.keys()),
            index=list(optionen.keys()).index(st.session_state.get(f"radio_{frage}", "")),
            key=f"radio_{frage}"
        )
        if auswahl != "":
            punkte.append(optionen[auswahl])
            auswahl_typen.append(auswahl[0])
            faktor_namen.append(frage)

    submitted = st.form_submit_button("Bewerten")

# --- Setzungsfeld anzeigen ---
if show_setzung_panel or st.session_state.get('setzung_visible'):
    st.session_state['setzung_visible'] = True
    st.subheader("Setzungsabschätzung")

    ns = st.slider("Neuschneemenge (cm)", 0, 200, st.session_state.ns_value, step=5, key='ns_input_slider')
    temp = st.slider("Temperatur (°C)", -30, 15, st.session_state.temp_value, step=1, key='temp_input_slider')
    stunden = st.slider("vergangene Stunden", 0, 100, st.session_state.stunden_value, step=1, key='stunden_input_slider')

    st.session_state.ns_value = ns
    st.session_state.temp_value = temp
    st.session_state.stunden_value = stunden

    automatische_setzung, punktwert_setzung = "", 0
    if ns > 0 and stunden > 0:
        automatische_setzung, punktwert_setzung = berechne_setzung_excel(ns, temp, stunden)
        punkte.append(punktwert_setzung)
        auswahl_typen.append(automatische_setzung[0])
        faktor_namen.append("Setzung des Neuschnees")

        farbe = "#ff4b4b" if automatische_setzung.startswith("1") else "#ffa500" if automatische_setzung.startswith("2") else "#4CAF50"
        st.markdown(f"""
            <div style='padding: 10px; background-color: {farbe}; color: white; border-radius: 8px; text-align: center;'>
                <strong>Automatische Setzung:</strong><br>{automatische_setzung}
            </div>
        """, unsafe_allow_html=True)

# --- Bewertung ---
if submitted:
    typ1 = auswahl_typen.count("1")
    typ2 = auswahl_typen.count("2")
    typ3 = auswahl_typen.count("3")
    if max(typ1, typ2, typ3) >= 3:
        gesamtpunkte = sum(punkte)
        gefahrenindex = gesamtpunkte / len(punkte)
        farbe_box = "#ff4b4b" if gefahrenindex >= 3.3 else "#ffa500" if gefahrenindex >= 2.2 else "#4CAF50"
        text_box = "⚠️ <strong>Hohe Lawinengefahr</strong><br>Besondere Vorsicht notwendig!" if gefahrenindex >= 3.3 else \
                   "⚠️ <strong>Moderate Lawinengefahr</strong><br>Erhöhte Vorsicht erforderlich." if gefahrenindex >= 2.2 else \
                   "✅ <strong>Geringe Lawinengefahr</strong>"

        st.markdown(f"""
            <div style='padding: 20px; background-color: {farbe_box}; color: white; border-radius: 10px; text-align: center;'>
                {text_box}
            </div>
        """, unsafe_allow_html=True)

        st.subheader("Gefahrenindex auf Skala")
        fig, ax = plt.subplots(figsize=(6, 1.5))
        cmap = plt.cm.colors.ListedColormap(['#4CAF50', '#ffa500', '#ff4b4b'])
        bounds = [1.95, 2.2, 3.3, 3.65]
        norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)
       
        min_scale_value = 1.0
        max_scale_value = 4.0

        gradient = np.linspace(1.0, 4.0, 400).reshape(1, -1)
        ax.imshow(gradient, extent=[1.0, 4.0, 0, 1], aspect='auto', cmap=cmap, norm=norm)
        ax.set_xlim(4.0, 1.0)
        ax.axhline(0.5, color='white', linestyle='--')
        ax.plot(gefahrenindex, 0.5, 'wo', markersize=10, markeredgecolor='black')
        ax.text(gefahrenindex, -0.3, f"{gefahrenindex:.2f}", ha='center', fontsize=10)
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.info("ℹ️ Bitte mindestens 3 Antworten mit dem gleichen Gefahren-Typ (1, 2 oder 3) auswählen.")

# --- Zurücksetzen ---
if st.button("🔄 Zurücksetzen"):
    st.session_state.clear()
    st.rerun()
