import os
import uuid
import logging
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de caminhos dinâmicos para a Vercel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static',
            static_url_path='/static')
app.secret_key = os.environ.get("SECRET_KEY", "voleipro-secret-key-v11-final")

# --- BANCO DE DADOS ---
MONGO_URI = os.environ.get("MONGO_URI")
db = None
DB_CONNECTED = False

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.get_database("voleipro")
        DB_CONNECTED = True
    except Exception as e:
        print(f"Erro MongoDB: {e}")

@app.context_processor
def inject_globals():
    return dict(db_status=DB_CONNECTED)

# --- FUNÇÕES DE APOIO ---
def get_users():
    if DB_CONNECTED:
        try: return list(db.users.find())
        except: pass
    
    # Fallback para dados locais (JSON)
    try:
        import json
        paths = [
            os.path.join(BASE_DIR, 'data', 'users.json'),
            os.path.join(os.getcwd(), 'data', 'users.json'),
            '/var/task/data/users.json'
        ]
        for p in paths:
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    users = json.load(f)
                    return users if isinstance(users, list) else []
    except Exception as e:
        print(f"Erro ao ler JSON de usuários: {e}")
    
    return []

def save_user(user_data):
    if DB_CONNECTED:
        try: db.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)
        except: pass

def get_camps():
    camps = []
    if DB_CONNECTED:
        try: 
            camps = list(db.campeonatos.find().sort("data_evento", 1))
            if camps: return camps
        except: pass
    
    # Fallback para dados locais (JSON)
    try:
        import json
        # Tenta múltiplos caminhos para garantir que encontre na Vercel
        paths = [
            os.path.join(BASE_DIR, 'data', 'campeonatos.json'),
            os.path.join(os.getcwd(), 'data', 'campeonatos.json'),
            '/var/task/data/campeonatos.json'
        ]
        for p in paths:
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    camps = json.load(f)
                    return sorted(camps, key=lambda x: x.get("data_evento", ""))
    except Exception as e:
        print(f"Erro ao ler JSON: {e}")
    
    return camps

def save_camp(camp_data):
    if DB_CONNECTED:
        try: db.campeonatos.update_one({"id": camp_data["id"]}, {"$set": camp_data}, upsert=True)
        except: pass

# --- PROTEÇÃO ---
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
            flash("Acesso restrito.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

# --- SERVIR ARQUIVOS ESTÁTICOS ---
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)

# --- ROTAS ---
@app.route("/")
def index():
    all_camps = get_camps()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Tenta filtrar ativos, mas se não houver nenhum, mostra os próximos 3 independente da data
    ativos = [c for c in all_camps if c.get("data_evento", "") >= today]
    
    display_camps = ativos if ativos else all_camps
    return render_template("index.html", campeonatos=display_camps[:3])

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        nome = request.form.get("nome", "").strip()
        if not email or not nome:
            flash("Preencha os campos obrigatórios.", "danger")
            return redirect(url_for("cadastro"))
        
        users = get_users()
        if any(u["email"] == email for u in users):
            flash("Email já cadastrado.", "danger")
            return redirect(url_for("cadastro"))
        
        new_user = {
            "id": str(uuid.uuid4()),
            "nome": nome,
            "email": email,
            "telefone": request.form.get("telefone", ""),
            "senha": generate_password_hash(request.form.get("senha", "")),
            "role": "admin" if email == "jhonybrandoborges@gmail.com" else "user",
            "data_cadastro": datetime.now().isoformat()
        }
        save_user(new_user)
        flash("Cadastro realizado! Faça login.", "success")
        return redirect(url_for("login"))
    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        senha = request.form.get("senha", "")
        
        users = get_users()
        user = next((u for u in users if u["email"] == email), None)
        
        if user and check_password_hash(user["senha"], senha):
            session["user_id"] = user["id"]
            session["user_nome"] = user["nome"]
            session["role"] = user["role"]
            return redirect(url_for("index"))
        
        flash("E-mail ou senha incorretos.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/campeonatos")
def campeonatos():
    return render_template("campeonatos.html", campeonatos=get_camps())

@app.route("/campeonato/<id>")
def detalhe_campeonato(id):
    camp = next((c for c in get_camps() if c["id"] == id), None)
    if not camp: return redirect(url_for("campeonatos"))
    
    inscritos_nomes = []
    espera_nomes = []
    
    users = get_users()
    for uid in camp.get("inscritos", []):
        u = next((usr for usr in users if usr["id"] == uid), None)
        if u: inscritos_nomes.append(u.get("nome", "Atleta Desconhecido"))
        
    for uid in camp.get("lista_espera", []):
        u = next((usr for usr in users if usr["id"] == uid), None)
        if u: espera_nomes.append(u.get("nome", "Atleta Desconhecido"))
    
    inscrito = False
    espera = False
    if session.get("user_id"):
        inscrito = session["user_id"] in camp.get("inscritos", [])
        espera = session["user_id"] in camp.get("lista_espera", [])
        
    return render_template("detalhe.html", camp=camp, inscritos_nomes=inscritos_nomes, espera_nomes=espera_nomes, inscrito=inscrito, espera=espera)

@app.route("/inscrever/<id>")
@login_required
def inscrever(id):
    camp = next((c for c in get_camps() if c["id"] == id), None)
    if not camp: return redirect(url_for("campeonatos"))
    
    user_id = session["user_id"]
    if user_id in camp.get("inscritos", []) or user_id in camp.get("lista_espera", []):
        flash("Você já está inscrito!", "info")
        return redirect(url_for("detalhe_campeonato", id=id))
    
    max_p = int(camp.get("max_participantes", 12))
    if len(camp.get("inscritos", [])) < max_p:
        if "inscritos" not in camp: camp["inscritos"] = []
        camp["inscritos"].append(user_id)
        flash("Inscrição realizada com sucesso!", "success")
    else:
        if "lista_espera" not in camp: camp["lista_espera"] = []
        camp["lista_espera"].append(user_id)
        flash("Vagas esgotadas! Você está na fila de espera.", "warning")
        
    save_camp(camp)
    return redirect(url_for("detalhe_campeonato", id=id))

@app.route("/cancelar_inscricao/<id>")
@login_required
def cancelar_inscricao(id):
    camp = next((c for c in get_camps() if c["id"] == id), None)
    if not camp: return redirect(url_for("campeonatos"))
    
    user_id = session["user_id"]
    if user_id in camp.get("inscritos", []):
        camp["inscritos"].remove(user_id)
        # Promover primeiro da espera
        if camp.get("lista_espera"):
            proximo = camp["lista_espera"].pop(0)
            camp["inscritos"].append(proximo)
    elif user_id in camp.get("lista_espera", []):
        camp["lista_espera"].remove(user_id)
        
    save_camp(camp)
    flash("Inscrição cancelada.", "info")
    return redirect(url_for("detalhe_campeonato", id=id))

@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    users = get_users()
    user = next((u for u in users if u["id"] == session["user_id"]), None)
    
    if request.method == "POST":
        user["nome"] = request.form.get("nome", user["nome"])
        user["telefone"] = request.form.get("telefone", user["telefone"])
        save_user(user)
        session["user_nome"] = user["nome"]
        flash("Perfil atualizado!", "success")
        
    meus_camps = [c for c in get_camps() if session["user_id"] in c.get("inscritos", []) or session["user_id"] in c.get("lista_espera", [])]
    return render_template("perfil.html", user=user, campeonatos=meus_camps)

# --- ADMIN ---
@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin/dashboard.html", camps=get_camps(), users_count=len(get_users()))

@app.route("/admin/usuarios")
@admin_required
def admin_usuarios():
    return render_template("admin/usuarios.html", users=get_users())

@app.route("/admin/campeonatos/novo", methods=["GET", "POST"])
@admin_required
def admin_novo_camp():
    if request.method == "POST":
        new_camp = {
            "id": str(uuid.uuid4()),
            "nome": request.form.get("nome", ""),
            "data_evento": request.form.get("data", ""),
            "hora_evento": request.form.get("hora", ""),
            "local": request.form.get("local", ""),
            "categoria": request.form.get("categoria", "Geral"),
            "max_participantes": request.form.get("max_participantes", "12"),
            "regras": request.form.get("regras", ""),
            "inscritos": [], "lista_espera": []
        }
        save_camp(new_camp)
        flash("Campeonato criado!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/form_campeonato.html", camp=None)

@app.route("/admin/campeonatos/editar/<id>", methods=["GET", "POST"])
@admin_required
def admin_editar_camp(id):
    camp = next((c for c in get_camps() if c["id"] == id), None)
    if not camp: return redirect(url_for("admin_dashboard"))
    
    if request.method == "POST":
        try: new_max = int(request.form.get("max_participantes", 12))
        except: new_max = 12
        
        try: old_max = int(camp.get("max_participantes", 12))
        except: old_max = 12
            
        camp.update({
            "nome": request.form.get("nome", camp["nome"]),
            "data_evento": request.form.get("data", camp["data_evento"]),
            "hora_evento": request.form.get("hora", camp["hora_evento"]),
            "local": request.form.get("local", camp["local"]),
            "categoria": request.form.get("categoria", camp["categoria"]),
            "max_participantes": str(new_max),
            "regras": request.form.get("regras", camp["regras"])
        })
        
        if "inscritos" not in camp: camp["inscritos"] = []
        if "lista_espera" not in camp: camp["lista_espera"] = []
        
        # Se aumentou as vagas, promover pessoas da fila de espera
        if new_max > old_max:
            while len(camp["inscritos"]) < new_max and camp["lista_espera"]:
                promovido = camp["lista_espera"].pop(0)
                camp["inscritos"].append(promovido)
        # Se diminuiu as vagas, mover inscritos extras para fila de espera
        elif new_max < old_max:
            while len(camp["inscritos"]) > new_max:
                removido = camp["inscritos"].pop()
                camp["lista_espera"].insert(0, removido)
            
        save_camp(camp)
        flash("Campeonato atualizado!", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin/form_campeonato.html", camp=camp)

@app.route("/admin/campeonatos/excluir/<id>")
@admin_required
def admin_excluir_camp(id):
    if DB_CONNECTED:
        db.campeonatos.delete_one({"id": id})
    flash("Campeonato excluído.", "info")
    return redirect(url_for("admin_dashboard"))

# --- GERENCIAMENTO DE USUÁRIOS ---
@app.route("/admin/usuarios/promover/<id>")
@admin_required
def admin_promover(id):
    users = get_users()
    user = next((u for u in users if u["id"] == id), None)
    if user:
        user["role"] = "admin"
        save_user(user)
        flash(f"{user['nome']} foi promovido a Admin!", "success")
    else:
        flash("Usuário não encontrado.", "danger")
    return redirect(url_for("admin_usuarios"))

@app.route("/admin/usuarios/excluir/<id>")
@admin_required
def admin_excluir_usuario(id):
    if id == session.get("user_id"):
        flash("Você não pode excluir a si mesmo.", "danger")
        return redirect(url_for("admin_usuarios"))
    
    users = get_users()
    user = next((u for u in users if u["id"] == id), None)
    if user:
        users.remove(user)
        if DB_CONNECTED:
            try:
                db.users.delete_one({"id": id})
            except:
                pass
        flash(f"{user['nome']} foi excluído.", "success")
    else:
        flash("Usuário não encontrado.", "danger")
    return redirect(url_for("admin_usuarios"))

if __name__ == "__main__":
    app.run(debug=True)
