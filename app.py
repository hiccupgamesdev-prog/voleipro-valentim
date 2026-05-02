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
    try: return list(db.users.find()) if DB_CONNECTED else []
    except: return []

def save_user(user_data):
    if DB_CONNECTED:
        try: db.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)
        except: pass

def get_camps():
    if DB_CONNECTED:
        try: return list(db.campeonatos.find().sort("data_evento", 1))
        except: pass
    
    # Fallback para dados locais
    try:
        import json
        data_file = os.path.join(BASE_DIR, 'data', 'campeonatos.json')
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                camps = json.load(f)
                return sorted(camps, key=lambda x: x.get("data_evento", ""))
    except:
        pass
    return []

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
    ativos = [c for c in all_camps if c.get("data_evento", "") >= today]
    return render_template("index.html", campeonatos=ativos[:3])

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        nome = request.form.get("nome", "").strip()
        if not email or not nome:
            flash("Preencha os campos obrigatórios.", "danger")
            return redirect(url_for("cadastro"))
        
        users = get_users()
        if any(u.get("email") == email for u in users):
            flash("E-mail já cadastrado.", "danger")
            return redirect(url_for("cadastro"))

        new_user = {
            "id": str(uuid.uuid4()),
            "nome": nome,
            "email": email,
            "telefone": request.form.get("telefone", ""),
            "senha": generate_password_hash(request.form.get("senha", "123456")),
            "role": "user",
            "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if email == "jhonybrandoborges@gmail.com" or not users:
            new_user["role"] = "admin"

        save_user(new_user)
        session.update({"user_id": new_user["id"], "user_nome": new_user["nome"], "role": new_user["role"]})
        return redirect(url_for("campeonatos"))
    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        user = next((u for u in get_users() if u.get("email") == email), None)
        if user and check_password_hash(user.get("senha", ""), request.form.get("senha", "")):
            session.update({"user_id": user["id"], "user_nome": user["nome"], "role": user.get("role", "user")})
            return redirect(url_for("campeonatos"))
        flash("E-mail ou senha incorretos.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/campeonatos")
def campeonatos():
    return render_template("campeonatos.html", campeonatos=get_camps())

@app.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    user = next((u for u in get_users() if u["id"] == session.get("user_id")), None)
    if not user: return redirect(url_for("logout"))
    
    if request.method == "POST":
        user["nome"] = request.form.get("nome", user["nome"])
        user["telefone"] = request.form.get("telefone", user["telefone"])
        if request.form.get("nova_senha"):
            user["senha"] = generate_password_hash(request.form.get("nova_senha"))
        save_user(user)
        session["user_nome"] = user["nome"]
        flash("Perfil atualizado!", "success")
    return render_template("perfil.html", user=user)

@app.route("/campeonato/<id>")
@login_required
def detalhe_campeonato(id):
    camp = next((c for c in get_camps() if c["id"] == id), None)
    if not camp: return redirect(url_for("campeonatos"))
    
    users_dict = {u["id"]: u["nome"] for u in get_users()}
    inscritos_nomes = [users_dict.get(uid, "Atleta") for uid in camp.get("inscritos", [])]
    espera_nomes = [users_dict.get(uid, "Atleta") for uid in camp.get("lista_espera", [])]
    
    return render_template("detalhe.html", camp=camp, 
                           inscrito=(session["user_id"] in camp.get("inscritos", [])), 
                           espera=(session["user_id"] in camp.get("lista_espera", [])),
                           inscritos_nomes=inscritos_nomes,
                           espera_nomes=espera_nomes)

@app.route("/inscrever/<id>")
@login_required
def inscrever(id):
    camp = next((c for c in get_camps() if c["id"] == id), None)
    if not camp: return redirect(url_for("campeonatos"))
    
    u_id = session["user_id"]
    if u_id not in camp.get("inscritos", []) and u_id not in camp.get("lista_espera", []):
        if "inscritos" not in camp: camp["inscritos"] = []
        if "lista_espera" not in camp: camp["lista_espera"] = []
        
        try: max_p = int(camp.get("max_participantes", 12))
        except: max_p = 12
            
        if len(camp["inscritos"]) < max_p:
            camp["inscritos"].append(u_id)
            flash("Inscrição confirmada!", "success")
        else:
            camp["lista_espera"].append(u_id)
            flash("Você entrou na lista de espera.", "warning")
        save_camp(camp)
    return redirect(url_for("detalhe_campeonato", id=id))

@app.route("/cancelar_inscricao/<id>")
@login_required
def cancelar_inscricao(id):
    camp = next((c for c in get_camps() if c["id"] == id), None)
    if not camp: return redirect(url_for("campeonatos"))
    
    u_id = session["user_id"]
    if u_id in camp.get("inscritos", []):
        camp["inscritos"].remove(u_id)
        if camp.get("lista_espera"):
            promovido = camp["lista_espera"].pop(0)
            camp["inscritos"].append(promovido)
        flash("Inscrição cancelada.", "info")
    elif u_id in camp.get("lista_espera", []):
        camp["lista_espera"].remove(u_id)
        flash("Removido da lista de espera.", "info")
        
    save_camp(camp)
    return redirect(url_for("detalhe_campeonato", id=id))

# --- ADMIN ---
@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin/dashboard.html", camps=get_camps(), users_count=len(get_users()))

@app.route("/admin/usuarios")
@admin_required
def admin_usuarios():
    return render_template("admin/usuarios.html", users=get_users())

@app.route("/admin/usuarios/promover/<id>")
@admin_required
def admin_promover(id):
    user = next((u for u in get_users() if u["id"] == id), None)
    if user:
        user["role"] = "admin"
        save_user(user)
        flash(f"{user['nome']} agora é Admin!", "success")
    return redirect(url_for("admin_usuarios"))

@app.route("/admin/usuarios/excluir/<id>")
@admin_required
def admin_excluir_usuario(id):
    if id == session["user_id"]:
        flash("Não pode excluir a si mesmo.", "danger")
    elif DB_CONNECTED:
        db.users.delete_one({"id": id})
        flash("Usuário excluído.", "info")
    return redirect(url_for("admin_usuarios"))

@app.route("/admin/campeonatos/novo", methods=["GET", "POST"])
@admin_required
def admin_novo_camp():
    if request.method == "POST":
        new_camp = {
            "id": str(uuid.uuid4()),
            "nome": request.form.get("nome", "Novo Torneio"),
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

if __name__ == "__main__":
    app.run()
