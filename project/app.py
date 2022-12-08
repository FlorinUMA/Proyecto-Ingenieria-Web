from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite://", 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db' # 3 barras porque es un path relativo. SI fuera absoluto, serían 4 barras
with app.app_context():
    db = SQLAlchemy(app)

class Usuarios(db.Model):
    __tablename__ = 'Usuarios'
    usuario = db.Column(db.String(50), primary_key=True)
    contrasenya = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(10), nullable=False)
    def __repr__(self):
        return 'Usuario %r' % self.usuario

class Medicos(db.Model):
    __tablename__ = 'Medicos'
    usuarioMedico = db.Column(db.String(50), db.ForeignKey(Usuarios.usuario), primary_key=True)
    def __repr__(self):
        return 'Medico %r' % self.usuarioMedico

class Tecnicos(db.Model):
    __tablename__ = 'Tecnicos'
    usuarioTecnico = db.Column(db.String(50), db.ForeignKey(Usuarios.usuario), primary_key=True)
    def __repr__(self):
        return 'Tecnico %r' % self.usuarioMedico

class Estados(db.Model):
    __tablename__ = 'Estados'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(300), nullable = True)
    def __repr__(self):
        return 'Estado %r' % self.descripcion

class Robots(db.Model):
    __tablename__ = 'Robots'
    id = db.Column(db.Integer, primary_key=True)
    estadoId = db.Column(db.Integer, db.ForeignKey(Estados.id))
    def __repr__(self):
        return 'Robot %r' % self.id

class Tareas(db.Model):
    __tablename__ = 'tareas'
    nombre = db.Column(db.String(100), nullable=False)
    param0 = db.Column(db.String(100), nullable = True)
    param1 = db.Column(db.String(100), nullable = True)
    param2 = db.Column(db.String(100), nullable = True) 
    param3 = db.Column(db.String(100), nullable = True) 
    param4 = db.Column(db.String(100), nullable = True) 
    param5 = db.Column(db.String(100), nullable = True) 
    param6 = db.Column(db.String(100), nullable = True) 
    param7 = db.Column(db.String(100), nullable = True) 
    param8 = db.Column(db.String(100), nullable = True) 
    param9 = db.Column(db.String(100), nullable = True)

    rob_Id = db.Column(db.Integer, db.ForeignKey(Robots.id), primary_key=True)
    asignaTecnico = db.Column(db.String(50), db.ForeignKey(Tecnicos.usuarioTecnico))
    ejecutaMedico = db.Column(db.String(50), db.ForeignKey(Medicos.usuarioMedico))
    def __repr__(self):
        return 'Tarea %r' % self.nombre + " " + self.rob_Id
    

class Historial(db.Model):
    __tablename__ = 'historial'
    idEstado = db.Column(db.Integer, db.ForeignKey(Estados.id), primary_key=True)
    idTarea = db.Column(db.Integer, db.ForeignKey(Tareas.rob_Id), primary_key=True)
    def __repr__(self):
        return 'Historial %r' % self.idEstado + " " + self.idTarea


def inserta_usuarios():
    medico1 = Usuarios(usuario="medico1", contrasenya="12345", rol="medico")
    medico2 = Usuarios(usuario="medico2", contrasenya="11111", rol="medico")
    tecnico1 = Usuarios(usuario="tecnico1", contrasenya="0000", rol="tecnico")
    tecnico2 = Usuarios(usuario="tecnico2", contrasenya="soy_tecnico", rol="tecnico")

    db.session.add(medico1)
    db.session.commit()
    db.session.add(medico2)
    db.session.commit()
    db.session.add(tecnico1)
    db.session.commit()
    db.session.add(tecnico2)
    db.session.commit()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.jinja")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # print("post received")
        user = request.form.get("user")
        passw = request.form.get("password")

        query = Usuario.query.first()
        print(query.contrasenya)


        return redirect("/")
    else:
        return render_template("login.jinja")

# @app.route("/asig-tarea", methods=["POST"])
# def asig_tarea():
#     pass

if __name__ == "__main__":
    app.app_context().push()
    db.drop_all()
    db.create_all()
    inserta_usuarios()
    app.run(port=5000, debug=True)