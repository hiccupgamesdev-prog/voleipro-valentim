import os
import uuid
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("SECRET_KEY", "voleipro-secret-key-123")

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
MONGO_URI = os.environ.get("MONGO_URI")
db = None
DB_CONNECTED = False

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.get_database("voleipro")
        DB_CONNECTED = True
        print("Conectado ao MongoDB Atlas")
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")

# Memória temporária para evitar erros de escrita em disco na Vercel
_memory_cache = {"users": [], "camps": []}

# Context Processor para passar o status do banco para TODAS as páginas automaticamente
@app.context_processor
def inject_db_status():
    return dict(db_status=DB_CONNECTED)

def get_users():
    if DB_CONNECTED:
        return list(db.users.find())
    return _memory_cache["users"]

def save_user(user):
    if DB_CONNECTED:
        db.users.update_one({"id": user["id"]}, {"$set": user}, upsert=True)
    else:
        for i, u in enumerate(_memory_cache["users"]):
            if u["id"] == user["id"]:
                _memory_cache["users"][i] = user
                return
        _memory_cache["users"].append(user)

def get_camps():
    if DB_CONNECTED:
        return list(db.campeonatos.find().sort("data_evento", 1))
    return sorted(_memory_cache["camps"], key=lambda x: x.get("data_evento", ""))

def save_camp(camp):
    if DB_CONNECTED:
        db.campeonatos.update_one({"id": camp["id"]}, {"$set": camp}, upsert=True)
    else:
        for i, c in enumerate(_memory_cache["camps"]):
            if c["id"] == camp["id"]:
                _memory_cache["camps"][i] = camp
                return
        _memory_cache["camps"].append(camp)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# --- MIDDLEWARES ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS ---
@app.route("/")
def index():
    all_camps = get_camps()
    today = datetime.now().strftime("%Y-%m-%d")
    ativos = [c for c in all_camps if c.get("data_evento", "") >= today]
    return render_template("index.html", campeonatos=ativos[:3])

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email").lower().strip()
        telefone = request.form.get("telefone")
        senha = request.form.get("senha")
        confirma = request.form.get("confirma_senha")

        users = get_users()
        if any(u["email"] == email for u in users):
            flash("E-mail já cadastrado.", "danger")
            return redirect(url_for("cadastro"))

        if senha != confirma:
            flash("Senhas não coincidem.", "danger")
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
        
        if email == "jhonybrandoborges@gmail.com":
            new_user["role"] = "admin"
        elif len(users) == 0:
            new_user["role"] = "admin"

        save_user(new_user)
        # Login automático após cadastro
        session["user_id"] = new_user["id"]
        session["user_nome"] = new_user["nome"]
        session["role"] = new_user["role"]
        
        return redirect(url_for("campeonatos"))
    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").lower().strip()
        senha = request.form.get("senha")
        users = get_users()
        user = next((u for u in users if u["email"] == email), None)
        if user and check_password_hash(user["senha"], senha):
            session["user_id"] = user["id"]
            session["user_nome"] = user["nome"]
            session["role"] = user["role"]
            return redirect(url_for("campeonatos"))
        flash("Dados incorretos.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/campeonatos")
def campeonatos():
    return render_template("campeonatos.html", campeonatos=get_camps())

@app.route("/campeonato/<id>")
@login_required
def detalhe_campeonato(id):
    camps = get_camps()
    camp = next((c for c in camps if c["id"] == id), None)
    if not camp: return redirect(url_for("campeonatos"))
    inscrito = session["user_id"] in camp.get("inscritos", [])
    espera = session["user_id"] in camp.get("lista_espera", [])
    return render_template("detalhe.html", camp=camp, inscrito=inscrito, espera=espera)

@app.route("/inscrever/<id>")
@login_required
def inscrever(id):
    camps = get_camps()
    camp = next((c for c in camps if c["id"] == id), None)
    if not camp: return redirect(url_for("campeonatos"))
    user_id = session["user_id"]
    if user_id in camp.get("inscritos", []) or user_id in camp.get("lista_espera", []):
        return redirect(url_for("detalhe_campeonato", id=id))
    
    if "inscritos" not in camp: camp["inscritos"] = []
    if "lista_espera" not in camp: camp["lista_espera"] = []

    if len(camp["inscritos"]) < int(camp.get("max_participantes", 0)):
        camp["inscritos"].append(user_id)
        flash("Inscrição confirmada!", "success")
    else:
        camp["lista_espera"].append(user_id)
        flash("Você está na lista de espera.", "warning")
    save_camp(camp)
    return redirect(url_for("detalhe_campeonato", id=id))

@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    users = get_users()
    user = next((u for u in users if u["id"] == session["user_id"]), None)
    if not user:
        session.clear()
        return redirect(url_for("login"))
        
    if request.method == "POST":
        user["nome"] = request.form.get("nome")
        user["telefone"] = request.form.get("telefone")
        nova_senha = request.form.get("nova_senha")
        if nova_senha:
            user["senha"] = generate_password_hash(nova_senha)
        save_user(user)
        session["user_nome"] = user["nome"]
        flash("Perfil atualizado!", "success")
    return render_template("perfil.html", user=user)

@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin/dashboard.html", camps=get_camps(), users_count=len(get_users()))

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
            "inscritos": [], "lista_espera": []
        }
        save_camp(new_camp)
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/form_campeonato.html", camp=None)

# Exportar para Vercel
app.debug = False
if __name__ == "__main__":
    app.run()
