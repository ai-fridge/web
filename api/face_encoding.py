import face_recognition

def FaceEncoding(path):
    face_image = face_recognition.load_image_file(path)
    faceencoding = face_recognition.face_encodings(face_image)[0]
    list_face_encoding =faceencoding.tolist()
    return faceencoding

# a=FaceEncoding("../media/image/1.jpg")
# print(a)
def detect_faces_in_image(unknown_face_img, known_face_encoding, known_face_names):
    face_found = False
    is_face_authentication = False
    name = 'Unknown'
    unknown_face_encodings = FaceEncoding(unknown_face_img)

    if len(unknown_face_encodings) > 0:
        face_found = True

        # See if the first face in the uploaded image matches the known face of the database
        matches = face_recognition.compare_faces(known_face_encoding, unknown_face_encodings, tolerance=0.5)

        if True in matches:
            is_face_authentication = True
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

    # Return the result as json
    result = {
        "isFaceFound": face_found,
        "isFaceAuthentication": is_face_authentication,
        "name": name
    }

    return result
