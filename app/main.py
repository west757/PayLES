from flask import Flask
from flask import request, render_template, request, abort, make_response, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)


app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

ALLOWED_EXTENSIONS = {'pdf'}

#app.config['UPLOAD_FOLDER'] = 'C:\Users\blue\Documents\GitHub\PayLES\upload'


#import os
#file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename))


@app.route('/')
def home():
    return render_template('upload_form.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request', 400

    if 'file' in request.files:
        file = request.files['file']

        if file.filename == '':
            return 'No selected file', 400

        if file and not allowed_file(file.filename):
            return 'File type not allowed', 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            #try:
            #    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #except Exception as e:
            #    return f'Error saving file: {str(e)}', 500

            #file.save(UPLOAD_FOLDER)
            return 'File uploaded successfully'
    return 'File upload failed'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)


@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return 'File is too large, custom message', 413



#
#@app.route("/")
#def index():
#    celsius = request.args.get("celsius", "")
#    if celsius:
#        fahrenheit = fahrenheit_from(celsius)
#    else:
#        fahrenheit = ""
#    return (
#        """<form action="" method="get">
#                Celsius temperature: <input type="text" name="celsius">
#                <input type="submit" value="Convert to Fahrenheit">
#            </form>"""
#        + "Fahrenheit: "
#        + fahrenheit
#    )

#def fahrenheit_from(celsius):
#    """Convert Celsius to Fahrenheit degrees."""
#    try:
#        fahrenheit = float(celsius) * 9 / 5 + 32
#        fahrenheit = round(fahrenheit, 3)  # Round to three decimal places
#        return str(fahrenheit)
#    except ValueError:
#        return "invalid input"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)