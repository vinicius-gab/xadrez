from flask import Flask, render_template, request, redirect, url_for, flash, session
from utils import ConectarBD, InserirAlterarRemover, login, get_info, cad_cont_id, busca_cards, ajeitar_tabuleiro, buscar_conteudos
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

@app.route('/aberturas')
def pagina_aberturas():
    con = ConectarBD()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM abertura")
    aberturas = cursor.fetchall()

    favoritos_ids = []
    if 'id_usuario' in session:
        cursor.execute(
            "SELECT id_abertura FROM favorito WHERE id_user = %s",
            (session['id_usuario'],)
        )
        favoritos_ids = [f['id_abertura'] for f in cursor.fetchall()]

    cursor.close()
    con.close()

    return render_template(
        'aberturas.html',
        aberturas=aberturas,
        favoritos_ids=favoritos_ids,
        nome=session.get('nome_usuario')
    )





# -------- Página de favoritos --------
@app.route('/favoritos')
def pagina_favoritos():
    if 'id' not in session:
        flash('Você precisa fazer login primeiro.', 'error')
        return redirect(url_for('login_usuario'))

    id_user = session['id']
    nome_user = session['nome']

    conexao = ConectarBD()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("""
    SELECT 
        ab.idAbertura,
        ab.Nome,
        ab.Descricao,
        ab.estilo,
        ab.eco,
        ab.nivel,
        ab.tipo,
        ab.img_tabuleiro
    FROM abertura ab
    INNER JOIN favorito f 
        ON ab.idAbertura = f.id_abertura
    WHERE f.id_user = %s
    """, (id_user,))

    favoritos = cursor.fetchall()
    cursor.close()
    conexao.close()

    ajeitar_tabuleiro(favoritos)


    return render_template('favoritos.html', favoritos=favoritos, nome=nome_user)

@app.route('/desfavoritar/<int:id_abertura>', methods=['POST'])
def desfavoritar_abertura(id_abertura):
    if 'id_usuario' not in session:
        return redirect(url_for('login_usuario'))

    id_user = session['id_usuario']

    con = ConectarBD()
    cursor = con.cursor()

    cursor.execute(
        "DELETE FROM favorito WHERE id_user = %s AND id_abertura = %s",
        (id_user, id_abertura)
    )
    con.commit()

    cursor.close()
    con.close()

    return redirect(request.referrer)

@app.route('/favoritar/<int:id_abertura>', methods=['POST'])
def favoritar_abertura(id_abertura):
    if 'id_usuario' not in session:
        flash('Faça login para favoritar.', 'warning')
        return redirect(url_for('login_usuario'))

    id_user = session['id_usuario']

    con = ConectarBD()
    cursor = con.cursor()

    # evita duplicar favorito
    cursor.execute(
        "SELECT 1 FROM favorito WHERE id_user = %s AND id_abertura = %s",
        (id_user, id_abertura)
    )

    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO favorito (id_user, id_abertura) VALUES (%s, %s)",
            (id_user, id_abertura)
        )
        con.commit()

    cursor.close()
    con.close()

    return redirect(request.referrer)

@app.route('/login', methods=['GET', 'POST'])
def login_usuario():
    if request.method == 'POST':
        email = request.form['usuario']
        senha = request.form['senha']

        conexao = ConectarBD()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT idUsuario, Nome FROM usuario WHERE Email = %s AND Senha = %s",
            (email, senha)
        )

        usuario = cursor.fetchone()

        cursor.close()
        conexao.close()

        if usuario:
            # 🔑 PADRÃO ÚNICO DE SESSÃO
            session['id'] = usuario['idUsuario']
            session['nome'] = usuario['Nome']

            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'error')

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

    # 🔒 Bloqueio se não estiver logado
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

        # arquivo enviado
        img_file = request.files.get('img_tabuleiro')

        con = ConectarBD()
        cursor = con.cursor()

        # 1️⃣ Inserir sem imagem primeiro
        cursor.execute(
            """
            INSERT INTO abertura
            (Nome, estilo, Descricao, eco, tipo, nivel, img_tabuleiro)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (nome, estilo, descricao, eco, tipo, nivel, None)
        )

        con.commit()
        # pegar o ID da abertura recém-criada
        id_abertura = cursor.lastrowid

        # 2️⃣ Salvar imagem no diretório correto
        if img_file and img_file.filename:
            nome_arquivo, ext = os.path.splitext(img_file.filename)
            novo_nome = f"{id_abertura}{ext}"

            # pasta de upload
            upload_folder = os.path.join('static', 'tabuleiros')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)  # cria a pasta caso não exista

            caminho_upload = os.path.join(upload_folder, novo_nome)
            img_file.save(caminho_upload)

            # atualizar o banco com o nome do arquivo
            cursor.execute(
                "UPDATE abertura SET img_tabuleiro = %s WHERE idAbertura = %s",
                (novo_nome, id_abertura)
            )
            con.commit()

        cursor.close()
        con.close()

        flash('Abertura cadastrada com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('cadastro_ab.html', nome=session.get('nome_usuario'))
