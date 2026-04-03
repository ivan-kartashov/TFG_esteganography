#Aqui importamos las librerias necesarias 
import zlib #Permitira reducir el tamaño de los archivos, en este caso las imagenes
import random #Nos permitira reeemplazar los valores de bits completamente aleatorios, de esta manera siendo mucho más dificil de detectar
import hashlib #Aqui importamos los hashes para poder encriptar de una manera más segura
import base64 #Permitira traducir bytes y bits a formato de texto y viceversa
from PIL import Image #Permitira abrir y leer los datos de la imagen
from cryptography.fernet import Fernet #Permitira implementar cifrado simétrico
#

#Esta función convertira la contraseña introducida en un formato de hash
#para maximizar la seguridad de la contraseña
def generate_password(password):
    hash = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(hash)

#Esta es la funcion clave, esta será la responsable de esconder el mensage dentro de la imágen, utilizando los bits menos significativos
#para esconder ahi los bits, que luego si se reforman se puede extraer el mensage
def hide_message(img_input, img_output, message, password):

    #Conseguimos la imágen
    img = Image.open(img_input)
    pixels = img.load()
    width, height = img.size

    #Ahora comprimimos el mensaje proporcionado por el usuario
    compressed_message = zlib.compress(message.encode())

    #Haciendo uso de la funcion generate_password vamos a encriptar el mensaje con la contraseña cifrada
    final_password = generate_password(password)
    fernet = Fernet(final_password)
    message_cifrado = fernet.encrypt(compressed_message)

    #Convertimos el mensaje en formato binario
    binary = ''.join(format(b, '08b') for b in message_cifrado)
    binary += '1111111111111110'  # marcador fin

    #Aqui hemos creado una lista de posiciones para que el mensaje oculto sea repartido por los bits de la imagen de una manera
    #aleatoria y díficil de detectar
    positions = [(x, y, c) for y in range(height)
                            for x in range(width) 
                            for c in range(3)]

    random.seed(password)
    random.shuffle(positions)

    if len(binary) > len(positions):
        raise ValueError("Mensaje demasiado grande")

    #Aqui ocultamos los bits que componen nuestro mensaje escondido en los canales rgb de los pixeles
    for i, bit in enumerate(binary):
        x, y, c = positions[i]
        rgb = list(pixels[x, y])
        rgb[c] = (rgb[c] & ~1) | int(bit)
        pixels[x, y] = tuple(rgb)

    img.save(img_output)


#Con esta función descoprimiremos la imagen, o sea vamos a encontrar los bits de mensaje oculto
#y posteriormente volver a convertirlo en un mensaje de texto
def extract_message(hidden_image, password):

    #Extraemos la imagen donde hay un mensaje escondido
    img = Image.open(hidden_image)
    pixels = img.load()
    width, height = img.size

    positions = [(x, y, c) for y in range(height)
                            for x in range(width)
                            for c in range(3)]

    random.seed(password)
    random.shuffle(positions)

    bits = ""
    for x, y, c in positions:
        bits += str(pixels[x, y][c] & 1)

    #Buscamos el final
    fin = bits.find('1111111111111110')
    bits = bits[:fin]

    #Convertimos los bits en bytes
    data = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

    #Desciframos los bytes
    final_password = generate_password(password)
    fernet = Fernet(final_password)
    mensaje_comprimido = fernet.decrypt(data)

    #Descomprimimos el mensaje y lo devolvemos al usuario
    mensaje = zlib.decompress(mensaje_comprimido)

    return mensaje.decode()