#IMPORTANTE Sebas, la mayoria de los comentarios son para ti, quiero que entiendas el codigo perfectamente para trabajar con el
#Aqui importamos las librerias necesarias 
#Permitira reducir el tamaño de los archivos, en este caso los mensajes que meteremos en las imagenes
import zlib 


#Nos permitira reeemplazar los valores de bits completamente aleatorios, de esta manera siendo mucho más dificil de detectar
import random 


#Aqui importamos los hashes para poder encriptar de una manera más segura
import hashlib 


#Permitira traducir bytes y bits a formato de texto y viceversa
import base64 


#Permitira abrir, sacar los datos de la imagen, y trabajar con las imagenes
from PIL import Image 


#Permitira implementar cifrado simétrico para nuestra contraseña que utilizaremos para desbloquear los mensajes
from cryptography.fernet import Fernet 


#Esta función convertira la contraseña introducida en un formato de hash
#para que no se pueda sacar el mensaje sin tener la contraseña, ya que el hashing ayudara bastante con la seguridad
def generate_password(genpasswd):

    hash = hashlib.sha256(genpasswd.encode()).digest()

    return base64.urlsafe_b64encode(hash)

#Esta es la funcion que escondera el mensaje, utilizando los bits menos significativos de cada canal rgb de cada pixel de la imágen
def hide_message(soon_to_be_sus_img, img_sus, non_sus_message, user_password):

    #Aqui trabajamos con la imágen
    img = Image.open(soon_to_be_sus_img) #Abre la imágen, pero no la analiza, la deja abierta para su futuro analizamiento

    pixels = img.load() #Esta si que es la linea que ahora sacara los datos de la imagen como los metadatos

    #Ahora comprimimos el mensaje proporcionado por el usuario para máximizar la cantidad de carácteres permisibles
    compressed_message = zlib.compress(non_sus_message.encode())

    #Con esta funcion generate_password vamos a encriptar el mensaje con la contraseña que ciframos antes
    final_password = generate_password(user_password) 
    
    fernet = Fernet(final_password)

    mensaje_cifrado = fernet.encrypt(compressed_message) #En esta línea encriptamos el mensaje comprimido con la contraseña final barajeada y encriptada

    #Convertimos el mensaje a formato binario utizando un marcador único como de final
    try:
        binary = ''.join(format(b, '08b') for b in mensaje_cifrado) #Convierte la cadena del mensaje final a una cadena de bits
        binary += '1111111111111110'  #Este es el marcador del final
    except:
        print("Error en las cadenas binarias.")

    width, height = img.size #Ver el tamaño de imágen para luego calcular la cantidad de carácteres que le permitiremos al usuario

    #Aqui hemos creado una lista de posiciones para que el mensaje oculto sea repartido por los bits de la imagen de una manera aleatoria y díficil de detectar
    positions = [(x, y, c) for y in range(height)
                            for x in range(width) 
                            for c in range(3)] #Le tuve que meter enters porque de otra manera no se poruqe no me funcionaba XD

    random.seed(user_password) #Usando la semilla "password" podemos asegurarnos de que la encriptación va a ser única para cada contraseña, lo que significa que cada contraseña igual sera encriptada/desencriptada de la misma manera y sin dar errores (ojala)
    random.shuffle(positions)

    if len(binary) > len(positions): #Un puequeño flujo de errores
        raise ValueError("Mensaje demasiado grande")

    #Aqui ocultamos los bits que componen nuestro mensaje escondido en los canales rgb de los pixeles de la imágen
    for i, bit in enumerate(binary):
        x, y, c = positions[i]
        rgb = list(pixels[x, y])
        rgb[c] = (rgb[c] & ~1) | int(bit)
        pixels[x, y] = tuple(rgb)

    img.save(img_sus)


#Con esta función descoprimiremos la imagen, o sea vamos a encontrar los bits de mensaje oculto
#y posteriormente volver a convertirlo en un mensaje de texto
def extract_message(sus_img, user_password):

    #Abrimos la imagen donde hay un mensaje escondido
    img = Image.open(sus_img)

    pixels = img.load() #Cargamos los datos de la imágen donde supuestamente hay un mensaje escondido (guiño, guiño)

    width, height = img.size #Sacamos el tamaño de la imágen de nuevo

    positions = [(x, y, c) for y in range(height)
                            for x in range(width)
                            for c in range(3)]

    #ES IMPORTANTE: Aqui no hay flujo de errores porque el flujo de errores se encuentra en un nível más alto del backend, mire app.py para más detalles
    random.seed(user_password) #Generamos (O mejor dicho, regeneramos la contraseña) como antes pero esta vez para otro fin (extracción)
    random.shuffle(positions)

    bits = ""
    for x, y, c in positions:
        bits += str(pixels[x, y][c] & 1)

    #Buscamos el final de la secuencia
    fin = bits.find('1111111111111110')
    bits = bits[:fin]

    #Convertimos los bits en bytes
    data = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

    #Desciframos los bytes usando la contraseña final...
    final_password = generate_password(user_password)
    fernet = Fernet(final_password)
    mensaje_comprimido = fernet.decrypt(data)

    #Descomprimimos el mensaje y lo devolvemos al usuario
    mensaje = zlib.decompress(mensaje_comprimido)

    return mensaje.decode()