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

def ajeitar_tabuleiro(aberturas):
    for ab in aberturas:
        if ab['img_tabuleiro']:
            ab['TabuleiroPath'] = f"tabuleiros/{ab['img_tabuleiro']}"
        else:
            ab['TabuleiroPath'] = "assets/img/no_image.jpg"
            
def buscar_aberturas(termo):
    con = ConectarBD()
    cursor = con.cursor(dictionary=True)

    sql = """
        SELECT
            idAbertura,
            Nome,
            Descricao,
            estilo,
            eco,
            tipo,
            nivel,
            img_tabuleiro
        FROM abertura
        WHERE
            Nome LIKE %s OR
            Descricao LIKE %s OR
            estilo LIKE %s OR
            eco LIKE %s OR
            tipo LIKE %s OR
            nivel LIKE %s
    """

    like = f"%{termo}%"
    cursor.execute(sql, (like, like, like, like, like, like))

    resultados = cursor.fetchall()

    cursor.close()
    con.close()

    return resultados