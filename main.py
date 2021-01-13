import MySQLdb
import bcrypt
import camera
from flask import Flask, render_template, request, redirect, url_for, session, g, Response, flash
from flask_mysqldb import MySQL
import cv2
import numpy as np
from os import listdir
from os.path import isfile, join

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'python'

# Intialize MySQL
mysql = MySQL(app)


@app.before_request
def before_request():
    g.username = None
    if 'username' in session:
        g.username = session['username']


@app.route('/')
def root():
    return render_template('signin.html')


@app.route('/signin/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return render_template("signin.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    else:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("insert into student(username,email,password) values (%s,%s,%s)", (username, email, password))
        mysql.connection.commit()
        session['username'] = username
        session['email'] = email
        redirect(url_for('home'))
    return render_template('home.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            # redirect(url_for('home'))

            return render_template('home.html')

        else:
            msg = 'Incorrect username/password!'
            return render_template('home.html')

    return render_template('home.html')


@app.route('/signin/home/start')
def start():
    flash("new flash Successfully")
    return render_template('/demo/index.html', x=gen_frames())


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def gen_frames():  # generate frame by frame from camera
    data_path = "Cascade/Output_img/"
    only_files = [f for f in listdir(data_path) if isfile(join(data_path, f))]

    train_data, labels = [], []

    for i, files in enumerate(only_files):
        image_path = data_path + only_files[i]
        images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        train_data.append(np.asarray(images, dtype=np.uint8))
        labels.append(i)
        # prprint(i)

    labels = np.asarray(labels, dtype=np.int32)

    model = cv2.face.LBPHFaceRecognizer_create()

    model.train(np.asarray(train_data), np.asarray(labels))

    print("Model trained succesfully")
    phone_path="Phone_Cascade.xml"
    phone_cascade = cv2.CascadeClassifier(phone_path)
    cascade_path = "haarcascade_frontalcatface_extended.xml"
    face_path = cv2.CascadeClassifier(cascade_path)

    def face_dec(img, size=0.5):

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_path.detectMultiScale(gray, 1.3, 5)
        phones = phone_cascade.detectMultiScale(gray, 3, 9)
        for (x, y, w, h) in phones:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, 'Phone', (x - w, y - h), font, 0.5, (11, 255, 255), 2, cv2.LINE_AA)

        if faces is ():
            return img, []

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + y, y + h), (0, 255, 0), 2)

            roi = img[y:y + h, x:x + w]
            roi = cv2.resize(roi, (200, 200))
            # print(len(faces))
            # if(len(faces)<=1):
            # print("1")
            # flash("new nnnnn Successfully")
            # else:
            # print("2")
            # ("2")
            # if(len(faces)>1)

        return img, roi

    # flash("hi student")

    capture = cv2.VideoCapture(0)

    while True:

        ret, frame = capture.read()

        image, face = face_dec(frame)
        phone = face_dec(frame)
        # print(len(phone))
        try:

            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            result = model.predict(face)
            # print(result[1])

            if result[1] < 1000:
                confidence = int(100 * (1 - (result[1]) / 300))
                display_string = str(confidence) + " % Confidence it is user"
                cv2.putText(image, display_string, (100, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

                if confidence > 77 & (len(phone) < 1):
                    print('xx', len(phone))
                    cv2.putText(image, "Unlocked", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    #cv2.imshow("Face Cropper", image)
                    #print("xx")

                if  confidence > 77 | (len(phone) >= 1):
                    print('cc', len(phone))
                    cv2.putText(image, "LOCKED", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    #cv2.imshow("Face Cropper", image)
                    #print("locked phone")

        except:
            cv2.putText(image, "Face not Found", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            #cv2.imshow("Face Cropper", image)
            pass

        frame = cv2.imencode('.jpg', image)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # time.sleep(0.1)
        key = cv2.waitKey(20)
        if key == 27:
            break


if __name__ == "__main__":
    app.secret_key = "102#!ApaAjkdsjvdslkmvf()UY"
    app.run(debug=True)
