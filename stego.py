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
#Lo he vuelto a meter para hacer un shuffle y garantizar consistencia e integridad porque antes sobreescribia posicones y se perdia información
import random 
#La libreria math la utilizaremos para luego calcular la integridad de las posiciones para no escribirlas otra vez
import math
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
        #img.save(soon_to_be_sus_img) #Hacemos save para asegurar que la imagen sea integro
        #img = Image.open(soon_to_be_sus_img)  
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

    marker = '1111111111111110'#En esta línea le indicamos que el marcador final es esta secuencia, o sea, aquí termina el mensaje

    #Esta linea calcula el tamaño de la imágen y luego calcula el total de las posiciones totales
    width, height = img.size
    total_positions = width * height * 3
    total_bits = (len(mensaje_cifrado) * 8) + len(marker)

    #Aqui hacemos un raise si el mensaje del usuario es demasiado grande
    if total_bits > total_positions:
        raise ValueError("Mensaje demasiado grande")

    #Aquí creamos una "semilla" de secuencias pseudoaleatorias a partir de la contraseña encriptada para generar una secuencia pseudoaleatoria apartir de esta "seed"
    seed = int(hashlib.sha256(user_password.encode()).hexdigest(), 16)
    #Nos hacemos seguros de que a sea impar y también de que sea coprimo de total_positions para que no hayan colisiones
    a = (seed | 1) % total_positions
    while math.gcd(a, total_positions) != 1: #Aqui gcd (greatest common divisor es el máximo común divisor, y en ese caso queremos que sea 1 para garantizar la integridad)
        a = (a + 2) % total_positions  
    b = seed % total_positions

    bit_index = 0

    #Aquí usaremos nuestra seed para detectar cada posición y sobreescribir el bit menos significativo de canal rgb de cada pixel, en este caso procesando byte por byte
    for byte in mensaje_cifrado:
        for eachbit in range(8): #O sea, por cada bit

            bit = (byte >> (7 - eachbit)) & 1

            #Usando el maximo comun divisor podremos detectar posiciones sin guardarlas en listas, lo que permite ahorrar RAM y optimizar el programa
            idx = (a * bit_index + b) % total_positions
            pixel_index = idx // 3
            c = idx % 3
            x = pixel_index % width
            y = pixel_index // width

            rgb = list(pixels[x, y]) #Posiciones de píxeles
            rgb[c] = (rgb[c] & ~1) | bit #Aquí se quita el bit menos significativo de cada canal rgb y se sustituye por el bit que necesitemos
            pixels[x, y] = tuple(rgb)
            
            red, green, blue = pixels[x, y] #Posicionamos el píxel que vamos a cambiar

            #Este if selecciona el canal, si el canal es 0 (primer canal) se seleccioanra el canal rojo, si es 2 seleccionaremos el verde y si no es ninguno de los dos que es azul.
            if c == 0:
                red = (red & ~1) | int(bit) #Quitamos el bit menos significativo (LSB) y proseguimos a insertar un bit (La | es un AND)
            elif c == 1:
                green = (green & ~1) | int(bit)
            else:
                blue = (blue & ~1) | int(bit)
            pixels[x, y] = (red, green, blue) #Guardamos el píxel modificado, sumamos el indice y procedemos a reiterar otro píxel nuevo

            bit_index += 1

    #Ahora se añade el final de la escribientura con el marcador de final, utilizando la misma lógica del for anterior
    for bit in marker:
        idx = (a * bit_index + b) % total_positions
        pixels = idx // 3
        c = idx % 3
        x = pixels % width
        y = pixels // width  
        red, green, blue = pixels[x, y] 
        if c == 0:
            red = (red & ~1) | int(bit) 
        elif c == 1:
            green = (green & ~1) | int(bit)
        else:
            blue = (blue & ~1) | int(bit)
        pixels[x, y] = (red, green, blue) 
        bit_index += 1

    img.save(img_sus) #Guardamos la imágen con información escondida
#Con esta función descoprimiremos la imagen, o sea vamos a encontrar los bits de mensaje oculto
#y posteriormente volver a convertirlo en un mensaje de texto
def extract_message(sus_img, user_password):

    try:
        img = Image.open(sus_img).convert("RGB")
    except:
        return "Imagen no válida"

    pixels = img.load()
    width, height = img.size
    total_positions = width * height * 3

    #Esto tiene el mismo funcionamiento y garantiza lo mismo que el código mismo en hide_message
    seed = int(hashlib.sha256(user_password.encode()).hexdigest(), 16)
    a = (seed | 1) % total_positions
    while math.gcd(a, total_positions) != 1:
        a = (a + 2) % total_positions
    b = seed % total_positions

    #Ahora pondremos el marcador en formato de bytes, para que sea más eficiente en la memoria
    marker = b'\xff\xfe'  
    marker_len = len(marker)

    buffer = bytearray() #Aquí guardaremos el mensaje final reconstruido
    current_byte = 0
    bit_count = 0

    marker_buffer = bytearray() #Asegura que se guarden los ultimos bits para el marcador final


    for i in range(total_positions):

        # CALCULO DIRECTO DE POSICION USANDO LCG COPRIMO PARA EVITAR COLISIONES Y GARANTIZAR MISMO ORDEN
        idx = (a * i + b) % total_positions #Calculamos la posicion pseudoaleatoria y desde aqui el código es casi identico a /hide, con algunas excepciones

        pixel_index = idx // 3
        c = idx % 3
        x = pixel_index % width
        y = pixel_index // width

        bit = pixels[x, y][c] & 1 #Aquí extraemos el bit menos significativo de cada canal rgb de cada pixel

        #Aqui reconstruimos el bite bit a bit
        current_byte = (current_byte << 1) | bit
        bit_count += 1

        #Cuando el byte sea definitivo que se añada al mensaje final extraido
        if bit_count == 8:
            buffer.append(current_byte)
            #Desde esta linea se empieza a buscar el marker final para saber si es hora de parar de buscar o seguir sacando
            marker_buffer.append(current_byte)
            if len(marker_buffer) > marker_len:
                marker_buffer.pop(0)

            current_byte = 0
            bit_count = 0

            if bytes(marker_buffer) == marker: #Una vez que vimos el marker se para el for
                break

    if len(buffer) < marker_len:
        raise ValueError("No se encontró mensaje")

    #En esta linea le quitamos el marker al mensaje final
    data = bytes(buffer[:-marker_len])

    try:
        final_password = generate_password(user_password)
        fernet = Fernet(final_password)
        mensaje_comprimido = fernet.decrypt(data)

    except InvalidToken:
        raise ValueError("Contraseña incorrecta o Imágen corrompida")

    mensaje = zlib.decompress(mensaje_comprimido)
    return mensaje.decode()
