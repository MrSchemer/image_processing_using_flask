from flask import Flask, render_template, request, flash, redirect
from werkzeug.utils import secure_filename
from PIL import Image
import os
import cv2


app = Flask(__name__)

app.secret_key = 'the random string'
UPLOAD_FOLDER = os.path.abspath('uploads')
ALLOWED_EXTENSIONS = {'webp', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def fresizer(file, width, height):
    img = cv2.imread(f"uploads/{file}")

    try:
        width = int(width)
        height = int(height)
    except ValueError:
        raise ValueError("Width and height must be integers.")
    resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    nfilename = f"static/results/{file}"
    cv2.imwrite(nfilename, resized)
    return nfilename


def rotator(img, angle):
    rotated_img = img.rotate(angle)
    nfilename = f"static/results/{img}"
    cv2.imwrite(nfilename, rotated_img)
    return nfilename


def process(image, oper):
    print(f"{oper}")
    filename = cv2.imread(f"uploads/{image}")
    match oper:
        case "grayscale":
            imagep = cv2.cvtColor(filename, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(f"static/results/{image}", imagep)
            filename = f"static/results/{image}"
            return filename

        case "png":
            newfilename = f"static/results/{image.split('.')[0]}.png"
            cv2.imwrite(newfilename, filename)
            return newfilename
        case "jpg":
            newfilename = f"static/results/{image.split('.')[0]}.jpg"
            cv2.imwrite(newfilename, filename)
            return newfilename
        case "webp":
            newfilename = f"static/results/{image.split('.')[0]}.webp"
            cv2.imwrite(newfilename, filename)
            return newfilename

        case "blur":
            blur = cv2.GaussianBlur(filename, (5, 5), 0)
            cv2.imwrite(f"static/results/{image}", blur)
            filename = f"static/results/{image}"
            return filename


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/convert')
def convert():
    return render_template("formatconvertor.html")


@app.route('/resize')
def resize():
    return render_template("resizor.html")


@app.route('/adfilter')
def filter():
    return render_template("addfilters.html")

@app.route('/rotates')
def rot():
    return render_template("rotateimage.html")

@app.route('/edit', methods=["GET", "POST"])
def edit():
    if (request.method == "POST"):
        if 'file' not in request.files:
            flash('No file part')
            return "error"

        file = request.files['file']
        operation = request.form.get("operation")

        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nfilename = process(filename, operation)
            flash(
                f"your image hasbeen processed and available  <a href='/{nfilename}' target='_blank'>here</a>")
            return render_template("index.html")
    return redirect("/")


@app.route('/resize', methods=["GET", "POST"])
def resizer():
    if (request.method == "POST"):
        if 'file' not in request.files:
            flash('No file part')
            return "error"

        file = request.files['file']
        operation = request.form.get("operation")
        height = request.form.get("height")
        width = request.form.get("width")

        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"the filr is {filename} with {width}x{height}")
            nfilename = fresizer(filename, width, height)
            flash(
                f"your image hasbeen processed and available  <a href='/{nfilename}' target='_blank'>here</a>")
            return render_template("index.html")
    return redirect("/")


@app.route('/rotate', methods=["GET", "POST"])
def rotates():
    if (request.method == "POST"):
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        angle = request.form.get("angle")
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nfilename = rotator(filename, angle)
            flash(
                f"your image hasbeen processed and available  <a href='/{nfilename}' target='_blank'>here</a>")
            return render_template("index.html")
    pass


if __name__ == '__main__':
    app.run(debug=True, port=5500)
