
import json
import secrets
import base64

from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from secretsanta import input_names, assign_secret_santa


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.txt"

ITERATIONS = 600_000


def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS
    )

    return kdf.derive(password.encode("utf-8"))


def encrypt_data(data, password):
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)

    key = derive_key(password, salt)

    aes = AESGCM(key)

    plaintext = json.dumps(data).encode("utf-8")
    ciphertext = aes.encrypt(nonce, plaintext, None)

    return {
        "salt": base64.b64encode(salt).decode("utf-8"),
        "nonce": base64.b64encode(nonce).decode("utf-8"),
        "data": base64.b64encode(ciphertext).decode("utf-8")
    }


def generate_database():
    names = input_names()

    if len(names) != len(set(names)):
        raise ValueError("Duplicate participant names found")

    assignments = assign_secret_santa(names)

    if len(assignments) != len(names):
        raise ValueError("Incomplete Secret Santa assignments")

    database = {
        "version": 1,
        "kdf": "PBKDF2-HMAC-SHA256",
        "iterations": ITERATIONS,
        "cipher": "AES-256-GCM",
        "participants": {}
    }

    credentials = []

    for name in names:
        username = secrets.token_urlsafe(8)
        password = secrets.token_urlsafe(16)

        participant_data = {
            "name": name,
            "recipient": assignments[name],
            "wishlist": []
        }

        encrypted = encrypt_data(participant_data, password)

        database["participants"][username] = encrypted

        credentials.append(
            f"Participant: {name}\n"
            f"Username: {username}\n"
            f"Password: {password}\n"
            f"-------------------------\n"
        )

    with open(DATABASE_PATH, "w", encoding="utf-8") as file:
        json.dump(database, file, indent=4)

    with open(CREDENTIALS_PATH, "w", encoding="utf-8") as file:
        file.writelines(credentials)

    print(f"Generated database for {len(names)} participants.")
    print(f"Database: {DATABASE_PATH}")
    print(f"Credentials: {CREDENTIALS_PATH}")


if __name__ == "__main__":
    generate_database()
