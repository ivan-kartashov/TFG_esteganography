from flask import Flask, render_template, request, send_file #flask es el que se encargara de levantar la web, render_template permite 
#cargarar archivos html, request nos permitira que el usuario interactue con el codigo a través de la interfaz y send_file permite que 
#el codigo le envie datos descargables al usuario
import os #Permitira meternos en el sistema de archivos para sacar las imagenes
import uuid #Lo necesitamos para que no se vuelva a sobreescribir en la misma imágen, que me estaba pasando durante el testing del nuevo código optimizado
from stego import hide_message, extract_message, allowed_file
from werkzeug.utils import secure_filename #Asegura que los nombres de las imagenes no sean problematicos

app = Flask(__name__) #Crea una nueva instancia en el "servidor" flask
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") #Esto permitira mejorar la seguridad del sitio
app.config["MAX_CONTENT_LENGTH"] = 999 * 1024 * 1024 #Aquí limitaremos el tamaño de subida a 50 MB, Podriamos cambiarlo a 25 o 15 dependiendo de como nos ira
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")#Dice el nombre de la carpeta en la que se guadaran las imagenes y asegura que esta esté
os.makedirs(UPLOAD_FOLDER, exist_ok=True) #Le obliga crear la carpeta uploads al SO, si ya esta deberá seguir con el código sin dar errores


#Esto hara que main.html se muestre como página principal si el usuario busca localhost:5000/ en su navegador
@app.route("/")
def index():
    return render_template("main.html") #La carpeta templates es estrictamente llamada así para que esto funcione correctamente

#Esto hara que se pueda acceder a está funcionalidad de la app con el enlace /escondinator
@app.route("/escondinator")
def escondinator():
    return render_template("escondinator.html")

@app.route("/hide", methods=["POST"]) #Define una dirección nueva "/hide"
def hide():

    image = request.files["imagen"] #Aqui le pediremos al usuario que le meta la imagen (esto esta entrelazado con las names del html) 

    #A continuación le pediremos al usuario que introduzca los demás campos (esto esta entrelazado con los name del html)
    #En el campo de mensaje le bloquearemos la opción de escribir manualmente si selecciona archivo, además si no hay archivo seleccionado permitiremos escribir (esto en javascript)
    if "file_message" in request.files and request.files["file_message"].filename != "":
        message_file = request.files["file_message"]
        message = message_file.read().decode()
    else:
        message = request.form["mensaje"]

    password = request.form["password"]

    if not allowed_file(image.filename):
        return "Formato no permitido"

    unique_id = str(uuid.uuid4()) #Este tio hará que hayan identificadores únicos en los nombres de las imágenes para que no se lien en el testing...
    filename = secure_filename(image.filename) #Aqui utilizamos el secure filename para eliminar espacios y hacer que el nombre sea seguro para nuestro programa
    #input guardara la imagen original en el fichero uploads y output guardara la nueva imágen con el mensaje oculto, utilizando el unique_id generado para cada imágen como identificador para que la app no se confunda de imagenes
    input = os.path.join(UPLOAD_FOLDER,f"{unique_id}_{filename}") 
    output = os.path.join(UPLOAD_FOLDER, f"{unique_id}_hidden.png")

    #Ahora la imagen se guarda físicamente, es decir, sin esto solamente se guardaria en la RAM y llamamos a la función final
    image.save(input)
    try:
        hide_message(input, output, message, password)
        if not os.path.exists(output): #Si no se genera la imágen/no está en la ruta
            return "No se genero la imágen"
    except Exception as e:
        print("ERROR REAL:", e)
        return f"Error al ocultar el mensaje: {str(e)}" #Salimos del programa si hay un error en la lógica en si, no en los archivos

    return send_file(output, as_attachment=True)


#Esta es la función que se encargara de calcular la capacidad mágica de la imágen, para poder mostrarselo al usuario y para tener las métricas de errores
@app.route("/lengthofmessage", methods=["POST"])
def lengthofmessage():

    #Las siguientes tres lineas le piden al usuario que seleccione una imagen y a continuación calcularemos su capacidad
    img = request.files["imagen"]

    path = os.path.join(UPLOAD_FOLDER, img.filename)
    img.save(path)

    from PIL import Image
    img = Image.open(path)
    width, height = img.size

    capacidad_bits = width * height * 3 #Esta es la formula que tengo explicada en el .txt
    max_chars = (capacidad_bits - 16) // 8 #Esto es la formula de capacidad final, también explicada en el .txt bajo el nombre "Ivan"

    return str(max_chars)

#Esta ruta de nuestra app permitira extraer los mensajes ocultos que se escondieron en las imagenes (Creo que si son solo mediante esta aplicación)
@app.route("/extract", methods=["POST"]) 
def extraer():
    imagen = request.files["imagen"] #Recibe la imagen que tiene el mensaje oculto
    password = request.form["password"] #Recibe la contraseña del usuario

    path = os.path.join(UPLOAD_FOLDER, imagen.filename) #Guarda la imágen
    imagen.save(path) #Guarda el archivo en el disco para que se pueda leer pixel por pixel

#Control de errores para ver si la contraseña o la imagen son correctas
    try: 
        message = extract_message(path, password)
    except:
        message = "Error: contraseña incorrecta/Imagen Sin mensaje"

    return render_template("escondinator.html", mensaje_extraido=message)


#Comprueba si el archivo se ejecuta directamente
if __name__ == "__main__": 

    #Lanza el servidor (Le quite el puerto y el debug para que render no se vuelva loco)
    app.run(debug=False) 