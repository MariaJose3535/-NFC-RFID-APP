import serial
import mysql.connector
import tkinter as tk
from tkinter import messagebox

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="nfc"
)
cursor = db.cursor()

ser = serial.Serial('COM10', 115200, timeout=1)

modo_registro = False

def registrar_tarjeta():
    global modo_registro
    nombre = entry_nombre.get()

    if nombre.strip() == "":
        messagebox.showwarning("Error", "Ingresa un nombre")
        return

    modo_registro = True
    label_estado.config(text="Modo registro activo, pasa la tarjeta", fg="blue")

def leer_serial():
    global modo_registro

    linea = ser.readline().decode('utf-8').strip()

    if "HEX:" in linea:
        uid = linea.replace("HEX:", "").strip()
        label_uid.config(text="UID: " + uid)

        if modo_registro:
            nombre = entry_nombre.get()

            try:
                cursor.execute(
                    "INSERT INTO autorizados (uid, nombre) VALUES (%s, %s)",
                    (uid, nombre)
                )
                db.commit()
                messagebox.showinfo("Registro", "Tarjeta registrada")
            except:
                messagebox.showwarning("Error", "Tarjeta ya registrada")

            modo_registro = False
            label_estado.config(text="Esperando tarjeta...", fg="black")
        else:
            cursor.execute("SELECT nombre FROM autorizados WHERE uid = %s", (uid,))
            resultado = cursor.fetchone()

            if resultado:
                estado = "PERMITIDO"
                nombre = resultado[0]
                label_estado.config(text="ACCESO PERMITIDO: " + nombre, fg="green")
            else:
                estado = "DENEGADO"
                nombre = "Desconocido"
                label_estado.config(text="ACCESO DENEGADO", fg="red")

            cursor.execute(
                "INSERT INTO accesos (uid, estado, nombre) VALUES (%s, %s, %s)",
                (uid, estado, nombre)
            )
            db.commit()

    ventana.after(100, leer_serial)

ventana = tk.Tk()
ventana.title("Sistema NFC")
ventana.geometry("400x300")

label_uid = tk.Label(ventana, text="UID: ---", font=("Arial", 12))
label_uid.pack(pady=10)

entry_nombre = tk.Entry(ventana)
entry_nombre.pack(pady=5)

label_estado = tk.Label(ventana, text="Esperando tarjeta...", font=("Arial", 14))
label_estado.pack(pady=10)

btn_registrar = tk.Button(ventana, text="Registrar Tarjeta", command=registrar_tarjeta)
btn_registrar.pack(pady=20)

ventana.after(100, leer_serial)

ventana.mainloop()