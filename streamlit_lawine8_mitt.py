# Lawinenbewertung – Streamlit Web-App
import streamlit as st
from PIL import Image

# Setzt die Seitenkonfiguration für die Streamlit-App
st.set_page_config(page_title="Lawinenbewertung", layout="centered")

# --- Logo anzeigen ---
try:
    # Versucht, das Logo zu laden und anzuzeigen.
    # Stellt sicher, dass 'mein_logo.jpg' im selben Verzeichnis wie das Skript liegt.
    logo = Image.open("mein_logo.jpg")
    st.image(logo, width=200)
except Exception:
    # Zeigt eine Warnung an, wenn das Logo nicht geladen werden kann.
    st.warning("⚠️ Logo konnte nicht geladen werden. Bitte stellen Sie sicher, dass 'mein_logo.jpg' vorhanden ist.")

# Setzt den Titel der Anwendung
st.title("🧭 Lawinenbewertung – Massen- & Reichweitenanalyse")

# --- Konstanten für Farb-Schwellenwerte der Bewertung ---
FARB_SCHWELLENWERTE = {
    "gering": {"wert": 3.26, "text": "🟢 Geringe Gefahr", "farbe": "#90EE90"},
    "maessig": {"wert": 4.21, "text": "🟡 Mäßige Gefahr", "farbe": "#FFF176"},
    "hoch": {"text": "🔴 Hohe Gefahr", "farbe": "#FF7F7F"}
}

# --- Definition der Fragen, Optionen und Gewichte ---
fragen = [
    ("Frage 1: Größe des Geländes", [
        ("Sehr klein (z.B. schmaler Hangabschnitt - wenig Masse)", 1),
        ("Klein bis mittelgroß (einzelne Hänge oder kurze Rinnen)", 2.5),
        ("Groß (mehrere zusammenhängende Hangbereiche)", 4.5),
        ("Sehr groß (ausgedehntes Kar oder verbundenes Gelände)", 7)
    ], 1.5),
    ("Frage 2: Schneemenge und Stabilität", [
        ("Wenig Schnee, stabil (kaum Lawinenpotenzial)", 1),
        ("Mittlere Schneemenge, eher stabil (lokale Auslösungen möglich)", 4),
        ("Viel Schnee, mit Schwachschichten (erhöhtes Gefahrenpotenzial)", 5),
        ("Sehr viel Schnee, instabil - Hohe verfügbare Masse für weite Reichweite (z. B. Triebschnee, Nass- Gleitschnee,  großes Schwimmschneefundament)", 8)
    ], 2),
    ("Frage 3: Schneemenge in der Lawinenbahn", [
        ('Kaum Schnee – Lawine "verhungert"', 1),
        ("Wenig Schnee – geringe Massenvergrößerung", 4),
        ("Viel Schnee – deutliche Massenvergrößerung", 5),
        ("Sehr viel Schnee – erhebliche Massenvergrößerung (z.B. große Neuschneemengen bis ins Tal oder Triebschnee im Verlauf)", 8)
    ], 1.5),
    ("Frage 4: Bodenbeschaffenheit", [
        ("Hohe Bremswirkung → Viele Hindernisse oder rauer Boden: z. B. Felsen, Blöcke, dichter Bewuchs – verlangsamt Lawine deutlich", 1),
        ("Mäßige Bremswirkung → Teilweise bremsende Elemente: Vegetation, kleinere Unebenheiten – begrenzte Reichweitenverlängerung", 2),
        ("Geringe Bremswirkung → Glatter, harter Untergrund: z. B. kompakte Altschneedecke, verharschter Schnee – fördert längeren Fluss", 4),
        ("Sehr geringe Bremswirkung → Eisige oder steile, glatte Flächen: z. B. Lawinengras, Wasserfalleis, vereiste Altschneedecke – Lawine gleitet weit", 7)
    ], 1.2),
    ("Frage 5: Hangauslauf / Reichweite", [
        ("Kurzer Auslauf, flach → Lawine wird rasch gebremst", 1),
        ("Langer, steiler Auslauf mit Hindernissen (z.B. Bäume, Geländestufen)", 2),
        ("Langer Auslauf, wenige Hindernisse/Staubereiche → große Reichweite möglich (Pauschalgefälle-Gefälle ~ 26–27°, von Auslösepunkt bis Ende Aufschüttung)", 4),
        ("Langer, freier Auslauf – keine Hindernisse → sehr große Reichweite(Pauschalgefälle-Gefälle ~ 26–27°, von Auslösepunkt bis Ende Aufschüttung)", 7)
    ], 1),
    ("Frage 6: Potenzielle Auswirkungen – Massenbewegung", [
        ("Keine Gefahr- geringe Massenbewegung", 1),
        ("Gefahr für Einzelpersonen → könnte Menschen erfassen", 3),
        ("Gefahr für Objekte (z.B. Fahrzeuge, Bäume, kleine Bauwerke)", 8),
        ("Gefahr für Infrastruktur (z.B. Straßen, Häuser, Bahnlinien)", 8)
    ], 2),
    ("Frage 7: Potenzielle Erreichbarkeit von Skipisten oder Infrastruktur", [
        ("Weit entfernt → keine relevante Gefährdung", 1),
        ("In Sichtweite → Wahrnehmung möglich, aber keine direkte Gefährdung", 3),
        ("Kann Pisten oder Infrastruktur erreichen → potenzielle Beeinträchtigung", 8),
        ("Direkter Einfluss → trifft auf Pisten, Häuser, Verkehrswege", 8)
    ], 2)
]

# --- Initialisierung des Session State ---
# Stellt sicher, dass der Session State nur einmal initialisiert wird,
# wenn die App zum ersten Mal geladen wird oder nach einem Reset.
if "initialisiert" not in st.session_state:
    st.session_state.initialisiert = True
    st.session_state.submitted = False # Flag, ob der Berechnen-Button geklickt wurde
    # Initialisiert alle Antworten auf None
    for idx, _ in enumerate(fragen):
        st.session_state[f"antwort_{idx+1}"] = None

# --- Hilfsfunktion: Ermittlung der Bewertungsfarbe und des Textes ---
def get_bewertung_farbe(wert):
    """
    Ermittelt den Gefahrentext und die entsprechende Farbe basierend auf dem berechneten Wert.
    """
    if wert <= FARB_SCHWELLENWERTE["gering"]["wert"]:
        return FARB_SCHWELLENWERTE["gering"]["text"], FARB_SCHWELLENWERTE["gering"]["farbe"]
    elif wert <= FARB_SCHWELLENWERTE["maessig"]["wert"]:
        return FARB_SCHWELLENWERTE["maessig"]["text"], FARB_SCHWELLENWERTE["maessig"]["farbe"]
    else:
        return FARB_SCHWELLENWERTE["hoch"]["text"], FARB_SCHWELLENWERTE["hoch"]["farbe"]

# --- Callback-Funktion für Radio-Buttons ---
def handle_radio_selection(question_idx):
    """
    Diese Callback-Funktion wird ausgelöst, wenn ein Radio-Button ausgewählt wird.
    Sie aktualisiert den Wert der Antwort im Session State basierend auf der Auswahl
    und triggert dann einen Rerun der App.
    """
    # Den Key des Radio-Buttons basierend auf dem Frage-Index erstellen
    key = f"frage_{question_idx}"
    # Den aktuell ausgewählten Textwert direkt aus st.session_state holen
    # (dieser ist zum Zeitpunkt des Callback-Aufrufs bereits aktualisiert)
    selected_option_text = st.session_state[key]

    # Finde die Optionen für die aktuelle Frage
    current_question_options = fragen[question_idx - 1][1] # -1, da 'fragen' 0-indiziert ist

    # Finde den numerischen Wert, der dem ausgewählten Text entspricht
    selected_value = None
    for text, val in current_question_options:
        if selected_option_text == text:
            selected_value = val
            break
    
    # Wenn die leere Option ausgewählt wurde, setze den Wert auf None
    if selected_option_text == "":
        selected_value = None

    # Aktualisiere den Session State für die entsprechende Antwort
    st.session_state[f"antwort_{question_idx}"] = selected_value
    
    # Erzwinge einen Rerun, um die UI-Änderungen (Deaktivierung/Aktivierung) sofort anzuzeigen
    st.rerun()

# --- Anzeigen der Fragen und Verwalten der Auswahl ---
for idx, (frage, optionen, gewicht) in enumerate(fragen):
    key = f"frage_{idx+1}"
    initial_index = 0
    # Holt den zuvor gespeicherten Wert aus dem Session State
    gespeicherter_wert = st.session_state.get(f"antwort_{idx+1}")

    # Setzt den initialen Index, falls ein Wert bereits ausgewählt wurde
    if gespeicherter_wert is not None:
        for i, (text, val) in enumerate(optionen):
            if val == gespeicherter_wert:
                initial_index = i + 1 # +1, da die options-Liste einen leeren String am Anfang hat
                break

    disabled = False
    # Logik zur Deaktivierung von Frage 6 oder 7:
    # Frage 6 (idx 5) wird deaktiviert, wenn Frage 7 (idx 6) eine ausgewählte Antwort hat (nicht None).
    # Frage 7 (idx 6) wird deaktiviert, wenn Frage 6 (idx 5) eine ausgewählte Antwort hat (nicht None).
    if idx == 5: # Wenn es Frage 6 ist (Index 5 in der 'fragen'-Liste)
        # Frage 6 deaktivieren, wenn eine Antwort für Frage 7 existiert (d.h. nicht None ist)
        if st.session_state.get("antwort_7") is not None:
            disabled = True
    elif idx == 6: # Wenn es Frage 7 ist (Index 6 in der 'fragen'-Liste)
        # Frage 7 deaktivieren, wenn eine Antwort für Frage 6 existiert (d.h. nicht None ist)
        if st.session_state.get("antwort_6") is not None:
            disabled = True

    # Zeigt das Radio-Button-Widget für die aktuelle Frage an
    # Die `on_change` Callback-Funktion wird nun nur mit dem `question_idx` aufgerufen.
    auswahl = st.radio(
        frage,
        options=[""] + [opt[0] for opt in optionen], # Fügt eine leere Option am Anfang hinzu
        index=initial_index, # Setzt den voreingestellten Wert
        key=key, # Ein eindeutiger Schlüssel für das Widget im Session State
        disabled=disabled, # Steuert die Deaktivierung des Widgets
        on_change=handle_radio_selection,
        args=(idx + 1,) # Übergebe nur den Index der aktuellen Frage an den Callback
    )
    
    # Die Zeile zur Aktualisierung von st.session_state[f"antwort_{idx+1}"] direkt im Loop ist nicht mehr notwendig,
    # da die `handle_radio_selection` Callback-Funktion dies bereits erledigt.


# --- Buttons für Berechnung und Zurücksetzen ---
col1, col2 = st.columns(2)

with col1:
    # Button zum Berechnen der Lawinengefahr
    if st.button("🔍 Berechnen"):
        st.session_state.submitted = True # Setzt den Submitted-Flag

        # Prüft, ob Frage 6 oder Frage 7 beantwortet wurde
        frage6_beantwortet = st.session_state.get("antwort_6") is not None
        frage7_beantwortet = st.session_state.get("antwort_7") is not None

        # Validierung der Pflichtfragen (1-5)
        for idx in range(5):
            if st.session_state.get(f"antwort_{idx+1}") is None:
                st.warning("⚠️ Bitte alle Pflichtfragen (1-5) beantworten.")
                st.stop() # Stoppt die Ausführung, wenn nicht alle Pflichtfragen beantwortet sind

        # Validierung, dass nur Frage 6 ODER Frage 7, nicht beide, beantwortet wurden
        if frage6_beantwortet and frage7_beantwortet:
            st.error("❗ Bitte **nur Frage 6 oder Frage 7** beantworten – nicht beide.")
            st.stop()
        if not frage6_beantwortet and not frage7_beantwortet:
            st.error("❗ Bitte **Frage 6 oder Frage 7** beantworten.")
            st.stop()

        werte = []
        gewichte = []

        # Sammelt Werte und Gewichte für die Fragen 1-5
        for idx in range(5):
            wert = st.session_state.get(f"antwort_{idx+1}")
            gewicht = fragen[idx][2]
            if wert is not None:
                werte.append(wert)
                gewichte.append(gewicht)

        # Fügt den Wert und das Gewicht der ausgewählten Frage 6 oder 7 hinzu
        if frage6_beantwortet:
            wert = st.session_state.get("antwort_6")
            gewicht = fragen[5][2] # Gewicht für Frage 6
        else: # frage7_beantwortet muss True sein aufgrund der Validierung
            wert = st.session_state.get("antwort_7")
            gewicht = fragen[6][2] # Gewicht für Frage 7

        werte.append(wert)
        gewichte.append(gewicht)

        # Letzte Prüfung, ob Werte zur Berechnung vorhanden sind
        if not werte:
            st.error("❌ Es konnten keine gültigen Werte zur Berechnung erfasst werden.")
            st.stop()

        # Berechnet den ungewichteten und gewichteten Mittelwert
        mw_ung = sum(werte) / len(werte)
        mw_gew = sum(v * g for v, g in zip(werte, gewichte)) / sum(gewichte)

        # Ermittelt Text und Farbe für die Ergebnisse
        txt_ung, farbe_ung = get_bewertung_farbe(mw_ung)
        txt_gew, farbe_gew = get_bewertung_farbe(mw_gew)

        # --- Ergebnisanzeige ---
        st.subheader("📊 Ergebnisse")
        st.info("Die Bewertung zeigt die Gefahreneinschätzung nach zwei Methoden.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Ungewichteter Mittelwert:**")
            # Zeigt das Ergebnis mit Hintergrundfarbe und dem berechneten Wert an
            st.markdown(f"<div style='background-color:{farbe_ung};padding:10px;border-radius:8px'><b>{txt_ung}<br>{mw_ung:.2f}</b></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("**Gewichteter Mittelwert:**")
            # Zeigt das Ergebnis mit Hintergrundfarbe und dem berechneten Wert an
            st.markdown(f"<div style='background-color:{farbe_gew};padding:10px;border-radius:8px'><b>{txt_gew}<br>{mw_gew:.2f}</b></div>", unsafe_allow_html=True)

with col2:
    # Button zum Zurücksetzen der App
    if st.button("🔄 Zurücksetzen"):
        # Löscht alle relevanten Keys aus dem Session State, um die App auf den Initialzustand zurückzusetzen
        keys_to_delete = [key for key in st.session_state.keys() if key.startswith("antwort_") or key in ("submitted", "initialisiert")]
        for key in keys_to_delete:
            del st.session_state[key]
        st.rerun() # Erzwingt einen kompletten Neustart der Streamlit-App
