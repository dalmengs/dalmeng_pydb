def StringField(name: str, max_length: int = 256):
    return {
        "type": "string",
        "name": name,
        "max_length": max_length
    }

def VectorField(name: str,):
    return {
        "type": "vector",
        "name": name
    }
