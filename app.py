from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import csv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

app = Flask(__name__)

# ------------------------
# CONFIGURACIÓN DE ARCHIVOS
# ------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_DIR = os.path.join(BASE_DIR, "datos")
DB_DIR = os.path.join(BASE_DIR, "database")

# ------------------------
# CONFIGURACIÓN DE SQLITE
# ------------------------
engine = create_engine(f"sqlite:///{os.path.join(DB_DIR, 'usuarios.db')}", echo=True)
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String)
    email = Column(String)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# ------------------------
# RUTAS PRINCIPALES
# ------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")

@app.route("/guardar", methods=["POST"])
def guardar():
    nombre = request.form["nombre"]
    email = request.form["email"]

    # Guardar en TXT
    with open(os.path.join(DATOS_DIR, "datos.txt"), "a", encoding="utf-8") as f:
        f.write(f"{nombre}, {email}\n")

    # Guardar en JSON
    datos_json = {"nombre": nombre, "email": email}
    with open(os.path.join(DATOS_DIR, "datos.json"), "a", encoding="utf-8") as f:
        f.write(json.dumps(datos_json) + "\n")

    # Guardar en CSV
    with open(os.path.join(DATOS_DIR, "datos.csv"), "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nombre, email])

    # Guardar en SQLite
    nuevo_usuario = Usuario(nombre=nombre, email=email)
    session.add(nuevo_usuario)
    session.commit()

    return redirect(url_for("resultado", nombre=nombre, email=email))

@app.route("/resultado")
def resultado():
    nombre = request.args.get("nombre")
    email = request.args.get("email")
    return render_template("resultado.html", nombre=nombre, email=email)

# ------------------------
# RUTAS PARA LEER DATOS
# ------------------------
@app.route("/leer/txt")
def leer_txt():
    with open(os.path.join(DATOS_DIR, "datos.txt"), "r", encoding="utf-8") as f:
        lineas = f.readlines()
    return "<br>".join(lineas)

@app.route("/leer/json")
def leer_json():
    datos = []
    with open(os.path.join(DATOS_DIR, "datos.json"), "r", encoding="utf-8") as f:
        for linea in f:
            datos.append(json.loads(linea))
    return jsonify(datos)

@app.route("/leer/csv")
def leer_csv():
    datos = []
    with open(os.path.join(DATOS_DIR, "datos.csv"), "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            datos.append(row)
    return jsonify(datos)

@app.route("/leer/sqlite")
def leer_sqlite():
    usuarios = session.query(Usuario).all()
    datos = [{"id": u.id, "nombre": u.nombre, "email": u.email} for u in usuarios]
    return jsonify(datos)

# ------------------------
# MAIN
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)
