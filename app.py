import os
from flask import Flask, render_template, request, send_from_directory, send_file
from pattern import ImageEditor

app = Flask(__name__, static_url_path='')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return render_template("upload.html")

# upload files to a given path

@app.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, 'input')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    filename = None

    #TODO: only one file
    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        file.save(destination)

    renamed_file = 'input_img.jpg'
    os.rename(r'./input/'+filename, r'./input/'+renamed_file)

    n_col = int(request.form['n_col'])
    n_sts = int(request.form['n_sts'])

    r_gauge = int(request.form['row_gauge'])
    s_gauge = int(request.form['st_gauge'])

    #fixed_img, colours = generate_pattern(renamed_file, n_col, n_sts, r_gauge, s_gauge)
    ie = ImageEditor(renamed_file)
    ie.fit(n_col, n_sts, r_gauge, s_gauge)
    ie.prepare_img()
    ie.draw_gridlines()
    ie.save_img()

    return render_template("complete.html", fixed_img=ie.saved_name, colours=ie.colour_swatches, nc=n_col, ns=n_sts, rg=r_gauge, sg=s_gauge)



@app.route("/refresh", methods=['POST'])
def refresh():

    filename = 'input_img.jpg'

    n_col = int(request.form['n_col'])
    n_sts = int(request.form['n_sts'])

    r_gauge = int(request.form['row_gauge'])
    s_gauge = int(request.form['st_gauge'])

    ie = ImageEditor(filename)
    ie.fit(n_col, n_sts, r_gauge, s_gauge)
    ie.prepare_img()
    ie.draw_gridlines()
    ie.save_img()

    return render_template("complete.html", fixed_img=ie.saved_name, colours=ie.colour_swatches, nc=n_col, ns=n_sts, rg=r_gauge, sg=s_gauge)





# display the uploaded image
@app.route('/static/<fixed_img>')
def send_image(fixed_img):
    return send_from_directory(directory='static',
                               filename=fixed_img, as_attachment=True)



if __name__ == '__main__':
    app.run(port=4555, debug=True)


