import os
import json

print("🚀 Starte automatischen Projekt-Aufbau für EcoLens...")

# 1. Ordnerstruktur erstellen
dirs = [
    "app_teachable",
    "app_florence",
    "models/teachable_model"
]
for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"📁 Ordner erstellt: {d}")

# 2. requirements.txt schreiben
reqs = """streamlit>=1.28.0
pillow>=9.0.0
numpy>=1.20.0
transformers>=4.38.0
torch>=2.0.0
einops>=0.6.0
# tensorflow>=2.10.0  # Auskommentieren, wenn Teachable Machine (.h5) lokal genutzt wird
"""
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(reqs)

# 3. Nachhaltigkeits-Datenbank (sustainability_db.json)
db_content = {
  "marken": [
    {"name": "Shein", "aliase": ["SHEIN", "shein"], "kategorie": "fast_fashion", "score": 8, "co2_pro_teil_kg": 14.5, "bemerkung": "Sehr hohe Umweltauswirkungen durch Ultrafast-Fashion."},
    {"name": "Temu", "aliase": ["TEMU", "temu"], "kategorie": "fast_fashion", "score": 8, "co2_pro_teil_kg": 15.0, "bemerkung": "Sehr hohes Frachtaufkommen (Luftfracht)."},
    {"name": "Primark", "aliase": ["PRIMARK", "primark"], "kategorie": "fast_fashion", "score": 15, "co2_pro_teil_kg": 12.0, "bemerkung": "Sehr niedrige Preise verleiten zum Wegwerfkonsum."},
    {"name": "Zara", "aliase": ["ZARA", "zara", "ZARA BASIC"], "kategorie": "fast_fashion", "score": 25, "co2_pro_teil_kg": 11.0, "bemerkung": "Pionier des Fast-Fashion-Modells."},
    {"name": "Bershka", "aliase": ["BERSHKA", "bershka"], "kategorie": "fast_fashion", "score": 25, "co2_pro_teil_kg": 11.0, "bemerkung": "Gehört zur Inditex-Gruppe."},
    {"name": "H&M", "aliase": ["H&M", "HM", "HENNES & MAURITZ"], "kategorie": "fast_fashion", "score": 30, "co2_pro_teil_kg": 10.0, "bemerkung": "Große Produktionsmengen trotz Recycling-Initiativen."},
    {"name": "Uniqlo", "aliase": ["UNIQLO", "uniqlo"], "kategorie": "mittel", "score": 40, "co2_pro_teil_kg": 9.0, "bemerkung": "Fokus auf langlebigere Basic-Kleidung."},
    {"name": "Nike", "aliase": ["NIKE", "nike"], "kategorie": "mittel", "score": 40, "co2_pro_teil_kg": 9.5, "bemerkung": "Hohe Emissionen durch Sportbekleidungsproduktion."},
    {"name": "s.Oliver", "aliase": ["S.OLIVER", "s.oliver"], "kategorie": "mittel", "score": 40, "co2_pro_teil_kg": 8.5, "bemerkung": "Klassischer Anbieter im Mittelfeld."},
    {"name": "C&A", "aliase": ["C&A", "c&a"], "kategorie": "mittel", "score": 45, "co2_pro_teil_kg": 8.0, "bemerkung": "Großer Anbieter von Bio-Baumwolle."},
    {"name": "Adidas", "aliase": ["ADIDAS", "adidas"], "kategorie": "mittel", "score": 45, "co2_pro_teil_kg": 8.5, "bemerkung": "Einsatz von recycelten Materialien."},
    {"name": "Puma", "aliase": ["PUMA", "puma"], "kategorie": "mittel", "score": 45, "co2_pro_teil_kg": 8.5, "bemerkung": "Setzt auf Klimaziele im Mittelfeld."},
    {"name": "Patagonia", "aliase": ["PATAGONIA", "patagonia"], "kategorie": "nachhaltig", "score": 85, "co2_pro_teil_kg": 5.5, "bemerkung": "Branchenvorreiter für Umweltschutz."},
    {"name": "Vaude", "aliase": ["VAUDE", "vaude"], "kategorie": "nachhaltig", "score": 85, "co2_pro_teil_kg": 5.5, "bemerkung": "Strenge Öko-Standards (Green Shape)."},
    {"name": "Armedangels", "aliase": ["ARMEDANGELS", "armedangels"], "kategorie": "nachhaltig", "score": 85, "co2_pro_teil_kg": 5.0, "bemerkung": "Faire Mode aus Bio-Baumwolle, GOTS zertifiziert."},
    {"name": "Nudie Jeans", "aliase": ["NUDIE JEANS", "nudie"], "kategorie": "nachhaltig", "score": 85, "co2_pro_teil_kg": 6.0, "bemerkung": "100% Bio-Baumwolle & Reparaturservice."},
    {"name": "hessnatur", "aliase": ["HESSNATUR", "hessnatur"], "kategorie": "nachhaltig", "score": 90, "co2_pro_teil_kg": 4.5, "bemerkung": "Pionier für Naturtextilien."},
    {"name": "Secondhand/Vintage", "aliase": ["SECONDHAND", "VINTAGE"], "kategorie": "nachhaltig", "score": 95, "co2_pro_teil_kg": 0.5, "bemerkung": "Die nachhaltigste Wahl überhaupt."}
  ]
}

for path in ["app_teachable/sustainability_db.json", "app_florence/sustainability_db.json"]:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(db_content, f, ensure_ascii=False, indent=2)

# 4. scoring.py
scoring_code = '''import json
import difflib

WASCHGANG_KWH = 1.0
CO2_PRO_KWH = 0.38
TEILE_PRO_TROMMEL = 4.0

def lade_datenbank(pfad="sustainability_db.json"):
    try:
        with open(pfad, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"marken": []}

def finde_marke(db, suchtext):
    if not suchtext:
        return None
    text_clean = suchtext.strip().upper()
    marken = db.get("marken", [])
    for marke in marken:
        if marke["name"].upper() == text_clean:
            return marke
        for alias in marke.get("aliase", []):
            if alias.upper() == text_clean:
                return marke
    for marke in marken:
        names_to_check = [marke["name"].upper()] + [a.upper() for a in marke.get("aliase", [])]
        for name in names_to_check:
            if len(name) >= 3 and name in text_clean:
                return marke
    alle_namen = []
    name_zu_marke = {}
    for marke in marken:
        alle_namen.append(marke["name"].upper())
        name_zu_marke[marke["name"].upper()] = marke
        for alias in marke.get("aliase", []):
            alle_namen.append(alias.upper())
            name_zu_marke[alias.upper()] = marke
    matches = difflib.get_close_matches(text_clean, alle_namen, n=1, cutoff=0.8)
    if matches:
        return name_zu_marke[matches[0]]
    return None

def eintrag_fuer_kategorie(kategorie):
    kat = kategorie.lower()
    if "fast" in kat:
        return {"name": "Unbekannte Marke (Fast Fashion)", "kategorie": "fast_fashion", "score": 20, "co2_pro_teil_kg": 12.0, "bemerkung": "Hohe Umweltbelastung."}
    elif "nachhaltig" in kat or "fair" in kat:
        return {"name": "Unbekannte Marke (Nachhaltig)", "kategorie": "nachhaltig", "score": 85, "co2_pro_teil_kg": 5.5, "bemerkung": "Fokus auf Umweltfreundlichkeit."}
    else:
        return {"name": "Unbekannte Marke (Standard)", "kategorie": "mittel", "score": 45, "co2_pro_teil_kg": 9.0, "bemerkung": "Durchschnittliches Mittelfeld."}

def eintrag_fuer_ergebnis(db, sucht_label, kategorie=None):
    marke = finde_marke(db, sucht_label)
    if marke:
        return marke
    if kategorie:
        return eintrag_fuer_kategorie(kategorie)
    return eintrag_fuer_kategorie(sucht_label)

def material_erkennen(text):
    if not text:
        return []
    stoffe = [
        ("BIO-BAUMWOLLE", "Bio-Baumwolle (Nachhaltig)"),
        ("ORGANIC COTTON", "Bio-Baumwolle (Nachhaltig)"),
        ("POLYESTER", "Polyester (Synthetisch/Mikroplastik)"),
        ("BAUMWOLLE", "Baumwolle (Konventionell)"),
        ("COTTON", "Baumwolle (Konventionell)"),
        ("ELASTHAN", "Elasthan (Synthetisch)"),
        ("WOLLE", "Wolle (Naturfaser)")
    ]
    gefundene = []
    text_up = text.upper()
    for key, label in stoffe:
        if key in text_up and label not in gefundene:
            gefundene.append(label)
    return gefundene

def berechne_co2(herstellung, waschgaenge_woche, jahre):
    gesamt_wasch = waschgaenge_woche * 52 * jahre
    waschen = gesamt_wasch * (WASCHGANG_KWH * CO2_PRO_KWH / TEILE_PRO_TROMMEL)
    gesamt = herstellung + waschen
    return round(herstellung, 2), round(waschen, 2), round(gesamt, 2)
'''

for path in ["app_teachable/scoring.py", "app_florence/scoring.py"]:
    with open(path, "w", encoding="utf-8") as f:
        f.write(scoring_code)

# 5. app_teachable/model_a.py
model_a_code = '''import os
import numpy as np
import hashlib

MODEL_PATH = "models/teachable_model/keras_model.h5"
LABELS_PATH = "models/teachable_model/labels.txt"

def lade_labels():
    if os.path.exists(LABELS_PATH):
        with open(LABELS_PATH, "r", encoding="utf-8") as f:
            return [line.strip().split(" ", 1)[-1] if " " in line else line.strip() for line in f.readlines()]
    return ["H&M", "Zara", "Patagonia", "Armedangels", "Sonstige"]

def modell_vorhanden():
    return os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH)

def klassifiziere_bild(pil_bild):
    labels = lade_labels()
    if not modell_vorhanden():
        img_bytes = pil_bild.tobytes()
        hash_val = int(hashlib.md5(img_bytes).hexdigest(), 16)
        idx = hash_val % len(labels)
        return {"label": labels[idx], "konfidenz": 0.85, "modus": "Dummy-Modus (Keine .h5 Datei)"}
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)
        img = pil_bild.convert("RGB").resize((224, 224))
        arr = (np.array(img, dtype=np.float32) / 127.5) - 1.0
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = arr
        pred = model.predict(data)
        idx = np.argmax(pred[0])
        return {"label": labels[idx], "konfidenz": float(pred[0][idx]), "modus": "Teachable Machine (.h5)"}
    except Exception as e:
        return {"label": labels[0], "konfidenz": 0.5, "modus": f"Fehler: {str(e)}"}
'''
with open("app_teachable/model_a.py", "w", encoding="utf-8") as f:
    f.write(model_a_code)

# 6. app_teachable/app.py
app_t_code = '''import streamlit as st
from PIL import Image
import scoring
import model_a

st.set_page_config(page_title="EcoLens - Teachable Machine", page_icon="☁️", layout="centered")

st.markdown(\"\"\"
<style>
.stApp { background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%); }
h1, h2, h3 { color: #007782 !important; }
div.stAlert { background-color: #ffffff; border: 1px solid #bae6fd; border-radius: 12px; }
.stButton>button { background-color: #007782; color: white; border-radius: 8px; border: none; font-weight: bold; }
.stButton>button:hover { background-color: #005f66; color: white; }
</style>
\"\"\", unsafe_allow_html=True)

st.title("☁️ EcoLens: Teachable Machine (Version A)")
st.markdown("### Nachhaltigkeits-Tracker (Optische Klassifikation)")

with st.sidebar:
    st.info("ℹ️ **Version A:** Nutzt ein lokales Teachable-Machine-Modell.")
    if model_a.modell_vorhanden():
        st.success("✅ .h5 Modell aktiv!")
    else:
        st.warning("⚠️ Im Dummy-Modus. Lege dein `.h5` nach `models/teachable_model/`.")

db = scoring.lade_datenbank("sustainability_db.json")
up = st.file_uploader("Foto hochladen (.jpg, .png)", type=["jpg", "jpeg", "png"])

if up:
    img = Image.open(up)
    st.image(img, caption="Hochgeladenes Bild", use_container_width=True)
    res = model_a.klassifiziere_bild(img)
    eintrag = scoring.eintrag_fuer_ergebnis(db, res["label"])
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("Erkannte Marke", eintrag["name"])
    c2.metric("Konfidenz", f"{int(res['konfidenz']*100)}%")
    
    score = eintrag["score"]
    st.markdown(f"### Öko-Score: {score} / 100")
    st.progress(score / 100.0)
    st.info(eintrag["bemerkung"])
    
    st.markdown("---")
    w = st.slider("Waschgänge / Woche", 0.0, 3.0, 0.5, 0.1)
    y = st.slider("Nutzungsjahre", 0.5, 10.0, 3.0, 0.5)
    h_co2, w_co2, g_co2 = scoring.berechne_co2(eintrag["co2_pro_teil_kg"], w, y)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Herstellung", f"{h_co2} kg")
    col2.metric("Waschen", f"{w_co2} kg")
    col3.metric("Gesamt", f"{g_co2} kg")
'''
with open("app_teachable/app.py", "w", encoding="utf-8") as f:
    f.write(app_t_code)

# 7. app_florence/model_b.py
model_b_code = '''import torch
from transformers import AutoProcessor, AutoModelForCausalLM

MODEL_ID = "microsoft/Florence-2-base"

def load_florence():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=torch.float32, trust_remote_code=True).to(device)
    model.eval()
    return processor, model, device

def analysiere_etikett(pil_image):
    try:
        import streamlit as st
        @st.cache_resource
        def cached_model():
            return load_florence()
        processor, model, device = cached_model()
        
        image = pil_image.convert("RGB")
        inputs = processor(text="<OCR>", images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            gen = model.generate(input_ids=inputs["input_ids"], pixel_values=inputs["pixel_values"], max_new_tokens=512, num_beams=3)
        text = processor.batch_decode(gen, skip_special_tokens=True)[0]
        return {"ocr": text, "erfolg": True}
    except Exception as e:
        return {"ocr": f"Fehler: {str(e)}", "erfolg": False}
'''
with open("app_florence/model_b.py", "w", encoding="utf-8") as f:
    f.write(model_b_code)

# 8. app_florence/app.py
app_f_code = '''import streamlit as st
from PIL import Image
import scoring
import model_b

st.set_page_config(page_title="EcoLens - Florence-2 OCR", page_icon="☁️", layout="centered")

st.markdown(\"\"\"
<style>
.stApp { background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%); }
h1, h2, h3 { color: #007782 !important; }
div.stAlert { background-color: #ffffff; border: 1px solid #bae6fd; border-radius: 12px; }
.stButton>button { background-color: #007782; color: white; border-radius: 8px; border: none; font-weight: bold; }
.stButton>button:hover { background-color: #005f66; color: white; }
</style>
\"\"\", unsafe_allow_html=True)

st.title("☁️ EcoLens: Florence-2 (Version B)")
st.markdown("### Nachhaltigkeits-Tracker (OCR & Textanalyse)")

with st.sidebar:
    st.info("ℹ️ **Version B:** Nutzt Microsoft Florence-2 für lokale Texterkennung auf Waschetiketten.")
    st.success("✅ Modell: `microsoft/Florence-2-base`")

db = scoring.lade_datenbank("sustainability_db.json")
up = st.file_uploader("Etikett / Foto hochladen (.jpg, .png)", type=["jpg", "jpeg", "png"])

if up:
    img = Image.open(up)
    st.image(img, caption="Hochgeladenes Etikett", use_container_width=True)
    
    with st.spinner("Analysiere Etikett per OCR (Erststart lädt ~500 MB)..."):
        res = model_b.analysiere_etikett(img)
        ocr_text = res["ocr"]
        
    eintrag = scoring.eintrag_fuer_ergebnis(db, ocr_text)
    stoffe = scoring.material_erkennen(ocr_text)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("Erkannte Marke", eintrag["name"])
    c2.metric("Kategorie", eintrag["kategorie"].upper())
    
    with st.expander("🔍 OCR-Rohdaten"):
        st.write(ocr_text)
        if stoffe:
            st.write("Erkannte Stoffe:", ", ".join(stoffe))
            
    score = eintrag["score"]
    st.markdown(f"### Öko-Score: {score} / 100")
    st.progress(score / 100.0)
    st.info(eintrag["bemerkung"])
    
    st.markdown("---")
    w = st.slider("Waschgänge / Woche", 0.0, 3.0, 0.5, 0.1)
    y = st.slider("Nutzungsjahre", 0.5, 10.0, 3.0, 0.5)
    h_co2, w_co2, g_co2 = scoring.berechne_co2(eintrag["co2_pro_teil_kg"], w, y)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Herstellung", f"{h_co2} kg")
    col2.metric("Waschen", f"{w_co2} kg")
    col3.metric("Gesamt", f"{g_co2} kg")
'''
with open("app_florence/app.py", "w", encoding="utf-8") as f:
    f.write(app_f_code)

print("✅ Alle Dateien und Ordner wurden erfolgreich und fehlerfrei erstellt!")
