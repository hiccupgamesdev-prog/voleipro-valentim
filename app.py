import os
import uuid
import json
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get("SECRET_KEY", "voleipro-secret-key-123")

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
MONGO_URI = os.environ.get("MONGO_URI")
db = None

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        db = client.get_database("voleipro")
        print("Conectado ao MongoDB Atlas")
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")

# Fallback para JSON se não houver MongoDB (útil para desenvolvimento local)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

USERS_FILE = os.path.join(DATA_DIR, "users.json")
CAMPS_FILE = os.path.join(DATA_DIR, "campeonatos.json")

def load_json(file_path, default=[]):
    if not os.path.exists(file_path):
        return default
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- AUXILIARES DE PERSISTÊNCIA ---
def get_users():
    if db is not None:
        return list(db.users.find())
    return load_json(USERS_FILE)

def save_user(user):
    if db is not None:
        db.users.update_one({"id": user["id"]}, {"$set": user}, upsert=True)
    else:
        users = load_json(USERS_FILE)
        # Update or append
        found = False
        for i, u in enumerate(users):
            if u["id"] == user["id"]:
                users[i] = user
                found = True
                break
        if not found:
            users.append(user)
        save_json(USERS_FILE, users)

def get_camps():
    if db is not None:
        return list(db.campeonatos.find().sort("data_evento", 1))
    return sorted(load_json(CAMPS_FILE), key=lambda x: x.get("data_evento", ""))

def save_camp(camp):
    if db is not None:
        db.campeonatos.update_one({"id": camp["id"]}, {"$set": camp}, upsert=True)
    else:
        camps = load_json(CAMPS_FILE)
        found = False
        for i, c in enumerate(camps):
            if c["id"] == camp["id"]:
                camps[i] = camp
                found = True
                break
        if not found:
            camps.append(camp)
        save_json(CAMPS_FILE, camps)

# --- MIDDLEWARES ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, faça login para acessar esta página.", "info")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Acesso restrito a administradores.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS ---
@app.route("/")
def index():
    all_camps = get_camps()
    # Filtrar apenas campeonatos ativos (data >= hoje)
    today = datetime.now().strftime("%Y-%m-%d")
    ativos = [c for c in all_camps if c.get("data_evento", "") >= today]
    return render_template("index.html", campeonatos=ativos[:3])

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email").lower()
        telefone = request.form.get("telefone")
        senha = request.form.get("senha")
        confirma = request.form.get("confirma_senha")

        users = get_users()
        if any(u["email"] == email for u in users):
            flash("Este e-mail já está cadastrado.", "danger")
            return redirect(url_for("cadastro"))

        if senha != confirma:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for("cadastro"))

        new_user = {
            "id": str(uuid.uuid4()),
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "senha": generate_password_hash(senha),
            "role": "user",
            "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Configuração Admin do Jhony
        if email == "jhonybrandoborges@gmail.com":
            new_user["role"] = "admin"
        elif len(users) == 0:
            new_user["role"] = "admin"

        save_user(new_user)
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").lower()
        senha = request.form.get("senha")

        users = get_users()
        user = next((u for u in users if u["email"] == email), None)

        if user and check_password_hash(user["senha"], senha):
            session["user_id"] = user["id"]
            session["user_nome"] = user["nome"]
            session["role"] = user["role"]
            flash(f"Bem-vindo, {user['nome']}!", "success")
            return redirect(url_for("index"))
        
        flash("E-mail ou senha incorretos.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "info")
    return redirect(url_for("index"))

@app.route("/campeonatos")
def campeonatos():
    all_camps = get_camps()
    return render_template("campeonatos.html", campeonatos=all_camps)

@app.route("/campeonato/<id>")
@login_required
def detalhe_campeonato(id):
    camps = get_camps()
    camp = next((c for c in camps if c["id"] == id), None)
    if not camp:
        flash("Campeonato não encontrado.", "danger")
        return redirect(url_for("campeonatos"))
    
    # Verificar se usuário já está inscrito
    user_id = session["user_id"]
    inscrito = user_id in camp.get("inscritos", [])
    espera = user_id in camp.get("lista_espera", [])
    
    return render_template("detalhe.html", camp=camp, inscrito=inscrito, espera=espera)

@app.route("/inscrever/<id>")
@login_required
def inscrever(id):
    camps = get_camps()
    camp = next((c for c in camps if c["id"] == id), None)
    if not camp:
        flash("Campeonato não encontrado.", "danger")
        return redirect(url_for("campeonatos"))

    user_id = session["user_id"]
    if user_id in camp.get("inscritos", []) or user_id in camp.get("lista_espera", []):
        flash("Você já está na lista deste campeonato.", "info")
        return redirect(url_for("detalhe_campeonato", id=id))

    if "inscritos" not in camp: camp["inscritos"] = []
    if "lista_espera" not in camp: camp["lista_espera"] = []

    if len(camp["inscritos"]) < int(camp["max_participantes"]):
        camp["inscritos"].append(user_id)
        flash("Inscrição confirmada com sucesso!", "success")
    else:
        camp["lista_espera"].append(user_id)
        flash("Vagas esgotadas! Você entrou na lista de espera.", "warning")

    save_camp(camp)
    return redirect(url_for("detalhe_campeonato", id=id))

@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    users = get_users()
    user = next((u for u in users if u["id"] == session["user_id"]), None)
    
    if request.method == "POST":
        user["nome"] = request.form.get("nome")
        user["telefone"] = request.form.get("telefone")
        nova_senha = request.form.get("nova_senha")
        if nova_senha:
            user["senha"] = generate_password_hash(nova_senha)
        
        save_user(user)
        session["user_nome"] = user["nome"]
        flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for("perfil"))
        
    return render_template("perfil.html", user=user)

# --- ROTAS ADMIN ---
@app.route("/admin")
@admin_required
def admin_dashboard():
    camps = get_camps()
    users = get_users()
    return render_template("admin/dashboard.html", camps=camps, users_count=len(users))

@app.route("/admin/campeonatos/novo", methods=["GET", "POST"])
@admin_required
def admin_novo_camp():
    if request.method == "POST":
        new_camp = {
            "id": str(uuid.uuid4()),
            "nome": request.form.get("nome"),
            "data_evento": request.form.get("data"),
            "hora_evento": request.form.get("hora"),
            "local": request.form.get("local"),
            "categoria": request.form.get("categoria"),
            "max_participantes": request.form.get("max_participantes"),
            "regras": request.form.get("regras"),
            "inscritos": [],
            "lista_espera": []
        }
        save_camp(new_camp)
        flash("Campeonato criado com sucesso!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/form_campeonato.html", camp=None)

# Vercel entry point
app.debug = False
if __name__ == "__main__":
    app.run(debug=True)
