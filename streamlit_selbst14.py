import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Konfiguriere die Seite
st.set_page_config(page_title="Lawinenbewertung", layout="centered")

# --- Ampelsymbole ---
ampel_icons = {
    "1: 🔴 Stabilität Sehr schlecht / schlecht": "<div style='display:inline-block; width: 20px; height: 20px; background-color: #ff4b4b; border-radius: 50%; text-align:center; color: white; font-weight: bold;'>×</div>",
    "2: 🟡 Stabilität mittel": "<div style='display:inline-block; width: 20px; height: 20px; background-color: #ffa500; border-radius: 50%; text-align:center; color: white; font-weight: bold;'>!</div>",
    "3: 🟢 Stabilität gut": "<div style='display:inline-block; width: 20px; height: 20px; background-color: #4CAF50; border-radius: 50%; text-align:center; color: white; font-weight: bold;'>✓</div>"
}

# --- Verhaltensempfehlungen Texte (angepasst für direkte Anzeige) ---
verhaltensempfehlungen = {
    "🔴 Hohe Lawinengefahr": """
**Empfehlungen bei ROT:**
- **Verzicht** auf Betreten / Sperrung des betroffenen Geländes.
- **Aktive Gefahrenreduktion**: z. B. Lawinensprengung, Absprengen von Wechten.
- **Umgehung** oder Wahl sicherer Routen (z.B. Wald, Rücken, andere Talseite).
- **Informationsweitergabe** an Behörden, Rettungskräfte, Betreiber, Kommandant.
- **Einsatz von Drohnen** zur Fernbeobachtung (z. B. Heeresbergführer, Lawinenkommissionen).
- **Notfallpläne aktivieren**, z. B. Evakuierung von Straßen / Objekten.
- **Temporäre Sperre**: z. B. bis nach Setzung/Temperaturrückgang.
""",
    "🟡 Moderate Lawinengefahr": """
**Empfehlungen bei GELB:**
- **Grenzwerte setzen**! 
- **Ausreichend Abstand** zum Hang halten (Ø-Gefälle Anriss-mein Standpunkt mind. ~ 26–27°)
- **Zeitorientierte Planung**: Tourenstart sehr früh, Rückkehr vor Erwärmung.
- **Laufende Beobachtung**: Schneedeckenveränderung, Setzungsgrad, Gleitschneerisse.
- **SSD und vSSD** (systematische Schneedeckendiagnose / vereinfachte SSD)
- **Staffelung von Gruppen** – nie mehrere Personen im Hang.
- Nach Möglichkeit: **kritische Passage sichern** oder umgehen.
""",
    "🟢 Geringe Lawinengefahr": """
**Empfehlungen bei GRÜN:**
- **Standardmäßige Vorsicht** nicht aufgeben (v. a. bei Einzelrisiken).
- **Trotzdem laufend beobachten**: Temperaturanstieg, Sonnenhang etc.
- **Keine falsche Sicherheit** vermitteln – andere Faktoren (z. B. Gleitschnee) beachten.
- Ggf. **kombinieren** mit anderen Tools (z. B. LLB, Systematische Schneedeckendiagnose).
"""
}

# --- Fragen & Punktwerte für die Bewertung ---
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

# Initialisiere den Session State für Radio-Buttons, falls noch nicht vorhanden
for frage in fragen_definitions:
    st.session_state.setdefault(f"radio_{frage}", "")

# Initialisiere den Zustand für die ausgewählte Verhaltensempfehlung
if "selected_final_recommendation" not in st.session_state:
    st.session_state.selected_final_recommendation = list(verhaltensempfehlungen.keys())[0]

st.title("Selbstauslösung von Neuschnee-Lawinen")
st.markdown("Bewertung nach Ampelsystem")

# --- Hauptformular ---
with st.form("lawinen_form_main"):
    punkte = []
    auswahl_typen = []

    # Fragen zur Lawinenbewertung
    for frage, optionen in fragen_definitions.items():
        auswahl = st.radio(frage, list(optionen.keys()),
                               index=list(optionen.keys()).index(st.session_state[f"radio_{frage}"]),
                               key=f"radio_{frage}")

        if frage == "SSD (vSSD)" and auswahl in ampel_icons:
            st.markdown(f"<div style='margin-top: -10px; margin-bottom: 10px;'>{ampel_icons[auswahl]}</div>", unsafe_allow_html=True)

        if auswahl:
            punkte.append(optionen[auswahl])
            # Extrahiere den Typ (1, 2, oder 3) für die Bewertung
            if auswahl in ["1: > 40 cm / Tag", "1: starker Regen (> 5 mm)", "1: > 4 °C Erwärmung",
                            "1: Altschnee mitgerissen", "1: schlecht (kaltes Einschneien)",
                            "1: starker Wind (> 40 km/h)", "1: starke Sonneneinstrahlung",
                            "1: 🔴 Stabilität Sehr schlecht / schlecht",
                            "1: > 35° und ungünstige Exposition",
                            "2: 20–40 cm / Tag", "2: leichter Regen (< 5 mm)", "2: bis 4 °C Erwärmung",
                            "2: nicht tragfähiger Harschdeckel", "2: Beginn bei 0–2 °C",
                            "2: mäßiger Wind (< 40 km/h)", "2: mäßige Sonneneinstrahlung",
                            "2: 🟡 Stabilität mittel",
                            "2: 30–35° oder teils ungünstig",
                            "3: < 20 cm / Tag", "3: kein Regen", "3: kalt oder keine Erwärmung",
                            "3: tragfähiger Harschdeckel oder keine Schwachschicht", "3: gut (Regen, dann Temperaturabfall)",
                            "3: kein/wenig Wind", "3: kaum oder keine Sonneneinstrahlung",
                            "3: 🟢 Stabilität gut",
                            "3: < 30° oder günstige Exposition"]:
                auswahl_typen.append(auswahl[0]) # Nimmt '1', '2', oder '3'
            else:
                auswahl_typen.append("") # Für die leere Auswahl

    # --- Setzungsblock (Optional) ---
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
        # Hinzufügen des Typs zur auswahl_typen Liste (für die Statistik unten)
        if beschreibung.startswith("1"):
            auswahl_typen.append("1")
        elif beschreibung.startswith("2"):
            auswahl_typen.append("2")
        elif beschreibung.startswith("3"):
            auswahl_typen.append("3")
        else:
            auswahl_typen.append("S") # Für "Setzung", falls kein 1,2,3 am Anfang


    # --- Schieberegler für eigene Einschätzung ---
    st.markdown("---") 
    st.markdown("🧭 **Eigene Einschätzung der Lawinengefahr**")

    # Hier die Reihenfolge der Labels im HTML-Code anpassen
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
        /* Beibehaltung des Farbverlaufs von rot nach grün */
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
        <span>hoch</span>  <span>mittel</span>
        <span>gering</span> </div>
    """
    st.markdown(slider_html, unsafe_allow_html=True)

    eigene_einschaetzung = st.slider(
        "Gefahr selbst einschätzen (hoch = links, gering = rechts)",
        min_value=1.0,  # Kleinster Wert (rechts, gering)
        max_value=4.0,  # Größter Wert (links, hoch)
        value=2.5,
        step=0.01,
        format="%.2f",
        label_visibility="collapsed"
    )

    # --- Verhaltensempfehlungen als aufklappbare Expander (diese bleiben zum Nachschlagen) ---
    st.markdown("---")
    st.markdown("### **Verhaltensempfehlungen (zum Nachschlagen):**")
    st.markdown("Klicken Sie auf eine Empfehlung, um die Details zu sehen:")

    # Initialisiere den Zustand für den aktuell geöffneten Expander
    if "open_expander" not in st.session_state:
        st.session_state.open_expander = None

    for gefahren_stufe_key, empfehlungen_text in verhaltensempfehlungen.items():
        with st.expander(gefahren_stufe_key, expanded=(st.session_state.open_expander == gefahren_stufe_key)):
            st.markdown(empfehlungen_text)
    
    st.markdown("---") 
    
    # --- Finale Auswahl der Verhaltensempfehlung (innerhalb des Forms) ---
    st.markdown("### **Wählen Sie Ihre finale Einschätzung:**")
        
    selected_final_recommendation_radio = st.radio(
        "Ihre finale Auswahl:",
        options=list(verhaltensempfehlungen.keys()),
        index=list(verhaltensempfehlungen.keys()).index(st.session_state.selected_final_recommendation),
        key="final_recommendation_radio",
        label_visibility="collapsed" # Versteckt das Label des Radios
    )
    # Speichere die Auswahl direkt im Session State
    st.session_state.selected_final_recommendation = selected_final_recommendation_radio

    st.info(f"Sie werden **{st.session_state.selected_final_recommendation}** speichern.")
    st.markdown("---")

    # --- Checkbox und Submit Button des Formulars ---
    bestaetigt = st.checkbox("✅ Ich habe meine persönliche Einschätzung getroffen")
    submitted = st.form_submit_button("Formular speichern")


# --- Ergebnisberechnung und Anzeige (nach dem Formular-Submit) ---
if submitted and bestaetigt: 
    typ1 = auswahl_typen.count("1")
    typ2 = auswahl_typen.count("2")
    typ3 = auswahl_typen.count("3")

    if len(punkte) > 0 and (typ1 >= 3 or typ2 >= 3 or typ3 >= 3):
        summe_punkte = sum(punkte) 
        anzahl_fragen = len(punkte)
        gefahrenindex = summe_punkte / anzahl_fragen if anzahl_fragen > 0 else 0
        
        # Bestimme Text und Farbe basierend auf dem Gefahrenindex
        if gefahrenindex >= 3.3:
            farbe_box = "#ff4b4b"
            text_box = "🔴 <strong>Hohe Lawinengefahr</strong><br>Besondere Vorsicht notwendig!"
            verhalten_zu_anzeigen = verhaltensempfehlungen["🔴 Hohe Lawinengefahr"]
        elif gefahrenindex >= 2.2:
            farbe_box = "#ffa500"
            text_box = "🟡 <strong>Moderate Lawinengefahr</strong><br>Erhöhte Vorsicht erforderlich."
            verhalten_zu_anzeigen = verhaltensempfehlungen["🟡 Moderate Lawinengefahr"]
        else:
            farbe_box = "#4CAF50"
            text_box = "🟢 <strong>Geringe Lawinengefahr</strong>"
            verhalten_zu_anzeigen = verhaltensempfehlungen["🟢 Geringe Lawinengefahr"]

        st.markdown(f"""
            <div style='padding: 20px; background-color: {farbe_box}; color: white; border-radius: 10px; text-align: center;'>
                {text_box}
            </div>
        """, unsafe_allow_html=True)

        st.subheader("Gefahrenindex auf Skala")
        fig, ax = plt.subplots(figsize=(6, 1.5))
        cmap = plt.cm.colors.ListedColormap(['#4CAF50', '#ffa500', '#ff4b4b'])
        bounds = [1.95, 2.2, 3.3, 3.65] # Die Bereiche der Ampelfarben auf der Skala
        norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)

        gradient = np.linspace(1.0, 4.0, 400).reshape(1, -1)
        ax.imshow(gradient, extent=[1.0, 4.0, 0, 1], aspect='auto', cmap=cmap, norm=norm)
        ax.set_xlim(4.0, 1.0) # Skala von rechts (gering) nach links (hoch)
        ax.axhline(0.5, color='white', linestyle='--')
        ax.plot(gefahrenindex, 0.5, 'wo', markersize=10, markeredgecolor='black')
        ax.text(gefahrenindex, -0.3, f"{gefahrenindex:.2f}", ha='center', fontsize=10)
        ax.axis('off')
        st.pyplot(fig)
        
        # --- Anzeige der spezifischen Verhaltensempfehlungen basierend auf dem Index ---
        st.markdown("---")
        st.subheader("Ihre Verhaltensempfehlung:")
        st.markdown(verhalten_zu_anzeigen)

    else:
        if len(punkte) == 0:
            st.info("ℹ️ Bitte füllen Sie mindestens eine Frage aus, um eine Bewertung zu erhalten.")
        else:
            st.info("ℹ️ Bitte mindestens 3 Antworten mit dem gleichen Gefahren-Typ (1, 2 oder 3) auswählen, um eine detaillierte Gefahrenindex-Berechnung zu erhalten.")

# --- Zurücksetzen der Anwendung ---
if st.button("🔄 Zurücksetzen"):
    st.session_state.clear()
    st.rerun()
