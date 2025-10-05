from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user
import os, json, csv

# --------------------- Configuración ---------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret_key'

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database', 'app.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345678@localhost/mi_proyecto'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# --------------------- Modelos ---------------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))

    def set_password(self, password):
        self.password = password  # En producción usa hashing!

    def check_password(self, password):
        return self.password == password

    # Para Flask-Login
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)

class ProductoModel(db.Model):
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    precio = db.Column(db.Float)
    stock = db.Column(db.Integer)

# --------------------- Inventario en memoria ---------------------
class Producto:
    def __init__(self, id=None, nombre='', cantidad=0, precio=0.0):
        self.id = id
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

class Inventario:
    def __init__(self):
        self.productos = {}
    def add_producto(self, p: Producto, save_db=True):
        self.productos[p.id] = p
    def update_producto(self, id, nombre, cantidad, precio):
        if id in self.productos:
            self.productos[id].nombre = nombre
            self.productos[id].cantidad = cantidad
            self.productos[id].precio = precio
    def eliminar_producto(self, id):
        if id in self.productos:
            del self.productos[id]
    def mostrar_todos(self):
        return list(self.productos.values())

inventario = Inventario()

# --------------------- Inicializar DB y cargar inventario ---------------------
with app.app_context():
    db.create_all()
    productos_db = ProductoModel.query.all()
    for p in productos_db:
        if p.id_producto not in inventario.productos:
            prod = Producto(id=p.id_producto, nombre=p.nombre, cantidad=p.stock, precio=p.precio)
            inventario.add_producto(prod, save_db=False)

# --------------------- Login Manager ---------------------
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --------------------- Rutas ---------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f'Bienvenido, {nombre}!'

# Rutas CRUD Productos
@app.route('/productos')
def listar_productos():
    productos = inventario.mostrar_todos()
    return render_template('productos.html', productos=productos)

@app.route('/producto/nuevo', methods=['GET','POST'])
@login_required
def crear_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        # Guardar en DB
        p_model = ProductoModel(nombre=nombre, precio=precio, stock=cantidad)
        db.session.add(p_model)
        db.session.commit()
        # Guardar en inventario en memoria
        prod = Producto(id=p_model.id_producto, nombre=nombre, cantidad=cantidad, precio=precio)
        inventario.add_producto(prod, save_db=False)
        flash('Producto creado')
        return redirect(url_for('listar_productos'))
    return render_template('formulario.html', accion='Crear')

@app.route('/producto/editar/<int:id>', methods=['GET','POST'])
@login_required
def editar_producto(id):
    producto = inventario.productos.get(id)
    if request.method == 'POST':
        nombre = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        inventario.update_producto(id, nombre, cantidad, precio)
        p_db = ProductoModel.query.get(id)
        if p_db:
            p_db.nombre = nombre
            p_db.stock = cantidad
            p_db.precio = precio
            db.session.commit()
        flash('Producto actualizado')
        return redirect(url_for('listar_productos'))
    return render_template('formulario.html', accion='Editar', producto=producto)

@app.route('/producto/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    inventario.eliminar_producto(id)
    p_db = ProductoModel.query.get(id)
    if p_db:
        db.session.delete(p_db)
        db.session.commit()
    flash('Producto eliminado')
    return redirect(url_for('listar_productos'))

# --------------------- Autenticación ---------------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        if Usuario.query.filter_by(email=email).first():
            flash('Email ya registrado')
            return redirect(url_for('register'))
        user = Usuario(nombre=nombre, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Usuario registrado')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usr = Usuario.query.filter_by(email=email).first()
        if usr and usr.check_password(password):
            login_user(usr)
            flash('Sesión iniciada')
            return redirect(url_for('index'))
        flash('Credenciales inválidas')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada')
    return redirect(url_for('index'))

@app.route('/usuarios')
@login_required
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

if __name__ == '__main__':
    app.run(debug=True)