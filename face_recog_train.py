import cv2
import numpy as np
from os import listdir
from os.path import isfile, join
#camera = cv2.VideoCapture(0)  # use 0 for web camera

data_path = "C:/Users/user/Desktop/Cascade/Output_img/"
only_files = [f for f in listdir(data_path) if isfile(join(data_path, f))]

train_data, labels = [],[]

for i, files in enumerate(only_files):
    image_path = data_path + only_files[i]
    images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    train_data.append(np.asarray(images, dtype= np.uint8))
    labels.append(i)
    print(i)

labels = np.asarray(labels, dtype = np.int32)

model = cv2.face.LBPHFaceRecognizer_create()

model.train(np.asarray(train_data), np.asarray(labels))

print("Model trained succesfully")


face_path = cv2.CascadeClassifier("C:/Users/a.rayyan/Desktop/Cascade/haarcascade_frontalface_default.xml")


def camera_stream():
    gray = cv2.cvtColor(cv2.COLOR_BGR2GRAY)
    faces = face_path.detectMultiScale(gray, 1.3, 5)
    if faces is ():
        return cv2.imencode('.jpg', frame)[1].tobytes()

    for(x, y, w, h) in faces:
        cv2.rectangle( (x, y), (x + y, y + h), (0, 255, 0), 2)

        roi = cv2.resize(roi, (200, 200))
        print(len(faces))
    return cv2.imencode('.jpg', frame)[1].tobytes()


capture = cv2.VideoCapture(0)

while True:


    ret, frame = capture.read()

    image, face = camera_stream()

    try:

        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        result = model.predict(face)
        #print(result[1])



        if result[1] < 1000:
            confidence = int(100*(1-(result[1])/300))
            display_string = str(confidence)+ " % Confidence it is user"
        cv2.putText(image, display_string, (100, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        if confidence > 77:
            cv2.putText(image, "UNLOCKED", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Face Cropper", image)
        else:
            cv2.putText(image, "LOCKED", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Face Cropper", image)

    except:
            cv2.putText(image, "Face not Found", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Face Cropper", image)
            pass

    if cv2.waitKey(1) == 13:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
capture.release()
cv2.destroyAllWindows()
