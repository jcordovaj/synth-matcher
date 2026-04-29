import hashlib, sqlite3, json

def get_patient_hash(patient_id):
    return hashlib.sha256(patient_id.encode()).hexdigest()[:12]

def save_to_audit(db_path, data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO screening_log (patient_hash, trial_id, decision, reasoning, raw_json)
        VALUES (?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()