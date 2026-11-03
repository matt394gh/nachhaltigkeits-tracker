"""
model_b.py – Version B: vortrainiertes Modell (Microsoft Florence-2)
====================================================================

Modell:   microsoft/Florence-2-base
Quelle:   https://huggingface.co/microsoft/Florence-2-base
Lizenz:   MIT License (frei nutzbar - wichtig fuer die Doku!)

Warum dieses Modell (Begruendung fuer das Kriterienraster):
  - Multitask-Vision-Modell: kann OCR (Texterkennung) UND
    Bildbeschreibung - genau die zwei Faehigkeiten, die wir brauchen.
  - Kompakt (Base-Version, ca. 230 Mio. Parameter): laeuft auch auf
    einem normalen Schullaptop auf der CPU.
  - Laeuft KOMPLETT LOKAL: kein API-Key, keine Secrets, keine Kosten,
    keine Datenuebertragung an Dritte.
  - Offene Gewichte auf Hugging Face, MIT-Lizenz.

Wichtig: Beim ERSTEN Start laedt die App die Modellgewichte einmalig
aus dem Internet herunter (ca. 500 MB). Danach funktioniert alles
offline, weil die Dateien im lokalen Hugging-Face-Cache liegen.
"""

from PIL import Image

MODELL_ID = "microsoft/Florence-2-base"          # offizielle Modell-Adresse

# Cache, damit das Modell nur EINMAL pro App-Start geladen wird
# (None = noch nicht geladen, sonst: (modell, processor))
_KOMPONENTEN = None

# Aufgaben-Steuerwoerter der Florence-2-Sprachschicht:
TASK_OCR = "<OCR>"                                # reinen Text auslesen
TASK_BESCHREIBUNG = "<MORE_DETAILED_CAPTION>"     # ausfuehrliche Bildbeschreibung


def hole_modell():
    """Laedt Modell und Prozessor einmalig und gibt sie zurueck.

    'Lazy Loading': Die Installation/Das Laden passiert erst, wenn
    Version B wirklich benutzt wird - so startet die App auch ohne
    geladenes Modell sofort (z. B. wenn man nur Version A testet).
    """
    global _KOMPONENTEN
    if _KOMPONENTEN is None:
        # Schwere Bibliotheken erst hier importieren (lazy loading):
        # so startet die App auch, wenn torch/transformers noch
        # nicht installiert sind - solange man nur Version A testet.
        import torch
        from transformers import AutoModelForCausalLM, AutoProcessor

        prozessor = AutoProcessor.from_pretrained(MODELL_ID, trust_remote_code=True)
        modell = AutoModelForCausalLM.from_pretrained(
            MODELL_ID,
            trust_remote_code=True,   # laedt den vom Modell beigefuegten Code
            torch_dtype=torch.float32 # CPU arbeitet mit float32
        ).eval()                      # Auswertungsmodus (kein Training)
        _KOMPONENTEN = (modell, prozessor)
    return _KOMPONENTEN


def _aufgabe_ausfuehren(pil_bild: Image.Image, task: str,
                        max_neue_token: int = 1024) -> str:
    """Fuehrt eine Florence-2-Aufgabe aus und gibt den Text zurueck.

    Ablauf:
      1. Prozessor bereitet Prompt + Bild als Zahlen-Tensoren auf
      2. Modell erzeugt die Antwort (Sequenz von Token-IDs)
      3. post_process_generation schneidet Sonderzeichen raus und
         liefert das Ergebnis fuer die gewaehlte Aufgabe
    """
    modell, prozessor = hole_modell()

    eingaben = prozessor(text=task, images=pil_bild, return_tensors="pt")
    erzeugte_ids = modell.generate(
        input_ids=eingaben["input_ids"],
        pixel_values=eingaben["pixel_values"],
        max_new_tokens=max_neue_token,
        num_beams=3,          # Suchstrahl-Verfahren: bessere Ergebnisse als Greedy
        do_sample=False,      # deterministisch -> faire, wiederholbare Tests
    )
    rohtext = prozessor.batch_decode(erzeugte_ids, skip_special_tokens=False)[0]
    ergebnis = prozessor.post_process_generation(
        rohtext,
        task=task,
        image_size=(pil_bild.width, pil_bild.height),
    )
    return ergebnis.get(task, "")


def ocr(pil_bild: Image.Image) -> str:
    """Liest den sichtbaren Text aus dem Bild aus (Waschetikett, Print)."""
    return _aufgabe_ausfuehren(pil_bild, TASK_OCR, max_neue_token=1024).strip()


def bildbeschreibung(pil_bild: Image.Image) -> str:
    """Erzeugt eine ausfuehrliche Beschreibung des Bildinhalts."""
    return _aufgabe_ausfuehren(pil_bild, TASK_BESCHREIBUNG,
                               max_neue_token=256).strip()


def analysieren(pil_bild: Image.Image, aufgabe: str = "automatisch") -> dict:
    """Hauptfunktion von Modell B: Bild -> strukturiertes Ergebnis.

    aufgabe: 'automatisch'      -> erst OCR, sonst Bildbeschreibung
             'nur_ocr'          -> nur Texterkennung
             'nur_beschreibung' -> nur Bildbeschreibung

    Rueckgabe (gleiche Struktur wie Modell A, damit app.py beide
    Versionen gleich weiterverarbeiten kann):
        {
          "label":     Text, der gegen die Datenbank geprueft wird,
          "konfidenz": None (Florence-2 liefert keine Wahrscheinlichkeit),
          "details":   OCR-Text und/oder Bildbeschreibung
        }
    """
    details = {}

    if aufgabe in ("automatisch", "nur_ocr"):
        details["ocr_text"] = ocr(pil_bild)

    # 'automatisch': OCR hat fast nichts gefunden -> Beschreibung als Zusatzinfo
    if aufgabe == "automatisch" and len(details.get("ocr_text", "")) < 8:
        details["bildbeschreibung"] = bildbeschreibung(pil_bild)
    elif aufgabe == "nur_beschreibung":
        details["bildbeschreibung"] = bildbeschreibung(pil_bild)

    # Fuer den Datenbank-Abgleich nutzen wir den OCR-Text (dort steht
    # haeufig der Markenname). Ohne OCR-Text bleibt das Ergebnis unbekannt.
    label = details.get("ocr_text", "")

    return {
        "label": label,
        "konfidenz": None,
        "details": details,
    }
