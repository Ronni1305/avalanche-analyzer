import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Lawinenbewertung", layout="centered")

# --- Ampelsymbole ---
ampel_icons = {
    "1: 🔴 Stabilität Sehr schlecht / schlecht": "<div style='display:inline-block; width: 20px; height: 20px; background-color: #ff4b4b; border-radius: 50%; text-align:center; color: white; font-weight: bold;'>×</div>",
    "2: 🟡 Stabilität mittel": "<div style='display:inline-block; width: 20px; height: 20px; background-color: #ffa500; border-radius: 50%; text-align:center; color: white; font-weight: bold;'>!</div>",
    "3: 🟢 Stabilität gut": "<div style='display:inline-block; width: 20px; height: 20px; background-color: #4CAF50; border-radius: 50%; text-align:center; color: white; font-weight: bold;'>✓</div>"
}

# --- Verhaltensempfehlungen Texte ---
verhaltensempfehlungen = {
    "🔴": """
**Empfehlungen bei ROT:**
- Verzicht auf Betreten / Sperrung des betroffenen Geländes.
- Aktive Gefahrenreduktion: z. B. Lawinensprengung, Absprengen von Wechten.
- Umgehung oder Wahl sicherer Routen (z.B. Wald, Rücken, andere Talseite).
- Informationsweitergabe an Behörden, Rettungskräfte, Betreiber, Kommandant.
- Einsatz von Drohnen zur Fernbeobachtung (z. B. Heeresbergführer, Lawinenkommissionen).
- Notfallpläne aktivieren, z. B. Evakuierung von Straßen / Objekten.
- Temporäre Sperre: z. B. bis nach Setzung/Temperaturrückgang.
""",
    "🟡": """
**Empfehlungen bei GELB:**
- Grenzwerte setzen! 
- Ausreichend Abstand zum Hang halten (Ø-Gefälle Anriss-mein Standpunkt mind. ~ 26–27°)
- Zeitorientierte Planung: Tourenstart sehr früh, Rückkehr vor Erwärmung.
- Laufende Beobachtung: Schneedeckenveränderung, Setzungsgrad, Gleitschneerisse.
- SSD und vSSD
- Staffelung von Gruppen – nie mehrere Personen im Hang.
- Nach Möglichkeit: kritische Passage sichern oder umgehen.
""",
    "🟢": """
**Empfehlungen bei GRÜN:**
- Standardmäßige Vorsicht nicht aufgeben (v. a. bei Einzelrisiken).
- Trotzdem laufend beobachten: Temperaturanstieg, Sonnenhang etc.
- Keine falsche Sicherheit vermitteln – andere Faktoren (z. B. Gleitschnee) beachten.
- Ggf. kombinieren mit anderen Tools (z. B. LLB, Systematische Schneedeckendiagnose).
"""
}

# --- Fragen & Punktwerte ---
fragen_definitions = {
    "Neuschneemenge (24h)": {"": 0, "1: > 40 cm / Tag": 4, "2: 20–40 cm / Tag": 2.5, "3: < 20 cm / Tag": 2},
    "Regenmenge": {"": 0, "1: starker Regen (> 5 mm)": 4, "2: leichter Regen (< 5 mm)": 2.5, "3: kein Regen": 3},
    "Erwärmung": {"": 0, "1: > 4 °C Erwärmung": 3.5, "2: bis 4 °C Erwärmung": 2, "3: kalt oder keine Erwärmung": 3},
    "Schneedecken-Stabilität": {"": 0, "1: Altschnee mitgerissen": 4, "2: nicht tragfähiger Harschdeckel": 2.5, "3: tragfähiger Harschdeckel oder keine Schwachschicht": 1},
    "Verbindung zur Altschneedecke": {"": 0, "1: schlecht (kaltes Einschneien)": 3, "2: Beginn bei 0–2 °C": 2, "3: gut (Regen, dann Temperaturabfall)": 1},
    "Wind/Verfrachtung": {"": 0, "1: starker Wind (> 40 km/h)": 3, "2: mäßiger Wind (< 40 km/h)": 2, "3: kein/wenig Wind": 1},
    "Exposition/Sonneneinstrahlung": {"": 0, "1: starke Sonneneinstrahlung": 3.5, "2: mäßige Sonneneinstrahlung": 2.5, "3: kaum oder keine Sonneneinstrahlung": 2},
    "SSD (vSSD)": {
        "": 0,
        "1: 🔴 Stabilität Sehr schlecht / schlecht": 4,
        "2: 🟡 Stabilität mittel": 2.5,
        "3: 🟢 Stabilität gut": 2
    },
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
        auswahl = st.radio(frage, list(optionen.keys()),
                           index=list(optionen.keys()).index(st.session_state[f"radio_{frage}"]),
                           key=f"radio_{frage}")

        if frage == "SSD (vSSD)" and auswahl in ampel_icons:
            st.markdown(f"<div style='margin-top: -10px; margin-bottom: 10px;'>{ampel_icons[auswahl]}</div>", unsafe_allow_html=True)

        if auswahl:
            punkte.append(optionen[auswahl])
            auswahl_typen.append(auswahl[0])

    # --- Setzungsblock ---
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

    if punktwert_setzung:
        punkte.append(punktwert_setzung)
        auswahl_typen.append("S")

    # --- Eigene Einschätzung (Pflicht!) ---
    st.markdown("🧭 **Eigene Einschätzung der Lawinengefahr**")

    slider_html = """
    <style>
    .slider-container {
        position: relative;
        height: 60px;
        margin-top: 20px;
    }
    .slider-bg {
        position: absolute;
        top: 26px;
        left: 0;
        right: 0;
        height: 8px;
        border-radius: 10px;
        background: linear-gradient(to right, #ff4b4b, #ffa500, #4CAF50);
        z-index: 0;
    }
    .slider-labels {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        margin-top: 6px;
        color: #555;
    }
    </style>
    <div class="slider-container">
        <div class="slider-bg"></div>
    </div>
    <div class="slider-labels">
        <span>hoch</span>
        <span>mittel</span>
        <span>gering</span>
    </div>
    """
    st.markdown(slider_html, unsafe_allow_html=True)

    eigene_einschaetzung = st.slider(
        "Gefahr selbst einschätzen (rot = hoch, grün = gering)",
        min_value=1.0,
        max_value=4.0,
        value=2.5,
        step=0.01,
        format="%.2f",
        label_visibility="collapsed"
    )

    bestaetigt = st.checkbox("✅ Ich habe meine persönliche Einschätzung getroffen", value=False)
    submitted = st.form_submit_button("Formular speichern")

# --- Bewertung + Empfehlungen ---
if submitted:
    if not bestaetigt:
        st.warning("⚠️ Bitte treffen Sie Ihre persönliche Einschätzung und bestätigen Sie diese.")
    else:
        typ1 = auswahl_typen.count("1")
        typ2 = auswahl_typen.count("2")
        typ3 = auswahl_typen.count("3")

        if max(typ1, typ2, typ3) >= 3:
            gefahrenindex = sum(punkte) / len(punkte)
            if gefahrenindex >= 3.3:
                farbe_box = "#ff4b4b"
                text_box = "🔴 <strong>Hohe Lawinengefahr</strong><br>Besondere Vorsicht notwendig!"
                verhalten = verhaltensempfehlungen["🔴"]
            elif gefahrenindex >= 2.2:
                farbe_box = "#ffa500"
                text_box = "🟡 <strong>Moderate Lawinengefahr</strong><br>Erhöhte Vorsicht erforderlich."
                verhalten = verhaltensempfehlungen["🟡"]
            else:
                farbe_box = "#4CAF50"
                text_box = "🟢 <strong>Geringe Lawinengefahr</strong>"
                verhalten = verhaltensempfehlungen["🟢"]

            st.markdown(f"""
                <div style='padding: 20px; background-color: {farbe_box}; color: white; border-radius: 10px; text-align: center;'>
                    {text_box}
                </div>
            """, unsafe_allow_html=True)

            st.subheader("Verhaltensempfehlungen")
            st.markdown(verhalten)

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

# --- Zurücksetzen ---
if st.button("🔄 Zurücksetzen"):
    st.session_state.clear()
    st.rerun()
