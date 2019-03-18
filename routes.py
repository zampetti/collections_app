from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory, Response, stream_with_context
from forms import UploadForm
from werkzeug.utils import secure_filename
import os, cv2, glob, time, webbrowser
import pandas as pd

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:********@localhost/learningflask'
db.init_app(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "development-key"

webbrowser.open('http://localhost:5000/home')

@app.route("/")
def index():
#    return render_template("index.html")
    return redirect(url_for('home'))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if 'email' in session:
        return redirect(url_for('home'))
    
    form = SignupForm()
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signup.html', form=form)
        else:
            newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()
            
            session['email'] = newuser.email
            return redirect(url_for('home'))
        
    elif request.method == 'GET':
        return render_template("signup.html", form=form)
    
@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('home'))
    
    form = LoginForm()
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template("login.html", form=form)
        else:
            email = form.email.data
            password = form.password.data
            
            user = User.query.filter_by(email=email).first()
            if user is not None and user.check_password(password):
                session['email'] = form.email.data
                return redirect(url_for('home'))
            else:
                return redirect(url_for('login'))
            
    elif request.method == 'GET':
        return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))
    
@app.route("/home", methods=['GET', 'POST'])
def home():
#    if 'email' not in session:
#        return redirect(url_for('login'))
    
    form = UploadForm()
    image_paths = []
    
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('home.html', form=form)
        else:
            f = form.upload.data
            c = form.collection_path.data
            tfd = form.target_file_dir.data
            
            filename = secure_filename(f.filename)
            template_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(template_path)
            
            session['c'] = c
            session['tfd'] = tfd
            session['filename'] = filename
            session['template_path'] = template_path
                    
#            return render_template('home.html', form=form, path=path)
            return redirect(url_for('processing'))
    
    elif request.method == 'GET':
        return render_template("home.html", form=form, image_paths=image_paths)
    
    return render_template("home.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def stream_template(template_name, **context):   
    app.update_template_context(context)             
    t = app.jinja_env.get_template(template_name)      
    rv = t.stream(context)                            
    rv.disable_buffering()                            
    return rv  

@app.route('/processing')
def processing():
    filename = session.get('filename', None)
    template_path = session.get('template_path', None)
    c = session.get('c', None)
    tfd = session.get('tfd', None)
    
    fix_c = c.replace('"', '')
    folders = os.listdir(fix_c)
    total = len(folders)

    fix_tfd = tfd.replace('"', '')
    
    path = url_for('uploaded_file', filename=filename)
    
    def generate():
        for i, folder in enumerate(folders):
            fol = fix_c+'\\'+folder
            image_files = os.listdir(fol)
            total_infile = len(image_files)
            target_file_dir = fix_tfd+'\\'+os.path.basename(folder)+'_target_file_directory'
            os.mkdir(target_file_dir)
            for idx, image in enumerate(image_files):
                yield 'Currently processing file {} in folder {}'.format(image, folder)
                img = fol+'\\'+image
                template = cv2.imread(template_path,0)
                match = cv2.imread(img,0)

                th, tw = template.shape
                mh, mw = match.shape
                if mw < tw:
                    continue

                result = cv2.matchTemplate(match, template, cv2.TM_CCOEFF_NORMED)

                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_val > 0.6:
                    cv2.imwrite(target_file_dir+'\\'+os.path.basename(image), match.copy())
#
#            percentage = int(((i+1)/total)*100)
#            yield str(percentage)
#            yield 'folder: {}'.format(folder)
            
    rows = generate()
    return Response(stream_with_context(stream_template('processing.html', rows=rows, fix_c=fix_c, fix_tfd=fix_tfd, path=path, total=total)))

#@app.route('/completion')
#def completion():
#    return render_template('completion.html')
                
if __name__ == "__main__":
    app.run(debug=True)