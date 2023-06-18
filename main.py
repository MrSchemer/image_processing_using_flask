from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from PIL import Image
import os
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif','svg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maximum file size (16MB)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def rotate_image(image_path, output_path, angle):
    with Image.open(image_path) as image:
        rotated_image = image.rotate(angle, expand=True)
        rotated_image.save(output_path)

def fresizer(file, width, height):
    img = cv2.imread(f"static/uploads/{file}")

    try:
        width = int(width)
        height = int(height)
    except ValueError:
        raise ValueError("Width and height must be integers.")
    resized = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    nfilename = f"static/results/{file}"
    cv2.imwrite(nfilename, resized)
    return nfilename

def process(image, oper):
    print(f"{oper}")
    filename = cv2.imread(f"static/uploads/{image}")
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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert')
def convert():
    return render_template("formatconvertor.html")


@app.route('/resizor')
def resizer():
    return render_template("resizor.html")


@app.route('/adfilter')
def filter():
    return render_template("addfilters.html")

@app.route('/rotate', methods=['GET', 'POST'])
def rotate():
    if request.method == 'POST':
        # Check if file is present in the request
        if 'file' not in request.files:
            return 'No file part in the request'

        file = request.files['file']

        # Check if the file is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Read the angle from the form
            angle = int(request.form['angle'])

            # Generate a unique output filename
            output_filename = f'rotated_{angle}_{filename}'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

            # Rotate the image
            rotate_image(file_path, output_path, angle)

            # Pass the rotated image path to the template for display
            rotated_image_path = '/' + output_path
            print(rotated_image_path)
            return render_template('result.html', image_path=rotated_image_path)

    return render_template('rotate.html')
@app.route('/resize', methods=["GET", "POST"])
def resize():
    if (request.method == "POST"):
        if 'file' not in request.files:
            return "error"

        file = request.files['file']
        height = request.form.get("height")
        width = request.form.get("width")

        if file.filename == '':
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"the filr is {filename} with {width}x{height}")
            nfilename = fresizer(filename, width, height)
            outputpath = f"/{nfilename}"
            return render_template("result.html", image_path=outputpath)

    return render_template("resizor.html")


@app.route('/edit', methods=["GET", "POST"])
def edit():
    if (request.method == "POST"):
        if 'file' not in request.files:
            return "error"

        file = request.files['file']
        format = request.form.get("format")

        if file.filename == '':
            
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nfilename = process(filename, format)
            outputpath = f"/{nfilename}"
            return render_template("result.html", image_path=outputpath)

    return render_template("formatconvertor.html")
   
if __name__ == '__main__':
    app.run(debug=True)
