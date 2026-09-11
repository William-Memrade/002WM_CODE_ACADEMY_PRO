from functools import wraps
from flask import request, jsonify, session


def verify_jwt_token(token: str):
    """Valida el JWT y devuelve el usuario autenticado.

    Reemplaza esta función por tu propia lógica de decodificación JWT y carga
    de usuario desde la base de datos.
    """
    raise NotImplementedError("Implementa verify_jwt_token(token) según tu app Flask")


def get_current_user():
    """Obtiene el usuario autenticado actual.

    Soporta JWT en Authorization header o sesión de Flask.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        return verify_jwt_token(token)

    user_id = session.get("user_id")
    if user_id:
        from app.models.user import User  # Ajusta según tu modelo

        return User.query.get(user_id)

    return None


def role_required(allowed_roles):
    """Decorador para rutas que requieren uno o varios roles."""
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            user = get_current_user()

            if user is None:
                return jsonify({"error": "Unauthorized"}), 401

            user_roles = getattr(user, "roles", None) or getattr(user, "role", None)
            if isinstance(user_roles, str):
                user_roles = [user_roles]
            if user_roles is None:
                user_roles = []

            if not set(allowed_roles).intersection(user_roles):
                return jsonify({"error": "Unauthorized"}), 403

            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator


# Ejemplo de uso:
#
# from flask import Flask, jsonify
# from app.utils.flask_role_required import role_required
#
# app = Flask(__name__)
#
# @app.route("/admin/dashboard")
# @role_required(["admin"])
# def admin_dashboard():
#     return jsonify({"message": "Bienvenido, admin"}), 200
#
# @app.route("/teacher/grades")
# @role_required(["teacher", "admin"])
# def teacher_grades():
#     return jsonify({"message": "Acceso docente"}), 200
