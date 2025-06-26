import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Konfiguriere die Seite
st.set_page_config(page_title="Lawinenbewertung", layout="centered")

# --- Ampelsymbole (aus Tool 1) ---
ampel_icons = {
    "1: 🔴 Stabilität Sehr schlecht / schlecht": "<div style='display:inline-block; width: 20px; height: 20px; background-color: #ff4b4b; border-radius: 50%; text-align:center; color: white; font-weight: bold;'>×</div>",
    "2: 🟡 Stabilität mittel": "<div style='display:inline-block; width: 20px; height: 20px; background-color: #ffa500; border-radius: 50%; text-align:center; color: white; font-weight: bold;'>!</div>",
    "3: 🟢 Stabilität gut": "<div style='display:inline-block; width: 20px; height: 20px; background-color: #4CAF50; border-radius: 50%; text-align:center; color: white; font-weight: bold;'>✓</div>"
}

# --- Verhaltensempfehlungen Texte (aus Tool 1) ---
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

# --- Fragen & Punktwerte für die Bewertung (aus Tool 1) ---
fragen_definitions_tool1 = {
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

# --- Konstanten für Farb-Schwellenwerte der Bewertung (aus Tool 2) ---
FARB_SCHWELLENWERTE_TOOL2 = {
    "gering": {"wert": 3.26, "text": "🟢 Geringe Gefahr", "farbe": "#90EE90"},
    "maessig": {"wert": 4.21, "text": "🟡 Mäßige Gefahr", "farbe": "#FFF176"},
    "hoch": {"text": "🔴 Hohe Gefahr", "farbe": "#FF7F7F"}
}

# --- Definition der Fragen, Optionen und Gewichte (aus Tool 2) ---
fragen_tool2 = [
    ("Frage 1: Größe des Geländes", [
        ("Sehr klein (z.B. schmaler Hangabschnitt)", 1),
        ("Klein bis mittelgroß (einzelne Hänge oder kurze Rinnen)", 2.5),
        ("Groß (mehrere zusammenhängende Hangbereiche)", 4.5),
        ("Sehr groß (ausgedehntes Kar oder verbundenes Gelände)", 7)
    ], 1.5),
    ("Frage 2: Schneemenge und Stabilität", [
        ("Wenig Schnee, stabil (kaum Lawinenpotenzial)", 1),
        ("Mittlere Schneemenge, eher stabil (lokale Auslösungen möglich)", 4),
        ("Viel Schnee, mit Schwachschichten (erhöhtes Gefahrenpotenzial)", 5),
        ("Sehr viel Schnee, instabil - Hoher Auslösegrad (z. B. Triebschnee, Nass- Gleitschnee,  großes Schwimmschneefundament)", 8)
    ], 2),
    ("Frage 3: Schneemenge in der Lawinenbahn", [
        ('Kaum Schnee – Lawine "verhungert"', 1),
        ("Wenig Schnee – geringe Massenvergrößerung", 4),
        ("Viel Schnee – deutliche Massenvergrößerung", 5),
        ("Sehr viel Schnee – erhebliche Massenvergrößerung (z. B. durch Neuschnee oder Triebschnee im Verlauf)", 8)
    ], 1.5),
    ("Frage 4: Bodenbeschaffenheit", [
        ("Großer Widerstand → starke Bremswirkung (z.B. vorstehende Steine, Blöcke)", 1),
        ("Unregelmäßiger Boden → teilweiser Widerstand (z.B. Vegetation, Geländeunebenheiten", 2),
        ("Geglätteter Boden → wenig Widerstand (z.B. verdichtete Schneedecke oder Skirinnen)", 4),
        ("Vollständig glatt → maximale Gleitfähigkeit (z.B. Lawinengras, vereiste Altschneedecke)", 7)
    ], 1.2),
    ("Frage 5: Hangauslauf / Reichweite", [
        ("Kurzer Auslauf, flach → Lawine wird rasch gebremst", 1),
        ("Langer, steiler Auslauf mit Hindernissen (z.B. Bäume, Geländestufen)", 2),
        ("Langer Auslauf, wenige Hindernisse/Staubereiche → große Reichweite möglich (Ø-Gefälle ~ 26–27°)", 4),
        ("Langer, freier Auslauf – keine Hindernisse → sehr große Reichweite", 7)
    ], 1),
    ("Frage 6: Potenzielle Auswirkungen – Massenbewegung", [
        ("Keine Gefahr- geringe Massenbewegung", 1),
        ("Gefahr für Einzelpersonen → könnte Menschen erfassen", 3),
        ("Gefahr für Objekte (z.B. Fahrzeuge, Bäume, kleine Bauwerke)", 8),
        ("Gefahr für Infrastruktur (z.B. Straßen, Häuser, Bahnlinien)", 8)
    ], 2),
    ("Frage 7: Nähe zu Pisten oder Infrastruktur", [
        ("Weit entfernt → keine relevante Gefährdung", 1),
        ("In Sichtweite → Wahrnehmung möglich, aber keine direkte Gefährdung", 3),
        ("Kann Pisten oder Infrastruktur erreichen → potenzielle Beeinträchtigung", 8),
        ("Direkter Einfluss → trifft auf Pisten, Häuser, Verkehrswege", 8)
    ], 2)
]

# --- Initialisierung des Session State (Kombiniert für beide Tools) ---
# Tool 1 spezifisch
for frage in fragen_definitions_tool1:
    st.session_state.setdefault(f"tool1_radio_{frage}", "")
if "tool1_selected_final_recommendation" not in st.session_state:
    st.session_state.tool1_selected_final_recommendation = list(verhaltensempfehlungen.keys())[0]
if "tool1_final_radio_clicked" not in st.session_state:
    st.session_state.tool1_final_radio_clicked = False
if "tool1_gefahrenindex" not in st.session_state:
    st.session_state.tool1_gefahrenindex = None # Um den Index von Tool 1 zu speichern
if "tool1_submitted" not in st.session_state:
    st.session_state.tool1_submitted = False
if "tool1_result_category" not in st.session_state: # Speichert die Kategorie (rot, gelb, grün)
    st.session_state.tool1_result_category = None 
if "tool1_open_expander" not in st.session_state: # Für die Expander-Logik
    st.session_state.tool1_open_expander = None


# Tool 2 spezifisch
if "tool2_initialisiert" not in st.session_state:
    st.session_state.tool2_initialisiert = True
    st.session_state.tool2_submitted = False # Flag, ob der Berechnen-Button geklickt wurde
    # Initialisiert alle Antworten auf None
    for idx, _ in enumerate(fragen_tool2):
        st.session_state[f"tool2_antwort_{idx+1}"] = None


# --- Callback-Funktionen (aus Tool 1 und Tool 2) ---
def on_tool1_final_radio_change():
    st.session_state.tool1_final_radio_clicked = True
    # Der Wert wird automatisch über den 'key' im Session State aktualisiert

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

def get_bewertung_farbe_tool2(wert):
    """
    Ermittelt den Gefahrentext und die entsprechende Farbe basierend auf dem berechneten Wert für Tool 2.
    """
    if wert <= FARB_SCHWELLENWERTE_TOOL2["gering"]["wert"]:
        return FARB_SCHWELLENWERTE_TOOL2["gering"]["text"], FARB_SCHWELLENWERTE_TOOL2["gering"]["farbe"]
    elif wert <= FARB_SCHWELLENWERTE_TOOL2["maessig"]["wert"]:
        return FARB_SCHWELLENWERTE_TOOL2["maessig"]["text"], FARB_SCHWELLENWERTE_TOOL2["maessig"]["farbe"]
    else:
        return FARB_SCHWELLENWERTE_TOOL2["hoch"]["text"], FARB_SCHWELLENWERTE_TOOL2["hoch"]["farbe"]

def handle_tool2_radio_selection(question_idx):
    """
    Diese Callback-Funktion wird ausgelöst, wenn ein Radio-Button in Tool 2 ausgewählt wird.
    """
    key = f"tool2_frage_{question_idx}"
    selected_option_text = st.session_state[key]

    current_question_options = fragen_tool2[question_idx - 1][1]
    selected_value = None
    for text, val in current_question_options:
        if selected_option_text == text:
            selected_value = val
            break
            
    if selected_option_text == "": # Handle the empty option (initial state)
        selected_value = None

    st.session_state[f"tool2_antwort_{question_idx}"] = selected_value
    st.session_state.tool2_submitted = False # Zurücksetzen, damit man erneut "Berechnen" klicken muss
    # st.rerun() # Entfernen von reruns in Callbacks, um unnötige Neuzeichnungen zu vermeiden
    # Wenn st.rerun() entfernt wird, muss der Berechnen-Button geklickt werden,
    # um Änderungen in den Antworten zu reflektieren. Das ist bei Radio-Buttons im Formular üblich.
    # Wegen des Submit-Buttons wird das Formular ohnehin neu eingereicht.


# --- Logo anzeigen (aus Tool 2) ---
try:
    # Use the uploaded file directly
    logo = Image.open("image_7ebf12.png")
    st.image(logo, width=200)
except FileNotFoundError:
    st.warning("⚠️ Logo konnte nicht geladen werden. Bitte stellen Sie sicher, dass 'image_7ebf12.png' im selben Verzeichnis wie das Skript liegt.")
except Exception as e:
    st.warning(f"⚠️ Fehler beim Laden des Logos: {e}")

st.title("🏔️ Lawinenbewertung")
st.markdown("Führen Sie eine schrittweise Analyse der Lawinengefahr durch.")

st.header("Schritt 1: Kann sich eine Lawine lösen? (Tool 1)")
st.markdown("Beantworten Sie die folgenden Fragen, um die Wahrscheinlichkeit einer Selbstauslösung einzuschätzen.")

# --- Hauptformular für Tool 1 ---
with st.form("lawinen_form_main_tool1"):
    punkte_tool1 = []
    auswahl_typen_tool1 = []

    # Fragen zur Lawinenbewertung (Tool 1)
    for frage in fragen_definitions_tool1:
        optionen = fragen_definitions_tool1[frage]
        auswahl = st.radio(
            frage,
            list(optionen.keys()),
            index=list(optionen.keys()).index(st.session_state[f"tool1_radio_{frage}"]),
            key=f"tool1_radio_{frage}"
        )

        if frage == "SSD (vSSD)" and auswahl in ampel_icons:
            st.markdown(f"<div style='margin-top: -10px; margin-bottom: 10px;'>{ampel_icons[auswahl]}</div>", unsafe_allow_html=True)

        if auswahl:
            punkte_tool1.append(optionen[auswahl])
            if auswahl in [item for sublist in [list(fragen_definitions_tool1[k].keys())[1:] for k in fragen_definitions_tool1] for item in sublist]:
                auswahl_typen_tool1.append(auswahl[0])
            else:
                auswahl_typen_tool1.append("")

    # --- Setzungsblock (Optional für Tool 1) ---
    punktwert_setzung_tool1 = 0
    with st.expander("➕ Setzung des Neuschnees eingeben (Tool 1)"):
        ns_tool1 = st.slider("Neuschneemenge (cm)", 0, 150, 0, 5, key="ns_tool1")
        temp_tool1 = st.slider("Temperatur (°C)", -20, 10, 0, 1, key="temp_tool1")
        stunden_tool1 = st.slider("vergangene Stunden", 0, 72, 0, 1, key="stunden_tool1")

        beschreibung_tool1, punktwert_setzung_tool1 = berechne_setzung_excel(ns_tool1, temp_tool1, stunden_tool1)
        if beschreibung_tool1:
            farbe_tool1 = "#ff4b4b" if beschreibung_tool1.startswith("1") else "#ffa500" if beschreibung_tool1.startswith("2") else "#4CAF50"
            st.markdown(f"""
                <div style='padding: 10px; background-color: {farbe_tool1}; color: white; border-radius: 8px; text-align: center;'>
                    <strong>Automatische Setzung:</strong><br>{beschreibung_tool1}
                </div>
            """, unsafe_allow_html=True)

    if punktwert_setzung_tool1:
        punkte_tool1.append(punktwert_setzung_tool1)
        if beschreibung_tool1.startswith("1"):
            auswahl_typen_tool1.append("1")
        elif beschreibung_tool1.startswith("2"):
            auswahl_typen_tool1.append("2")
        elif beschreibung_tool1.startswith("3"):
            auswahl_typen_tool1.append("3")
        else:
            auswahl_typen_tool1.append("S")

    st.markdown("---") 
    st.markdown("🧭 **Eigene Einschätzung der Lawinengefahr (Tool 1)**")
    slider_html_tool1 = """
    <style>
    .slider-container-tool1 {
        position: relative;
        height: 60px;
        margin-top: 20px;
    }
    .slider-bg-tool1 {
        position: absolute;
        top: 26px;
        left: 0;
        right: 0;
        height: 8px;
        border-radius: 10px;
        background: linear-gradient(to right, #ff4b4b, #ffa500, #4CAF50); 
        z-index: 0;
    }
    .slider-labels-tool1 {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        margin-top: 6px;
        color: #555;
    }
    </style>
    <div class="slider-container-tool1">
        <div class="slider-bg-tool1"></div>
    </div>
    <div class="slider-labels-tool1">
        <span>hoch</span>  <span>mittel</span>
        <span>gering</span> </div>
    """
    st.markdown(slider_html_tool1, unsafe_allow_html=True)

    eigene_einschaetzung_tool1 = st.slider(
        "Gefahr selbst einschätzen (hoch = links, gering = rechts)",
        min_value=1.0, max_value=4.0, value=2.5, step=0.01, format="%.2f",
        label_visibility="collapsed", key="eigene_einschaetzung_tool1"
    )

    st.markdown("---")
    st.markdown("### **Verhaltensempfehlungen (zum Nachschlagen) (Tool 1):**")
    st.markdown("Klicken Sie auf eine Empfehlung, um die Details zu sehen:")

    for gefahren_stufe_key, empfehlungen_text in verhaltensempfehlungen.items():
        # Using a simple expanded argument as 'key' is not supported in older Streamlit versions
        # This means multiple expanders can be open simultaneously.
        with st.expander(gefahren_stufe_key):
            st.markdown(empfehlungen_text)

    st.markdown("---") 

    bestaetigt_tool1 = st.checkbox("✅ Ich habe meine persönliche Einschätzung getroffen (Tool 1)", key="bestaetigt_tool1")
    
    # --- Submit Button für Tool 1 (INNERHALB des Formulars) ---
    submitted_tool1 = st.form_submit_button("Berechnung Lawinenauslösung anzeigen")

# --- Finale Auswahl der Verhaltensempfehlung (Tool 1 - außerhalb des Formulars) ---
st.markdown("### **Treffen Sie Ihre finale Entscheidung zur Verhaltensweise (Tool 1):**")
    
selected_final_recommendation_radio_tool1 = st.radio(
    "Ihre finale Auswahl:",
    options=list(verhaltensempfehlungen.keys()),
    index=list(verhaltensempfehlungen.keys()).index(st.session_state.tool1_selected_final_recommendation),
    key="tool1_final_recommendation_radio",
    label_visibility="collapsed",
    on_change=on_tool1_final_radio_change
)
st.session_state.tool1_selected_final_recommendation = selected_final_recommendation_radio_tool1

if st.session_state.tool1_final_radio_clicked and st.session_state.tool1_selected_final_recommendation:
    st.info(f"Sie werden **{st.session_state.tool1_selected_final_recommendation}** speichern.")
st.markdown("---")

# --- Ergebnisberechnung und Anzeige (nach dem Formular-Submit von Tool 1) ---
if submitted_tool1 and bestaetigt_tool1: 
    typ1_tool1 = auswahl_typen_tool1.count("1")
    typ2_tool1 = auswahl_typen_tool1.count("2")
    typ3_tool1 = auswahl_typen_tool1.count("3")

    if len(punkte_tool1) > 0 and (typ1_tool1 >= 3 or typ2_tool1 >= 3 or typ3_tool1 >= 3):
        summe_punkte_tool1 = sum(punkte_tool1) 
        anzahl_fragen_tool1 = len(punkte_tool1)
        gefahrenindex_tool1 = summe_punkte_tool1 / anzahl_fragen_tool1 if anzahl_fragen_tool1 > 0 else 0
        st.session_state.tool1_gefahrenindex = gefahrenindex_tool1 # Speichere den Index im Session State
        
        # Bestimme die Ergebnis-Kategorie für Tool 1
        if gefahrenindex_tool1 >= 3.3:
            st.session_state.tool1_result_category = "hoch"
            farbe_box_tool1 = "#ff4b4b"
            text_box_tool1 = "🔴 <strong>Hohe Lawinengefahr</strong><br>Besondere Vorsicht notwendig!"
            verhalten_zu_anzeigen_tool1 = verhaltensempfehlungen["🔴 Hohe Lawinengefahr"]
        elif gefahrenindex_tool1 >= 2.2:
            st.session_state.tool1_result_category = "moderat"
            farbe_box_tool1 = "#ffa500"
            text_box_tool1 = "🟡 <strong>Moderate Lawinengefahr</strong><br>Erhöhte Vorsicht erforderlich."
            verhalten_zu_anzeigen_tool1 = verhaltensempfehlungen["🟡 Moderate Lawinengefahr"]
        else:
            st.session_state.tool1_result_category = "gering"
            farbe_box_tool1 = "#4CAF50"
            text_box_tool1 = "🟢 <strong>Geringe Lawinengefahr</strong>"
            verhalten_zu_anzeigen_tool1 = verhaltensempfehlungen["🟢 Geringe Lawinengefahr"]

        st.markdown(f"""
            <div style='padding: 20px; background-color: {farbe_box_tool1}; color: white; border-radius: 10px; text-align: center;'>
                {text_box_tool1}
            </div>
        """, unsafe_allow_html=True)

        st.subheader("Gefahrenindex auf Skala (System-Einschätzung) (Tool 1):") 
        fig_tool1, ax_tool1 = plt.subplots(figsize=(6, 1.5))
        cmap_tool1 = plt.cm.colors.ListedColormap(['#4CAF50', '#ffa500', '#ff4b4b'])
        bounds_tool1 = [1.95, 2.2, 3.3, 3.65]
        norm_tool1 = plt.cm.colors.BoundaryNorm(bounds_tool1, cmap_tool1.N)

        gradient_tool1 = np.linspace(1.0, 4.0, 400).reshape(1, -1)
        ax_tool1.imshow(gradient_tool1, extent=[1.0, 4.0, 0, 1], aspect='auto', cmap=cmap_tool1, norm=norm_tool1)
        ax_tool1.set_xlim(4.0, 1.0)
        ax_tool1.axhline(0.5, color='white', linestyle='--')
        ax_tool1.plot(gefahrenindex_tool1, 0.5, 'wo', markersize=10, markeredgecolor='black')
        ax_tool1.axis('off')
        st.pyplot(fig_tool1)
        
        st.markdown("---")
        st.subheader("Ihre Verhaltensempfehlung (berechnet vom System) (Tool 1):") 
        st.markdown(verhalten_zu_anzeigen_tool1)

    else:
        if len(punkte_tool1) == 0:
            st.warning("Bitte füllen Sie mindestens eine Frage aus, um eine Bewertung zu erhalten (Tool 1).")
        else:
            st.warning("Bitte mindestens 3 Antworten mit dem gleichen Gefahren-Typ (1, 2 oder 3) auswählen, um eine detaillierte Gefahrenindex-Berechnung zu erhalten (Tool 1).")
        # Wichtig: Wenn die Berechnung nicht erfolgreich war, setzen wir diese Flags zurück
        st.session_state.tool1_submitted = False 
        st.session_state.tool1_result_category = None
        st.session_state.tool1_gefahrenindex = None # Wichtig, um Tool 2 auszublenden

# --- Bedingte Anzeige von Tool 2 ---
st.markdown("---")
st.header("Schritt 2: Lawinengröße & Reichweite (Tool 2)")

# Tool 2 wird nur angezeigt, wenn Tool 1 erfolgreich verarbeitet wurde UND die Gefahrenkategorie hoch oder moderat ist.
if st.session_state.tool1_gefahrenindex is not None and st.session_state.tool1_result_category in ["hoch", "moderat"]:
    st.info("Da Tool 1 eine moderate oder hohe Lawinengefahr anzeigt, fahren Sie nun mit der Massen- und Reichweitenanalyse fort.")

    # --- Anzeigen der Fragen und Verwalten der Auswahl (Tool 2) ---
    # Hier verwenden wir KEIN `st.form` für Tool 2, da wir die Interaktion der Radio-Buttons direkt steuern
    # und den "Berechne"-Button separat handhaben.
    for idx, (frage, optionen, gewicht) in enumerate(fragen_tool2):
        key = f"tool2_frage_{idx+1}"
        initial_index = 0
        gespeicherter_wert = st.session_state.get(f"tool2_antwort_{idx+1}")

        # Find the index of the previously selected value to set the radio button correctly
        if gespeicherter_wert is not None:
            for i, (text, val) in enumerate(optionen):
                if val == gespeicherter_wert:
                    initial_index = i + 1 # +1 because of the empty string "" at the beginning
                    break
        
        # Disable logic for Q6 and Q7
        disabled = False
        if idx == 5: # Frage 6
            # Wenn Frage 7 beantwortet ist, deaktiviere Frage 6
            # Überprüfen Sie auch, ob der Wert nicht None ist, da der leere String beim ersten Laden None ergibt
            if st.session_state.get("tool2_antwort_7") is not None:
                disabled = True
        elif idx == 6: # Frage 7
            # Wenn Frage 6 beantwortet ist, deaktiviere Frage 7
            if st.session_state.get("tool2_antwort_6") is not None:
                disabled = True

        auswahl = st.radio(
            frage,
            options=[""] + [opt[0] for opt in optionen], # Add an empty string as the first option
            index=initial_index, # Set the index correctly
            key=key,
            disabled=disabled,
            on_change=handle_tool2_radio_selection,
            args=(idx + 1,)
        )
        
    # --- Buttons für Berechnung und Zurücksetzen (Tool 2) ---
    col1_tool2, col2_tool2 = st.columns(2)

    with col1_tool2:
        if st.button("🔍 Berechne Lawinenausmaß", key="berechne_tool2"):
            st.session_state.tool2_submitted = True # Setzt den Submitted-Flag

            frage6_beantwortet_tool2 = st.session_state.get("tool2_antwort_6") is not None
            frage7_beantwortet_tool2 = st.session_state.get("tool2_antwort_7") is not None

            # Überprüfung der Pflichtfragen 1-5
            all_mandatory_answered = True
            for idx_q in range(5): # Check all mandatory questions (1-5)
                if st.session_state.get(f"tool2_antwort_{idx_q+1}") is None:
                    all_mandatory_answered = False
                    break
            
            if not all_mandatory_answered:
                st.warning("⚠️ Bitte alle Pflichtfragen (1-5) für die Massen- & Reichweitenanalyse beantworten.")
                st.stop() # Stoppt die Ausführung hier, bis alle Pflichtfragen beantwortet sind

            # Überprüfung der exklusiven Fragen 6 ODER 7
            if frage6_beantwortet_tool2 and frage7_beantwortet_tool2:
                st.error("❗ Bitte **nur Frage 6 oder Frage 7** für die Massen- & Reichweitenanalyse beantworten – nicht beide.")
                st.stop()
            if not frage6_beantwortet_tool2 and not frage7_beantwortet_tool2:
                st.error("❗ Bitte **Frage 6 oder Frage 7** für die Massen- & Reichweitenanalyse beantworten.")
                st.stop()

            werte_tool2 = []
            gewichte_tool2 = []

            for idx_q in range(5): # Questions 1-5
                wert = st.session_state.get(f"tool2_antwort_{idx_q+1}")
                gewicht = fragen_tool2[idx_q][2]
                if wert is not None: 
                    werte_tool2.append(wert)
                    gewichte_tool2.append(gewicht)

            if frage6_beantwortet_tool2:
                wert = st.session_state.get("tool2_antwort_6")
                gewicht = fragen_tool2[5][2] # Index 5 ist Frage 6
            else: # frage7_beantwortet_tool2 muss True sein
                wert = st.session_state.get("tool2_antwort_7")
                gewicht = fragen_tool2[6][2] # Index 6 ist Frage 7

            werte_tool2.append(wert)
            gewichte_tool2.append(gewicht)

            if not werte_tool2:
                st.error("❌ Es konnten keine gültigen Werte zur Berechnung der Massen- & Reichweitenanalyse erfasst werden.")
                st.stop()

            mw_ung_tool2 = sum(werte_tool2) / len(werte_tool2)
            mw_gew_tool2 = sum(v * g for v, g in zip(werte_tool2, gewichte_tool2)) / sum(gewichte_tool2)

            txt_ung_tool2, farbe_ung_tool2 = get_bewertung_farbe_tool2(mw_ung_tool2)
            txt_gew_tool2, farbe_gew_tool2 = get_bewertung_farbe_tool2(mw_gew_tool2)

            st.subheader("📊 Ergebnisse der Massen- & Reichweitenanalyse")
            st.info("Die Bewertung zeigt die Gefahreneinschätzung nach zwei Methoden.")
            c1_tool2, c2_tool2 = st.columns(2)
            with c1_tool2:
                st.markdown("**Ungewichteter Mittelwert:**")
                st.markdown(f"<div style='background-color:{farbe_ung_tool2};padding:10px;border-radius:8px'><b>{txt_ung_tool2}<br>{mw_ung_tool2:.2f}</b></div>", unsafe_allow_html=True)
            with c2_tool2:
                st.markdown("**Gewichteter Mittelwert:**")
                st.markdown(f"<div style='background-color:{farbe_gew_tool2};padding:10px;border-radius:8px'><b>{txt_gew_tool2}<br>{mw_gew_tool2:.2f}</b></div>", unsafe_allow_html=True)

            # --- Integration des Gefahrenindex von Tool 1 (falls vorhanden) ---
            if st.session_state.tool1_gefahrenindex is not None:
                st.markdown("---")
                st.subheader("Ihre Gesamtbewertung:")
                
                # Hier könnten Sie eine finale, kombinierte Risikoaussage treffen
                # Basierend auf tool1_result_category und den gewichteten MW von Tool 2
                final_risk_text = "Keine eindeutige Gesamtbewertung möglich."
                final_risk_color = "#ccc"

                tool1_cat = st.session_state.tool1_result_category
                tool2_weighted_val = mw_gew_tool2

                # Einfaches Beispiel für eine kombinierte Logik
                if tool1_cat == "gering":
                    if tool2_weighted_val <= FARB_SCHWELLENWERTE_TOOL2["gering"]["wert"]:
                        final_risk_text = "✅ **Gesamtrisiko: GERING** (Geringe Auslösung, geringes Ausmaß)"
                        final_risk_color = "#4CAF50"
                    elif tool2_weighted_val <= FARB_SCHWELLENWERTE_TOOL2["maessig"]["wert"]:
                        final_risk_text = "🟡 **Gesamtrisiko: MODERAT** (Geringe Auslösung, aber mittleres Ausmaß möglich)"
                        final_risk_color = "#ffa500"
                    else:
                        final_risk_text = "🔴 **Gesamtrisiko: HOCH** (Geringe Auslösung, aber hohes Ausmaß möglich)"
                        final_risk_color = "#ff4b4b"
                elif tool1_cat == "moderat":
                    if tool2_weighted_val <= FARB_SCHWELLENWERTE_TOOL2["gering"]["wert"]:
                        final_risk_text = "🟡 **Gesamtrisiko: MODERAT** (Moderate Auslösung, aber geringes Ausmaß)"
                        final_risk_color = "#ffa500"
                    elif tool2_weighted_val <= FARB_SCHWELLENWERTE_TOOL2["maessig"]["wert"]:
                        final_risk_text = "🔴 **Gesamtrisiko: HOCH** (Moderate Auslösung, mittleres Ausmaß)"
                        final_risk_color = "#ff4b4b"
                    else:
                        final_risk_text = "💥 **Gesamtrisiko: SEHR HOCH** (Moderate Auslösung, hohes Ausmaß)"
                        final_risk_color = "#8B0000" # Dunkelrot
                elif tool1_cat == "hoch":
                    if tool2_weighted_val <= FARB_SCHWELLENWERTE_TOOL2["gering"]["wert"]:
                        final_risk_text = "🔴 **Gesamtrisiko: HOCH** (Hohe Auslösung, aber geringes Ausmaß)"
                        final_risk_color = "#ff4b4b"
                    else:
                        final_risk_text = "🔥🔥 **Gesamtrisiko: EXTREM HOCH** (Hohe Auslösung, hohes Ausmaß)"
                        final_risk_color = "#B22222" # Noch dunkler

                st.markdown(f"""
                    <div style='padding: 20px; background-color: {final_risk_color}; color: white; border-radius: 10px; text-align: center;'>
                        {final_risk_text}
                        <br><br>
                        (Auslösung: {st.session_state.tool1_result_category.capitalize()} - Ausmaß: {txt_gew_tool2})
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("Bitte beachten Sie, dass dies eine automatisierte Einschätzung ist und stets durch Geländebeobachtung und Expertenwissen zu ergänzen ist.")

    with col2_tool2:
        if st.button("🔄 Zurücksetzen Alle Werte (Tool 2)", key="reset_tool2_values"):
            # Setze nur die Werte von Tool 2 zurück
            for idx, _ in enumerate(fragen_tool2):
                st.session_state[f"tool2_antwort_{idx+1}"] = None
            st.session_state.tool2_submitted = False
            st.rerun()

else:
    st.info("Bitte füllen Sie zuerst die Fragen in 'Schritt 1: Kann sich eine Lawine lösen?' aus und klicken Sie auf 'Berechnung Lawinenauslösung anzeigen', um mit der Massen- und Reichweitenanalyse fortzufahren.")
    st.session_state.tool2_submitted = False # Stelle sicher, dass Tool 2 Ergebnisse ausgeblendet sind.

# --- Globaler Reset Button (falls der Benutzer nicht warten will) ---
st.markdown("---")
if st.button("Komplettes System zurücksetzen", key="global_reset_button"):
    st.session_state.clear()
    st.rerun()