# Lawinenbewertung – Streamlit Web-App (Final)
import streamlit as st

st.set_page_config(page_title="Lawinenbewertung", layout="centered")

# --- Logo hinzufügen ---
# Der Pfad zum Bild relativ zur Python-Datei der App
logo_path = "mein_logo.png" # Wenn das Bild im selben Ordner ist
# Oder: logo_path = "bilder/mein_logo.png" # Wenn das Bild in einem Unterordner namens 'bilder' ist

st.image(logo_path, caption='Dein Lawinen-Logo', width=150) # Passe width an die gewünschte Größe an
# Optional kannst du auch einen Link zum Bild angeben, falls es online gehostet wird:
# st.image("https://example.com/pfad/zu/deinem/logo.png", caption='Online-Logo', width=150)

st.title("🧭 Lawinenbewertung – Massen- & Reichweitenanalyse")

# --- Konstanten ---
FARB_SCHWELLENWERTE = {
    "gering": {"wert": 2, "text": "🟢 Geringe Gefahr", "farbe": "#90EE90"},
    "maessig": {"wert": 4, "text": "🟡 Mäßige Gefahr", "farbe": "#FFF176"},
    "hoch": {"text": "🔴 Hohe Gefahr", "farbe": "#FF7F7F"}
}

fragen = [
    ("Frage 1: Größe des Geländes", [
        ("Sehr klein (z. B. schmaler Hangabschnitt)", 1),
        ("Klein bis mittelgroß", 2.5),
        ("Groß (mehrere Hangbereiche)", 4.5),
        ("Sehr groß (Kar, verbundenes Gelände)", 7)
    ], 1.5),
    ("Frage 2: Schneemenge / Stabilität", [
        ("Wenig Schnee, stabil", 1),
        ("Mittlere Schneemenge, eher stabil", 4),
        ("Viel Schnee, mit Schwachschichten", 5),
        ("Sehr viel Schnee, instabil (z. B. Triebschnee, Nassschnee)", 8)
    ], 2),
    ("Frage 3: Schneemenge innerhalb der Lawine", [
        ("Kaum Schnee – Lawine \"verhungert\"", 1),
        ("Wenig Schnee – geringe Massenvergrößerung", 4),
        ("Viel Schnee – deutliche Massenvergrößerung", 5),
        ("Sehr viel Schnee – erhebliche Massenvergrößerung", 8)
    ], 1.5),
    ("Frage 4: Reibung / Unterlage", [
        ("Nein, viel Reibung → bremst Lawine", 1),
        ("Teilweise gefüllt", 2),
        ("Weitgehend glatt oder gefüllt → wenig Bremsung", 4),
        ("Vollständig glatt/eingefahren → fast keine Reibung", 7)
    ], 1.2),
    ("Frage 5: Hangauslauf / Reichweite", [
        ("Nur kurz steil, danach flach → bremst schnell", 1),
        ("Langer steiler Hangauslauf mit Hindernissen", 2),
        ("Lang steil, einige Hindernisse / Staubereiche, große Reichweite", 4),
        ("Lang steil, keine Hindernisse im Auslauf → sehr große Reichweite", 7)
    ], 1),
    ("Frage 6: Potenzielle Auswirkungen – Massenbewegung", [
        ("Keine Gefahr, kaum Massenbewegung", 1),
        ("Könnte eine Person erfassen", 3),
        ("Könnte Fahrzeuge zerstören / Bäume fällen", 5),
        ("Infrastruktur gefährdet (Straßen, Häuser, Züge)", 8)
    ], 2),
    ("Frage 7: Entfernung zu Pisten / Infrastruktur", [
        ("Lawine weit entfernt (keine Gefahr)", 1),
        ("In Sichtweite von Pisten", 3),
        ("Kann Pisten erreichen oder beeinflussen", 5),
        ("Trifft direkt auf Pisten / Infrastruktur", 8)
    ], 2)
]

# --- Initialisierung des Session State ---
if "initialisiert" not in st.session_state:
    st.session_state.initialisiert = True
    st.session_state.submitted = False
    st.session_state.frage_6_ausgewaehlt = False
    st.session_state.frage_7_ausgewaehlt = False
    for idx, _ in enumerate(fragen):
        st.session_state[f"antwort_{idx+1}"] = None # Speichert den ausgewählten Wert

# --- Funktionen ---
def get_bewertung_farbe(wert):
    """Gibt den Text und die Farbe basierend auf dem Wert zurück."""
    if wert <= FARB_SCHWELLENWERTE["gering"]["wert"]:
        return FARB_SCHWELLENWERTE["gering"]["text"], FARB_SCHWELLENWERTE["gering"]["farbe"]
    elif wert <= FARB_SCHWELLENWERTE["maessig"]["wert"]:
        return FARB_SCHWELLENWERTE["maessig"]["text"], FARB_SCHWELLENWERTE["maessig"]["farbe"]
    else:
        return FARB_SCHWELLENWERTE["hoch"]["text"], FARB_SCHWELLENWERTE["hoch"]["farbe"]

# --- Fragen anzeigen ---
for idx, (frage, optionen, gewicht) in enumerate(fragen):
    key = f"frage_{idx+1}"
    
    # Bestimme den Initialwert für das Radio-Widget aus dem Session State
    initial_index = 0
    gespeicherter_wert = st.session_state.get(f"antwort_{idx+1}")
    if gespeicherter_wert is not None:
        for i, (text, val) in enumerate(optionen):
            if val == gespeicherter_wert:
                initial_index = i + 1
                break

    # Deaktivierungslogik für Frage 6/7
    disabled = False
    if idx == 5: # Frage 6
        if st.session_state.frage_7_ausgewaehlt:
            disabled = True
    elif idx == 6: # Frage 7
        if st.session_state.frage_6_ausgewaehlt:
            disabled = True

    auswahl = st.radio(
        frage,
        options=[""] + [opt[0] for opt in optionen],
        index=initial_index,
        key=key,
        disabled=disabled
    )

    # Wert extrahieren und im Session State speichern
    wert = None
    for text, val in optionen:
        if auswahl == text:
            wert = val
            break
    st.session_state[f"antwort_{idx+1}"] = wert

    # Aktualisiere den Zustand für Frage 6 und 7
    if idx == 5: # Frage 6 (Index 5)
        st.session_state.frage_6_ausgewaehlt = (wert is not None)
    elif idx == 6: # Frage 7 (Index 6)
        st.session_state.frage_7_ausgewaehlt = (wert is not None)

# --- Buttons ---
col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 Berechnen"):
        st.session_state.submitted = True

        frage6_ausgewaehlt = st.session_state.frage_6_ausgewaehlt
        frage7_ausgewaehlt = st.session_state.frage_7_ausgewaehlt

        # Validierung: Alle Pflichtfragen beantwortet?
        alle_pflichtfragen_beantwortet = True
        for idx in range(5): # Fragen 1-5 sind immer Pflicht
            if st.session_state.get(f"antwort_{idx+1}") is None:
                alle_pflichtfragen_beantwortet = False
                break
        
        if not alle_pflichtfragen_beantwortet:
            st.warning(⚠️ Bitte alle Pflichtfragen (1-5) beantworten.")
            st.stop()

        # Validierung: Nur eine von Frage 6 oder 7 beantwortet?
        if frage6_ausgewaehlt and frage7_ausgewaehlt:
            st.error("❗ Bitte **nur Frage 6 oder Frage 7** beantworten – nicht beide.")
            st.stop()

        if not frage6_ausgewaehlt and not frage7_ausgewaehlt:
            st.error("❗ Bitte **Frage 6 oder Frage 7** beantworten.")
            st.stop()

        werte_fuer_berechnung = []
        gewichte_fuer_berechnung = []

        # Fragen 1-5 hinzufügen
        for idx in range(5):
            wert = st.session_state.get(f"antwort_{idx+1}")
            gewicht = fragen[idx][2]
            if wert is not None:
                werte_fuer_berechnung.append(wert)
                gewichte_fuer_berechnung.append(gewicht)

        # Entweder Frage 6 oder Frage 7 hinzufügen
        if frage6_ausgewaehlt:
            wert = st.session_state.get(f"antwort_6")
            gewicht = fragen[5][2]
            if wert is not None:
                werte_fuer_berechnung.append(wert)
                gewichte_fuer_berechnung.append(gewicht)
        elif frage7_ausgewaehlt:
            wert = st.session_state.get(f"antwort_7")
            gewicht = fragen[6][2]
            if wert is not None:
                werte_fuer_berechnung.append(wert)
                gewichte_fuer_berechnung.append(gewicht)

        if not werte_fuer_berechnung:
            st.error("❌ Es konnten keine gültigen Werte zur Berechnung erfasst werden.")
            st.stop()

        # --- Berechnung ---
        mw_ung = sum(werte_fuer_berechnung) / len(werte_fuer_berechnung)
        # KORRIGIERTE ZEILE FÜR GEWICHTETEN MITTELWERT
        mw_gew = sum(v * g for v, g in zip(werte_fuer_berechnung, gewichte_fuer_berechnung)) / sum(gewichte_fuer_berechnung)

        txt_ung, farbe_ung = get_bewertung_farbe(mw_ung)
        txt_gew, farbe_gew = get_bewertung_farbe(mw_gew)

        # --- Ergebnisse anzeigen ---
        st.subheader("📊 Ergebnisse")
        st.info("Der **ungewichtete Mittelwert** gibt einen generellen Überblick über das Gefahrenpotenzial. Der **gewichtete Mittelwert** berücksichtigt die individuelle Relevanz jeder Frage und bietet eine präzisere Einschätzung.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Ungewichteter Mittelwert:** {mw_ung:.2f}")
            st.markdown(f"<div style='background-color:{farbe_ung};padding:10px;border-radius:8px'><b>{txt_ung}</b></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"**Gewichteter Mittelwert:** {mw_gew:.2f}")
            st.markdown(f"<div style='background-color:{farbe_gew};padding:10px;border-radius:8px'><b>{txt_gew}</b></div>", unsafe_allow_html=True)

with col2:
    if st.button("🔄 Zurücksetzen"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()