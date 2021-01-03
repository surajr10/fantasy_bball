from flask import Flask
<<<<<<< HEAD

app = Flask(__name__)


@app.route("/")
def sup() -> str:
    return "sup"


if __name__ == "__main__":
    app.run()
=======
app = Flask(__name__)

@app.route('/')
def sup():
    return "sup"


if __name__ == '__main__':
    app.run()
>>>>>>> 96de2f9... random ish
