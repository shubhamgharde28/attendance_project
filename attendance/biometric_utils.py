import face_recognition
import tempfile
import numpy as np

def compare_face(uploaded_image_data, stored_encoding_binary):
    try:
        # Load uploaded image from bytes
        with tempfile.NamedTemporaryFile(delete=True, suffix=".jpg") as temp:
            temp.write(uploaded_image_data)
            temp.flush()
            uploaded_img = face_recognition.load_image_file(temp.name)

        uploaded_encodings = face_recognition.face_encodings(uploaded_img)
        if not uploaded_encodings:
            return False

        uploaded_encoding = uploaded_encodings[0]

        # Convert stored binary back to numpy array
        stored_encoding = np.frombuffer(stored_encoding_binary, dtype=np.float64)

        # Compare
        matches = face_recognition.compare_faces([stored_encoding], uploaded_encoding)
        return matches[0]
    except Exception as e:
        print("Face match error:", e)
        return False
