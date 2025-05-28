from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_str(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)


def hash_str(password: str):
    return pwd_context.hash(password)
