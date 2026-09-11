import sys
sys.path.insert(0, '/mnt/c/Users/guill/Documents/Personal_Projects/Academy_Test/backend')

from app.api.v1.users.router import router as ur
from app.api.v1.courses.router import router as cr
from app.api.v1.payments.router import router as pr
print("All routers imported OK")
print(f"Users routes: {[r.path for r in ur.routes]}")
print(f"Courses routes: {[r.path for r in cr.routes]}")
print(f"Payments routes: {[r.path for r in pr.routes]}")
