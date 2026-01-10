import spacy

nlp = spacy.load("en_core_web_sm")

def detect_entity(text: str):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "entity": ent.label_,
            "start_position": ent.start_char,
            "end_position": ent.end_char
        })
    
    for token in doc:

        if "obj" in token.dep_:
            entities.append({
                "text": token.text,
                "entity": "OBJECT_NOUN",
                "start_position": token.idx,
                "end_position": token.idx + len(token.text)
            })
    
    return entities
