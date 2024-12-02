from cryptography.fernet import Fernet

def generate_encryption_key():
    key = Fernet.generate_key()
    print(key.decode())

if __name__ == "__main__":
    generate_encryption_key()