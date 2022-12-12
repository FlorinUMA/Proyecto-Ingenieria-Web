from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    request
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, and_, select
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
        return 'Usuarios %r' % self.usuario

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
    asignaTecnico = db.Column(db.String(50), db.ForeignKey(Tecnicos.usuarioTecnico), nullable = False)
    ejecutaMedico = db.Column(db.String(50), db.ForeignKey(Medicos.usuarioMedico), nullable = True)
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

def inserta_robots():
    robot1 = Robots(id = 122, estadoId = 122)
    robot2 = Robots(id = 123, estadoId = 123)
    robot3 = Robots(id = 124, estadoId = 124)
    robot4 = Robots(id = 125, estadoId = 125)

    db.session.add(robot1)
    db.session.commit()
    db.session.add(robot2)
    db.session.commit()
    db.session.add(robot3)
    db.session.commit()
    db.session.add(robot4)
    db.session.commit()

def inserta_tecnicos():
    tecnico1 = Tecnicos(usuarioTecnico = "tecnico1")
    tecnico2 = Tecnicos(usuarioTecnico = "tecnico2")

    db.session.add(tecnico1)
    db.session.commit()
    db.session.add(tecnico2)
    db.session.commit()

def inserta_tareas():
    tarea1 = Tareas(nombre = "Limpieza", rob_Id = 122, asignaTecnico = "tecnico1", param0 = "DURACION=20")
    tarea2 = Tareas(nombre = "Videollamada", rob_Id = 123, asignaTecnico = "tecnico2", param0 = "NOMBRE_PROGRAMA=Skype")
    tarea3 = Tareas(nombre = "Aspirar", rob_Id = 124, asignaTecnico = "tecnico1")
    tarea4 = Tareas(nombre = "Desinfectar", rob_Id = 125, asignaTecnico = "tecnico1")

    db.session.add(tarea1)
    db.session.commit()
    db.session.add(tarea2)
    db.session.commit()
    db.session.add(tarea3)
    db.session.commit()
    db.session.add(tarea4)
    db.session.commit()

    # Corregido. He establecido las tareas tal que no hayan sido ejecutadas aún por ningún médico

@app.route("/", methods=["GET"])
def index():
    return render_template("index.jinja")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = False
    if request.method == "POST":
        # Cuando reciba un método post, recoge el usuario y la contraseña insertada
        user = request.form.get("user")
        passw = request.form.get("password")

        # Hacemos un try/except para controlar cuando no se encuentre al usuario
        try:
            # Creamos la query, seleccionando al usuario con el mismo usuario y contraseña insertado
            statement = select(Usuarios).where(
                    Usuarios.usuario == user,
                    Usuarios.contrasenya == passw
            )

            # Ejecutamos la query
            query = db.session.execute(statement)
            # Guardamos el resultado
            result = query.one()[0]

            # ==== PLACEHOLDER PARA COMPROBAR QUE FUNCIONA [BORRAR] ======
            print(result.usuario)
            print(result.contrasenya)
            print(result.rol)

            # ===== DESCOMENTAR CUANDO TENGAMOS VISTAS DE TECNICO Y MEDICO ==========
            
            # if (result.rol == "medico"):
            #     return render_template("medico.jinja")
            # elif (result.rol == "tecnico"):
            #     return render_template("medico.jinja")
            # else:
            #     flash("ERROR 501: El usuario no tiene un rol correcto asignado, consulte con su técnico")
            #     return redirect("/")

            return redirect("/")
        except:
            # Si no se encuentra al usuario se lanza una excepción que es controlada y se recarga la página de login esta vez mostrando un mensaje de contraseña o usuario incorrecto
            error=True
            return render_template("login.jinja", error=error)

    else:
        # Si recibe un GET se carga la página con normalidad
        return render_template("login.jinja", error=error)

# @app.route("/asig-tarea", methods=["POST"])
# def asig_tarea():
#     pass
@app.route("/medico", methods=["GET"])
def medico():
    return render_template("medico.jinja")

@app.route("/tecnico", methods=["GET"])
def tecnico():
    return render_template("tecnico.jinja")

@app.route("/task-editor", methods=["GET", "POST"])
def modifyTask():
    if request.method == "POST":
        IdTareaSeleccionada = request.form.get("seleccionar") # TODO: Cambiar como se obtiene el dato
        try:
            sentencia = select(Tareas).where(
                    Tareas.rob_Id == IdTareaSeleccionada
            )
            peticion = db.session.execute(sentencia)
            resultado = peticion.one()[0]
            render_template("taskEditor.jinja", idTareaExistente = IdTareaSeleccionada)
        except:
            return render_template("index.jinja") # TODO: ¿Es esto correcto?
    else:
        # pass # ¿Sería correcto?
        return render_template("taskEditor.jinja")


if __name__ == "__main__":
    app.app_context().push()
    db.drop_all()
    db.create_all()
    inserta_usuarios()
    inserta_robots()
    inserta_tecnicos()
    inserta_tareas()
    app.run(port=5000, debug=True)