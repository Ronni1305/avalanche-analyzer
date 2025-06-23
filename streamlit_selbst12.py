import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Initialisierung der Session State ---
defaults = {
    'ns_value': 0,
    'temp_value': 0,
    'stunden_value': 0
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

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
    }
}

# Initialisiere Radiobutton-Auswahl
for frage in fragen_definitions.keys():
    if f'radio_{frage}' not in st.session_state:
        st.session_state[f'radio_{frage}'] = ""

# --- UI: Titel ---
st.title("Selbstauslösung von Neuschnee-Lawinen")
st.markdown("Bewertung basierend auf Ampelsystem")

# --- Eingabebereich für Setzung ---
st.header("Setzungsabschätzung basierend auf Neuschnee, Temperatur und Zeit")
col1, col2, col3 = st.columns(3)

with col1:
    ns = st.number_input("Neuschneemenge (cm)", min_value=0, max_value=200, step=5, value=st.session_state.ns_value, key='ns_input')
with col2:
    temp = st.number_input("Temperatur (°C)", min_value=-30, max_value=15, step=1, value=st.session_state.temp_value, key='temp_input')
with col3:
    stunden = st.number_input("vergangene Stunden", min_value=0, max_value=100, step=1, value=st.session_state.stunden_value, key='stunden_input')

# Update session state
st.session_state.ns_value = ns
st.session_state.temp_value = temp
st.session_state.stunden_value = stunden

# --- Berechnungsfunktion ---
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

# --- Berechnung ausführen, auch wenn Temperatur = 0 ---
automatische_setzung, punktwert_setzung = "", 0
if ns > 0 and stunden > 0:
    automatische_setzung, punktwert_setzung = berechne_setzung_excel(ns, temp, stunden)

    farbe = "#ff4b4b" if automatische_setzung.startswith("1") else \
            "#ffa500" if automatische_setzung.startswith("2") else \
            "#4CAF50"

    st.markdown(f"""
        <div style='padding: 10px; background-color: {farbe}; color: white; border-radius: 8px; text-align: center;'>
            <strong>Automatische Setzung:</strong><br>{automatische_setzung}
        </div>
    """, unsafe_allow_html=True)

# --- Formular für weitere Risikofaktoren ---
punkte = []
auswahl_typen = []
faktor_namen = []

with st.form("lawinen_form_main"):
    for frage, optionen in fragen_definitions.items():
        auswahl = st.radio(
            frage,
            list(optionen.keys()),
            index=list(optionen.keys()).index(st.session_state[f'radio_{frage}']) if st.session_state[f'radio_{frage}'] in optionen else 0,
            key=f'radio_{frage}'
        )
        if auswahl != "":
            punkte.append(optionen[auswahl])
            auswahl_typen.append(auswahl[0])
            faktor_namen.append(frage)

    submitted = st.form_submit_button("Bewerten")

# --- Zurücksetzen ---
if st.button("🔄 Zurücksetzen"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- Bewertung und Anzeige ---
if submitted:
    typ1 = auswahl_typen.count("1")
    typ2 = auswahl_typen.count("2")
    typ3 = auswahl_typen.count("3")

    if max(typ1, typ2, typ3) >= 3:
        gesamtpunkte = sum(punkte)
        gefahrenindex = gesamtpunkte / len(punkte) if punkte else 0

        st.subheader(f"Gefahrenindex: {gefahrenindex:.2f}")

        farbe_box = "#ff4b4b" if gefahrenindex >= 3.3 else "#ffa500" if gefahrenindex >= 2.2 else "#4CAF50"
        text_box = "⚠️ <strong>Hohe Lawinengefahr</strong><br>Besondere Vorsicht notwendig!" if gefahrenindex >= 3.3 else \
                   "⚠️ <strong>Moderate Lawinengefahr</strong><br>Erhöhte Vorsicht erforderlich." if gefahrenindex >= 2.2 else \
                   "✅ <strong>Geringe Lawinengefahr</strong>"

        st.markdown(f"""
            <div style='padding: 20px; background-color: {farbe_box}; color: white; border-radius: 10px; text-align: center;'>
                {text_box}
            </div>
        """, unsafe_allow_html=True)

        # Farbskala anzeigen
        st.subheader("Gefahrenindex auf Skala")
        fig, ax = plt.subplots(figsize=(6, 1.5))
        cmap = plt.cm.colors.ListedColormap(['#4CAF50', '#ffa500', '#ff4b4b'])
        bounds = [1.95, 2.2, 3.3, 3.65]
        norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)
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
