import configparser
from flask import Flask, render_template
import mysql.connector

config = configparser.ConfigParser()
config.read("config.ini")
dbconfig = config["database"]

#mogu svoje ime staviti aplikacije ali ovako on to radi automatski
app = Flask(__name__)

cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    host = dbconfig["host"],
    user = dbconfig["user"],
    password = dbconfig["password"],
    database = dbconfig["database"],
    port = int(dbconfig["port"]),
)


@app.get("/studijski_program")
def get_studijski_program():
    lista_studijskog_programa=[]
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as sp_cur:
            sp_cur.execute(
                "select" + "sp.sifra_studijskog_programa" + "sp.naziv_studijskog_programa"
                "from studijski_program as sp" + "order by sp.sifra_studijskog_programa")
            lista_studijskog_programa=sp_cur.fetchall()
#render je ugrađeni template za web stranice
    return render_template("lista_studijskog_programa.html", lista_podataka=lista_studijskog_programa)


@app.route("/lista_predmeta_studijskog_programa.html")
def get_lista_predmeta_studijskog_programa_html():

    lista_predmeta_studijskog_programa = []
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as sp_cur:
            sp_cur.execute(
                "select"+"sp.naziv_studijskog_programa"+ "p.naziv_predmeta" +"from studijski_program sp"+
                 "join predmeti_za_studijski_program pp ON sp.sifra_studijskog_programa = pp.sifra_studijskog_programa"+
                "join predmet p ON pp.sifra_predmeta = p.sifra_predmeta")

            lista_predmeta_studijskog_programa = sp_cur.fetchall()

    return render_template("lista_predmeta_studijskog_programa", lista_predmeta=lista_predmeta_studijskog_programa)


