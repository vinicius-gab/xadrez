from mysql.connector import (connection)
from dotenv import load_dotenv
import os

load_dotenv()

def ConectarBD():
    cnx = connection.MySQLConnection(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv("DB_PORT"),
                database=os.getenv('DB_NAME')

        )
    
    return cnx

def InserirAlterarRemover(sql, dados):
    cnx = ConectarBD()

    cursor = cnx.cursor()

    cursor.execute(sql, dados)
    cnx.commit()

    cnx.close()

def login(email, senha):
    cnx = ConectarBD()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute(
        'SELECT idUsuario, Nome FROM usuario WHERE Email = %s AND Senha = %s',
        (email, senha)
    )

    resultado = cursor.fetchone()
    cnx.close()
    return resultado


def get_info(id):
    cnx = ConectarBD()

    cursor = cnx.cursor(dictionary=True)

    cursor.execute('select * from usuario where idUsuario  = %s', (id))

    resultado = cursor.fetchone()

    cnx.close()

    return resultado

def cad_cont_id(sql, dados):
    cnx = ConectarBD()
    cursor = cnx.cursor()

    cursor.execute(sql, dados)
    cnx.commit()

    last_id = cursor.lastrowid  # pega o ID da última linha inserida

    cnx.close()

    return last_id

def busca_cards(id_categoria, limite):
    cnx = ConectarBD()

    cursor = cnx.cursor(dictionary=True)

    sql = 'select ID_Conteudo, Nome, Sinopse, URL_Arquivo from conteudo where ID_Categoria = %s'
    dados = (id_categoria,)

    if limite != None:
        sql += ' limit %s'
        dados = id_categoria, limite

    cursor.execute(sql, dados)

    resultado = cursor.fetchall()

    cnx.close()

    return resultado

def ajeitar_capa(conteudos):

    upload_capas = os.path.join('static', 'assets', 'capas')

    for cont in conteudos:
        id_conteudo = cont['ID_Conteudo']
        capa_path = None

        for ext in ['.jpg', '.jpeg', '.png', '.webp', '.jfif']:
            caminho = os.path.join(upload_capas, f"{id_conteudo}{ext}")
            if os.path.exists(caminho):
                capa_path = f"assets/capas/{id_conteudo}{ext}"
                break

        if not capa_path:
            capa_path = "assets/img/no_image.jpg"

        cont['CapaPath'] = capa_path  # adiciona o caminho no próprio dicionário

def buscar_conteudos(termo):
    cnx = ConectarBD()
    cursor = cnx.cursor(dictionary=True)

    sql = """
        SELECT *,
            CASE
                WHEN Titulo LIKE %s THEN 3
                WHEN Autor LIKE %s THEN 2
                WHEN Sinopse LIKE %s THEN 1
                ELSE 0
            END AS relevancia
        FROM conteudo
        WHERE Titulo LIKE %s OR Autor LIKE %s OR Sinopse LIKE %s
        ORDER BY relevancia DESC, Data_Inclusao DESC;
    """

    
    termo_busca = f"%{termo}%"
    cursor.execute(sql, (termo_busca, termo_busca, termo_busca, termo_busca, termo_busca, termo_busca))

    resultados = cursor.fetchall()

    cnx.close()
    return resultados