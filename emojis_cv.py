import cv2
from fer import FER
from PIL import Image
import numpy as np

# Iniciando o modelo FER (Facial Expression Recognition)
detector = FER()

# Iniciando a captura da webcam
cap = cv2.VideoCapture(0)

# Checando se a webcam está funcionando
if not cap.isOpened():
    print("Erro: Não foi possível abrir a webcam")
    exit()

# Função para carregar e redimensionar a imagem do emoji
def load_emoji(emoji_path, size):
    emoji = Image.open(emoji_path).convert("RGBA")
    return emoji.resize((size, size), Image.LANCZOS)

# Função para adicionar emoji ao lado da face
def add_emoji(frame, emotion, x, y, w, h):
    # Definindo o caminho para os emojis
    emoji_paths = {
        'happy': 'emojis/happy.png',       # Caminho para o emoji "feliz"
        'angry': 'emojis/angry.png',       # Caminho para o emoji "raiva"
        'sad': 'emojis/sad.png',           # Caminho para o emoji "triste"
        'surprise': 'emojis/surprise.png', # Caminho para o emoji "surpreso"
        'neutral': 'emojis/neutral.png'    # Caminho para o emoji "normal/neutral"
    }
    
    if emotion in emoji_paths:
        # Carregar o emoji correspondente
        emoji_image = load_emoji(emoji_paths[emotion], h)  # Usando altura para manter a proporção

        # Converter o frame OpenCV (BGR) para PIL Image (RGB)
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Calcular a posição do emoji
        emoji_position = (x + w + 10, y)  # 10 pixels à direita da face

        # Sobrepor o emoji na posição calculada
        frame_pil.paste(emoji_image, emoji_position, emoji_image)

        # Converter de volta para OpenCV (BGR)
        frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)
    
    return frame

# Função para calcular o resumo das emoções
def summarize_emotions(emotions_detected):
    summary = {'happy': 0, 'angry': 0, 'sad': 0, 'surprise': 0, 'neutral': 0}
    for emotion in emotions_detected:
        emotion_name = max(emotion['emotions'], key=emotion['emotions'].get)
        if emotion_name in summary:
            summary[emotion_name] += 1
    return summary

while True:
    # Capturando frame da webcam
    ret, frame = cap.read()
    
    if not ret:
        print("Erro: Falha ao capturar a imagem")
        break
    
    # Detectando emoções no frame
    emotions = detector.detect_emotions(frame)

    # Resumo das emoções
    emotion_summary = summarize_emotions(emotions)

    # Desenhando a caixa ao redor da face e o rótulo da emoção
    for emotion in emotions:
        # Coletando a posição da face detectada
        (x, y, w, h) = emotion['box']

        # Detectando a emoção principal
        emotion_name = max(emotion['emotions'], key=emotion['emotions'].get)

        # Adicionando emoji ao lado da face detectada
        frame = add_emoji(frame, emotion_name, x, y, w, h)

    # Exibindo o resumo das emoções na tela
    y_offset = 30
    for emotion, count in emotion_summary.items():
        cv2.putText(frame, f'{emotion}: {count}', (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_offset += 30

    # Exibindo o frame com a detecção
    cv2.imshow('Deteccao de Expressoes Faciais com Emojis', frame)

    # Pressionar 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberando a webcam e fechando as janelas
cap.release()
cv2.destroyAllWindows()
