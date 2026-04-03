# from stego import hide_message, extract_message
# import tkinter as tk
# from tkinter import filedialog, messagebox, scrolledtext
# from stego import hide_message, extract_message


# def seleccionar_imagen():
#     ruta = filedialog.askopenfilename(
#         filetypes=[("Imagenes", "*.png *.bmp")]
#     )
#     return ruta

# def ocultar():
#     ruta = seleccionar_imagen()
#     if not ruta:
#         return

#     mensaje = texto_mensaje.get("1.0", tk.END).strip()
#     password = entrada_password.get()

#     if not mensaje or not password:
#         messagebox.showerror("Error", "Faltan datos")
#         return

#     salida = filedialog.asksaveasfilename(
#         defaultextension=".png",
#         filetypes=[("PNG", "*.png")]
#     )

#     if salida:
#         try:
#             hide_message(ruta, salida, mensaje, password)
#             messagebox.showinfo("Éxito", "Mensaje oculto correctamente")
#         except Exception as e:
#             messagebox.showerror("Error", str(e))

# def extraer():
#     ruta = seleccionar_imagen()
#     if not ruta:
#         return

#     password = entrada_password_extraer.get()

#     try:
#         mensaje = extract_message(ruta, password)
#         texto_resultado.delete("1.0", tk.END)
#         texto_resultado.insert(tk.END, mensaje)
#     except:
#         messagebox.showerror("Error", "Contraseña incorrecta o imagen inválida")

# # ---------------- INTERFAZ ---------------- #

# ventana = tk.Tk()
# ventana.title("Esteganografía")
# ventana.geometry("600x500")

# # ---- OCULTAR ----
# tk.Label(ventana, text="Ocultar mensaje", font=("Arial", 14, "bold")).pack(pady=5)

# texto_mensaje = scrolledtext.ScrolledText(ventana, height=5)
# texto_mensaje.pack(fill="x", padx=10)

# tk.Label(ventana, text="Contraseña").pack()
# entrada_password = tk.Entry(ventana, show="*")
# entrada_password.pack()

# tk.Button(ventana, text="Ocultar mensaje", command=ocultar).pack(pady=5)

# # ---- EXTRAER ----
# tk.Label(ventana, text="Extraer mensaje", font=("Arial", 14, "bold")).pack(pady=10)

# tk.Label(ventana, text="Contraseña").pack()
# entrada_password_extraer = tk.Entry(ventana, show="*")
# entrada_password_extraer.pack()

# tk.Button(ventana, text="Extraer mensaje", command=extraer).pack(pady=5)

# texto_resultado = scrolledtext.ScrolledText(ventana, height=5)
# texto_resultado.pack(fill="x", padx=10)

# # ---------------- EJECUCIÓN ---------------- #

# ventana.mainloop()