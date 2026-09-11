"""Check bcrypt version installed."""
import bcrypt
print("bcrypt version:", bcrypt.__version__)

from passlib.context import CryptContext
ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
h = ctx.hash("TestPass1!")
print("Hash OK:", h[:30])
print("Verify:", ctx.verify("TestPass1!", h))
