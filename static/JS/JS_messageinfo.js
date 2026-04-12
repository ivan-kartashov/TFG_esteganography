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
        // Guardamos el numerito que nos traen de python y lo ponemos
        maxChars = parseInt(data); 
        textCapacity.innerText = "Máx Char: " + maxChars;
        
        // Esto para actualizar el contador que viene siguiente
        updateCharCounter();
    })
    .catch(error => console.error("Error:", error));//Control de errores de consola para nosotros, los del backend Sebas
});

//Esto es lo que "escucha" a que el usuario ponga input
mensajeArea.addEventListener("input", updateCharCounter);

function updateCharCounter() {
    const longitud = mensajeArea.value.length;
    
    // Por si no hay imágen guardada:
    if (maxChars === 0 && longitud === 0) return;

    const remaining = maxChars - longitud;

    textRemaining.innerText = "Char. Remaining: " + remaining;

    //Esto es para que se vea más bonito cuando nos quedan pocos (relativamente pocos) caracteres pero es bastante (y muy bastante) imporbable que suceda
    if (remaining < 5000) {
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