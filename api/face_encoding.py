import face_recognition

def FaceEncoding(path):
    face_image = face_recognition.load_image_file(path)
    faceencoding = face_recognition.face_encodings(face_image)[0]
    list_face_encoding =faceencoding.tolist()
    return faceencoding

# a=FaceEncoding("../media/image/1.jpg")
# print(a)
