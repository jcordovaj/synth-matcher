import hashlib, sqlite3

def anonymize(patient_id):
    return hashlib.sha256(patient_id.encode()).hexdigest()[:12]

def save_log(db_name, data):
    # Lógica para guardar en screening_log
    pass