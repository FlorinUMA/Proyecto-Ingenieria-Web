from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request
)

app = Flask(__name__)

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