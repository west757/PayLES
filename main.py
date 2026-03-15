from app import flask_app

if __name__ == "__main__":
    flask_app.run(host="127.0.0.1", port=8080, debug=True)
    #flask_app.run(host="0.0.0.0", debug=False)