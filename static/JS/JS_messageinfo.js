// Estas serán las variables donde guardaremos los valores de los campos html por su id en el documento .html
const imagenInput = document.getElementById("imagenInput");
const mensajeArea = document.getElementById("mensajeInput");
const textCapacity = document.getElementById("TextCapacity");
const textRemaining = document.getElementById("TextRemaining");
const textWritten = document.getElementById("TextWritten");
const scripthideForm = document.getElementById("hideForm")
const password = document.getElementById("passwordEncode")

// Esta es la variable que traemos de app.py
let maxChars = 0;

//Comprobaremos que la contraseña no sea mayor que 250 carácteres
password.addEventListener("input", () => {
    if (password.value.length > 250) {
        alert("Máximo 250 caracteres");
        password.value = password.value.slice(0, 250);
    }
});

//Aquí apuntamos lo que sucede cuando cambiamos/ponemos imágen
imagenInput.addEventListener("change", function() {
    const file = this.files[0];
    const formData = new FormData();
    formData.append("imagen", file); //Aquí el código pilla la imágen introducida por el usuario

    fetch("/lengthofmessage", { //Aquí pilla la ruta /lengthofmessage del servidor flask para conseguir el valor del return en este caso
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        // Guardamos el numero de las posiciones disponibles totales y las mostramos, ademas de limitar el número de carácteres al usuario en el textarea
        maxChars = parseInt(data); 
        textCapacity.innerText = "Número máximo de carácteres: " + maxChars;
        mensajeArea.maxLength = maxChars;
        
        // Esto para actualizar el contador que viene siguiente
        updateCharCounter();
    })
    .catch(error => console.error("Error:", error));//Control de errores de consola, donde error es el error completo, los errores de JavaScript deberian salir en la terminal al hacer f11 en la web y mirarlo
});

//Esto es lo que "escucha" a que el usuario ponga input
mensajeArea.addEventListener("input", updateCharCounter);

//Esta es la función para actualizar la cantidad de carácteres restantes cada vez que el usuario 
function updateCharCounter() {
    const longitud = mensajeArea.value.length;

    // Por si no hay imágen guardada:
    if (maxChars === 0 && longitud === 0) return;

    const written = longitud;
    const remaining = maxChars - longitud;

    textWritten.innerText = "Carácteres escritos: " + written;
    textRemaining.innerText = "Carácteres restantes: " + remaining;



    //Aqui le mostraremos el usuario la cantidad de restantes en rojo si ha superado el 20% de la capacidad total de la imágen, esto se debe a que podria inflar el tamaño de la imágen/reducir su calidad muy notablemente
    if (remaining < (maxChars*0.8)) {
        textRemaining.style.color = "red";
    } else {
        textRemaining.style.color = "black";
    }
}

//Aqui esperamos que alguien haga submit al formulario de esconder información
scripthideForm.addEventListener("submit", function (outcome) {
    outcome.preventDefault(); //Esto evita que se envie de la manera predeterminada

    const formData = new FormData(scripthideForm);

    fetch("/hide", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {

        const taskId = data.task_id;

        //Indicamos al usuario que la imágen se está procesando está procesando
        document.getElementById("processingUnit").innerText = "Escondiendo información... Buscando insectos... Buscando em... pues buscando... emmm...";

        //Polling (Que es como la intensidad de actualización, aqui es cada 2 segundos)
        const updateinfo = setInterval(() => {
            //Aquí busca el json con el proceso de segundo plano para mirar su estado y devolver respuesta dependiendo del estado
            fetch(`/status/${taskId}`)
            .then(res => res.json()) //Cuando la respuesta se reciba que lo convertiamos a json
            .then(status => { //Esto ya es cuando los datos son json y podemos procesarlos correctamente
                console.log("El estado del proceso es este ahora mismo:", status);
                if (status.status === "done") { //Una vez se termine el proceso esto >>>
                    clearInterval(updateinfo);

                    document.getElementById("processingUnit").innerText = "Imágen normal inconspiciosa preparada para la descarga inocente *guiño guiño*";
                    
                    //Aquí hacemos una descarga automática cuando el estado dice "done", utilizamos los datos del json que sacamos antes que se genera en app.py
                    window.location.href = `/download/${taskId}`;
                }
                if (status.status.startsWith("error")) { //En caso de error mostramos esto
                    clearInterval(updateinfo);
                    alert("Critico: " + status.status);
                    document.getElementById("processingUnit").innerText = "Aibaaaa errorrrrr";
                }
            });
        }, 2000); //Esa es la intensidad de la actualización, en este caso son 2 segundos
    });
});

//esta es la funcion que actua cuando se quita la imagen en el botón de quitado del html
function quitarimgseleccionadahide() {
    document.getElementById("imagenInput").value = "";
    textCapacity.innerText = null;
    textRemaining.innerText = null;
    textRemaining.style.color = "black";
    mensajeArea.maxLength = null;
    mensajeArea.value = null;
    textWritten.innerText = null;
}

function quitarimgseleccionadaextract() {
    document.getElementById("imagenInputExt").value = "";
    textCapacity.innerText = null;
    textRemaining.innerText = null;
    textRemaining.style.color = "black";
    mensajeArea.maxLength = null;
    mensajeArea.value = null;
    //Aqui recorremos cada elemento de la clase para quitar el contenido del extracted message flabadazabalright
    const elementos = document.getElementsByClassName("extracted_message");
    for (let i = 0; i < elementos.length; i++) {
        elementos[i].innerText = "";
    }
}

//Código para detectar si el usuario escribe en el campo de mensaje o si elige el metodo del archivo
const textarea = document.querySelector("textarea");
const fileInput = document.getElementById("messagefile");
//Escuchamos los cambios de si es archivo o texto, y dependiendo de lo que sea le desactivamos el textarea o lo dejamos activo
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    textarea.disabled = true;
  } else {
    textarea.disabled = false;
  }
});

function quitararchivoinput() {
    document.getElementById("messagefile").value = "";
    textCapacity.innerText = null;
    textRemaining.innerText = null;
    textRemaining.style.color = "black";
    mensajeArea.maxLength = null;
    mensajeArea.value = null;
}

//Miramos si se metio algún archivo para calcular la cantidad de caracteres
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) { //Si no hay ningún archivo o se quita
    textarea.disabled = true;
    textWritten.innerText = null;
    textRemaining.innerText = null;
  } else { //
    textarea.disabled = false;
    updateCharCounter(); 
  }
});