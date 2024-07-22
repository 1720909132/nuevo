
import cv2
import mediapipe as mp
import serial
import time

# Inicializar el detector de manos de Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5)

# Configurar la captura de video
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Configurar comunicación serial
try:
    ser = serial.Serial('COM4', 9600)
    time.sleep(2)
except serial.SerialException as e:
    print(f"No se pudo abrir el puerto: {e}")
    exit()

def get_finger_states(landmarks):
    """Calcula los estados de los dedos"""
    states = []
    for i in range(5):  # Asumiendo 5 dedos
        base = landmarks[3 + i*4]
        tip = landmarks[4 + i*4]
        # Si la punta está más arriba que la base, el dedo está extendido
        states.append(int(tip.y < base.y))
    return states

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("No se puede recibir el frame.")
        break

    # Procesar el frame con Mediapipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = hand_landmarks.landmark
            states = get_finger_states(landmarks)
            # Enviar los estados de los dedos al Arduino
            states_str = ','.join([str(state) for state in states])
            ser.write((states_str + '\n').encode('ascii'))

            # Dibujar landmarks
            mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Mostrar el frame
    cv2.imshow('Hand Tracking', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Limpiar
cap.release()
cv2.destroyAllWindows()
ser.close()
print("Recursos liberados y programa terminado.")
