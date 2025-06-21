# Lawinenbewertung – Streamlit Web-App
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Lawinenbewertung", layout="centered")

# --- Logo anzeigen ---
try:
    logo = Image.open("mein_logo.jpg")
    st.image(logo, width=200)
except Exception:
    st.warning("⚠️ Logo konnte nicht geladen werden.")

st.title("🧭 Lawinenbewertung – Massen- & Reichweitenanalyse")

# --- Konstanten ---
FARB_SCHWELLENWERTE = {
    "gering": {"wert": 3.15, "text": "🟢 Geringe Gefahr", "farbe": "#90EE90"},
    "maessig": {"wert": 3.7, "text": "🟡 Mäßige Gefahr", "farbe": "#FFF176"},
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
    ("Frage 3: Schneemenge innerhalb der Lawinenbahn", [
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
        ("Könnte Fahrzeuge zerstören / Bäume fällen", 8),
        ("Infrastruktur gefährdet (Straßen, Häuser, Züge)", 8)
    ], 2),
    ("Frage 7: Entfernung zu Pisten / Infrastruktur", [
        ("Lawine weit entfernt (keine Gefahr)", 1),
        ("In Sichtweite von Pisten", 3),
        ("Kann Pisten erreichen oder beeinflussen", 8),
        ("Trifft direkt auf Pisten / Infrastruktur", 8)
    ], 2)
]

# --- Initialisierung ---
if "initialisiert" not in st.session_state:
    st.session_state.initialisiert = True
    st.session_state.submitted = False
    st.session_state.frage_6_ausgewaehlt = False
    st.session_state.frage_7_ausgewaehlt = False
    for idx, _ in enumerate(fragen):
        st.session_state[f"antwort_{idx+1}"] = None

# --- Hilfsfunktion ---
def get_bewertung_farbe(wert):
    if wert <= FARB_SCHWELLENWERTE["gering"]["wert"]:
        return FARB_SCHWELLENWERTE["gering"]["text"], FARB_SCHWELLENWERTE["gering"]["farbe"]
    elif wert <= FARB_SCHWELLENWERTE["maessig"]["wert"]:
        return FARB_SCHWELLENWERTE["maessig"]["text"], FARB_SCHWELLENWERTE["maessig"]["farbe"]
    else:
        return FARB_SCHWELLENWERTE["hoch"]["text"], FARB_SCHWELLENWERTE["hoch"]["farbe"]

# --- Fragen anzeigen ---
for idx, (frage, optionen, gewicht) in enumerate(fragen):
    key = f"frage_{idx+1}"
    initial_index = 0
    gespeicherter_wert = st.session_state.get(f"antwort_{idx+1}")
    if gespeicherter_wert is not None:
        for i, (text, val) in enumerate(optionen):
            if val == gespeicherter_wert:
                initial_index = i + 1
                break

    disabled = False
    if idx == 5 and st.session_state.frage_7_ausgewaehlt:
        disabled = True
    elif idx == 6 and st.session_state.frage_6_ausgewaehlt:
        disabled = True

    auswahl = st.radio(
        frage,
        options=[""] + [opt[0] for opt in optionen],
        index=initial_index,
        key=key,
        disabled=disabled
    )

    wert = None
    for text, val in optionen:
        if auswahl == text:
            wert = val
            break
    st.session_state[f"antwort_{idx+1}"] = wert

    if idx == 5:
        st.session_state.frage_6_ausgewaehlt = (wert is not None)
    elif idx == 6:
        st.session_state.frage_7_ausgewaehlt = (wert is not None)

# --- Buttons ---
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Berechnen"):
        st.session_state.submitted = True
        frage6 = st.session_state.frage_6_ausgewaehlt
        frage7 = st.session_state.frage_7_ausgewaehlt

        for idx in range(5):
            if st.session_state.get(f"antwort_{idx+1}") is None:
                st.warning("⚠️ Bitte alle Pflichtfragen (1-5) beantworten.")
                st.stop()

        if frage6 and frage7:
            st.error("❗ Bitte **nur Frage 6 oder Frage 7** beantworten – nicht beide.")
            st.stop()
        if not frage6 and not frage7:
            st.error("❗ Bitte **Frage 6 oder Frage 7** beantworten.")
            st.stop()

        werte = []
        gewichte = []

        for idx in range(5):
            wert = st.session_state.get(f"antwort_{idx+1}")
            gewicht = fragen[idx][2]
            if wert is not None:
                werte.append(wert)
                gewichte.append(gewicht)

        if frage6:
            wert = st.session_state.get("antwort_6")
            gewicht = fragen[5][2]
        else:
            wert = st.session_state.get("antwort_7")
            gewicht = fragen[6][2]

        werte.append(wert)
        gewichte.append(gewicht)

        if not werte:
            st.error("❌ Es konnten keine gültigen Werte zur Berechnung erfasst werden.")
            st.stop()

        mw_ung = sum(werte) / len(werte)
        mw_gew = sum(v * g for v, g in zip(werte, gewichte)) / sum(gewichte)

        txt_ung, farbe_ung = get_bewertung_farbe(mw_ung)
        txt_gew, farbe_gew = get_bewertung_farbe(mw_gew)

        # --- Ergebnisanzeige ---
        st.subheader("📊 Ergebnisse")
        st.info("Die Bewertung zeigt die Gefahreneinschätzung nach zwei Methoden.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Ungewichteter Mittelwert:**")
            st.markdown(f"<div style='background-color:{farbe_ung};padding:10px;border-radius:8px'><b>{txt_ung}<br>{mw_ung:.2f}</b></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("**Gewichteter Mittelwert:**")
            st.markdown(f"<div style='background-color:{farbe_gew};padding:10px;border-radius:8px'><b>{txt_gew}<br>{mw_gew:.2f}</b></div>", unsafe_allow_html=True)

with col2:
    if st.button("🔄 Zurücksetzen"):
        keys_to_delete = [key for key in st.session_state.keys() if key.startswith("antwort_") or key in ("frage_6_ausgewaehlt", "frage_7_ausgewaehlt", "submitted", "initialisiert")]
        for key in keys_to_delete:
            del st.session_state[key]
        st.rerun()
