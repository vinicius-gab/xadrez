from flask import Flask, render_template, request, redirect, url_for, flash, session
from utils import ConectarBD, InserirAlterarRemover, login, get_info, cad_cont_id, busca_cards, ajeitar_capa, buscar_conteudos
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('SECRET_KEY')

@app.route("/")
def index():
    return render_template("inicio.html")

# -------- Favoritar um conteúdo --------
@app.route('/favoritar/<int:conteudo_id>', methods=['POST'])
def favoritar(conteudo_id):
    if 'id' not in session:
        flash('Você precisa fazer login primeiro.', 'error')
        return redirect(url_for('login_usuario'))

    id_user = session['id']

    conexao = ConectarBD()
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT IGNORE INTO favorito (ID_Usuario, ID_Conteudo) VALUES (%s, %s)",
        (id_user, conteudo_id)
    )
    conexao.commit()

    cursor.close()
    conexao.close()

    return redirect(url_for(''))  # volta para a página da 

@app.route('/desfavoritar/<int:conteudo_id>', methods=['POST'])
def desfavoritar(conteudo_id):
    if 'id' not in session:
        flash('Você precisa fazer login primeiro.', 'error')
        return redirect(url_for('login_usuario'))

    id_user = session['id']

    conexao = ConectarBD()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM favorito WHERE ID_Usuario = %s AND ID_Conteudo = %s;",
        (id_user, conteudo_id)
    )
    conexao.commit()

    cursor.close()
    conexao.close()

    return redirect(url_for(''))  # volta para a página da 


# -------- Página de favoritos --------
@app.route('/favoritos')
def pagina_favoritos():
    if 'id' not in session:
        flash('Você precisa fazer login primeiro.', 'error')
        return redirect(url_for('login_simples'))

    id_user = session['id']
    nome_user = session['nome']

    conexao = ConectarBD()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.ID_Conteudo, c.Titulo, c.Sinopse, c.URL_Arquivo, c.ID_Categoria, c.Capa
        FROM conteudo c
        INNER JOIN favorito f ON c.ID_Conteudo = f.ID_Conteudo
        WHERE f.ID_Usuario = %s
    """, (id_user,))
    favoritos = cursor.fetchall()
    cursor.close()
    conexao.close()

    ajeitar_capa(favoritos)

    return render_template('favoritos.html', favoritos=favoritos, nome=nome_user)


@app.route('/login', methods=['GET', 'POST'])
def login_usuario():
    if request.method == 'POST':
        email = request.form['usuario']
        senha = request.form['senha']

        conexao = ConectarBD()
        cursor = conexao.cursor(dictionary=True, buffered=True)

        cursor.execute(
            "SELECT * FROM usuario WHERE email = %s AND senha = %s",
            (email, senha)
        )

        usuario = cursor.fetchone()

        cursor.close()
        conexao.close()

        if usuario:
            session['id_usuario'] = usuario['idUsuario']
            session['nome_usuario'] = usuario['Nome']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'danger')

    return render_template('login_usuario.html')



@app.route('/cadastro-usuario', methods=['GET','POST'])
def cadastro_usuario():
    if request.method == 'POST':
        nome = request.form['nome_user']
        senha = request.form['Senha']
        email = request.form['Email_do_User']

        if email == '':
            email = None
        
        sql = 'INSERT INTO usuario (Nome, Senha, Email) \
            VALUES (%s, %s, %s)'
        
        dados = (nome,  senha, email)

        InserirAlterarRemover(sql, dados)

        return redirect(url_for('login_usuario'))
    return render_template('cadastro_user.html')

@app.route('/cadastro_abertura', methods=['GET', 'POST'])
def cadastro_abertura():

    # 🔒 BLOQUEIO SE NÃO ESTIVER LOGADO
    if 'id_usuario' not in session:
        flash('Você precisa estar logado para acessar essa página.', 'warning')
        return redirect(url_for('login_usuario'))

    if request.method == 'POST':
        nome = request.form['nome']
        estilo = request.form['estilo']
        descricao = request.form['descricao']
        eco = request.form['eco']
        tipo = request.form['tipo']
        nivel = request.form['nivel']

        con = ConectarBD()
        cursor = con.cursor()

        cursor.execute(
            """
            INSERT INTO abertura
            (Nome, estilo, Descricao, eco, tipo, nivel)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nome, estilo, descricao, eco, tipo, nivel)
        )

        con.commit()

        cursor.close()
        con.close()


        flash('Abertura cadastrada com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template(
        'cadastro_ab.html',
        nome=session.get('nome_usuario')
    )
