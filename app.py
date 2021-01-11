from flask import Flask

app = Flask(__name__)


@app.route("/")
def sup() -> str:
    return "sup"


if __name__ == "__main__":
    app.run()
