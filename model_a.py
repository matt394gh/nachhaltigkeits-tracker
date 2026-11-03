"""
model_a.py – Version A: eigenes Modell (Google Teachable Machine)
================================================================

Geplanter Ablauf im echten Betrieb:
  1. In der Teachable Machine ein Bild-Klassifikationsmodell trainieren
     (z. B. Klassen: "H&M", "Zara", "Patagonia", "Armedangels", "Sonstige")
  2. Als "TensorFlow -> Keras" exportieren (Download als .zip)
  3. keras_model.h5 + labels.txt in den Ordner models/teachable_model/ legen
  4. Diese Datei laedt das Modell automatisch und klassifiziert Fotos.

Bis das echte Modell trainiert ist, laeuft ein DUMMY-Modus:
Er liefert eine DETERMINISTISCHE (nachvollziehbare) Vorhersage aus
einem Hash des Bildes. Vorteil: Die App ist komplett testbar, und
weil der Dummy immer dasselbe Bild -> dasselbe Ergebnis liefert,
bleiben Vergleichstests mit Modell B fair und wiederholbar.
"""

import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

# Ordner mit dem exportierten Teachable-Machine-Modell
MODELL_ORDNER = Path("models/teachable_model")
EINGABEGROESSE = 224          # Teachable Machine erwartet 224x224 Pixel

# Cache, damit das schwere Keras-Modell nur EINMAL geladen wird
# (None = noch nicht geladen, False = TensorFlow fehlt, sonst: Modell)
_KERAS_MODELL = None
_LABELS = None

# Klassen, die der Dummy verwenden kann (entsprechen den Kategorien der DB)
DUMMY_KATEGORIEN = ["fast_fashion", "mittel", "nachhaltig"]


def modell_status() -> str:
    """Prueft, ob ein echtes Teachable-Machine-Modell vorliegt.

    Rueckgabe: 'echt'  -> Dateien keras_model.h5 + labels.txt existieren
               'dummy' -> noch kein Modell, App nutzt den Platzhalter
    """
    datei_modell = MODELL_ORDNER / "keras_model.h5"
    datei_labels = MODELL_ORDNER / "labels.txt"
    if datei_modell.exists() and datei_labels.exists():
        return "echt"
    return "dummy"


def _lade_labels(pfad: Path) -> list:
    """Liest labels.txt ein.

    Format der Teachable Machine (eine Klasse pro Zeile):
        0 H&M
        1 Patagonia
    Wir brauchen nur den Text nach der Nummer.
    """
    labels = []
    for zeile in pfad.read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if not zeile:
            continue
        teile = zeile.split(" ", 1)      # erste Leerstelle trennt Nummer und Name
        name = teile[1] if len(teile) > 1 else teile[0]
        labels.append(name)
    return labels


def _lade_keras_modell():
    """Laedt das Keras-Modell einmalig (lazy loading).

    ImportError -> TensorFlow ist nicht installiert. Dann geben wir eine
    verstaendliche Fehlermeldung weiter (requirements.txt beachten).
    """
    global _KERAS_MODELL, _LABELS
    if _KERAS_MODELL is False:
        raise RuntimeError(
            "TensorFlow ist nicht installiert. Bitte 'pip install tensorflow' "
            "ausfuehren (siehe requirements.txt)."
        )
    if _KERAS_MODELL is None:
        try:
            import tensorflow as tf          # erst hier importieren -> schneller Start
        except ImportError:
            _KERAS_MODELL = False
            raise RuntimeError(
                "TensorFlow ist nicht installiert. Bitte 'pip install tensorflow' "
                "ausfuehren (siehe requirements.txt)."
            )
        _KERAS_MODELL = tf.keras.models.load_model(MODELL_ORDNER / "keras_model.h5")
        _LABELS = _lade_labels(MODELL_ORDNER / "labels.txt")
    return _KERAS_MODELL


def _bild_vorbereiten(pil_bild: Image.Image) -> "np.ndarray":
    """Wandelt ein PIL-Bild in das Eingabeformat von Teachable Machine um.

    Teachable Machine erwartet: 224x224 Pixel, 3 Farbkanaele,
    Normalisierung auf den Bereich [-1, 1].
    """
    bild_rgb = pil_bild.convert("RGB").resize((EINGABEGROESSE, EINGABEGROESSE))
    array = np.asarray(bild_rgb, dtype=np.float32)
    array = (array / 127.5) - 1.0            # 0..255  ->  -1..1
    return array.reshape(1, EINGABEGROESSE, EINGABEGROESSE, 3)


def klassifizieren(pil_bild: Image.Image) -> dict:
    """Hauptfunktion von Modell A: Bild -> Vorhersage.

    Rueckgabe (immer gleich aufgebaut, damit app.py beide Versionen
    gleich behandeln kann):
        {
          "label":     erkannte Klasse (Klassenname oder Kategorie),
          "konfidenz": Wahrscheinlichkeit 0..1,
          "details":   Textzusammenfassung fuer die Anzeige
        }
    """
    if modell_status() == "echt":
        return _echtes_modell(pil_bild)
    return _dummy_modell(pil_bild)


def _echtes_modell(pil_bild: Image.Image) -> dict:
    """Klassifikation mit dem trainierten Teachable-Machine-Modell."""
    modell = _lade_keras_modell()
    eingabe = _bild_vorbereiten(pil_bild)
    vorhersagen = modell.predict(eingabe, verbose=0)[0]   # Array mit Wahrscheinlichkeiten

    index = int(np.argmax(vorhersagen))                    # Position des Hoechstwerts
    label = _LABELS[index] if index < len(_LABELS) else f"Klasse {index}"
    konfidenz = float(vorhersagen[index])

    # Top-3 fuer die Anzeige in der App vorbereiten
    sortierte_indizes = np.argsort(vorhersagen)[::-1][:3]
    top3 = [f"{_LABELS[i] if i < len(_LABELS) else i}: {vorhersagen[i]*100:.1f} %"
            for i in sortierte_indizes]

    return {
        "label": label,
        "konfidenz": round(konfidenz, 4),
        "details": "Top-3-Klassen: " + " | ".join(top3),
    }


def _dummy_modell(pil_bild: Image.Image) -> dict:
    """Platzhalter-Klassifikator (bis das echte Modell trainiert ist).

    Funktionsweise: Aus den Bild-Bytes wird ein MD5-Hash berechnet.
    Der Hash entscheidet (deterministisch = immer gleich), welche der
    drei Kategorien und welche 'Konfidenz' zurueckgegeben wird.
    """
    bild_bytes = pil_bild.tobytes()
    hash_wert = int(hashlib.md5(bild_bytes).hexdigest(), 16)

    kategorie = DUMMY_KATEGORIEN[hash_wert % len(DUMMY_KATEGORIEN)]
    konfidenz = 0.55 + (hash_wert % 40) / 100.0     # 0.55 bis 0.94

    return {
        "label": kategorie,
        "konfidenz": round(konfidenz, 4),
        "details": ("DUMMY-MODELL: Platzhalter-Klassifikator aus einem Bild-Hash. "
                    "Sobald models/teachable_model/ ein echtes Teachable-Machine-Modell "
                    "enthaelt (siehe models/ANLEITUNG-teachable-machine.md), wird es "
                    "automatisch benutzt."),
    }
