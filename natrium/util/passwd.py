import bcrypt

def verify_passwd(raw: str, hashed: bytes):
    return bcrypt.checkpw(raw.encode(), hashed)