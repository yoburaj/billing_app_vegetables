import uuid

def generate_bill_number():
    return str(uuid.uuid4())[:8]
