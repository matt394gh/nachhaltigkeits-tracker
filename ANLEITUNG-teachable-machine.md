# Anleitung: Eigenes Modell mit der Google Teachable Machine trainieren
(Versions A des Kriterienrasters - 20 % der Gesamtpunktzahl!)

## Schritt 0: Was wird trainiert?

Wir klassifizieren **Marken** (oder Marken-Kategorien) über Fotos von
Kleidungsstücken. Das Modell lernt optische Merkmale wie Logo-Prints,
Etiketten-Stil und Farbtypik der Marke.

Empfohlene Klassen (müssen Namen aus `sustainability_db.json`
entsprechen, damit der Datenbank-Abgleich automatisch klappt):

- `H&M`
- `Zara`
- `Patagonia`
- `Armedangels`
- `Sonstige` (alles andere - wichtig, damit das Modell nicht alles erzwingt)

## Schritt 1: Trainingsdaten sammeln

- **50-100 Fotos pro Klasse** (Qualität statt Quantität, aber genug Vielfalt)
- Eigene Kleidungsstücke + Familie/Freunde fotografieren (Datenschutz: keine Personen!
  Nur das Kleidungsstück)
- Abwechslung beachten (das macht das Modell robust):
  - verschiedene Hintergründe (Bett, Tisch, Boden)
  - verschiedene Lichtverhältnisse
  - Nahaufnahme Brandprint und normale Aufnahme des ganzen Stücks
  - leicht gedrehte Perspektiven
- Unterteilung in Teachable Machine: ca. 80 % Training / 10 % Validation / 10 % Test
  (die TM macht das automatisch; du kannst Kategorien auch manuell anpassen)

## Schritt 2: Trainieren

1. Öffne https://teachablemachine.withgoogle.com/ → "Get Started" → "Image Project" → "Standard image model"
2. Klassen umbenennen und Fotos pro Klasse hochladen (Drag & Drop)
3. "Train Model" klicken (Standardeinstellungen: 50 Epochs, Batch 16, Lernrate 0.001 reichen)
4. Nach dem Training mit dem Live-Preview testen: eigene Fotos reinziehen
   und prüfen, ob die richtige Klasse gewinnt

## Schritt 3: Exportieren und einbinden

1. "Export Model" → Reiter **TensorFlow** → **Download my model** (Keras-Format)
2. Die heruntergeladene ZIP entpacken. Wichtige Dateien:
   - `keras_model.h5` (das trainierte neuronale Netz)
   - `labels.txt` (die Klassennamen)
3. Beide Dateien in diesen Ordner legen: `models/teachable_model/`
4. App neu starten (`streamlit run app.py`) - die Sidebar zeigt jetzt
   "Echtes Teachable-Machine-Modell gefunden".

## Schritt 4: TensorFlow installieren (einmalig)

```bash
pip install tensorflow
```

## Troubleshooting

| Problem | Lösung |
|---|---|
| `ValueError: This model has not been built` | Neu exportieren, wichtig ist der Export-Typ "TensorFlow/Keras", nicht TensorFlow.js oder TFLite |
| Alle Fotos landen in einer Klasse | Mehr trainieren, mehr Foto-Vielfalt, Klassen ausbalancieren (ähnlich viele Fotos pro Klasse) |
| Konfidenz immer unter 60 % | Fotos schärfer und näher aufnehmen; Beleuchtung verbessern |
| `labels.txt` passt nicht zur DB | Klassennamen exakt wie die Markennamen in `sustainability_db.json` nennen (z. B. `H&M` mit &) |

## Für die Dokumentation dokumentieren (wird bewertet!)

- Wie viele Fotos pro Klasse? Wie sieht die Verteilung aus?
- Welche Probleme gab es (Verwechslungen, schlechte Beleuchtung) und wie gelöst?
- Testgenauigkeit: Wie oft war die Vorhersage bei 10 Testfotos richtig?
