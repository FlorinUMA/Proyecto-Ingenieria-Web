from flask import (
    Flask,
    render_template,
    redirect,
    url_for
)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.jinja")

@app.route("/error", methods=["GET"])
def error():
    return render_template("error.jinja")

# @app.route("/asig-tarea", methods=["POST"])
# def asig_tarea():
#     pass

if __name__ == "__main__":
    app.run(port=5000, debug=True)