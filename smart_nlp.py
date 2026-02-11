import re
import dateparser
import spacy
from calendar_logic import parse_datetime


nlp = spacy.load("en_core_web_sm")

DISEASES = [
    "fever", "cough", "cold", "headache",
    "stomach pain", "stomach ache",
    "diabetes", "bp", "back pain", "flu"
]



def extract_disease(text):

    text = text.lower()

    for d in DISEASES:
        if d in text:
            return d

    return text



def extract_time(text):

    dt = parse_datetime(text)

    if dt:
        return dt.strftime("%Y-%m-%d %I:%M %p")
    

def extract_name(text):
    text = text.strip()


    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    text_lower = text.lower()

    patterns = [
        r"my name is ([a-zA-Z]+)",
        r"i am ([a-zA-Z]+)",
        r"i'm ([a-zA-Z]+)",
        r"this is ([a-zA-Z]+)",
        r"([a-zA-Z]+) this side",
        r"([a-zA-Z]+) here",
        r"hello[, ]+([a-zA-Z]+)",
        r"hi[, ]+([a-zA-Z]+)",
        r"hey[, ]+([a-zA-Z]+)"
    ]

    for p in patterns:
        m = re.search(p, text_lower, re.I)
        if m:

            return m.group(1).capitalize()

    # 3️⃣ If user spoke single word → assume name
    words = text.split()
    if len(words) == 1:
        return words[0].capitalize()

    # 4️⃣ Fallback – first proper noun style word
    for w in words:
        if w[0].isupper():
            return w

    return "User"





def understand(text):

    return {
        "name": extract_name(text),
        "disease": extract_disease(text),
        "time": extract_time(text)
    }
