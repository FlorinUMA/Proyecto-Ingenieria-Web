from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db' # 3 barras porque es un path relativo. SI fuera absoluto, serían 4 barras
with app.app_context():
    db = SQLAlchemy(app)

class Personal(db.Model):
    __tablename__ = 'Personal'
    usuario = db.Column(db.String(50), primary_key=True)
    contrasenya = db.Column(db.String(200), nullable=False)
    def __repr__(self):
        return 'Usuario %r' % self.usuario

class Medicos(db.Model):
    __tablename__ = 'Medicos'
    usuarioMedico = db.Column(db.String(50), db.ForeignKey(Personal.usuario), primary_key=True)
    def __repr__(self):
        return 'Medico %r' % self.usuarioMedico

class Tecnicos(db.Model):
    __tablename__ = 'Tecnicos'
    usuarioTecnico = db.Column(db.String(50), db.ForeignKey(Personal.usuario), primary_key=True)
    def __repr__(self):
        return 'Tecnico %r' % self.usuarioMedico

class Robots(db.Model):
    __tablename__ = 'Robots'
    id = db.Column(db.Integer, primary_key=True)
    def __repr__(self):
        return 'Robot %r' % self.id

class Tareas(db.Model):
    __tablename__ = 'tareas'
    nombre = db.Column(db.String(100), primary_key=True)
    rob_Id = db.Column(db.Integer, db.ForeignKey(Robots.id), primary_key=True)
    param0 = db.Column(db.String(100), nullable = True) # ¿Debería ser null o string vacío? Yo creo que null tendría más sentido
    param1 = db.Column(db.String(100), nullable = True)
    param2 = db.Column(db.String(100), nullable = True) 
    param3 = db.Column(db.String(100), nullable = True) 
    param4 = db.Column(db.String(100), nullable = True) 
    param5 = db.Column(db.String(100), nullable = True) 
    param6 = db.Column(db.String(100), nullable = True) 
    param7 = db.Column(db.String(100), nullable = True) 
    param8 = db.Column(db.String(100), nullable = True) 
    param9 = db.Column(db.String(100), nullable = True) 
    def __repr__(self):
        return 'Tarea %r' % self.nombre + " " + self.rob_Id

@app.route("/", methods=["GET"])
def index():
    return render_template("index.jinja")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print("post received")
        print(request.get_json())
        return redirect("/")
    else:
        return render_template("login.jinja")

# @app.route("/asig-tarea", methods=["POST"])
# def asig_tarea():
#     pass

if __name__ == "__main__":
    app.run(port=5000, debug=True)