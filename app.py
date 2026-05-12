from flask import Flask, render_template, request, send_file, jsonify #flask es el que se encargara de levantar la web, render_template permite 
#cargarar archivos html, request nos permitira que el usuario interactue con el codigo a través de la interfaz y send_file permite que 
#el codigo le envie datos descargables al usuario
#Además, gracias a after_this_request podremos borrar los archivos creados en el servidor despúes de ejecutar todo el codigo necesario del usuario
import os #Permitira meternos en el sistema de archivos para sacar las imagenes
import uuid #Lo necesitamos para que no se vuelva a sobreescribir en la misma imágen, que me estaba pasando durante el testing del nuevo código optimizado
import threading #Importamos threading para crear 
from stego import hide_message, extract_message, allowed_file
from werkzeug.utils import secure_filename #Asegura que los nombres de las imagenes no sean problematicos
from PIL import Image

tasks = {} #Son las "tareas" del background, esto nos ayuda implementar un sistema asíncrona en el sistema para permitir que la web no cuelgue en render

app = Flask(__name__) #Crea una nueva instancia en el "servidor" flask
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") #Esto permitira mejorar la seguridad del sitio
app.config["MAX_CONTENT_LENGTH"] = 350 * 1024 * 1024 #Aquí limitaremos el tamaño de subida a 50 MB, Podriamos cambiarlo a 25 o 15 dependiendo de como nos ira
Image.MAX_IMAGE_PIXELS = 250_000_000 #Lo limitamos a 250.000.000 de píxeles
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

    if len(password) > 250:
        return "Contraseña demasiado grande, máximo 250 carácteres"
    
    if not allowed_file(image.filename):
        return "Formato no permitido"

    unique_id = str(uuid.uuid4()) #Este tio hará que hayan identificadores únicos en los nombres de las imágenes para que no se lien en el testing...
    filename = secure_filename(image.filename) #Aqui utilizamos el secure filename para eliminar espacios y hacer que el nombre sea seguro para nuestro programa
    
    #input guardara la imagen original en el fichero uploads y output guardara la nueva imágen con el mensaje oculto, utilizando el unique_id generado para cada imágen como identificador para que la app no se confunda de imagenes
    input = os.path.join(UPLOAD_FOLDER,f"{unique_id}_{filename}") 
    output = os.path.join(UPLOAD_FOLDER, f"{unique_id}_hidden.png")

    #Ahora la imagen se guarda físicamente, es decir, sin esto solamente se guardaria en la RAM y llamamos a la función final
    image.save(input)

    #CREAMOS EL ESTADO DE LA TAREA PARA PODER CONSULTAR SU PROGRESO DESDE EL FRONTEND
    tasks[unique_id] = {"status": "processing"}

    #DEFINIMOS LA FUNCION QUE SE EJECUTARA EN SEGUNDO PLANO PARA EVITAR BLOQUEAR EL SERVIDOR
    def background_task():
        try:
            hide_message(input, output, message, password)

            #Verificamos que la imagen se generó correctamente
            if not os.path.exists(output): #Si no se genera la imágen/no está en la ruta
                tasks[unique_id]["status"] = "error: No se genero la imagen"
                return

            #Marcamos la tarea como finalizada correctamente
            tasks[unique_id]["status"] = "done"

        except Exception as e:
            print("ERROR REAL:", e)
            tasks[unique_id]["status"] = f"error: {str(e)}"

        #BORRAMOS LOS ARCHIVOS PARA NO LLENAR EL DISCO EN RENDER (SE HACE AL FINAL DEL PROCESO ASINCRONO)
        try:
            if os.path.exists(input):
                os.remove(input)

        except Exception as e:
            print("Error borrando archivo de entrada:", e)

    #LANZAMOS EL HILO EN SEGUNDO PLANO PARA QUE LA PETICION HTTP NO ESPERE
    threading.Thread(target=background_task).start()

    #DEVOLVEMOS EL ID DE LA TAREA EN VEZ DEL ARCHIVO (AHORA EL FRONTEND LO GESTIONA)
    return {"task_id": unique_id}

#Esta es la función que se encargara de calcular la capacidad mágica de la imágen, para poder mostrarselo al usuario y para tener las métricas de errores
@app.route("/lengthofmessage", methods=["POST"])
def lengthofmessage():

    #La siguientes linea le pedira al usuario que seleccione una imagen y a continuación calcularemos su capacidad
    img_file = request.files["imagen"]

    try:
        img = Image.open(img_file)
        width, height = img.size

        capacidad_bits = width * height * 3 #Esta es la formula que tengo explicada en el .txt
        max_chars = (capacidad_bits - 16) // 8 #Esto es la formula de capacidad final, también explicada en el .txt bajo el nombre "Ivan"

        return str(max_chars)

    except Exception as e:
        print("ERROR:", e)
        return "0"



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

    #Aquí intentamos eliminar la imágen de la extracción cuando se extraiga el mensaje
    try:
        if os.path.exists(path):
            os.remove(path)

    except Exception as e:
        print("Error borrando archivo:", e)

    return render_template("escondinator.html", mensaje_extraido=message)

#Aquí comprobamos el estado del task devolviendo su id para nuestro javascript
@app.route("/status/<task_id>")
def status(task_id):

    if task_id not in tasks: #Si no hay task, entonces tampoco hay id de la task GAHOOK
        return jsonify({"status": "not_found"})

    return tasks[task_id]

#La ruta que de la app que utiliza JS para descargar el archivp
@app.route("/download/<task_id>")
def download(task_id):

    path = os.path.join(UPLOAD_FOLDER, f"{task_id}_hidden.png")

    if os.path.exists(path): #Si el archivo se genero correctamente en /hide
        return send_file(path, as_attachment=True)

    return jsonify("Archivo no listo") #Esto si no se genero o todavia no hay archivo

#Comprueba si el archivo se ejecuta directamente
if __name__ == "__main__": 

    #Lanza el servidor (Le quite el puerto y el debug para que render no se vuelva loco)
    app.run(debug=False) 
