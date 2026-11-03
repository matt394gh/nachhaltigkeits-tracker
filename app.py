"""
app.py – Nachhaltigkeits-Tracker für Kleidung (Haupt-App)
=========================================================

Klausurersatzleistung Informatik (profilaffin)

So funktioniert die App:
  1. Nutzer:in lädt ein Foto von einem Kleidungsstück oder Waschetikett hoch.
  2. In der Sidebar wählt man, welche KI-Version analysieren soll:
       Version A – eigenes Modell (Teachable Machine, bis dahin: Dummy)
       Version B – vortrainiertes Modell (Florence-2, läuft lokal)
  3. Das KI-Ergebnis wird mit der lokalen Markendatenbank
     (sustainability_db.json, ganz ohne API-Key/Secrets) abgeglichen.
  4. Die App zeigt Öko-Score, Einordnung und die geschätzte
     CO2-Bilanz (inkl. Waschgängen).
  5. Die Ergebnis-Historie unten sammelt beide Versionen, damit man
     sie später fair vergleichen kann (Punkt "Vergleich der Versionen").

Start im Terminal:   streamlit run app.py
"""

import os
from pathlib import Path

import streamlit as st
from PIL import Image

import model_a
import model_b
import scoring

DB_PFAD = "sustainability_db.json"

# Seiteneinstellungen MÜSSEN als erster Streamlit-Befehl stehen
st.set_page_config(
    page_title="Nachhaltigkeits-Tracker für Kleidung",
    layout="wide",
)

# ---------------------------------------------------------------
# Datenbank laden (lokale JSON-Datei – keine Secrets nötig!)
# ---------------------------------------------------------------
if "datenbank" not in st.session_state:
    st.session_state.datenbank = scoring.lade_datenbank(DB_PFAD)
datenbank = st.session_state.datenbank


def text_kurz(text: str, max_zeichen: int = 120) -> str:
    """Kürzt lange Texte für Überschriften."""
    if len(text) > max_zeichen:
        return text[:max_zeichen] + " ..."
    return text


# ---------------------------------------------------------------
# SIDEBAR: Auswahl der KI-Version
# ---------------------------------------------------------------
st.sidebar.title("Einstellungen")

version = st.sidebar.radio(
    "Welche KI-Version soll analysieren?",
    [
        "Version A - eigenes Modell (Teachable Machine)",
        "Version B - vortrainiertes Modell (Florence-2)",
    ],
)

# ----- Zusatzoptionen je nach Version -----
if version.startswith("Version A"):
    status = model_a.modell_status()
    if status == "echt":
        st.sidebar.success(
            "Echtes Teachable-Machine-Modell gefunden (models/teachable_model/)."
        )
    else:
        st.sidebar.warning(
            "Noch kein Modell trainiert: Es läuft der DUMMY-Klassifikator. "
            "Anleitung: models/ANLEITUNG-teachable-machine.md"
        )
else:
    st.sidebar.info(
        "Florence-2 läuft komplett lokal - kein API-Key, keine Secrets, "
        "keine Kosten. Beim ersten Start werden einmalig ca. 500 MB "
        "Modellgewichte heruntergeladen."
    )
    aufgabe_b = st.sidebar.radio(
        "Was soll Florence-2 tun?",
        ["Automatisch (OCR, sonst Beschreibung)", "Nur OCR (Etikett)",
         "Nur Bildbeschreibung"],
    )

st.sidebar.divider()
st.sidebar.caption(
    "Klausurersatzleistung Informatik: "
    "Vergleich eines selbst trainierten Modells (A) mit einem "
    "vortrainierten Modell (B)."
)

# ---------------------------------------------------------------
# HAUPTBEREICH: Titel + Upload
# ---------------------------------------------------------------
st.title("Nachhaltigkeits-Tracker für Kleidung")
st.markdown(
    "Foto von einem Kleidungsstück oder Waschetikett hochladen - "
    "die KI erkennt Marke bzw. Kategorie und die App schätzt den "
    "Öko-Score sowie die CO2-Bilanz ein."
)

hochgeladene_datei = st.file_uploader(
    "Foto hochladen (JPG oder PNG)",
    type=["jpg", "jpeg", "png"],
)

# ---------------------------------------------------------------
# Ergebnis-Historie über mehrere Analysen hinweg (für den Vergleich)
# ---------------------------------------------------------------
if "historie" not in st.session_state:
    st.session_state.historie = []

if hochgeladene_datei is not None:

    # Bild öffnen (PIL kann mit den Streamlit-Upload-Daten umgehen)
    bild = Image.open(hochgeladene_datei)

    linke_spalte, rechte_spalte = st.columns([1, 1.4])

    with linke_spalte:
        st.subheader("Hochgeladenes Foto")
        st.image(bild, use_container_width=True)
        st.caption(
            f"Datei: {hochgeladene_datei.name} | "
            f"Größe: {bild.width} x {bild.height} Pixel"
        )

    with rechte_spalte:
        st.subheader("KI-Analyse")

        # ----- Schritt 1: Die gewählte KI-Version ausführen -----
        if version.startswith("Version A"):
            with st.spinner("Modell A klassifiziert das Foto ..."):
                ergebnis = model_a.klassifizieren(bild)
                quelle = "Modell A (Teachable Machine)"
                if model_a.modell_status() == "dummy":
                    quelle = "Modell A (DUMMY - Platzhalter)"
        else:
            aufgabe_map = {
                "Automatisch (OCR, sonst Beschreibung)": "automatisch",
                "Nur OCR (Etikett)": "nur_ocr",
                "Nur Bildbeschreibung": "nur_beschreibung",
            }
            with st.spinner(
                "Florence-2 analysiert das Foto "
                "(beim ersten Start: Modell wird geladen) ..."
            ):
                try:
                    ergebnis = model_b.analysieren(bild, aufgabe_map[aufgabe_b])
                    quelle = f"Modell B (Florence-2, {aufgabe_b})"
                except Exception as fehler:   # z. B. kein Internet beim Download
                    st.error(
                        "Florence-2 konnte nicht geladen werden. "
                        "Prüfe die Installation von 'transformers' und 'torch' "
                        "(siehe requirements.txt) bzw. die Internetverbindung "
                        "beim allerersten Start."
                    )
                    st.exception(fehler)
                    st.stop()

        st.caption(f"Quelle: {quelle}")

        # ----- Schritt 2: KI-Ergebnis anzeigen -----
        st.markdown(f"**Erkennung:** {text_kurz(ergebnis['label'] or '(kein Text erkannt)')}")
        if ergebnis["konfidenz"] is not None:
            st.markdown(f"**Konfidenz:** {ergebnis['konfidenz'] * 100:.1f} %")

        details = ergebnis.get("details", {})
        if isinstance(details, dict) and "ocr_text" in details:
            st.markdown("**Von Florence-2 gelesener Text (OCR):**")
            st.code(details["ocr_text"] or "(kein Text erkannt)", language=None)
        if isinstance(details, dict) and "bildbeschreibung" in details:
            st.markdown("**Bildbeschreibung von Florence-2:**")
            st.write(details["bildbeschreibung"])

        # ----- Schritt 3: Abgleich mit der Markendatenbank -----
        st.markdown("---")
        st.markdown("**Abgleich mit der Markendatenbank**")

        # scoring prueft zuerst Marken, danach Kategorie-Fallback
        eintrag, info = scoring.eintrag_fuer_ergebnis(
            datenbank,
            ergebnis["label"],
            kategorie=ergebnis["label"],
        )

        if eintrag is None:
            st.warning(
                "Keine Marke in der Datenbank gefunden. Tipp: Foto vom "
                "Brandprint oder Waschetikett machen, dann den OCR-Text "
                "in der Tabelle unten mit den Datenbank-Marken vergleichen."
            )
            materialien = []
            if isinstance(details, dict):
                materialien = scoring.material_erkennen(
                    details.get("ocr_text", "")
                    + " " + details.get("bildbeschreibung", "")
                )
            if materialien:
                st.markdown("**Erkannte Materialien:** " + ", ".join(materialien))
        else:
            st.markdown(f"**Gefunden:** {eintrag['name']} "
                        f"*(Abgleich: {info['treffer_art']}, {info['methode']})*")
            st.info(eintrag["bemerkung"])

            stufe = scoring.oeko_stufe(eintrag["score"])
            score_spalte1, score_spalte2 = st.columns([1, 2])
            with score_spalte1:
                st.metric("Öko-Score (Schätzung)", f"{eintrag['score']} / 100",
                          help=stufe["stufe"])
            with score_spalte2:
                st.markdown(f"**Einordnung:** {stufe['stufe']}")
                st.progress(eintrag["score"] / 100)
            st.caption("Kategorie: " + eintrag["kategorie"].replace("_", " "))

            # ----- Schritt 4: CO2-Bilanz (Extra-Feature) -----
            st.markdown("#### CO2-Bilanz-Rechner")
            wasch_spalte1, wasch_spalte2 = st.columns(2)
            with wasch_spalte1:
                waschgaenge = st.slider(
                    "Waschgänge pro Woche (Anteil an einer Trommel)",
                    min_value=0.0, max_value=2.0, value=0.25, step=0.05,
                    help="0.25 bedeutet: das Stück ist bei jeder vierten Wäsche dabei.",
                )
            with wasch_spalte2:
                nutzungsjahre = st.slider(
                    "Geplante Nutzungsdauer in Jahren",
                    min_value=0.5, max_value=15.0, value=3.0, step=0.5,
                )

            co2 = scoring.berechne_co2(
                eintrag["co2_pro_teil_kg"], waschgaenge, nutzungsjahre
            )
            c_spalte1, c_spalte2, c_spalte3 = st.columns(3)
            c_spalte1.metric("Herstellung", f"{co2['co2_herstellung_kg']} kg")
            c_spalte2.metric("Waschen", f"{co2['co2_waschen_kg']} kg")
            c_spalte3.metric("Gesamt", f"{co2['co2_gesamt_kg']} kg CO2e")

            with st.expander("Annahmen des Rechners (Transparenz)"):
                st.write(
                    f"- {scoring.KWH_PRO_WASCHGANG} kWh pro Waschgang (40 Grad, volle Trommel)\n"
                    f"- {scoring.STROMMIX_KG_CO2_PRO_KWH} kg CO2 pro kWh (deutscher Strommix, Schätzung)\n"
                    f"- durchschnittlich {scoring.TEILE_PRO_TROMMEL} Teile pro Trommel\n"
                    f"- rund {co2['waschgaenge_gesamt']} Wäschen, an denen das Stück beteiligt ist"
                )
                st.caption(
                    "Alle Werte sind Schätzungen für dieses Schulprojekt "
                    "(siehe Projektdokumentation, Kapitel Grenzen)."
                )

        # ----- Schritt 5: Ergebnis für den Modellvergleich merken -----
        st.session_state.historie.append({
            "Version": quelle,
            "Erkennung": text_kurz(ergebnis["label"] or "(kein Text)", 40),
            "Treffer": (eintrag["name"] if eintrag else "-"),
            "Score": (eintrag["score"] if eintrag else None),
            "Datei": hochgeladene_datei.name,
        })

else:
    st.info(
        "Zuerst ein Foto hochladen. Gute Testmotive: Brandprint auf der "
        "Brust, Etikett im Kragen oder Waschetikett in der Seitennaht."
    )

# ---------------------------------------------------------------
# HISTORIE (unten): sammelt Ergebnisse beider Versionen
# -> Grundlage für den fairen Vergleich im Kriterienraster
# ---------------------------------------------------------------
st.markdown("---")
st.subheader("Ergebnis-Historie (Grundlage für den Modellvergleich)")
st.caption(
    "Wichtig für faire Testbedingungen: dasselbe Foto mit Version A UND "
    "Version B analysieren, dann stehen beide Ergebnisse nebeneinander."
)

if st.session_state.historie:
    historie_spalte, knopf_spalte = st.columns([4, 1])
    with historie_spalte:
        st.dataframe(
            st.session_state.historie,
            use_container_width=True,
            hide_index=True,
        )
    with knopf_spalte:
        if st.button("Historie löschen"):
            st.session_state.historie = []
            st.rerun()
else:
    st.write("Noch keine Analysen in dieser Sitzung.")

# ---------------------------------------------------------------
# Hinweise & Grenzen (wird im Kriterienraster bewertet)
# ---------------------------------------------------------------
with st.expander("Was diese App kann - und was nicht (Grenzen)"):
    st.markdown(
        """
        - Alle Scores und CO2-Werte sind **didaktische Schätzwerte** aus der
          lokalen Datei `sustainability_db.json` - keine offizielle Zertifizierung.
        - Version A ist so gut wie die selbst aufgenommenen Trainingsbilder
          (Beleuchtung, Ausschnitt, Anzahl pro Klasse).
        - Version B liest nur sichtbaren Text; unscharfe Etiketten kann sie
          nicht rekonstruieren.
        - Die App bewertet einzelne Stücke - echtes Konsumverhalten
          (Kaufhäufigkeit, Pflege, Entsorgung) bleibt außen vor.
        """
    )
