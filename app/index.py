from app import app

@app.route("/")
def index():
    print("hello")
    return "<h1>hello<h1>"
