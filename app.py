from flask import Flask, render_template, request, send_file #flask es el que se encargara de levantar la web, render_template permite 
#cargarar archivos html, request nos permitira que el usuario interactue con el codigo a través de la interfaz y send_file permite que 
#el codigo le envie datos descargables al usuario

import os #Permitira meternos en el sistema de archivos para sacar las imagenes

from stego import hide_message, extract_message


app = Flask(__name__) #Crea una nueva instancia en el "servidor" flask
UPLOAD_FOLDER = "uploads" #Dice el nombre de la carpeta en la que se guadaran las imagenes
os.makedirs(UPLOAD_FOLDER, exist_ok=True) #Le obliga crear la carpeta uploads al SO, si ya esta deberá seguir con el código sin dar errores


#Esto hara que index.html se muestre como página principal si el usuario busca localhost:5000/ en su navegador
@app.route("/")
def index():
    return render_template("index.html") #La carpeta templates es estrictamente llamada así para que esto funcione correctamente


@app.route("/hide", methods=["POST"]) #Define una dirección nueva "/hide"
def hide():
    #Las siguientes tres lineas le piden al usuario que seleccione una imagen y introduzca los demás campos
    image = request.files["imagen"]
    message = request.form["mensaje"]
    password = request.form["password"]

    #input guardara la imagen original en el fichero uploads y output guardara la nueva imágen con el mensaje oculto
    input = os.path.join(UPLOAD_FOLDER, image.filename)
    output = os.path.join(UPLOAD_FOLDER, "hidden.png")

    #Ahora la imagen se guarda físicamente, es decir, sin esto solamente se guardaria en la RAM y llamamos a la función final
    image.save(input)
    hide_message(input, output, message, password)

    return send_file(output, as_attachment=True)


@app.route("/extract", methods=["POST"]) #Lo mismo que lo anterior pero ahora con la funcionalidad de extraer el mensaje oculto
def extraer():
    imagen = request.files["imagen"] #Recibe la imagen que tiene el mensaje oculto
    password = request.form["password"] #Recibe la contraseña del usuario

    path = os.path.join(UPLOAD_FOLDER, imagen.filename) #Guarda temporalmene la imágen
    imagen.save(path) #Guarda el archivo en el disco para que se pueda leer pixel por pixel

    try: #Control de errores para ver si la contraseña o la imagen son correctas
        message = extract_message(path, password)
    except:
        message = "Error: contraseña incorrecta o imagen inválida"

    return render_template("index.html", mensaje_extraido=message)

if __name__ == "__main__": #Comprueba si el archivo se ejecuta directamente
    app.run(debug=True) #Lanza el servidor