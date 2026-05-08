// Estas serán las variables donde guardaremos los valores de los campos html
const imagenInput = document.getElementById("imagenInput");
const mensajeArea = document.getElementById("mensajeInput");
const textCapacity = document.getElementById("TextCapacity");
const textRemaining = document.getElementById("TextRemaining");

// Esta es la variable que traemos de app.py
let maxChars = 0;

//Aquí apuntamos lo que sucede cuando cambiamos/ponemos imágen
imagenInput.addEventListener("change", function() {
    const file = this.files[0];
    const formData = new FormData();
    formData.append("imagen", file);

    fetch("/lengthofmessage", {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        // Guardamos el numero de las posiciones disponibles totales y las mostramos, ademas de limitar el número de carácteres al usuario en el textarea
        maxChars = parseInt(data); 
        textCapacity.innerText = "Número máximo de carácteres: " + maxChars;
        mensajeInput.maxLength = maxChars;
        
        // Esto para actualizar el contador que viene siguiente
        updateCharCounter();
    })
    .catch(error => console.error("Error:", error));//Control de errores de consola
});

//Esto es lo que "escucha" a que el usuario ponga input
mensajeArea.addEventListener("input", updateCharCounter);

function updateCharCounter() {
    const longitud = mensajeArea.value.length;
    
    // Por si no hay imágen guardada:
    if (maxChars === 0 && longitud === 0) return;

    const remaining = maxChars - longitud;

    textRemaining.innerText = "Carácteres restantes: " + remaining;

    //Aqui le mostraremos el usuario la cantidad de restantes en rojo si ha superado el 20% de la capacidad total de la imágen, esto se debe a que podria inflar el tamaño de la imágen/reducir su calidad muy notablemente
    if (remaining < (maxChars*0.8)) {
        textRemaining.style.color = "red";
    } else {
        textRemaining.style.color = "black";
    }
}















// document.getElementById("imagenInput").addEventListener("change", function() {
//     const file = this.files[0];
//     const formData = new FormData();
//     formData.append("imagen", file);

//     fetch("/lengthofmessage", {
//         method: "POST",
//         body: formData
//     })
//     .then(response => {
//         console.log("Respuesta:", response);
//         return response.text();
//     })
//     .then(data => {
//         console.log("Data:", data);
//         document.getElementById("TextCapacity").innerText =
//             "Máx Char: " + data;
//     });
// });


//         mensaje.addEventListener("input", updateCharCounter);

// function updateCharCounter() {
//     const longitud = mensaje.value.length;
//     const remaining = getElementById("TextCapacity") - longitud;

//     document.getElementById("TextRemaining").innerText =
//         "Char. Remaining: " + remaining;

//     if (remaining < 0) {
//         document.getElementById("TextRemaining").style.color = "red";
//     } else {
//         document.getElementById("TextRemaining").style.color = "black";
//     }
// }