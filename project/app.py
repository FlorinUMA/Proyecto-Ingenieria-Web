from flask import (
    Flask,
    render_template,
    redirect,
    url_for
)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("base.jinja")

if __name__ == "__main__":
    app.run(port=5000, debug=True)