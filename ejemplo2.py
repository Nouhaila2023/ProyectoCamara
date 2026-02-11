import cv2
import pytesseract
import numpy as np

# -------------------------------
# Configuración de Tesseract
# -------------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -------------------------------
# Cargar imagen del contador
# -------------------------------
img = cv2.imread("img/img1.jpeg")
if img is None:
    print("No se pudo cargar la imagen. Revisa el nombre o la ruta.")
    exit()

h, w, _ = img.shape

# -------------------------------
# Recorte de la zona de números
# Ajusta estos valores según tu contador
# -------------------------------
#x1 = int(w * 0.43)
#x2 = int(w * 0.80)
#y1 = int(h * 0.30)
#y2 = int(h * 0.50)
#roi = img[y1:y2, x1:x2]


x1 = int(w * 0.59)
x2 = int(w * 0.80)
y1 = int(h * 0.45)
y2 = int(h * 0.55)
roi = img[y1:y2, x1:x2]

if roi.size == 0:
    print("Error: el recorte está vacío. Revisa los valores de x1,x2,y1,y2")
    exit()

cv2.imwrite("img/img1_1.webp", roi)  # Guardar recorte para verificar

# -------------------------------
# Preprocesamiento
# -------------------------------
# Convertir a gris
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

# Mejorar contraste
gray = cv2.equalizeHist(gray)
gray_visible = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)  # Ajusta alpha para más contraste

# Suavizar ligeramente
gray_visible = cv2.GaussianBlur(gray_visible, (3,3), 0)

# Guardar imagen visible en gris
cv2.imwrite("img/img1_2.webp", gray_visible)

# -------------------------------
# OCR con Tesseract usando la imagen gris visible
# -------------------------------
config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'
texto = pytesseract.image_to_string(gray_visible, config=config)
numeros = ''.join(filter(str.isdigit, texto))

print("Lectura contador:", numeros)
