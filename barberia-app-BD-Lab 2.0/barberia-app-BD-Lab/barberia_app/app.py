from tkinter import ttk, messagebox, Label, END
import tkinter as tk
from tkcalendar import DateEntry
from pymongo import MongoClient
from dotenv import load_dotenv
import os  
from PIL import Image, ImageTk
from datetime import datetime

# Cargar variables del .env
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

# Verifica colección sino existe la crearla
if "citas" not in db.list_collection_names():
    db.create_collection("citas")
citas = db["citas"]
barberos = db["barberos"]
servicios = db["servicios"]

#Función para refrescar los datos ----------------------------------------
def actualizar_listas():
    combo_servicio['values'] = obtener_servicios()
    combo_barbero['values'] = obtener_barberos()

# Datos de la colección servicios ----------------------------
def obtener_servicios():
    try:
        return [servicio["nombre"] for servicio in servicios.find()]
    except Exception as e:
        print("Error al obtener servicios:", e)
        return []

# Datos de la colección Barberos ------------------------------
def obtener_barberos():
    return [barbero["nombre"] for barbero in barberos.find()] 


# --- Verificar conexión y colección ---
print("Colecciones en la base de datos:", db.list_collection_names())  

# --- Insertar una cita de prueba ---
if citas.count_documents({}) == 0:  
    citas.insert_one({
        "nombre_cliente": "Cliente de Prueba",
        "fecha": "2025-02-02",
        "hora": "10:00",
        "servicio": "Corte clásico",
        "barbero": "Lolo (Prueba)"
    })
    print("Cita de prueba insertada.")


# Función para agregar cita
def agregar_cita():
    try:
        # Validar campos vacíos
        if not all([entry_nombre.get(), combo_hora.get(), combo_servicio.get(), combo_barbero.get()]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        # Convertir fecha a string "YYYY-MM-DD"
        fecha_str = cal_fecha.get_date().strftime("%Y-%m-%d") 

        # Verificar duplicados
        if citas.find_one({"fecha": fecha_str, "hora": combo_hora.get()}):
            messagebox.showerror("Error", "¡Ya hay una cita agendada a esa hora!")
            return

        # Guardar cita
        nueva_cita = {
            "nombre_cliente": entry_nombre.get(),
            "fecha": fecha_str,  # Se guarda como string
            "hora": combo_hora.get(),
            "servicio": combo_servicio.get(),
            "barbero": combo_barbero.get()
        }
        citas.insert_one(nueva_cita)
        messagebox.showinfo("Éxito", "Cita agendada!")
        limpiar_campos()
        mostrar_citas()

    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    

# Función para mostrar citas en la tabla
def mostrar_citas():
    # Limpiar tabla antes de actualizar
    for row in tabla.get_children():
        tabla.delete(row)
    # Obtener todas las citas de MongoDB
    for cita in citas.find():
        tabla.insert("", "end", values=(
            cita["nombre_cliente"],
            cita["fecha"],
            cita["hora"],
            cita["servicio"],
            cita["barbero"]
        ))

# Función para limpiar campos después de guardar
def limpiar_campos():
    entry_nombre.delete(0, END)
    combo_hora.set("")
    combo_servicio.set("")
    combo_barbero.set("")

# Ventana principal
root = tk.Tk()
root.title("Formulario de Cita - Barbería")
root.geometry("500x400")
root.configure(bg="#f2f2f2")  # Fondo claro


# Logo de la barbería
try:
# Cargar imagen y redimensionar (ej: 200px de ancho)
    logo_original = Image.open("logo.png")
    logo_redimensionado = logo_original.resize((200, 200), Image.LANCZOS)  # Ajustar el tamaño (ancho, alto)
    logo = ImageTk.PhotoImage(logo_redimensionado)
    Label(root, image=logo).pack(pady=10)
except Exception as e:
    print("Error al cargar el logo:", e)
    Label(root, text="Barbería Clásica", font=("Arial", 16)).pack(pady=10)

# ----- Estilo con ttk -----
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 11), background="#f2f2f2")
style.configure("TButton",
                font=("Arial", 12, "bold"),
                foreground="white",
                background="#003366",
                padding=10)
style.map("TButton",
        background=[("active", "#cc0000")])

style.configure("TCombobox",
                padding=5,
                font=("Arial", 11))

# ----- Frame principal -----
frame_principal = tk.Frame(root, bg="#f2f2f2")
frame_principal.pack(padx=20, pady=20)

frame_form = tk.Frame(frame_principal, bg="#f2f2f2")
frame_form.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# ----- Campos del formulario -----
ttk.Label(frame_form, text="Nombre del cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_nombre = ttk.Entry(frame_form, width=30)
entry_nombre.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_form, text="Fecha:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
cal_fecha = DateEntry(frame_form, width=27, background="#003366", foreground="white", borderwidth=2)
cal_fecha.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_form, text="Hora:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
horas = ["04:00", "05:00", "06:00", "07:00", "08:00", "09:00",
        "10:00", "11:00", "12:00", "13:00", "14:00", "15:00",
        "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
combo_hora = ttk.Combobox(frame_form, values=horas, width=27)
combo_hora.grid(row=2, column=1, padx=5, pady=5)

# Combobox para servicio
ttk.Label(frame_form, text="Servicio:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
combo_servicio = ttk.Combobox(frame_form, width=27)
combo_servicio.grid(row=3, column=1, padx=5, pady=5)

# Combobox para barbero
ttk.Label(frame_form, text="Barbero:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
combo_barbero = ttk.Combobox(frame_form, width=27)
combo_barbero.grid(row=4, column=1, padx=5, pady=5)

# Actualizar los valores de los Combobox
actualizar_listas()



# ----- Botón estilizado -----
ttk.Button(frame_form, text="Guardar Cita", command=agregar_cita).grid(row=5, column=0, columnspan=2, pady=15)

# Función para borrar cita
def borrar_cita():
    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showerror("Error", "Selecciona una cita para borrar")
        return
    datos = tabla.item(seleccionado)
    nombre = datos["values"][0]
    fecha = datos["values"][1]
    hora = datos["values"][2]
    
    confirmar = messagebox.askyesno("Confirmar", f"¿Borrar cita de {nombre} el {fecha} a las {hora}?")
    if confirmar:
        citas.delete_one({"nombre_cliente": nombre, "fecha": fecha, "hora": hora})
        mostrar_citas()
        messagebox.showinfo("Éxito", "Cita borrada")

# Función para editar cita (rellena el formulario al seleccionar)
def editar_cita():
    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showerror("Error", "Selecciona una cita para editar")
        return
    datos = tabla.item(seleccionado)
    limpiar_campos()
    entry_nombre.insert(0, datos["values"][0])
    cal_fecha.set_date(datos["values"][1])
    combo_hora.set(datos["values"][2])
    combo_servicio.set(datos["values"][3])
    combo_barbero.set(datos["values"][4])

#Función para actualizar cita tras el formulario
def actualizar_cita():
    seleccionado = tabla.focus()
    if not seleccionado:
        messagebox.showerror("Error", "Selecciona una cita para actualizar")
        return

    # Obtener datos originales
    datos = tabla.item(seleccionado)
    nombre_original = datos["values"][0]
    fecha_original = str(datos["values"][1])  # asegurarse que sea string
    hora_original = str(datos["values"][2])

    # Filtro original para encontrar la cita en MongoDB
    filtro = {
        "nombre_cliente": nombre_original,
        "fecha": fecha_original,
        "hora": hora_original
    }

    # Nuevos datos del formulario
    nuevos_datos = {
        "nombre_cliente": entry_nombre.get(),
        "fecha": str(cal_fecha.get_date()),  # convertir a string
        "hora": combo_hora.get(),
        "servicio": combo_servicio.get(),
        "barbero": combo_barbero.get()
    }

    # Actualizar en la base de datos
    resultado = citas.update_one(filtro, {"$set": nuevos_datos})
    
    if resultado.modified_count > 0:
        messagebox.showinfo("Éxito", "Cita actualizada")
        mostrar_citas()  # <<<<<<<<<<<<<< Refrescar tabla
        limpiar_campos()  # (opcional)
    else:
        messagebox.showwarning("Sin cambios", "No se modificó ningún dato")


# ----- Frame para botones debajo de la tabla -----
frame_botones = tk.Frame(root, bg="#f2f2f2")
frame_botones.pack(pady=10)

# Botón Editar
btn_editar = ttk.Button(frame_botones, text="Editar Cita", command=editar_cita)
btn_editar.grid(row=0, column=0, padx=10)

# Botón Actualizar
btn_actualizar = ttk.Button(frame_botones, text="Actualizar Cita", command=actualizar_cita)
btn_actualizar.grid(row=0, column=1, padx=10)

# Botón Borrar
btn_borrar = ttk.Button(frame_botones, text="Borrar Cita", command=borrar_cita)
btn_borrar.grid(row=0, column=2, padx=10)


# Frame de la tabla (ya con fondo gris claro como el resto)
frame_tabla = tk.Frame(root, bg="#f2f2f2")
frame_tabla.pack(pady=10)

# Estilo para el Treeview
style.configure("Treeview",
                font=("Arial", 11),
                rowheight=28,
                background="white",
                fieldbackground="white",
                foreground="black")

style.configure("Treeview.Heading",
                font=("Arial", 12, "bold"),
                background="#003366",
                foreground="white")

style.map("Treeview", 
        background=[("selected", "#cc0000")], 
        foreground=[("selected", "white")])

# Crear la tabla
columnas = ("Nombre", "Fecha", "Hora", "Servicio", "Barbero")
tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=12)

# Encabezados
for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=150, anchor="center")  # Centrado y tamaño ajustado

tabla.pack()

# Alternar colores de filas (estilo zebra)
tabla.tag_configure("oddrow", background="#f9f9f9")
tabla.tag_configure("evenrow", background="#e0e0e0")

# Ejemplo: Agregar citas simuladas
tabla.insert("", "end", values=("Juan", "2025-05-29", "10:00", "Corte clásico", "Carlos"), tags=("oddrow",))
tabla.insert("", "end", values=("Ana", "2025-05-30", "12:00", "Tinte", "Ana"), tags=("evenrow",))


# Cargar citas al iniciar
mostrar_citas()

root.mainloop()