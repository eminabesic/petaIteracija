import json
import configparser
from flask import Flask, render_template, request
import mysql.connector
 
config = configparser.ConfigParser()
config.read("config.ini")
dbconfig = config["database"]
 

app = Flask(__name__)
 
cnxpool = mysql.connector.pooling.MySQLConnectionPool(
    host=dbconfig["host"],
    user=dbconfig["username"],
    password=dbconfig["password"],
    database=dbconfig["database"],
    port=int(dbconfig["port"])
)
 
# json
@app.route("/json")
def get_json():
    lista_studijskog_programa = []
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as sp_cur:
            sp_cur.execute(
                "select sp.sifra_studijskog_programa, sp.naziv_studijskog_programa from studijski_program as sp order by sp.sifra_studijskog_programa"
            )
            lista_podataka = sp_cur.fetchall()
            json_data = json.dumps(lista_podataka, indent=4)
           
            return json_data
            

 
 
@app.route("/lista_predmeta_studijskog_programa.html", methods=['POST', 'GET'])
def get_lista_predmeta_studijskog_programa_html():
    lista_predmeta_studijskog_programa = []
    with cnxpool.get_connection() as cnx:
        with cnx.cursor() as sp_cur:
            sp_cur.execute(
                "select sp.naziv_studijskog_programa, p.naziv_predmeta from studijski_program sp join predmeti_za_studijski_program pp ON sp.sifra_studijskog_programa = pp.sifra_studijskog_programa join predmet p ON pp.sifra_predmeta = p.sifra_predmeta")
 
            lista_predmeta_studijskog_programa = sp_cur.fetchall()
 
    return render_template("lista_predmeta_studijskog_programa.html", lista_predmeta=lista_predmeta_studijskog_programa)


@app.route("/submit", methods=['POST', 'GET'])
def get_submit():
    if request.method == 'POST':
        sifra_godine = request.form['sifra_godine']
        naziv_godine = request.form['naziv_godine']

        with cnxpool.get_connection() as cnx:
            with cnx.cursor() as sp_cur:
                sp_cur.execute("INSERT INTO akademska_godina (sifra_godine, naziv_godine) VALUES (%s, %s)",(sifra_godine, naziv_godine))
                cnx.commit() 
    return render_template("submit.html")  