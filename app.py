from flask import Flask, render_template, request, redirect, url_for, flash, session
from utils import ConectarBD, InserirAlterarRemover, login, get_info, cad_cont_id, busca_cards, ajeitar_tabuleiro, buscar_aberturas
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

# -------- Página de favoritos --------
@app.route('/favoritos')
def pagina_favoritos():
    if 'id_usuario' not in session:
        return redirect(url_for('login_usuario'))

    id_user = session['id_usuario']
    nome_user = session['Nome']


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
        INNER JOIN favoritos f 
            ON ab.idAbertura = f.id_abertura
        WHERE f.id_user = %s
    """, (id_user,))

    favoritos = cursor.fetchall()

    cursor.close()
    conexao.close()

    ajeitar_tabuleiro(favoritos)

    return render_template(
        'favoritos.html',
        favoritos=favoritos,
        nome=nome_user
    )

@app.route('/desfavoritar/<int:id_abertura>', methods=['POST'])
def desfavoritar_abertura(id_abertura):
    if 'id_usuario' not in session:
        return redirect(url_for('login_usuario'))

    id_user = session['id_usuario']

    con = ConectarBD()
    cursor = con.cursor()

    cursor.execute(
        "DELETE FROM favoritos WHERE id_user = %s AND id_abertura = %s",
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
        "SELECT 1 FROM favoritos WHERE id_user = %s AND id_abertura = %s",
        (id_user, id_abertura)
    )

    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO favoritos (id_user, id_abertura) VALUES (%s, %s)",
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
            session['id_usuario'] = usuario['idUsuario']
            session['Nome'] = usuario['Nome']

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
    if request.method == 'POST':
        nome = request.form['nome']
        estilo = request.form['estilo']
        descricao = request.form['descricao']
        eco = request.form['eco']
        tipo = request.form['tipo']
        nivel = request.form['nivel']
        img_file = request.files.get('img_tabuleiro')

        con = ConectarBD()
        cursor = con.cursor()

        cursor.execute("""
            INSERT INTO abertura
            (Nome, estilo, Descricao, eco, tipo, nivel, img_tabuleiro)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nome, estilo, descricao, eco, tipo, nivel, None))

        con.commit()
        id_abertura = cursor.lastrowid

        if img_file and img_file.filename:
            ext = os.path.splitext(img_file.filename)[1]
            novo_nome = f"{id_abertura}{ext}"

            pasta = os.path.join('static', 'tabuleiros')
            os.makedirs(pasta, exist_ok=True)

            caminho = os.path.join(pasta, novo_nome)
            img_file.save(caminho)

            cursor.execute(
                "UPDATE abertura SET img_tabuleiro = %s WHERE idAbertura = %s",
                (novo_nome, id_abertura)
            )
            con.commit()

        cursor.close()
        con.close()

        flash('Abertura cadastrada com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template(
    'cadastro_ab.html',
    nome=session.get('Nome')
    )
   
@app.route('/aberturas')
def pagina_aberturas():
    termo = request.args.get('q')  # pega o texto da pesquisa

    conexao = ConectarBD()
    cursor = conexao.cursor(dictionary=True)

    if termo:
        cursor.execute(
            """
            SELECT *
            FROM abertura
            WHERE Nome LIKE %s
               OR Descricao LIKE %s
               OR Eco LIKE %s
            """,
            (f"%{termo}%", f"%{termo}%", f"%{termo}%")
        )
    else:
        cursor.execute("SELECT * FROM abertura")

    aberturas = cursor.fetchall()

    cursor.close()
    conexao.close()

    ajeitar_tabuleiro(aberturas)

    return render_template(
        'pesquisa.html',
        aberturas=aberturas,
        nome=session.get('nome_usuario')
    )

@app.route('/abertura/<int:id_abertura>')
def abertura_detalhada(id_abertura):
    conexao = ConectarBD()
    cursor = conexao.cursor(dictionary=True)

    # Buscar abertura
    cursor.execute(
        "SELECT * FROM abertura WHERE idAbertura = %s",
        (id_abertura,)
    )
    abertura = cursor.fetchone()

    if not abertura:
        cursor.close()
        conexao.close()
        flash('Abertura não encontrada.', 'error')
        return redirect(url_for('pagina_aberturas'))

    # Buscar comentários DAQUELA abertura
    cursor.execute(
        """
        SELECT c.Texto, c.DataCriacao, u.Nome
        FROM comentario c
        INNER JOIN usuario u ON c.id_user = u.idUsuario
        WHERE c.id_abertura = %s
        ORDER BY c.DataCriacao DESC
        """,
        (id_abertura,)
    )
    comentarios = cursor.fetchall()

    cursor.close()
    conexao.close()

    ajeitar_tabuleiro([abertura])

    return render_template(
        'abertura_detalhada.html',
        abertura=abertura,
        comentarios=comentarios,
        nome=session.get('nome_usuario')
    )

@app.route('/abertura/<int:id_abertura>/comentar', methods=['POST'])
def comentar_abertura(id_abertura):
    if 'id_usuario' not in session:
        flash('Você precisa estar logado para comentar.', 'error')
        return redirect(url_for('abertura_detalhada', id_abertura=id_abertura))

    texto = request.form.get('comentario')

    if not texto:
        flash('O comentário não pode estar vazio.', 'error')
        return redirect(url_for('abertura_detalhada', id_abertura=id_abertura))

    conexao = ConectarBD()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO comentario (Texto, DataCriacao, id_user, id_abertura)
        VALUES (%s, NOW(), %s, %s)
        """,
        (texto, session['id_usuario'], id_abertura)
    )

    conexao.commit()
    cursor.close()
    conexao.close()

    flash('Comentário adicionado com sucesso!', 'success')
    return redirect(url_for('abertura_detalhada', id_abertura=id_abertura))

