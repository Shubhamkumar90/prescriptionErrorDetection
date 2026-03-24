import re
from rapidfuzz import process, fuzz
import pandas as pd
from errorDetectionAgent import *


# OCR_API = "https://shubham879-trocrapi.hf.space/process-image"
# imgpath = "images/prescription_2.png"
DOSAGE_FORMS = {
    "mg","ml","g","tablet","tab","cap","capsule",
    "inj","injection","syrup","daily","hours","hour"
}
HEADER_WORDS = {
    "dr", "doctor", "physician", "signature", "signed",
    "rx", "prescription", "presented", "issued",
    "clinic", "hospital", "medical", "health", "center", "centre",
    "address", "street", "st", "road", "rd", "lane", "ln",
    "blvd", "boulevard", "ave", "avenue",
    "patient", "name", "age", "sex", "male", "female",
    "date", "time", "ref", "reference", "id", "no",
    "phone", "mobile", "tel", "fax", "email",
    "stamp", "seal"
}

FREQ_MAP = {
    "bd": "twice daily",
    "tds": "three times daily",
    "with food": "with food",
    "before food": "before food",
    "after food": "after food",
    "with meal": "with food",
    "before meal": "before food",
    "after meal": "after food",
    # "od": "once daily",
    "1-0-1": "twice daily",
    "1-1-1": "three times daily",
    "0-1-0": "once daily",
    "every 12 hours": "twice daily",
    "every 8 hours": "three times daily",
    "twice daily": "twice daily",
    "once daily": "once daily",
    "three times daily": "three times daily"
}


def clean_text(text):

    text = text.replace("\r", "\n")

    text = re.sub(r"(\d)(mg|ml|g)", r"\1 \2", text, flags=re.I)
    text = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", text)
    text = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", text)

    # collapse spaces but keep newlines
    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n+", "\n", text)

    return text.strip()

def is_prescription_line(line):
    line_l = line.lower()
    if re.search(r"[0-9ol]+\s*(mg|ml|g)", line_l):
        return True

    # accept if dosage form present
    # for form in DOSAGE_FORMS:
    #     if form in line_l:
    #         return True

    # possible drug-only line (short)
    # if len(line_l.split()) <= 2 and line_l.isalpha():
    #     return True

    return False

# def is_prescription_line(line):
#     return bool(re.search(r"\d+\s*(mg|ml|g)", line.lower()))

def load_drug_vocab(path="DrugData/drugs1.csv"):
    df = pd.read_csv(path)
    df["drug_name"] = df["drug_name"].str.lower().str.strip()

    df = df[df["drug_name"].str.len() >= 4]
    df = df[~df["drug_name"].str.contains(r"\d", regex=True)]
    df = df[df["drug_name"].str.match(r"^[a-z\- ]+$")]

    vocab = df["drug_name"].tolist()
    return vocab

def extract_drug_token(line):
    tokens = line.lower().split()
    for token in tokens:

        if token in DOSAGE_FORMS:
            continue

        if any(char.isdigit() for char in token):
            continue

        return token

    return None

def correct_drug(word):
    drug_vocab=load_drug_vocab()
    candidates = process.extract(
        word,
        drug_vocab,
        scorer=fuzz.WRatio,
        limit=20
    )

    best_match = word
    best_score = 0

    for match, score, _ in candidates:
        # reject weak matches
        if score < 65:
            continue
        # reject large length differences
        if abs(len(match) - len(word)) > 3:
            continue
        # # reject very short words
        if len(match) < 5:
            continue

        if score > best_score:
            best_match = match
            best_score = score

    return best_match, best_score




def extract_frequency(line):

    line_l = line.lower()

    for key, value in FREQ_MAP.items():
        if key in line_l:
            return value

    return None

def fuzzy_frequency(line):

    candidates = process.extract(
        line.lower(),
        list(FREQ_MAP.keys()),
        scorer=fuzz.WRatio,
        limit=5
    )

    for match, score, _ in candidates:
        if score >= 70:
            return FREQ_MAP[match]

    return None

def extract_dose(line):

    line = line.lower()

    # normalize OCR mistakes
    line = line.replace("o", "0")
    line = line.replace("l", "1")

    # common unit OCR mistakes
    line = re.sub(r'\bmq\b', 'mg', line)
    line = re.sub(r'\bm9\b', 'mg', line)

    # extract dose
    match = re.search(r'(\d+)\s*(mg|ml|g)', line)

    if match:
        return match.group(1), match.group(2)

    return None, None

INSTRUCTION_MAP = [
    "before meals",
    "after meals",
    "with food",
    "empty stomach",
    "after food"
]


def process_drug_detail(text,keywords):
    if not text:
        return None
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[•*▪◦]', ' ', text)
    text = text.replace('\r', ' ')
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'[.;]', text)
    useful = []
    for s in sentences:
        s = s.strip()
        sLower=s.lower()
        if any(k in sLower for k in keywords):
            useful.append(s)

        if len(useful) == 2:
            break

    return ". ".join(useful)


def get_drugbank_id(drug):
    df=pd.read_csv('DrugData/drugs1.csv')
    row = df[df["drug_name"] == drug.lower()]
    if len(row) == 0:
        return None

    return row.iloc[0]["drugbank_id"]

def get_present_interactions(drug, detected_drugs):
    interaction_db = pd.read_csv('DrugData/interactions.csv')
    drug_id = get_drugbank_id(drug)

    if not drug_id:
        return []

    rows = interaction_db[interaction_db["drugbank_id"] == drug_id]

    interactions = rows["interacting_drug"].tolist()

    present = []

    for med in interactions:
        if med in detected_drugs and med != drug:
            present.append(med)

    return present


def get_drug_info(drug):
    keywords1 = [
        "overdose", "high dose", "adverse", "toxicity",
        "renal", "bleeding", "infection", "hypotension",
        "tachycardia", "arrhythmia", "failure"
    ]
    keywords2 = [
        "indicated", "treatment", "used for",
        "infection", "inflammation", "ulcer",
        "hyperlipidemia", "immunosuppressive"
    ]
    drug_db = pd.read_csv('DrugData/drug_prescription1.csv')
    drug_db["drug_name"] = drug_db["drug_name"].str.lower()
    row = drug_db[drug_db["drug_name"] == drug.lower()]
    if len(row) == 0:
        return None
    row = row.iloc[0]
    return {
        # "information": row["information"] if pd.notna(row["information"]) else "",
        "indication": process_drug_detail(row["indication"] if pd.notna(row["indication"]) else "",keywords2),
        "toxicity": process_drug_detail(row["toxicity"] if pd.notna(row["toxicity"]) else "",keywords1)
    }


def Controller(ocr_text):
    cleaned_text = clean_text(ocr_text)
    lines = [l.strip() for l in cleaned_text.split("\n") if l.strip()]
    prescription_lines = [l for l in lines if is_prescription_line(l)]
    data=[]
    for line in prescription_lines:
        token = extract_drug_token(line)
        if token:
            corrected, score = correct_drug(token)
            dose, unit = extract_dose(line)
            frequency = extract_frequency(line)
            if frequency is None:
                frequency = fuzzy_frequency(line)
            drug_info = get_drug_info(corrected)
            data.append({
                "line": line,
                "drug": corrected,
                "confidence": score,
                "dose": dose,
                "unit": unit,
                "frequency": frequency,
                "drug_info": drug_info
            })
    detected_drugs = [item["drug"] for item in data]
    final_payload = []

    for item in data:
        final_payload.append({
            "raw_line": item["line"],
            "drug": item["drug"],
            "dose": f'{item["dose"]} {item["unit"]}',
            "frequency": item["frequency"],
            "indication": item["drug_info"]["indication"] if item["drug_info"] else None,
            "toxicity": item["drug_info"]["toxicity"] if item["drug_info"] else None,
            "confidence": item["confidence"],
            "interactions": get_present_interactions(item["drug"],detected_drugs)
        })
    return detect_prescription_errors(final_payload)
