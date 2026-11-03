# Nachhaltigkeits-Tracker für Kleidung

Klausurersatzleistung Informatik (profilaffin).
Eine Streamlit-Web-App, die ein Foto von einem Kleidungsstück oder
Waschetikett analysiert und den ökologischen Impact einschätzt
(Öko-Score, CO2-Bilanz). Dabei werden zwei KI-Ansätze verglichen:

| | Version A | Version B |
|---|---|---|
| Modell | eigenes Modell (Google Teachable Machine) | vortrainiertes Microsoft Florence-2 |
| Aufgabe | optische Klassifikation (Marke/Kategorie) | OCR auf Waschetiketten + Bildbeschreibung |
| Ort | lokal (TensorFlow/Keras) | lokal (Hugging Face transformers, CPU) |
| Lizenz | eigen trainiert | MIT-Lizenz (https://huggingface.co/microsoft/Florence-2-base) |

## Schnellstart

```bash
# 1. Virtuelle Umgebung anlegen (einmalig)
python -m venv venv

# 2. Umgebung aktivieren
#    Windows:
venv\Scripts\activate
#    Linux/Mac:
source venv/bin/activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. App starten
streamlit run app.py
```

Die App öffnet sich automatisch im Browser (http://localhost:8501).
**Kein API-Key, keine Secrets, keine Konten nötig** - alle Daten
(Markendatenbank, Modelle) liegen lokal im Projekt.

Hinweis zu Version B: Beim allerersten Start lädt die App die
Florence-2-Gewichte einmalig aus dem Internet (ca. 500 MB) und speichert
sie im lokalen Hugging-Face-Cache. Danach läuft sie offline.

## Projektstruktur

```
nachhaltigkeits-tracker/
├── app.py                       Streamlit-Haupt-App (UI, Ablaufsteuerung)
├── model_a.py                   Version A: Teachable Machine + Dummy-Modus
├── model_b.py                   Version B: Florence-2 (OCR + Beschreibung)
├── scoring.py                   DB-Abgleich, Öko-Score, CO2-Rechner
├── sustainability_db.json       lokale Markendatenbank (keine Secrets!)
├── requirements.txt             Abhängigkeiten
├── models/
│   ├── ANLEITUNG-teachable-machine.md   Schritt-für-Schritt zum eigenen Modell
│   └── teachable_model/         hier kommen keras_model.h5 + labels.txt
├── testbilder/HINWEIS.md        Anleitung für den fairen Modellvergleich
└── ANLEITUNG-github.md          So kommt das Projekt auf deinen GitHub-Account
```

## Version A: eigenes Modell einbinden

Solange kein Modell trainiert ist, läuft automatisch ein
**Dummy-Klassifikator** (Platzhalter), damit die App testbar bleibt.
Das echte Modell trainierst du mit der Google Teachable Machine und
legst `keras_model.h5` + `labels.txt` in `models/teachable_model/` -
genaue Schritte: `models/ANLEITUNG-teachable-machine.md`.
Dafür zusätzlich installieren: `pip install tensorflow`.

## Version B: Warum Florence-2? (Begründung für die Doku)

- **Multitask-Fähigkeiten**: OCR (Text auf Etiketten) und ausführliche
  Bildbeschreibung in einem Modell - genau die zwei benötigten Aufgaben.
- **Kompakt**: Base-Version (ca. 230 Mio. Parameter) läuft auf normaler
  CPU-Hardware, z. B. Schullaptop.
- **Lokal und offen**: offene Gewichte auf Hugging Face, MIT-Lizenz,
  keine Datenübertragung an Cloud-Dienste, keine laufenden Kosten.
- Quelle und Lizenz: https://huggingface.co/microsoft/Florence-2-base

## Faire Testbedingungen für den Vergleich A vs. B

1. 15-20 Testfotos sammeln (siehe `testbilder/HINWEIS.md`).
2. **Dasselbe** Foto nacheinander mit Version A und Version B analysieren.
3. Ergebnisse werden in der Ergebnis-Historie der App gesammelt und in
   der Dokumentation als Tabelle festgehalten.
4. Vergleichskriterien: Trefferquote, Geschwindigkeit, Konfidenz, Aufwand.

## Auf GitHub veröffentlichen

Das Projekt ist upload-fertig: README, requirements.txt und .gitignore
liegen bei. Wie du es in ca. 5 Minuten auf deinen eigenen GitHub-Account
hochlädst (Browser-Upload reicht völlig), steht in `ANLEITUNG-github.md`.

## Grenzen (bewusst benannt)

- Alle Scores und CO2-Werte in `sustainability_db.json` sind didaktische
  Schätzwerte, keine offizielle Zertifizierung.
- Die Qualität von Version A hängt von den eigenen Trainingsdaten ab.
- Version B erkennt nur wirklich sichtbaren Text (keine Rekonstruktion).
- Die App bewertet einzelne Kleidungsstücke, kein Konsumverhalten.

## Quellen

- Teachable Machine: https://teachablemachine.withgoogle.com/
- Florence-2: https://huggingface.co/microsoft/Florence-2-base
- Streamlit-Doku: https://docs.streamlit.io/
- Hugging Face Transformers: https://huggingface.co/docs/transformers
- Umweltbundesamt, Textilien:
  https://www.umweltbundesamt.de/themen/abfall-ressourcen/produktverantwortung-in-der-abfallwirtschaft/textilien
