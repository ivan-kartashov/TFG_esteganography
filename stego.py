#IMPORTANTE Sebas, la mayoria de los comentarios son para ti, quiero que entiendas el codigo perfectamente para trabajar con el
#Aqui importamos las librerias necesarias 
#Permitira reducir el tamaño de los archivos, en este caso los mensajes que meteremos en las imagenes
import zlib 

#Aqui importamos los hashes para poder encriptar de una manera más segura
import hashlib 

#Permitira traducir bytes y bits a formato de texto y viceversa
import base64 

#Permitira abrir, sacar los datos de la imagen, y trabajar con las imagenes
from PIL import Image 

#Permitira implementar cifrado simétrico para nuestra contraseña que utilizaremos para desbloquear los mensajes
from cryptography.fernet import Fernet, InvalidToken

#Esta función convertira la contraseña introducida en un formato de hash
#para que no se pueda sacar el mensaje sin tener la contraseña, ya que el hashing ayudara bastante con la seguridad
def generate_password(genpasswd):

    hash = hashlib.sha256(genpasswd.encode()).digest()
    return base64.urlsafe_b64encode(hash)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"} #Extensiones de imágenes permitidas para ser subidas

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )


#Esta es la funcion que escondera el mensaje, utilizando los bits menos significativos de cada canal rgb de cada pixel de la imágen
def hide_message(soon_to_be_sus_img, img_sus, non_sus_message, user_password):

    #Aqui trabajamos con la imágen, y si la imágen falla alguna de las pruebas le devovlemos al usuario que la imágen no es válida
    try:
        img = Image.open(soon_to_be_sus_img)
        img = img.convert("RGB")  
        img.save(soon_to_be_sus_img) #Hacemos save para asegurar que la imagen sea integro
        img = Image.open(soon_to_be_sus_img)  

    except:
        return "Imágen no válida"
    pixels = img.load() #Esta si que es la linea que ahora sacara los datos de la imagen como los metadatos para que ahora trabajemos utilizandolos

    #Ahora comprimimos el mensaje proporcionado por el usuario para máximizar la cantidad de carácteres permisibles
    compressed_message = zlib.compress(non_sus_message.encode(), level=1)

    #Estas lineas encriptan la contraseña introducida por el usuario
    final_password = generate_password(user_password)
    fernet = Fernet(final_password)

    #En esta línea encriptamos el mensaje comprimido con la contraseña final barajeada y encriptada
    mensaje_cifrado = fernet.encrypt(compressed_message) 

#Aquí lo pasamos todo al formato binario
    binary = ''.join(format(b, '08b') for b in mensaje_cifrado)
    binary += '1111111111111110' #En esta línea le indicamos que el marcador final es esta secuencia, o sea, aquí termina el mensaje

    #Esta linea calcula el tamaño de la imágen y luego calcula el total de las posiciones totales
    width, height = img.size
    total_positions = width * height * 3

    #Aqui hacemos un raise si el mensaje del usuario es demasiado grande
    if len(binary) > total_positions:
        raise ValueError("Mensaje demasiado grande")

    #Aquí creamos una "semilla" a partir de la contraseña encriptada para generar una secuencia pseudoaleatoria apartir de esta "seed"
    seed = int(hashlib.sha256(user_password.encode()).hexdigest(), 16)
    a = (seed | 1) 
    b = seed % total_positions

    #Aquí usaremos nuestra seed para detectar cada posición y sobreescribir el bit menos significativo de canal rgb de cada pixel
    for i, bit in enumerate(binary):
        idx = (a * i + b) % total_positions #Está es la secuencia que ahora dependera de la "seed" creada antes, aquí se hace la indexación pseudoaleatoria de los bits

        #En estas lineas convertimos el idx en posiciones exáctas como (x, y) para posiciones de píxeles y (R=0,G=0,B=0) para los canales RGB de los píxeles
        pixel_index = idx // 3
        c = idx % 3
        x = pixel_index % width
        y = pixel_index // width

        rgb = list(pixels[x, y]) #Posiciones de píxeles
        rgb[c] = (rgb[c] & ~1) | int(bit) #Aquí se quita el bit menos significativo de cada canal rgb y se sustituye por el bit que necesitemos
        pixels[x, y] = tuple(rgb)

    img.save(img_sus) #Guardamos la imágen con información escondida


    img.save(img_sus) #Guardamos la imágen con información escondida

#Con esta función descoprimiremos la imagen, o sea vamos a encontrar los bits de mensaje oculto
#y posteriormente volver a convertirlo en un mensaje de texto
def extract_message(sus_img, user_password):

    try:
        img = Image.open(sus_img).convert("RGB")
    except Exception:
        return "Imagen no válida"
    pixels = img.load()

    width, height = img.size
    total_positions = width * height * 3

    #Aquí intentamos aberiguar la "seed" usada en la encriptación de datos para poder desencriptar correctamente las posiciones, en caso de que la contraseña sea correcta por supuesto
    seed = int(hashlib.sha256(user_password.encode()).hexdigest(), 16)
    a = (seed | 1)
    b = seed % total_positions

    #Creamos la lista de los bits menos significativos y le añadimos el mismo marcador que hay en el hide_message para detectar cuando se extrajo el mensaje completo
    bits = ""
    marker = '1111111111111110'

    #Aquí recorremos todas las posiciones, utilizando el indexing de una manera casi identica a como lo utilizamos en la función hide_message
    for i in range(total_positions):

        idx = (a * i + b) % total_positions

        pixel_index = idx // 3
        c = idx % 3
        x = pixel_index % width
        y = pixel_index // width

        bits += str(pixels[x, y][c] & 1) #Aquí extraemos el último bit de cada canal RGB

        if bits.endswith(marker): #Ahora le diremos que si encuentra el marcador de final que paré el for
            break

    fin = bits.find(marker)
    if fin == -1:
        raise ValueError("No se encontró mensaje")

    bits = bits[:fin] #Aquí utilizamos slicing para quitar el marcador de final ya que no aporta ninguna parte del mensaje, que ahora intentaremos de desencriptar con la contraseña

    data = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8)) #Esta linea reconstruira el mensaje, pero todavia cifrado

    #Aquí intentaremos descomprimir el mensaje utilizando la contraseña 
    try:
        final_password = generate_password(user_password)
        fernet = Fernet(final_password)
        mensaje_comprimido = fernet.decrypt(data)

    except InvalidToken:
        raise ValueError("Contraseña incorrecta o Imágen corrompida")

    mensaje = zlib.decompress(mensaje_comprimido) 
    return mensaje.decode()
