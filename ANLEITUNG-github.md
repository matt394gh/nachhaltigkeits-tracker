# Anleitung: Projekt auf deinen eigenen GitHub-Account hochladen

Dauer: ca. 5 Minuten. Du brauchst nur einen (kostenlosen) GitHub-Account.

> Wichtig: Das Repository muss für die Lehrkraft sichtbar sein.
> Entweder als **Public** anlegen oder die Lehrkraft unter
> Settings → Collaborators einladen.

## Vorbereitung

1. Das Projekt-ZIP entpacken, z. B. nach `D:\Projekte\nachhaltigkeits-tracker`.
2. Falls der Ordner `__pycache__` vorhanden ist: **löschen**
   (das ist nur ein Python-Zwischenspeicher, gehört nicht auf GitHub).

## Variante A: Upload im Browser (am einfachsten - empfohlen)

1. https://github.com öffnen → anmelden (oder Account erstellen).
2. Oben rechts auf das **+** → **New repository** klicken.
3. Einstellungen:
   - Repository name: `nachhaltigkeits-tracker`
   - Sichtbarkeit: **Public**
   - Haken bei "Add a README file" **weglassen**
     (README.md existiert im Projekt schon - sonst gibt es einen Konflikt)
4. **Create repository** klicken.
5. Auf der neuen Seite auf den Link **"uploading an existing file"** klicken.
6. Alle Dateien **und** die Ordner (`models/`, `testbilder/`) aus dem
   Projektordner markieren und zusammen in das Browser-Fenster ziehen.
   Die Ordnerstruktur wird automatisch übernommen.
7. Unten auf **Commit changes** klicken - fertig!

Falls eine Datei zu groß sein sollte (Fehlermeldung "file is larger
than 100 MB"): Das darf eigentlich nicht passieren - `keras_model.h5`
ist nur ca. 10-15 MB. Melde dich bei der Lehrkraft bzw. prüfe, ob du
aus Versehen andere große Dateien mit hochlädst.

## Variante B: GitHub Desktop (komfortabel, wenn du öfter mit Git arbeitest)

1. GitHub Desktop installieren: https://desktop.github.com/
2. File → **Add local repository** → Projektordner auswählen.
3. Falls die Meldung "not a repository" kommt: im selben Dialog
   **Create a repository** anklicken (Name prüfen, dann Erstellen).
4. Summary eintragen, z. B. "Erste Version" → **Commit to main**.
5. Oben rechts **Publish repository** → Namen prüfen → **Publish**.

## Variante C: Git im Terminal (für Fortgeschrittene)

```bash
cd nachhaltigkeits-tracker
git init
git add .
git commit -m "Nachhaltigkeits-Tracker: erste Version"
git branch -M main
git remote add origin https://github.com/DEIN-NAME/nachhaltigkeits-tracker.git
git push -u origin main
```

(Dabei fragt GitHub beim ersten Push nach der Anmeldung im Browser.)

## Später: trainiertes Teachable-Machine-Modell nachschieben

Wenn du dein Modell trainiert hast (siehe `models/ANLEITUNG-teachable-machine.md`),
kommen die zwei Dateien `keras_model.h5` und `labels.txt` in den Ordner
`models/teachable_model/`. Dann:

- Variante A: Dateien über "Add file → Upload files" erneut hochladen, oder
- Variante B/C: Dateien in den Ordner legen → wieder commit + push.

Die `.gitignore` ist so eingestellt, dass genau diese zwei Dateien
hochgeladen werden und die Lehrkraft sie im Repo sieht.

## Checkliste vor der Abgabe

- [ ] README.md ist im Repo sichtbar (Raster-Punkt: "GitHub-Repository mit README und requirements.txt")
- [ ] requirements.txt ist im Repo sichtbar
- [ ] Repository ist Public (oder Lehrkraft eingeladen)
- [ ] `models/teachable_model/` enthält das trainierte Modell (kein PLATZHALTER-Modus mehr)
- [ ] Repo-Link in die Abgabe/Pitch-Folie eintragen
