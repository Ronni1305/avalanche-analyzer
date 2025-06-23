import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Lawinenbewertung", layout="centered")

# --- Session State Initialisierung ---
fragen_definitions = {
    "Neuschneemenge (24h)": {"": 0, "1: > 40 cm / Tag": 4, "2: 20–40 cm / Tag": 2.5, "3: < 20 cm / Tag": 2},
    "Regenmenge": {"": 0, "1: starker Regen (> 5 mm)": 4, "2: leichter Regen (< 5 mm)": 2.5, "3: kein Regen": 3},
    "Erwärmung": {"": 0, "1: > 4 °C Erwärmung": 3.5, "2: bis 4 °C Erwärmung": 2, "3: kalt oder keine Erwärmung": 3},
    "Schneedecken-Stabilität": {"": 0, "1: Altschnee mitgerissen": 4, "2: nicht tragfähiger Harschdeckel": 2.5, "3: tragfähiger Harschdeckel oder keine Schwachschicht": 1},
    "Verbindung zur Altschneedecke": {"": 0, "1: schlecht (kaltes Einschneien)": 3, "2: Beginn bei 0–2 °C": 2, "3: gut (Regen, dann Temperaturabfall)": 1},
    "Wind/Verfrachtung": {"": 0, "1: starker Wind (> 40 km/h)": 3, "2: mäßiger Wind (< 40 km/h)": 2, "3: kein/wenig Wind": 1},
    "Exposition/Sonneneinstrahlung": {"": 0, "1: starke Sonneneinstrahlung": 3.5, "2: mäßige Sonneneinstrahlung": 2.5, "3: kaum oder keine Sonneneinstrahlung": 2},
    "SSD (vSSD)": {"": 0, "1: schlechte Struktur (große Kristalle, weich, dünn)": 4, "2: teils kritische Schwachschichten": 2.5, "3: stabile Struktur (klein, fest, dick)": 2},
    "Hangneigung / Exposition": {"": 0, "1: > 35° und ungünstige Exposition": 4, "2: 30–35° oder teils ungünstig": 2, "3: < 30° oder günstige Exposition": 1}
}

for frage in fragen_definitions:
    st.session_state.setdefault(f"radio_{frage}", "")

st.title("Selbstauslösung von Neuschnee-Lawinen")
st.markdown("Bewertung nach Ampelsystem")

punkte = []
auswahl_typen = []

with st.form("lawinen_form_main"):
    for frage, optionen in fragen_definitions.items():
        auswahl = st.radio(frage, list(optionen.keys()), index=list(optionen.keys()).index(st.session_state[f"radio_{frage}"]), key=f"radio_{frage}")
        if auswahl:
            punkte.append(optionen[auswahl])
            auswahl_typen.append(auswahl[0])

    # Setzungsbereich aufklappbar
    punktwert_setzung = 0
    with st.expander("➕ Setzung des Neuschnees eingeben"):
        ns = st.slider("Neuschneemenge (cm)", 0, 150, 0, 5)
        temp = st.slider("Temperatur (°C)", -20, 10, 0, 1)
        stunden = st.slider("vergangene Stunden", 0, 72, 0, 1)

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

        beschreibung, punktwert_setzung = berechne_setzung_excel(ns, temp, stunden)
        if beschreibung:
            farbe = "#ff4b4b" if beschreibung.startswith("1") else "#ffa500" if beschreibung.startswith("2") else "#4CAF50"
            st.markdown(f"""
                <div style='padding: 10px; background-color: {farbe}; color: white; border-radius: 8px; text-align: center;'>
                    <strong>Automatische Setzung:</strong><br>{beschreibung}
                </div>
            """, unsafe_allow_html=True)

    # Punktwert aus Setzung nur einbeziehen, wenn berechnet
    if punktwert_setzung:
        punkte.append(punktwert_setzung)
        auswahl_typen.append("S")

    st.form_submit_button("Bewerten")

# Nach Formularbewertung
if st.session_state.get("radio_Neuschneemenge (24h)"):
    von_typ1 = auswahl_typen.count("1")
    von_typ2 = auswahl_typen.count("2")
    von_typ3 = auswahl_typen.count("3")

    if any(x >= 3 for x in [von_typ1, von_typ2, von_typ3]):
        gefahrenindex = sum(punkte) / len(punkte) if punkte else 0
        st.subheader(f"Gefahrenindex: {gefahrenindex:.2f}")

        if gefahrenindex >= 3.3:
            st.markdown("""
                <div style='padding: 20px; background-color: #ff4b4b; color: white; border-radius: 10px; text-align: center;'>
                    ⚠️ <strong>Hohe Lawinengefahr</strong><br>Besondere Vorsicht notwendig!
                </div>
            """, unsafe_allow_html=True)
        elif gefahrenindex >= 2.2:
            st.markdown("""
                <div style='padding: 20px; background-color: #ffa500; color: black; border-radius: 10px; text-align: center;'>
                    ⚠️ <strong>Moderate Lawinengefahr</strong><br>Erhöhte Vorsicht erforderlich.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style='padding: 20px; background-color: #4CAF50; color: white; border-radius: 10px; text-align: center;'>
                    ✅ <strong>Geringe Lawinengefahr</strong>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Bitte mindestens 3 Antworten mit dem gleichen Gefahren-Typ (1, 2 oder 3) auswählen, um eine Bewertung zu erhalten.")

# --- Zurücksetzen ---
if st.button("🔄 Zurücksetzen"):
    st.session_state.clear()
    st.rerun()

