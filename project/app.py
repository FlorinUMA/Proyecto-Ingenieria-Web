from flask import Flask, render_template, redirect, flash, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, and_, select, update, func
from sqlalchemy.pool import StaticPool
from uuid import uuid4
from sqlalchemy import func
import datetime

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)


app = Flask(__name__)
app.config["SECRET_KEY"] = uuid4().hex


# ======= CREACIÓN DE LA BASE DE DATOS =======


app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///hospital.db" 
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


manyRobots_manyTypes = db.Table(
    "manyRobots_manyTypes",
    db.Column("robot_id", db.ForeignKey("Robots.id")),
    db.Column("tipo_tarea", db.ForeignKey("Tipo_tarea.tipo")),
)


class Robots(db.Model):
    __tablename__ = "Robots"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), nullable=True)
    tipos_tareas = db.relationship(
        "Tipo_tarea", secondary=manyRobots_manyTypes, back_populates="robots_ids"
    )

    def __repr__(self):
        return "Robot %r" % self.id


class Tipo_tarea(db.Model):
    __tablename__ = "Tipo_tarea"
    tipo = db.Column(db.String(30), primary_key=True)

    robots_ids = db.relationship(
        "Robots", secondary=manyRobots_manyTypes, back_populates="tipos_tareas"
    )
    tareas = db.relationship("Tareas")

    def __repr__(self):
        return "Tipo tarea %r" % self.tipo


class Tareas(db.Model):
    __tablename__ = "tareas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_ejecucion = db.Column(db.DateTime(), nullable=True)
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

    tipo_tarea = db.Column(
        db.String(30), db.ForeignKey(Tipo_tarea.tipo), nullable=False
    )

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


# ======= CONTROL DE ERRORES =======


@app.errorhandler(404)
def error404(err):
    return render_template("error404.jinja")


# ======= FILTROS =======
# Dichos filtros se usarán para representar cieta información de otra manera para poder mostrarla en la Web de manera más amigable

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


@app.template_filter("mostrarNombreVariable")
def presentNameParam(variable):
    return variable.split("=")[0] if len(variable) > 0 else ""


@app.template_filter("mostrarValorVariable")
def presentValueParam(variable):
    return variable.split("=")[1] if len(variable) > 0 else ""


@app.template_filter("filtroFecha")
def filtroFecha(fecha: datetime.datetime):
    if fecha == None:
        return ""
    return fecha.strftime("%d/%m/%Y %H:%M")


# ======= WEBPAGE ENDPOINTS =======

# Definimos el endpoint inicial, es decir, la primera web que aparecerá nada más acceder el usuario a la URL
@app.route("/", methods=["GET"])
def index():
    user = request.args.get("user")
    if user != None:
        try:
            rol = (
                Usuarios.query.with_entities(Usuarios.rol)
                .filter(Usuarios.usuario == user)
                .one()[0]
            )
            if rol == "medico":
                return render_template(
                    "index.jinja", user=user, ismedico=True, istecnico=False
                )
            elif rol == "tecnico":
                return render_template(
                    "index.jinja", user=user, ismedico=False, istecnico=True
                )
            else:
                return render_template(
                    "index.jinja", user=user, ismedico=False, istecnico=False
                )
        except:
            return render_template(
                "index.jinja", user=user, ismedico=False, istecnico=False
            )

    return render_template("index.jinja", user=user, ismedico=False, istecnico=False)

# Implementamos la pantalla de inicio de sesión
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

# Definimos el endpoint principal del médico. Es decir, implementamos la vista Task List del diagrama IFML del médico
@app.route("/medico", methods=["GET"])
def medico():
    user = request.args.get("user")
    tareas = Tareas.query.with_entities(Tareas).all()
    return render_template("medico.jinja", user=user, tareas=tareas)

# Implementamos la vista Task Manager del diagrama IFML de médico
@app.route("/medico/asigna-robot", methods=["GET", "POST"])
def asignaRobot():
    user = request.args.get("user")
    tarea_id = request.args.get("id_tarea")

    if request.method == "POST":
        robot_id = request.form.get("robot")
        tarea_id = request.form.get("id_tarea")
        user = request.form.get("user")

        # Actualizamos el robot asignado en la base de datos
        db.session.query(Tareas).filter(Tareas.id == int(tarea_id)).update(
            {
                Tareas.rob_Id: int(robot_id),
                Tareas.estado_id: 1,
                Tareas.ejecutaMedico: user,
                Tareas.fecha_ejecucion: datetime.datetime.today(),
            },
            synchronize_session=False,
        )
        db.session.commit()

        print(
            db.session.query(Tareas)
            .filter(Tareas.id == int(tarea_id))
            .one()
            .ejecutaMedico
        )

        return redirect(f"/medico?user={request.form.get('user')}")

    tarea = Tareas.query.with_entities(Tareas).filter(Tareas.id == tarea_id).one()
    tipo = (
        Tipo_tarea.query.with_entities(Tipo_tarea)
        .filter(Tipo_tarea.tipo == tarea.tipo_tarea)
        .one()
    )

    robots = (
        Robots.query.with_entities(Robots)
        .filter(Robots.tipos_tareas.contains(tipo))
        .all()
    )

    return render_template("asignaRobot.jinja", user=user, tarea=tarea, robots=robots)

# Enpoint auxiliar para facilitar la usabilidad de la vista anteriormente mencionada
@app.route("/medico/cancelar-tarea", methods=["POST"])
def cancelar_tarea():
    body = request.get_json()
    idTarea = body["idTarea"]  # Recibe el ID de la tarea a cancelar
    print(idTarea)
    try:
        db.session.query(Tareas).filter(Tareas.id == int(idTarea)).update(
            {
                Tareas.estado_id: 0,
                Tareas.rob_Id: None,
                Tareas.ejecutaMedico: None,
                Tareas.fecha_ejecucion: None,
            },
            synchronize_session=False,
        )
        db.session.commit()
        return "Tarea cancelada"
    except:
        return abort(404)

# Implementación del componente Robot List del diagrama IFML del técnico
@app.route("/tecnico", methods=["GET"])
def tecnico():
    user = request.args.get("user")
    row = Robots.query.with_entities(Robots).all()
    tareas = Tareas.query.with_entities(Tareas).all()
    return render_template("tecnico.jinja", user=user, row=row, tareas=tareas)

# Implementación de la vista Task viewer del diagrama IFML del técnico
@app.route("/tecnico/ver-tareas", methods=["GET"])
def ver_tareas():
    user = request.args.get("user")
    tareas = Tareas.query.with_entities(Tareas).all()
    return render_template("verTareas.jinja", user=user, tareas=tareas)

# Implementación de la vista Robot Details del diagrama IFML del técnico
@app.route("/tecnico/robotDetails", methods=["GET"])
def robotDetails():
    user = request.args.get("user")
    id_robot = request.args.get("id", type=int)
    row = Tareas.query.with_entities(Tareas).filter(Tareas.rob_Id == id_robot).all()
    print(row)
    robot = Robots.query.with_entities(Robots).filter(Robots.id == id_robot).one()
    return render_template(
        "robotDetails.jinja", user=user, row=row, robot=robot, id_robot=str(id_robot)
    )

# Método auxiliar para transformar la sintaxis de los parámetros de las tareas
def _putParams(tareaNueva: Tareas):
    if request.form.get("var0") != "" and request.form.get("val0") != "":
        tareaNueva.param0 = request.form.get("var0") + "=" + request.form.get("val0")
    else:
        tareaNueva.param0 = ""
    if request.form.get("var1") != "" and request.form.get("val1") != "":
        tareaNueva.param1 = request.form.get("var1") + "=" + request.form.get("val1")
    else:
        tareaNueva.param1 = ""
    if request.form.get("var2") != "" and request.form.get("val2") != "":
        tareaNueva.param2 = request.form.get("var2") + "=" + request.form.get("val2")
    else:
        tareaNueva.param2 = ""
    if request.form.get("var3") != "" and request.form.get("val3") != "":
        tareaNueva.param3 = request.form.get("var3") + "=" + request.form.get("val3")
    else:
        tareaNueva.param3 = ""
    if request.form.get("var4") != "" and request.form.get("val4") != "":
        tareaNueva.param4 = request.form.get("var4") + "=" + request.form.get("val4")
    else:
        tareaNueva.param4 = ""
    if request.form.get("var5") != "" and request.form.get("val5") != "":
        tareaNueva.param5 = request.form.get("var5") + "=" + request.form.get("val5")
    else:
        tareaNueva.param5 = ""
    if request.form.get("var6") != "" and request.form.get("val6") != "":
        tareaNueva.param6 = request.form.get("var6") + "=" + request.form.get("val6")
    else:
        tareaNueva.param6 = ""
    if request.form.get("var7") != "" and request.form.get("val7") != "":
        tareaNueva.param7 = request.form.get("var7") + "=" + request.form.get("val7")
    else:
        tareaNueva.param7 = ""
    if request.form.get("var8") != "" and request.form.get("val8") != "":
        tareaNueva.param8 = request.form.get("var8") + "=" + request.form.get("val8")
    else:
        tareaNueva.param8 = ""
    if request.form.get("var9") != "" and request.form.get("val9") != "":
        tareaNueva.param9 = request.form.get("var9") + "=" + request.form.get("val9")
    else:
        tareaNueva.param9 = ""

# Implementación del contenedor Task Creator del diagrama IFML del técnico
@app.route("/tecnico/task-creator", methods=["GET", "POST"])
def modifyTask():
    if request.method == "POST":
        user = request.form.get("user")
        idTarea = request.form.get("idTarea")
        tipoTarea = request.form.get("tipo")
        estadoTarea = request.form.get("estado")
        idRobot = request.form.get("idRobot")
        nom = request.form.get("nombre")

        print(estadoTarea)
        print(idRobot)
        # Si se desea crear una nueva tarea genérica (sin ser asignada a ningún robot en específico), se asignará su estado a Sin Asignar
        if estadoTarea == None and idRobot == "None":
            estadoTarea = 0
        # Si se desea crear una tarea para un robot en concreto, se establecerá su futuro estado a En Espera
        elif estadoTarea == None and idRobot != "None":
            estadoTarea = 1
        # Rutina para crear una nueva tarea
        if idTarea == "" or idTarea == None:
            nuevoId = Tareas.query.with_entities(func.max(Tareas.id)).one()[0]
            # Este if permite generar un id nuevo incluso si no existe ninguna tarea existente
            if nuevoId == None or nuevoId == "":
                nuevoId = 0
            nuevoId += 1
            tareaNueva = Tareas(
                id=nuevoId,
                nombre=nom,
                estado_id=estadoTarea,
                asignaTecnico=user,
                tipo_tarea=tipoTarea,
                rob_Id=idRobot,
            )
            _putParams(tareaNueva)

            db.session.add(tareaNueva)
            db.session.commit()
        # Rutina para modificar una tarea existente
        else:
            tareaNueva = (
                Tareas.query.with_entities(Tareas).filter(Tareas.id == idTarea).one()
            )
            if tareaNueva.nombre != nom:
                tareaNueva.nombre = nom
            tareaNueva.asignaTecnico = user
            tareaNueva.tipo_tarea = tipoTarea
            tareaNueva.estado_id = estadoTarea
            _putParams(tareaNueva)

            db.session.query(Tareas).filter(Tareas.id == tareaNueva.id).update(
                {
                    Tareas.nombre: tareaNueva.nombre,
                    Tareas.param0: tareaNueva.param0,
                    Tareas.param1: tareaNueva.param1,
                    Tareas.param2: tareaNueva.param2,
                    Tareas.param3: tareaNueva.param3,
                    Tareas.param4: tareaNueva.param4,
                    Tareas.param5: tareaNueva.param5,
                    Tareas.param6: tareaNueva.param6,
                    Tareas.param7: tareaNueva.param7,
                    Tareas.param8: tareaNueva.param8,
                    Tareas.param9: tareaNueva.param9,
                    Tareas.tipo_tarea: tareaNueva.tipo_tarea,
                    Tareas.estado_id: tareaNueva.estado_id,
                    Tareas.rob_Id: tareaNueva.rob_Id,
                    Tareas.asignaTecnico: tareaNueva.asignaTecnico,
                },
                synchronize_session=False,
            )
            db.session.commit()

        return redirect(f"/tecnico?user={user}")
    
    # En caso de no recibir un POST, se cargará el editor de tareas con los datos ya existentes en la base de datos de una tarea
    else:
        idTarea = request.args.get("idTarea")
        user = request.args.get("user")
        idRobot = request.args.get("idRobot")
        tipos = Tipo_tarea.query.with_entities(Tipo_tarea).all()
        estados = Estados.query.with_entities(Estados).all()
        # Detectamos el tipo de robot que se ha seleccionado para solo poder asignarle un tipo de tarea en concreto
        if idRobot != None:
            robot = (
                Robots.query.with_entities(Robots).filter(Robots.id == idRobot).one()
            )
            tipos = robot.tipos_tareas
        # Cargamos los datos de la tarea y los representamos
        if idTarea != None:
            try:
                tarea = (
                    Tareas.query.with_entities(Tareas)
                    .filter(Tareas.id == idTarea)
                    .one()
                )
                par0 = tarea.param0 if tarea.param0 != None else ""
                par1 = tarea.param1 if tarea.param1 != None else ""
                par2 = tarea.param2 if tarea.param2 != None else ""
                par3 = tarea.param3 if tarea.param3 != None else ""
                par4 = tarea.param4 if tarea.param4 != None else ""
                par5 = tarea.param5 if tarea.param5 != None else ""
                par6 = tarea.param6 if tarea.param6 != None else ""
                par7 = tarea.param7 if tarea.param7 != None else ""
                par8 = tarea.param8 if tarea.param8 != None else ""
                par9 = tarea.param9 if tarea.param9 != None else ""
                return render_template(
                    "taskEditor.jinja",
                    par0=par0,
                    par1=par1,
                    par2=par2,
                    par3=par3,
                    par4=par4,
                    par5=par5,
                    par6=par6,
                    par7=par7,
                    par8=par8,
                    par9=par9,
                    nombre=str(tarea.nombre),
                    user=user,
                    idTarea=idTarea,
                    tipoTarea=tarea.tipo_tarea,
                    estadoTarea=tarea.estado_id,
                    estados=estados,
                    tipos=tipos,
                    idRobot=idRobot,
                )
            except:
                return render_template(
                    "taskEditor.jinja",
                    par0="",
                    par1="",
                    par2="",
                    par3="",
                    par4="",
                    par5="",
                    par6="",
                    par7="",
                    par8="",
                    par9="",
                    nombre="",
                    user=user,
                    idTarea="",
                    tipoTarea="",
                    estadoTarea="",
                    estados=estados,
                    tipos=tipos,
                    idRobot=idRobot,
                )
        # Si se crea una nueva tarea, el formulario se cargará vacío
        return render_template(
            "taskEditor.jinja",
            par0="",
            par1="",
            par2="",
            par3="",
            par4="",
            par5="",
            par6="",
            par7="",
            par8="",
            par9="",
            nombre="",
            user=user,
            idTarea="",
            tipoTarea="",
            estadoTarea="",
            estados=estados,
            tipos=tipos,
            idRobot=idRobot,
        )

# Endpoint auxiliar para eliminar una tarea creada
@app.route("/tecnico/borrar-tarea", methods=["POST"])
def borrar_tarea():
    body = request.get_json()
    idTarea = body["idTarea"]  # Recibe el ID de la tarea a eliminar
    try:
        db.session.query(Tareas).filter(Tareas.id == idTarea).delete()
        db.session.commit()
        return "Tarea eliminada"
    except:
        return abort(404)

# Implementa el contenedor Type creator del diagrama IFML del técnico
@app.route("/tecnico/nuevo-tipo", methods=["POST"])
def nuevo_tipo():
    body = request.get_json()
    print(body)
    nuevoTipo = body["tipoNuevo"]
    try:
        db.session.add(Tipo_tarea(tipo=nuevoTipo))
        db.session.commit()
        return "Tipo creado"
    except:
        return jsonify({"message": "No se pudo crear el tipo"})


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


@app.route("/api/robot", methods=["POST"])
def addRobot():
    try:
        body = request.get_json()
        nom = body["nombre"]
        id_tipos = body["tipos"]
        tipos = []
        for t in id_tipos:
            try:
                tipo = Tipo_tarea.query.with_entities(Tipo_tarea).filter(Tipo_tarea.tipo == t).one()
                tipos.append(tipo)
            except:
                pass
        nuevo_id = Robots.query.with_entities(func.max(Robots.id)).one()[0]
        if nuevo_id == None or nuevo_id == "":
            nuevo_id = 0
        nuevo_id += 1

        robot = Robots(id=nuevo_id, nombre=nom, tipos_tareas=tipos)
        db.session.add(robot)
        db.session.commit()
        return jsonify({"statusCode": 200, "message": "Robot creado"})
    except:
        return jsonify({"statusCode": 400, "message": "Bad request"})


# ======= FUNCIONES DE INSERCIÓN DE DATOS EJEMPLO EN LA BASE DE DATOS=======


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
    robot1 = Robots(
        id=1,
        nombre="XLR8",
        tipos_tareas=[
            Tipo_tarea.query.get("limpieza"),
            Tipo_tarea.query.get("desinfeccion"),
            Tipo_tarea.query.get("transporte"),
        ],
    )
    robot2 = Robots(
        id=2,
        nombre="C3PO",
        tipos_tareas=[
            Tipo_tarea.query.get("limpieza"),
            Tipo_tarea.query.get("transporte"),
        ],
    )
    robot3 = Robots(
        id=3,
        nombre="R2D2",
        tipos_tareas=[
            Tipo_tarea.query.get("videollamada"),
            Tipo_tarea.query.get("desinfeccion"),
        ],
    )
    robot4 = Robots(
        id=4,
        nombre="GR0GU",
        tipos_tareas=[
            Tipo_tarea.query.get("videollamada"),
            Tipo_tarea.query.get("transporte"),
        ],
    )
    robot5 = Robots(
        id=5,
        nombre="Lavatronix3000",
        tipos_tareas=[
            Tipo_tarea.query.get("limpieza"),
            Tipo_tarea.query.get("desinfeccion"),
        ],
    )
    robot6 = Robots(
        id=6, nombre="TorboCleaner5000", tipos_tareas=[Tipo_tarea.query.get("limpieza")]
    )

    db.session.add(robot1)
    db.session.commit()
    db.session.add(robot2)
    db.session.commit()
    db.session.add(robot3)
    db.session.commit()
    db.session.add(robot4)
    db.session.commit()
    db.session.add(robot5)
    db.session.commit()
    db.session.add(robot6)
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
    estado5 = Estados(
        id=5, nombre="Avería mecánica", descripcion="La aspiradora se ha atascado"
    )
    estado6 = Estados(
        id=6, nombre="Batería baja", descripcion="Volviendo a la base de carga"
    )

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
    db.session.add(estado5)
    db.session.commit()
    db.session.add(estado6)
    db.session.commit()


def inserta_tipos():
    tipo1 = Tipo_tarea(tipo="limpieza")
    tipo2 = Tipo_tarea(tipo="desinfeccion")
    tipo3 = Tipo_tarea(tipo="transporte")
    tipo4 = Tipo_tarea(tipo="videollamada")

    db.session.add(tipo1)
    db.session.commit()
    db.session.add(tipo2)
    db.session.commit()
    db.session.add(tipo3)
    db.session.commit()
    db.session.add(tipo4)
    db.session.commit()


def inserta_tareas():
    tarea1 = Tareas(
        id=1,
        nombre="Limpieza",
        tipo_tarea="limpieza",
        rob_Id=1,
        fecha_ejecucion=datetime.datetime.today(),
        estado_id=1,
        asignaTecnico="tecnico1",
        param0="DURACION=20",
    )

    tarea2 = Tareas(
        id=2,
        nombre="Videollamada",
        tipo_tarea="videollamada",
        rob_Id=3,
        fecha_ejecucion=datetime.datetime(
            day=12, month=2, year=2021, hour=16, minute=52
        ),
        estado_id=2,
        asignaTecnico="tecnico2",
        param0="NOMBRE_PROGRAMA=Skype",
    )

    tarea3 = Tareas(
        id=3,
        nombre="Aspirar",
        tipo_tarea="limpieza",
        rob_Id=2,
        fecha_ejecucion=datetime.datetime.today(),
        estado_id=2,
        asignaTecnico="tecnico1",
    )

    tarea4 = Tareas(
        id=4,
        nombre="Desinfectar",
        tipo_tarea="desinfeccion",
        rob_Id=3,
        fecha_ejecucion=datetime.datetime(
            day=13, month=6, year=2022, hour=23, minute=32
        ),
        estado_id=3,
        asignaTecnico="tecnico1",
        ejecutaMedico="medico1",
    )

    tarea5 = Tareas(
        id=5,
        nombre="Limpieza a fondo",
        tipo_tarea="limpieza",
        rob_Id=5,
        fecha_ejecucion=datetime.datetime(day=7, month=10, year=2022, hour=7, minute=1),
        estado_id=1,
        asignaTecnico="tecnico1",
        param0="POTENCIA=560",
        param1="TIEMPO=3000",
        param2="RAYOS=UV",
        param3="ENERGIA=BATERIA",
        param4="PARAR.SI=BATERIA-BAJA",
    )

    tarea6 = Tareas(
        id=6,
        nombre="Fregar suelo",
        tipo_tarea="limpieza",
        rob_Id=6,
        fecha_ejecucion=datetime.datetime.today(),
        estado_id=3,
        asignaTecnico="tecnico1",
        param0="MODO=FREGONA",
        param1="TIEMPO=3600",
        param2="RAYOS=GAMMA",
        param3="AGRESIVIDAD=MODERADA",
        param4="BOCINA=NO",
    )

    tarea7 = Tareas(
        id=7,
        nombre="Luz en quirófano",
        tipo_tarea="transporte",
        rob_Id=2,
        fecha_ejecucion=datetime.datetime(
            day=30, month=8, year=2019, hour=9, minute=45
        ),
        estado_id=4,
        asignaTecnico="tecnico1",
        ejecutaMedico="medico1",
        param0="POTENCIA=30",
        param1="COLOR=3000K",
        param2="UBICACION=QUIROFANO1",
    )

    tarea8 = Tareas(
        id=8,
        nombre="Videllamada consulta 1",
        tipo_tarea="videollamada",
        estado_id=0,
        asignaTecnico="tecnico1",
        ejecutaMedico="medico1",
    )
    tarea9 = Tareas(
        id=9,
        nombre="Videollamada consulta 23",
        tipo_tarea="videollamada",
        estado_id=0,
        asignaTecnico="tecnico1",
        ejecutaMedico="medico1",
    )
    tarea10 = Tareas(
        id=10,
        nombre="LLevar medicamentos a sala 119",
        tipo_tarea="transporte",
        estado_id=0,
        asignaTecnico="tecnico1",
        ejecutaMedico="medico1",
    )
    tarea11 = Tareas(
        id=11,
        nombre="Llevar herramientas a quirófano 3",
        tipo_tarea="transporte",
        estado_id=0,
        asignaTecnico="tecnico1",
        ejecutaMedico="medico1",
    )
    tarea12 = Tareas(
        id=12,
        nombre="Llevar herramientas a quirófano 5",
        tipo_tarea="transporte",
        estado_id=0,
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
    db.session.add(tarea5)
    db.session.commit()
    db.session.add(tarea6)
    db.session.commit()
    db.session.add(tarea7)
    db.session.commit()
    db.session.add(tarea8)
    db.session.commit()
    db.session.add(tarea9)
    db.session.commit()
    db.session.add(tarea10)
    db.session.commit()
    db.session.add(tarea11)
    db.session.commit()
    db.session.add(tarea12)
    db.session.commit()


# ======= INICIO DE LA APLICACIÓN =======


if __name__ == "__main__":
    app.app_context().push()
    db.drop_all()
    db.create_all()
    inserta_usuarios()
    inserta_estados()
    inserta_tipos()
    inserta_robots()
    inserta_subclases()
    inserta_tareas()

    app.run(port=5000, debug=True)
