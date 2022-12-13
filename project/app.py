from flask import Flask, render_template, redirect, flash, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, and_, select, update
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)


app = Flask(__name__)


# ======= CREACIÓN DE LA BASE DE DATOS =======


app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///hospital.db"  # 3 barras porque es un path relativo. SI fuera absoluto, serían 4 barras
with app.app_context():
    db = SQLAlchemy(app)


class Usuarios(db.Model):
    __tablename__ = "Usuarios"
    usuario = db.Column(db.String(50), primary_key=True)
    contrasenya = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return "Usuarios %r" % self.usuario


class Medicos(db.Model):
    __tablename__ = "Medicos"
    usuarioMedico = db.Column(
        db.String(50), db.ForeignKey(Usuarios.usuario), primary_key=True
    )

    def __repr__(self):
        return "Medico %r" % self.usuarioMedico


class Tecnicos(db.Model):
    __tablename__ = "Tecnicos"
    usuarioTecnico = db.Column(
        db.String(50), db.ForeignKey(Usuarios.usuario), primary_key=True
    )

    def __repr__(self):
        return "Tecnico %r" % self.usuarioMedico


class Estados(db.Model):
    __tablename__ = "Estados"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    descripcion = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return "Estado %r" % self.descripcion


class Robots(db.Model):
    __tablename__ = "Robots"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=True)

    def __repr__(self):
        return "Robot %r" % self.id


class Tareas(db.Model):
    __tablename__ = "tareas"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    param0 = db.Column(db.String(100), nullable=True)
    param1 = db.Column(db.String(100), nullable=True)
    param2 = db.Column(db.String(100), nullable=True)
    param3 = db.Column(db.String(100), nullable=True)
    param4 = db.Column(db.String(100), nullable=True)
    param5 = db.Column(db.String(100), nullable=True)
    param6 = db.Column(db.String(100), nullable=True)
    param7 = db.Column(db.String(100), nullable=True)
    param8 = db.Column(db.String(100), nullable=True)
    param9 = db.Column(db.String(100), nullable=True)

    estado_id = db.Column(db.Integer, db.ForeignKey(Estados.id), nullable=False)
    rob_Id = db.Column(db.Integer, db.ForeignKey(Robots.id), nullable=True)
    asignaTecnico = db.Column(
        db.String(50), db.ForeignKey(Tecnicos.usuarioTecnico), nullable=False
    )
    ejecutaMedico = db.Column(
        db.String(50), db.ForeignKey(Medicos.usuarioMedico), nullable=True
    )

    def __repr__(self):
        return (
            "Tarea %r" % self.nombre
            + " "
            + str(self.rob_Id)
            + " "
            + str(self.estado_id)
        )


class Historial(db.Model):
    __tablename__ = "historial"
    idEstado = db.Column(db.Integer, db.ForeignKey(Estados.id), primary_key=True)
    idTarea = db.Column(db.Integer, db.ForeignKey(Tareas.rob_Id), primary_key=True)

    def __repr__(self):
        return "Historial %r" % self.idEstado + " " + self.idTarea


# ======= CONTROL DE ERRORES =======


@app.errorhandler(404)
def error404(err):
    return render_template("error404.jinja")


# ======= FILTROS =======


@app.template_filter("muestraEstado")
def searchStatus(estado_id):
    out = Estados.query.with_entities(Estados).filter(Estados.id == estado_id).one()
    return out.nombre

@app.template_filter("muestraRobot")
def searchRobot(robot_id):
    try:
        out = Robots.query.with_entities(Robots).filter(Robots.id == robot_id).one()
        return out.nombre
    except:
        return ""


@app.template_filter("buscaTareas")
def searchTask(robot_id, tareas):
    out = []
    for tarea in tareas:
        if tarea.rob_Id == robot_id:
            out.append(tarea.nombre)
    return ", ".join(out)


# ======= WEBPAGE ENDPOINTS =======


@app.route("/", methods=["GET"])
def index():
    user = request.args.get("user")
    if user != None :
        try:
            rol = Usuarios.query.with_entities(Usuarios.rol).filter(Usuarios.usuario == user).one()[0]
            if rol == "medico":
                return render_template("index.jinja", user=user, ismedico=True, istecnico=False)
            elif rol == "tecnico":
                return render_template("index.jinja", user=user, ismedico=False, istecnico=True)
            else:
                return render_template("index.jinja", user=user, ismedico=False, istecnico=False)
        except:
            return render_template("index.jinja", user=user, ismedico=False, istecnico=False)

    return render_template("index.jinja", user=user, ismedico=False, istecnico=False)


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
                Usuarios.usuario == user, Usuarios.contrasenya == passw
            )

            # Ejecutamos la query
            query = db.session.execute(statement)
            # Guardamos el resultado
            result = query.one()[0]

            # ==== PLACEHOLDER PARA COMPROBAR QUE FUNCIONA [BORRAR] ======
            # print(result.usuario)
            # print(result.contrasenya)
            # print(result.rol)

            if result.rol == "medico":
                return redirect(f"/medico?user={result.usuario}")
            elif result.rol == "tecnico":
                return redirect(f"/tecnico?user={result.usuario}")
            else:
                flash(
                    "ERROR 501: El usuario no tiene un rol correcto asignado, consulte con su técnico"
                )
                return redirect("/")
        except:
            # Si no se encuentra al usuario se lanza una excepción que es controlada y se recarga la página de login esta vez mostrando un mensaje de contraseña o usuario incorrecto
            error = True
            return render_template("login.jinja", error=error)

    else:
        # Si recibe un GET se carga la página con normalidad
        return render_template("login.jinja", error=error)


@app.route("/medico", methods=["GET"])
def medico():
    user = request.args.get("user")
    print(user)
    tareas = Tareas.query.with_entities(Tareas).all()
    # id = request.args.get('id', type=int)
    # if id == None:
    #     return abort(code=404)
    return render_template("medico.jinja", user=user, tareas=tareas)


@app.route("/tecnico", methods=["GET"])
def tecnico():
    user = request.args.get("user")
    row = Robots.query.with_entities(Robots).all()
    tareas = Tareas.query.with_entities(Tareas).all()
    return render_template("tecnico.jinja", user=user, row=row, tareas=tareas)


@app.route("/robotDetails", methods=["GET"])
def robotDetails():
    user = request.args.get("user")
    id_robot = request.args.get("id", type=int)
    # print(id_robot)
    row = Tareas.query.with_entities(Tareas).filter(Tareas.rob_Id == id_robot).all()
    print(row)
    robot = Robots.query.with_entities(Robots).filter(Robots.id == id_robot).one()
    return render_template("robotDetails.jinja", user=user, row=row, robot=robot)


@app.route("/nueva-tarea", methods=["GET", "POST"])
def modifyTask():
    if request.method == "POST":
        IdTareaSeleccionada = request.args.get("idTarea")
        # if(IdTareaSeleccionada == None)
        try:
            sentencia = select(Tareas).where(Tareas.rob_Id == IdTareaSeleccionada)
            peticion = db.session.execute(sentencia)
            resultado = peticion.one()[0]
            render_template("taskEditor.jinja", idTareaExistente=IdTareaSeleccionada)
        except:
            return render_template("index.jinja")  # TODO: ¿Es esto correcto?
    else:
        # pass # ¿Sería correcto?
        return render_template("taskEditor.jinja")


# ======= API ENDPOINTS =======
# Creamos los endpoints de la API para que los robots puedan acceder al sistema


@app.route("/api/status/<id_tarea>", methods=["POST"])
def changeTaskStatus(id_tarea):
    # debe recibir un json de la forma {status:<id_status>} siendo id_status el identificador del nuevo estado
    estado = request.get_json()["status"]

    try:
        db.session.query(Tareas).filter(Tareas.id == int(id_tarea)).update(
            {Tareas.estado_id: int(estado)}, synchronize_session=False
        )
        db.session.commit()
        return jsonify({"statusCode": 200, "message": "Task status updated"})
    except:
        return jsonify({"statusCode": 400, "message": "Bad request"})


# ======= FUNCIONES DE INSERCIÓN DE DATOS =======


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
    robot1 = Robots(id=122, nombre="XLR8")
    robot2 = Robots(id=123, nombre="C3PO")
    robot3 = Robots(id=124, nombre="R2D2")
    robot4 = Robots(id=125, nombre="GR0GU")

    db.session.add(robot1)
    db.session.commit()
    db.session.add(robot2)
    db.session.commit()
    db.session.add(robot3)
    db.session.commit()
    db.session.add(robot4)
    db.session.commit()


def inserta_subclases():
    tecnico1 = Tecnicos(usuarioTecnico="tecnico1")
    tecnico2 = Tecnicos(usuarioTecnico="tecnico2")
    medico1 = Medicos(usuarioMedico="medico1")
    medico2 = Medicos(usuarioMedico="medico2")

    db.session.add(tecnico1)
    db.session.commit()
    db.session.add(tecnico2)
    db.session.commit()
    db.session.add(medico1)
    db.session.commit()
    db.session.add(medico2)
    db.session.commit()


def inserta_estados():
    estado0 = Estados(id=0, nombre="Sin asignar")
    estado1 = Estados(id=1, nombre="En espera")
    estado2 = Estados(id=2, nombre="De camino", descripcion="De camino a la tarea")
    estado3 = Estados(id=3, nombre="En proceso", descripcion="Realizando la tarea")
    estado4 = Estados(id=4, nombre="Terminado", descripcion="Tarea terminada")

    db.session.add(estado0)
    db.session.commit()
    db.session.add(estado1)
    db.session.commit()
    db.session.add(estado2)
    db.session.commit()
    db.session.add(estado3)
    db.session.commit()
    db.session.add(estado4)
    db.session.commit()


def inserta_tareas():
    tarea1 = Tareas(
        id=1,
        nombre="Limpieza",
        rob_Id=122,
        estado_id=1,
        asignaTecnico="tecnico1",
        param0="DURACION=20",
    )
    tarea2 = Tareas(
        id=2,
        nombre="Videollamada",
        rob_Id=122,
        estado_id=2,
        asignaTecnico="tecnico2",
        param0="NOMBRE_PROGRAMA=Skype",
    )
    tarea3 = Tareas(
        id=3, nombre="Aspirar", rob_Id=124, estado_id=2, asignaTecnico="tecnico1"
    )
    tarea4 = Tareas(
        id=4,
        nombre="Desinfectar",
        rob_Id=125,
        estado_id=3,
        asignaTecnico="tecnico1",
        ejecutaMedico="medico1",
    )

    db.session.add(tarea1)
    db.session.commit()
    db.session.add(tarea2)
    db.session.commit()
    db.session.add(tarea3)
    db.session.commit()
    db.session.add(tarea4)
    db.session.commit()


# ======= INICIO DE LA APLICACIÓN =======


if __name__ == "__main__":
    app.app_context().push()
    db.drop_all()
    db.create_all()
    inserta_usuarios()
    inserta_estados()
    inserta_robots()
    inserta_subclases()
    inserta_tareas()

    app.run(port=5000, debug=True)
