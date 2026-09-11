from passlib.context import CryptContext
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
print("ADMIN:", pwd.hash("Admin123!"))
print("TEACHER:", pwd.hash("Teacher123!"))
