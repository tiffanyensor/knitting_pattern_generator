import os
import glob
from flask import Flask, render_template, request, send_from_directory, send_file
from pattern import ImageEditor

app = Flask(__name__, static_url_path='')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    # empty the old files out
    input_directory = os.path.join(APP_ROOT, 'input')
    static_directory = os.path.join(APP_ROOT, 'static')

    if not os.path.isdir(input_directory):
        os.mkdir(input_directory)

    for f in glob.glob(input_directory+'/*'):
        os.remove(f)

    for f in glob.glob(static_directory+'/*.png'):
        os.remove(f)

    return render_template("upload.html")

# upload files to a given path

@app.route("/upload", methods=['POST'])
def upload():

    input_directory = os.path.join(APP_ROOT, 'input')
    filename = None

    #TODO: only one file
    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        filename = filename.replace(' ', '_')
        destination = "/".join([input_directory, filename])
        file.save(destination)

    # initialize some values
    n_col = 4
    n_sts = 40
    r_gauge = 24
    s_gauge = 18
    blur = 10

    ie = ImageEditor(filename)
    ie.fit(n_col, n_sts, r_gauge, s_gauge, blur)

    return render_template("complete.html",
                           original_img = filename,
                           fixed_img=ie.saved_name,
                           colours=ie.colour_swatches[ie.saved_name],
                           nc=n_col,
                           ns=n_sts,
                           rg=r_gauge,
                           sg=s_gauge,
                           blur = blur)



@app.route("/refresh/<original_img>", methods=['POST', 'GET'])
def refresh(original_img):
    #filename = 'input_img.jpg'

    n_col = int(request.form['n_col'])
    n_sts = int(request.form['n_sts'])

    r_gauge = int(request.form['row_gauge'])
    s_gauge = int(request.form['st_gauge'])

    blur = int(request.form['blur'])


    ie = ImageEditor(original_img)
    ie.fit(n_col, n_sts, r_gauge, s_gauge, blur)

    return render_template("complete.html",
                           original_img = original_img,
                           fixed_img=ie.saved_name,
                           colours=ie.colour_swatches[ie.saved_name],
                           nc=n_col,
                           ns=n_sts,
                           rg=r_gauge,
                           sg=s_gauge,
                           blur = blur)





# display the uploaded image
@app.route('/static/<fixed_img>')
def send_image(fixed_img):
    return send_from_directory(directory='static',
                               filename=fixed_img,
                               as_attachment=True)




if __name__ == '__main__':
    app.run(debug=True)


