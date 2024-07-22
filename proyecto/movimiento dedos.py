import cv2
import mediapipe as mp
import serial
import time

# Configuración del puerto serial
arduino = serial.Serial('COM4', 9600)  # Reemplaza 'COM3' con el puerto correcto
time.sleep(2)  # Espera a que se establezca la conexión

# Inicialización de Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Función para detectar si un dedo está extendido
def is_finger_extended(hand_landmarks, finger_tip_idx, finger_mcp_idx):
    return hand_landmarks.landmark[finger_tip_idx].y < hand_landmarks.landmark[finger_mcp_idx].y

# Inicialización de la cámara
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger_extended = is_finger_extended(hand_landmarks, 8, 5)
            middle_finger_extended = is_finger_extended(hand_landmarks, 12, 9)

            if index_finger_extended:
                print("Index finger extended")
                arduino.write(b'I')
            else:
                print("Index finger not extended")
                arduino.write(b'i')

            if middle_finger_extended:
                print("Middle finger extended")
                arduino.write(b'M')
            else:
                print("Middle finger not extended")
                arduino.write(b'm')

            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Hand Tracking', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()
