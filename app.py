from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)

# Configuração do banco de dados
DATABASE = "users.db"

def create_table():
    """Cria a tabela de usuários no banco de dados."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            access_until TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(username, password, access_days):
    """Adiciona um novo usuário com acesso temporário."""
    access_until = (datetime.now() + timedelta(days=access_days)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password, access_until)
        VALUES (?, ?, ?)
    """, (username, password, access_until))
    conn.commit()
    conn.close()

def verify_access(username, password):
    """Verifica se o usuário tem acesso válido."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT access_until FROM users
        WHERE username = ? AND password = ?
    """, (username, password))
    result = cursor.fetchone()
    conn.close()

    if result:
        access_until = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        return access_until > datetime.now()
    return False

# Rotas da API
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    access_days = data.get("access_days", 30)  # 30 dias de acesso por padrão

    if not username or not password:
        return jsonify({"error": "Username e password são obrigatórios"}), 400

    add_user(username, password, access_days)
    return jsonify({"message": "Usuário registrado com sucesso"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username e password são obrigatórios"}), 400

    if verify_access(username, password):
        return jsonify({"message": "Acesso permitido"})
    else:
        return jsonify({"error": "Acesso negado ou expirado"}), 403

if __name__ == "__main__":
    create_table()
    app.run(debug=True)