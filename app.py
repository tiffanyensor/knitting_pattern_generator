import os
from flask import Flask, render_template, request, send_from_directory, send_file
from pattern import generate_pattern

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

    fixed_img = generate_pattern(renamed_file, n_col, n_sts, r_gauge, s_gauge)
    fixed_img = fixed_img.split('/')[1]

    return render_template("complete.html", fixed_img=fixed_img, nc=n_col, ns=n_sts, rg=r_gauge, sg=s_gauge)

    #return render_template("complete.html", image_name=filename)
    #return render_template("complete.html", image_name=fixed_img)


#@app.route("/refresh/<filename>", methods=['POST'])
@app.route("/refresh", methods=['POST'])
def refresh():

    filename = 'input_img.jpg'

    n_col = int(request.form['n_col'])
    n_sts = int(request.form['n_sts'])

    r_gauge = int(request.form['row_gauge'])
    s_gauge = int(request.form['st_gauge'])

    fixed_img = generate_pattern(filename, n_col, n_sts, r_gauge, s_gauge)
    fixed_img = fixed_img.split('/')[1]

    return render_template("complete.html", fixed_img=fixed_img, nc=n_col, ns=n_sts, rg=r_gauge, sg=s_gauge)




"""
def generate_image(filename):

    n_col = int(request.form['n_col'])
    n_sts = int(request.form['n_sts'])

    fixed_img = generate_pattern(filename, n_col, n_sts)
    print('********* done generating file *******')

    return render_template("complete.html", image_name=fixed_img)

    #return send_from_directory("output", fixed_img)
"""



# display the uploaded image
@app.route('/output/<fixed_img>')
def send_image(fixed_img):
    return send_from_directory(directory='output',
                               filename=fixed_img, as_attachment=True)

#def send_image(fixed_img):
#    print('The output image is ', fixed_img)
#    return send_from_directory("output", fixed_img)




if __name__ == '__main__':
    app.run(port=4555, debug=True)


