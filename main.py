from flask import Flask, request, render_template, redirect, flash, url_for, session
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'AssimQueSeFaz'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logado' not in session or not session['logado']:
            flash('Você precisa estar logado para acessar esta página.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    session['logado'] = False
    return render_template('index.html')

@app.route('/adm')
@login_required
def adm():
    return render_template('admin.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Verifica se é administrador
    with open('administradores.json') as administradoresTemp:
        administradores = json.load(administradoresTemp)
        for administrador in administradores:
            if administrador['usuario'] == username and administrador['senha'] == password:
                session['logado'] = True
                return redirect(url_for('adm'))

    # Verifica se é usuário comum
    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)
        for usuario in usuarios:
            if usuario['usuario'] == username and usuario['senha'] == password:
                session['logado'] = False
                return 'login aceito'

    flash('Seu nome de usuário ou senha podem estar incorretos!', 'danger')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def registrar():
    return render_template('register.html')

@app.route('/cadastrarUsuario', methods=['POST'])
def cadastrarUsuario():
    username = request.form.get('username')
    password = request.form.get('password')
    tipo = request.form.get('tipo')
    session['logado'] = False

    if tipo == 'adm':
        with open('administradores.json', 'r') as administradoresTemp:
            administradores = json.load(administradoresTemp)

        novo_administrador = {
            "usuario": username,
            "senha": password
        }
        administradores.append(novo_administrador)

        with open('administradores.json', 'w') as gravarTemp:
            json.dump(administradores, gravarTemp, indent=4)
    else:
        with open('usuarios.json', 'r') as usuariosTemp:
            usuarios = json.load(usuariosTemp)

        novo_usuario = {
            "usuario": username,
            "senha": password,
            "tipo": "user"
        }
        usuarios.append(novo_usuario)

        with open('usuarios.json', 'w') as gravarTemp:
            json.dump(usuarios, gravarTemp, indent=4)

    flash('Usuário Cadastrado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/manage-registrations')
@login_required
def manage_registrations():
    with open('usuarios.json') as usuariosTemp:
        usuarios = json.load(usuariosTemp)
    with open('administradores.json') as administradoresTemp:
        administradores = json.load(administradoresTemp)

    total_usuarios = len(usuarios)
    total_adms = len(administradores)

    return render_template('manage_registrations.html', usuarios=usuarios, administradores=administradores, total_usuarios=total_usuarios, total_adms=total_adms)

@app.route('/delete-user/<username>', methods=['POST'])
@login_required
def delete_user(username):
    with open('usuarios.json', 'r') as usuariosTemp:
        usuarios = json.load(usuariosTemp)
    usuarios = [user for user in usuarios if user['usuario'] != username]
    with open('usuarios.json', 'w') as gravarTemp:
        json.dump(usuarios, gravarTemp, indent=4)

    with open('administradores.json', 'r') as administradoresTemp:
        administradores = json.load(administradoresTemp)
    administradores = [admin for admin in administradores if admin['usuario'] != username]
    with open('administradores.json', 'w') as gravarTemp:
        json.dump(administradores, gravarTemp, indent=4)

    flash('Usuário deletado com sucesso!', 'success')
    return redirect(url_for('manage_registrations'))

@app.route('/logout')
@login_required
def logout():
    session.pop('logado', None)
    flash('Você saiu da sua conta com sucesso.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
