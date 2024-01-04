import json
import configparser
from flask import Flask, render_template, request, jsonify
import mysql.connector
import traceback
 
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
#dodatne rute
@app.route("/dodajUPredmetiZaStudijskiProgram", methods=['POST','GET'])
def dodajUPredmetiZaStudijskiProgram():
    try:
        data = request.get_json()
        sifra_studijskog_programa = data.get('sifra_studijskog_programa')
        predmet = data.get('predmet')

        
        cnx = cnxpool.get_connection()
        with cnx.cursor() as sp_cur:
            zahtjev = """
                INSERT INTO predmeti_za_studijski_program 
                (sifra_studijskog_programa, sifra_predmeta, sifra_semestra, tip_predmeta, broj_ETCS_bodova) 
                VALUES (%s, %s, %s, %s, %s)
            """
            VALUES = (
                sifra_studijskog_programa,
                predmet.get('sifra_predmeta'),
                predmet.get('sifra_semestra'),
                predmet.get('tip_predmeta'),
                predmet.get('broj_ETCS_bodova')
            )
            sp_cur.execute(zahtjev, VALUES)

        cnx.commit()

    except Exception as e:
        print(f"Greška: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': 'Ima greska'}), 500


    return jsonify({'status': 'success', 'message': 'Podaci su  uneseni.'})
# testiranje rute
url = 'http://localhost:5000/dodajUPredmetiZaStudijskiProgram'

data = {
    'sifra_studijskog_programa': '1',
    'predmet': {
        'sifra_predmeta': '15',
        'sifra_semestra': '3',
        'tip_predmeta': 'obavezni',
        'broj_ETCS_bodova': '6'
    }
}

zaglavlje = {'Content-Type': 'application/json'}

odgovor = request.post(url, json=data, headers=zaglavlje)