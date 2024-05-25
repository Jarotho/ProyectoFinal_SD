from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import bcrypt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'clave-secreta' 
jwt = JWTManager(app)

# Datos de ejemplo para usuarios (en producción, deben almacenarse de forma segura en una base de datos)
USUARIOS = {
    'usuario1': bcrypt.hashpw('contraseña1'.encode('utf-8'), bcrypt.gensalt()),
    'usuario2': bcrypt.hashpw('contraseña2'.encode('utf-8'), bcrypt.gensalt())
}

# Función para autenticar usuarios
def autenticar(username, password):
    if username in USUARIOS and bcrypt.checkpw(password.encode('utf-8'), USUARIOS[username]):
        return True
    else:
        return False

# Ruta para autenticar y obtener token de acceso
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)
    if not username or not password:
        return jsonify({"error": "Usuario y contraseña son requeridos"}), 400

    if autenticar(username, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Credenciales inválidas"}), 401

# Ruta protegida para obtener información del clima (ejemplo de endpoint protegido)
@app.route("/api/clima/<ciudad>", methods=["GET"])
@jwt_required()
def obtener_clima_api(ciudad):
    # Lógica para obtener información del clima
    return jsonify({"temperatura": 25, "descripcion": "Soleado"})

# Ruta protegida para otras operaciones (ejemplo de endpoint protegido)
@app.route("/api/operacion", methods=["POST"])
@jwt_required()
def realizar_operacion():
    data = request.get_json()
    # Procesar la solicitud y devolver resultados
    return jsonify({"mensaje": "Operación realizada con éxito"})

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
