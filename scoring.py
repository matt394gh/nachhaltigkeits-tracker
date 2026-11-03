"""
scoring.py – Logik zwischen KI-Ergebnis und Markendatenbank
===========================================================

Dieses Modul verbindet die beiden KI-Versionen mit der Datenbank:

1.  lade_datenbank()      : liest sustainability_db.json ein (einfach,
                            ohne API-Key und ohne Secrets).
2.  finde_marke()         : sucht einen Markennamen im Datenbank-Abgleich.
3.  eintrag_fuer_ergebnis(): ordnet das KI-Ergebnis (Marke ODER Kategorie)
                            einem Datenbank-Eintrag zu.
4.  material_erkennen()   : findet Stoffangaben im erkannten Text.
5.  oeko_stufe()          : wandelt den Score in eine Stufe + Farbe um.
6.  berechne_co2()        : rechnet die CO2-Bilanz inklusive Waschgängen aus.
"""

import difflib
import json
from pathlib import Path

# ---------------------------------------------------------------
# Konstanten für den CO2-Rechner (Schaetzwerte, in der Doku begründet)
# ---------------------------------------------------------------
STROMMIX_KG_CO2_PRO_KWH = 0.38   # deutscher Strommix (grobe Schätzung)
KWH_PRO_WASCHGANG = 1.0          # Waschmaschine bei 40 Grad, volle Trommel
TEILE_PRO_TROMMEL = 4.0          # durchschnittliche Anzahl Teile pro Wäsche
WOCHEN_PRO_JAHR = 52

# Beispiele für Stoffangaben, die auf Etiketten vorkommen können.
# Schlüssel = Suchwort (kleingeschrieben), Wert = schöner Anzeigename.
MATERIAL_SUCHWOERTER = {
    "baumwolle": "Baumwolle (konventionell)",
    "cotton": "Baumwolle (konventionell)",
    "bio-baumwolle": "Bio-Baumwolle",
    "organic cotton": "Bio-Baumwolle",
    "recyceltes polyester": "Recyceltes Polyester",
    "recycled polyester": "Recyceltes Polyester",
    "polyester": "Polyester (Neuproduktion)",
    "wolle": "Wolle",
    "wool": "Wolle",
    "leinen": "Leinen",
    "linen": "Leinen",
    "viskose": "Viskose",
    "elastan": "Elasthan",
    "elasthan": "Elasthan",
    "polyamid": "Polyamid",
    "seide": "Seide",
    "silk": "Seide",
    "leder": "Leder",
}

# Durchschnittswerte pro Kategorie – falls das KI-Ergebnis nur eine
# Kategorie (z. B. "fast_fashion") statt einer Marke liefert.
KATEGORIE_STANDARDWERTE = {
    "fast_fashion": {"score": 20, "co2_pro_teil_kg": 12.0,
                     "bemerkung": "Durchschnittswert der Kategorie Fast Fashion (Schaetzung)."},
    "mittel": {"score": 45, "co2_pro_teil_kg": 9.0,
               "bemerkung": "Durchschnittswert der Kategorie Mittel (Schaetzung)."},
    "nachhaltig": {"score": 85, "co2_pro_teil_kg": 6.0,
                   "bemerkung": "Durchschnittswert der Kategorie Nachhaltig (Schaetzung)."},
}


def lade_datenbank(pfad: str = "sustainability_db.json") -> dict:
    """Liest die lokale Markendatenbank als JSON-Datei ein.

    Wichtig fuer die Doku: Es handelt sich um einen simplen lokalen
    Dateizugriff - es braucht dazu keine API-Keys und keine Secrets.
    """
    with open(Path(pfad), "r", encoding="utf-8") as datei:
        return json.load(datei)


def _normalisiere(text: str) -> str:
    """Vereinfacht einen Text fuer den Vergleich.

    Beispiele:  'H&M!' -> 'hm'   |   '  SHEIN ' -> 'shein'
    """
    kleinschrift = text.lower().strip()
    erlaubt = "abcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(zeichen for zeichen in kleinschrift if zeichen in erlaubt)


def finde_marke(datenbank: dict, suchtext: str):
    """Sucht in der Datenbank nach einer Marke.

    Vorgehen (von schnell nach teuer):
      1. Exakter Treffer bei Name oder Alias (nach Normalisierung)
      2. Enthaltener Text (z. B. 'SHEIN 100% POLYESTER' enthaelt 'shein')
      3. Fuzzy-Match (aehnliche Schreibweise, z. B. Tippfehler der OCR)

    Rueckgabe: (marken_eintrag | None, methode: str)
    """
    if not suchtext:
        return None, "kein Text"

    suchtext_normalisiert = _normalisiere(suchtext)
    if not suchtext_normalisiert:
        return None, "kein Text"

    # 1) Exakter Treffer
    for marke in datenbank["marken"]:
        kandidaten = [marke["name"]] + marke.get("aliase", [])
        for kandidat in kandidaten:
            if _normalisiere(kandidat) == suchtext_normalisiert:
                return marke, "exakter Treffer"

    # 2) Marke steckt im laengeren Text (typisch bei OCR vom Etikett)
    for marke in datenbank["marken"]:
        kandidaten = [marke["name"]] + marke.get("aliase", [])
        for kandidat in kandidaten:
            if len(_normalisiere(kandidat)) >= 3 and _normalisiere(kandidat) in suchtext_normalisiert:
                return marke, "im Text gefunden"

    # 3) Fuzzy-Match ueber difflib (Standardbibliothek)
    #    Wichtig: Vergleich auf Basis der NORMALISIERTEN Namen, sonst
    #    wuerden Gross-/Kleinschreibung und Sonderzeichen (&, %) den
    #    Aehnlichkeitsvergleich verfaelschen.
    kandidaten_normalisiert = []   # Liste aus (normalisiert, marke)
    for marke in datenbank["marken"]:
        for kandidat in [marke["name"]] + marke.get("aliase", []):
            kandidaten_normalisiert.append((_normalisiere(kandidat), marke))

    beste = difflib.get_close_matches(
        suchtext_normalisiert,
        [k for k, _ in kandidaten_normalisiert],
        n=1, cutoff=0.8,
    )
    if beste:
        for kandidat, marke in kandidaten_normalisiert:
            if kandidat == beste[0]:
                return marke, "aehnliche Schreibweise (Fuzzy)"

    return None, "nicht gefunden"


def eintrag_fuer_kategorie(datenbank: dict, kategorie: str):
    """Baut aus einer Kategorie (z. B. 'fast_fashion') einen pseudo-Eintrag.

    Das brauchen wir, wenn das Modell keine Marke, sondern nur eine
    Kategorie erkannt hat (typisch bei Modell A im Dummy-Modus).
    """
    kategorie = (kategorie or "").lower().strip()
    if kategorie in KATEGORIE_STANDARDWERTE:
        standard = KATEGORIE_STANDARDWERTE[kategorie]
        anzahl = sum(1 for m in datenbank["marken"] if m["kategorie"] == kategorie)
        return {
            "name": f"Kategorie: {kategorie.replace('_', ' ').capitalize()}",
            "kategorie": kategorie,
            "score": standard["score"],
            "co2_pro_teil_kg": standard["co2_pro_teil_kg"],
            "bemerkung": standard["bemerkung"] + f" ({anzahl} Marken in der Datenbank)",
        }
    return None


def eintrag_fuer_ergebnis(datenbank: dict, label_text: str, kategorie: str = ""):
    """Kernfunktion: KI-Ergebnis -> Datenbank-Eintrag.

    Reihenfolge:
      1. Marke im Label-Text suchen (Modell B: OCR-Text, Modell A: Klassenname)
      2. Falls nichts gefunden: Kategorie als Fallback benutzen
    Rueckgabe: (eintrag | None, info_dict mit Details zum Abgleich)
    """
    marke, methode = finde_marke(datenbank, label_text or "")
    if marke:
        return marke, {"treffer_art": "Marke", "methode": methode, "suchtext": label_text}

    fallback = eintrag_fuer_kategorie(datenbank, kategorie or label_text)
    if fallback:
        return fallback, {"treffer_art": "Kategorie", "methode": "Kategorie-Fallback",
                          "suchtext": kategorie or label_text}

    return None, {"treffer_art": "kein Treffer", "methode": methode, "suchtext": label_text}


def material_erkennen(text: str) -> list:
    """Findet Stoffangaben (z. B. 'Baumwolle', 'Polyester') in einem Text.

    Trick gegen Teilwort-Fehltreffer: Wir pruefen die Suchwoerter vom
    LAENGSTEN zum KUERZESTEN und schneiden jeden Fund aus dem Text
    heraus. Dadurch meldet 'BAUMWOLLE' nur Baumwolle - und nicht
    zusaetzlich 'Wolle' (das als Teilwort darin steckt).

    Rueckgabe: Liste von Anzeigenamen, ohne Duplikate, in Fundreihenfolge.
    """
    gefundene = []
    arbeitstext = (text or "").lower()
    # Nach Laenge absteigend sortieren -> lange Suchwoerter zuerst
    sortierte_woerter = sorted(MATERIAL_SUCHWOERTER.items(),
                               key=lambda eintrag: len(eintrag[0]),
                               reverse=True)
    for suchwort, anzeigename in sortierte_woerter:
        if suchwort in arbeitstext and anzeigename not in gefundene:
            gefundene.append(anzeigename)
            arbeitstext = arbeitstext.replace(suchwort, " ")   # Fund entfernen
    return gefundene


def oeko_stufe(score: int) -> dict:
    """Wandelt einen Score (0-100) in eine Stufe mit Farbe um.

    Die Farben entsprechen den Streamlit-Farbelementen:
    green (gut), orange (mittel), red (schlecht).
    """
    if score >= 75:
        return {"stufe": "Sehr gut", "farbe": "green", "emoji_aehnlich": "Plus"}
    if score >= 50:
        return {"stufe": "Gut", "farbe": "green", "emoji_aehnlich": "Leicht"}
    if score >= 30:
        return {"stufe": "Mittel", "farbe": "orange", "emoji_aehnlich": "Mittel"}
    return {"stufe": "Problematisch", "farbe": "red", "emoji_aehnlich": "Schwer"}


def berechne_co2(co2_pro_teil_kg: float,
                 waschgaenge_pro_woche: float,
                 nutzungsjahre: float) -> dict:
    """Berechnet die geschaetzte CO2-Bilanz eines Kleidungsstuecks.

    Formel:
        CO2_Herstellung        = co2_pro_teil_kg                    (aus DB)
        CO2_Waschen            = waschgaenge_pro_Woche * 52 * Jahre
                                 * kWh_pro_Waschgang * kgCO2_pro_kWh
                                 / Teile_pro_Trommel
        CO2_Gesamt             = Herstellung + Waschen

    Alle Annahmen sind als Konstanten oben dokumentiert und werden
    auch in der App angezeigt (nachvollziehbar fuer den Modellvergleich).
    """
    waschgaenge_gesamt = waschgaenge_pro_woche * WOCHEN_PRO_JAHR * nutzungsjahre
    co2_waschen = (waschgaenge_gesamt * KWH_PRO_WASCHGANG
                   * STROMMIX_KG_CO2_PRO_KWH / TEILE_PRO_TROMMEL)
    co2_gesamt = co2_pro_teil_kg + co2_waschen

    return {
        "co2_herstellung_kg": round(co2_pro_teil_kg, 1),
        "co2_waschen_kg": round(co2_waschen, 1),
        "co2_gesamt_kg": round(co2_gesamt, 1),
        "waschgaenge_gesamt": int(waschgaenge_gesamt),
        "annahmen": {
            "strommix_kg_co2_pro_kwh": STROMMIX_KG_CO2_PRO_KWH,
            "kwh_pro_waschgang": KWH_PRO_WASCHGANG,
            "teile_pro_trommel": TEILE_PRO_TROMMEL,
        },
    }
