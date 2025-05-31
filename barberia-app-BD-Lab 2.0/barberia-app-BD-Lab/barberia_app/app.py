from tkinter import ttk, messagebox, Label, END, Frame
import tkinter as tk
from tkcalendar import DateEntry
from pymongo import MongoClient
from dotenv import load_dotenv
import os  
from PIL import Image, ImageTk
from datetime import datetime

# --- Funciones de utilidad ---
# Obtiene una lista con los nombres de todos los servicios almacenados en la base de datos
def obtener_servicios():
    try:
        return [servicio["nombre"] for servicio in servicios.find()]
    except Exception as e:
        print("Error al obtener servicios:", e)
        return []

#Obtiene una lista con los nombres completos de todos los barberos almacenados en la base de datos
def obtener_barberos():
    return [barbero["nombre"]+" "+barbero["ap_primero"]+" "+barbero["ap_segundo"] for barbero in barberos.find()] 

#Obtiene una lista de tuplas con el nombre, primer apellido y segundo apellido de cada barbero en la base de datos
def obtener_barberos_completo():
    return [(barbero["nombre"], barbero["ap_primero"], barbero["ap_segundo"]) for barbero in barberos.find()]

# Actualiza los combos y tablas de servicios y barberos con la información más reciente de la base de datos
def actualizar_listas():
    combo_servicio['values'] = obtener_servicios()
    combo_barbero['values'] = obtener_barberos()
    if hasattr(barberos_frame, 'tabla_barberos'):
        mostrar_barberos()
    if hasattr(servicios_frame, 'tabla_servicios'):
        mostrar_servicios()

# --- Funciones para mostrar/ocultar secciones ---
def mostrar_menu():
    ocultar_todos_frames()
    menu_frame.pack(fill="both", expand=True)

def mostrar_citas_seccion():
    ocultar_todos_frames()
    citas_frame.pack(fill="both", expand=True)
    mostrar_citas()
    actualizar_listas()

def mostrar_barberos_seccion():
    ocultar_todos_frames()
    barberos_frame.pack(fill="both", expand=True)
    mostrar_barberos()

def mostrar_servicios_seccion():
    ocultar_todos_frames()
    servicios_frame.pack(fill="both", expand=True)
    mostrar_servicios()

def ocultar_todos_frames():
    menu_frame.pack_forget()
    citas_frame.pack_forget()
    barberos_frame.pack_forget()
    servicios_frame.pack_forget()

# --- Funciones para Barberos ---
# Agrega un nuevo barbero a la base de datos si no existe, valida campos obligatorios y actualiza la interfaz
def agregar_barbero():
    nombre = entry_nombre_barbero.get().strip()
    ap1 = entry_ap1_barbero.get().strip()
    ap2 = entry_ap2_barbero.get().strip()
    
    if not nombre or not ap1:
        messagebox.showerror("Error", "Nombre y primer apellido son obligatorios")
        return
    
    if barberos.find_one({"nombre": nombre, "ap_primero": ap1, "ap_segundo": ap2}):
        messagebox.showerror("Error", "Este barbero ya existe")
        return
        
    barberos.insert_one({
        "nombre": nombre,
        "ap_primero": ap1,
        "ap_segundo": ap2
    })
    messagebox.showinfo("Éxito", "Barbero agregado")
    limpiar_campos_barbero()
    mostrar_barberos()
    actualizar_listas()

# Muestra la lista de barberos en la tabla, limpia los campos de entrada y permite borrar un barbero seleccionado tras confirmación
def mostrar_barberos():
    for row in tabla_barberos.get_children():
        tabla_barberos.delete(row)
    
    for barbero in barberos.find():
        tabla_barberos.insert("", "end", values=(
            barbero["nombre"],
            barbero["ap_primero"],
            barbero["ap_segundo"] if barbero["ap_segundo"] else ""
        ))

def limpiar_campos_barbero():
    entry_nombre_barbero.delete(0, END)
    entry_ap1_barbero.delete(0, END)
    entry_ap2_barbero.delete(0, END)

def borrar_barbero():
    seleccionado = tabla_barberos.focus()
    if not seleccionado:
        return
    
    datos = tabla_barberos.item(seleccionado)
    nombre = datos["values"][0]
    ap1 = datos["values"][1]
    
    if messagebox.askyesno("Confirmar", f"¿Borrar barbero {nombre} {ap1}?"):
        barberos.delete_one({"nombre": nombre, "ap_primero": ap1})
        mostrar_barberos()
        actualizar_listas()

# --- Funciones para Servicios ---
# Agrega un nuevo servicio si no existe, mostrando mensajes de error o éxito según corresponda
def agregar_servicio():
    nombre = entry_nombre_servicio.get().strip()
    
    if not nombre:
        messagebox.showerror("Error", "Nombre del servicio es obligatorio")
        return
    
    if servicios.find_one({"nombre": nombre}):
        messagebox.showerror("Error", "Este servicio ya existe")
        return
        
    servicios.insert_one({"nombre": nombre})
    messagebox.showinfo("Éxito", "Servicio agregado")
    entry_nombre_servicio.delete(0, END)
    mostrar_servicios()
    actualizar_listas()

# Muestra la lista de servicios en la tabla limpiando primero los datos previos
def mostrar_servicios():
    for row in tabla_servicios.get_children():
        tabla_servicios.delete(row)
    
    for servicio in servicios.find():
        tabla_servicios.insert("", "end", values=(servicio["nombre"],))

# Elimina el servicio seleccionado tras confirmar y actualiza la interfaz
def borrar_servicio():
    seleccionado = tabla_servicios.focus()
    if not seleccionado:
        return
    
    servicio = tabla_servicios.item(seleccionado)["values"][0]
    
    if messagebox.askyesno("Confirmar", f"¿Borrar servicio {servicio}?"):
        servicios.delete_one({"nombre": servicio})
        mostrar_servicios()
        actualizar_listas()

# --- Funciones para Citas (modificadas) ---
# Agrega una nueva cita verificando campos obligatorios, evita duplicados y actualiza la interfaz
def agregar_cita():
    try:
        if not all([entry_nombre.get(), combo_hora.get(), combo_servicio.get(), combo_barbero.get()]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        fecha_str = cal_fecha.get_date().strftime("%Y-%m-%d") 

        if citas.find_one({"fecha": fecha_str, "hora": combo_hora.get()}):
            messagebox.showerror("Error", "¡Ya hay una cita agendada a esa hora!")
            return

        nueva_cita = {
            "nombre_cliente": entry_nombre.get(),
            "fecha": fecha_str,
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

# Muestra todas las citas actuales en la tabla limpiando primero los datos previos
def mostrar_citas():
    for row in tabla.get_children():
        tabla.delete(row)
    for cita in citas.find():
        tabla.insert("", "end", values=(
            cita["nombre_cliente"],
            cita["fecha"],
            cita["hora"],
            cita["servicio"],
            cita["barbero"]
        ))

# Limpia los campos de entrada y selección del formulario de citas
def limpiar_campos():
    entry_nombre.delete(0, END)
    combo_hora.set("")
    combo_servicio.set("")
    combo_barbero.set("")

# Elimina la cita seleccionada tras confirmación del usuario
def borrar_cita():
    seleccionado = tabla.focus()
    if not seleccionado:
        return
    datos = tabla.item(seleccionado)
    nombre = datos["values"][0]
    fecha = datos["values"][1]
    hora = datos["values"][2]
    
    if messagebox.askyesno("Confirmar", f"¿Borrar cita de {nombre} el {fecha} a las {hora}?"):
        citas.delete_one({"nombre_cliente": nombre, "fecha": fecha, "hora": hora})
        mostrar_citas()

# Carga los datos de la cita seleccionada en los campos del formulario para editarla
def editar_cita():
    seleccionado = tabla.focus()
    if not seleccionado:
        return
    datos = tabla.item(seleccionado)
    limpiar_campos()
    entry_nombre.insert(0, datos["values"][0])
    cal_fecha.set_date(datetime.strptime(datos["values"][1], "%Y-%m-%d").date())
    combo_hora.set(datos["values"][2])
    combo_servicio.set(datos["values"][3])
    combo_barbero.set(datos["values"][4])

# Actualiza la cita seleccionada con los datos nuevos ingresados en el formulario
def actualizar_cita():
    seleccionado = tabla.focus()
    if not seleccionado:
        return
    if not all([entry_nombre.get(), combo_hora.get(), combo_servicio.get(), combo_barbero.get()]):
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return

    datos = tabla.item(seleccionado)
    nombre_original = datos["values"][0]
    fecha_original = str(datos["values"][1])
    hora_original = str(datos["values"][2])

    filtro = {
        "nombre_cliente": nombre_original,
        "fecha": fecha_original,
        "hora": hora_original
    }

    nuevos_datos = {
        "nombre_cliente": entry_nombre.get(),
        "fecha": str(cal_fecha.get_date()),
        "hora": combo_hora.get(),
        "servicio": combo_servicio.get(),
        "barbero": combo_barbero.get()
    }

    resultado = citas.update_one(filtro, {"$set": nuevos_datos})
    
    if resultado.modified_count > 0:
        messagebox.showinfo("Éxito", "Cita actualizada")
        mostrar_citas()
        limpiar_campos()
    else:
        messagebox.showwarning("Sin cambios", "No se modificó ningún dato")

# Función para mostrar el logo en diferentes secciones
# Muestra el logo en el frame dado, o un texto alternativo si no se puede cargar la imagen
def mostrar_logo(frame):
    try:
        logo_original = Image.open("logo.png")
        logo_redimensionado = logo_original.resize((100, 100), Image.LANCZOS)
        logo = ImageTk.PhotoImage(logo_redimensionado)
        logo_label = Label(frame, image=logo, bg="#f2f2f2")
        logo_label.image = logo
        logo_label.pack(side="top", pady=(10, 0))
    except:
        Label(frame, text="Barbería Clásica", font=("Arial", 14, "bold"), 
              bg="#f2f2f2", fg="#003366").pack(side="top", pady=(10, 0))

# ======================
# MENÚ PRINCIPAL
# ======================
# Crea el menú principal con logo, título, botones de navegación y pie de página en el frame del menú
def crear_menu():
    # Logo
    try:
        logo_original = Image.open("logo.png")
        logo_redimensionado = logo_original.resize((200, 200), Image.LANCZOS)
        logo = ImageTk.PhotoImage(logo_redimensionado)
        Label(menu_frame, image=logo, bg="#f2f2f2").image = logo
        Label(menu_frame, image=logo, bg="#f2f2f2").pack(pady=20)
    except:
        Label(menu_frame, text="Barbería Clásica", font=("Arial", 24, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=40)

    # Título
    Label(menu_frame, text="Sistema de Gestión de Barbería", 
          font=("Arial", 18, "bold"), bg="#f2f2f2", fg="#003366").pack(pady=10)

    # Botones
    btn_frame = Frame(menu_frame, bg="#f2f2f2")
    btn_frame.pack(pady=30)
    
    ttk.Button(btn_frame, text="Gestión de Citas", width=20, 
               command=mostrar_citas_seccion).pack(pady=15)
    ttk.Button(btn_frame, text="Gestión de Barberos", width=20, 
               command=mostrar_barberos_seccion).pack(pady=15)
    ttk.Button(btn_frame, text="Gestión de Servicios", width=20, 
               command=mostrar_servicios_seccion).pack(pady=15)
    
    # Footer
    Label(menu_frame, text="© 2025 Barbería Clásica", 
          font=("Arial", 10), bg="#f2f2f2", fg="#666666").pack(side="bottom", pady=10)

# ======================
# SECCIÓN CITAS
# ======================
# Crea la interfaz para la sección de gestión de citas, con formulario, botones, tabla y navegación al menú principal
def crear_seccion_citas():
    top_button_frame = Frame(citas_frame, bg="#f2f2f2")
    top_button_frame.pack(fill="x", pady=(10, 0))
    ttk.Button(top_button_frame, text="← Menú Principal", 
               command=mostrar_menu).pack(side="left", padx=10, anchor="nw")  # anchor nw para esquina noroeste

    mostrar_logo(citas_frame)
    
    header_frame = Frame(citas_frame, bg="#f2f2f2")
    header_frame.pack(fill="x", pady=10)
    
    Label(header_frame, text="Gestión de Citas", 
        font=("Arial", 16, "bold"), bg="#f2f2f2", fg="#003366").pack(padx=20, pady=10)

    # Contenedor para centrar el formulario
    form_container = Frame(citas_frame, bg="#f2f2f2")
    form_container.pack(pady=10, fill="x")
    
    # Formulario centrado
    form_frame = Frame(form_container, bg="#f2f2f2")
    form_frame.pack(anchor="center", pady=10)
    
    global entry_nombre, cal_fecha, combo_hora, combo_servicio, combo_barbero
    
    ttk.Label(form_frame, text="Nombre del cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_nombre = ttk.Entry(form_frame, width=30)
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Fecha:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    cal_fecha = DateEntry(form_frame, width=27, background="#003366", foreground="white", borderwidth=2)
    cal_fecha.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Hora:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    horas = ["04:00", "05:00", "06:00", "07:00", "08:00", "09:00",
            "10:00", "11:00", "12:00", "13:00", "14:00", "15:00",
            "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
    combo_hora = ttk.Combobox(form_frame, values=horas, width=27)
    combo_hora.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Servicio:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    combo_servicio = ttk.Combobox(form_frame, width=27)
    combo_servicio.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Barbero:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    combo_barbero = ttk.Combobox(form_frame, width=27)
    combo_barbero.grid(row=4, column=1, padx=5, pady=5)

    ttk.Button(form_frame, text="Guardar Cita", command=agregar_cita).grid(row=5, column=0, columnspan=2, pady=15)

    # Botones de acciones
    btn_frame = Frame(citas_frame, bg="#f2f2f2")
    btn_frame.pack(pady=10)
    
    ttk.Button(btn_frame, text="Editar Cita", command=editar_cita).grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Actualizar Cita", command=actualizar_cita).grid(row=0, column=1, padx=10)
    ttk.Button(btn_frame, text="Borrar Cita", command=borrar_cita).grid(row=0, column=2, padx=10)

    # Tabla de citas
    tabla_frame = Frame(citas_frame, bg="#f2f2f2")
    tabla_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    global tabla
    columnas = ("Nombre", "Fecha", "Hora", "Servicio", "Barbero")
    tabla = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=12)
    
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=150, anchor="center")
    
    scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
    scroll.pack(side="right", fill="y")
    tabla.configure(yscrollcommand=scroll.set)
    tabla.pack(fill="both", expand=True)

# ======================
# SECCIÓN BARBEROS
# ======================
# Crea la interfaz para la sección de gestión de barberos, con formulario, botones, tabla y navegación al menú principal
def crear_seccion_barberos():
    # Botón superior izquierdo
    top_button_frame = Frame(barberos_frame, bg="#f2f2f2")
    top_button_frame.pack(fill="x", pady=(10, 0))
    ttk.Button(top_button_frame, text="← Menú Principal", 
               command=mostrar_menu).pack(side="left", padx=10, anchor="nw")
    
    mostrar_logo(barberos_frame)
    
    header_frame = Frame(barberos_frame, bg="#f2f2f2")
    header_frame.pack(fill="x", pady=10)
    
    Label(header_frame, text="Gestión de Barberos", 
          font=("Arial", 16, "bold"), bg="#f2f2f2", fg="#003366").pack(padx=20, pady=10)

    # Contenedor para centrar el formulario
    form_container = Frame(barberos_frame, bg="#f2f2f2")
    form_container.pack(pady=10, fill="x")
    
    # Formulario centrado
    form_frame = Frame(form_container, bg="#f2f2f2")
    form_frame.pack(anchor="center", pady=10)
    
    global entry_nombre_barbero, entry_ap1_barbero, entry_ap2_barbero
    
    ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_nombre_barbero = ttk.Entry(form_frame, width=30)
    entry_nombre_barbero.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Primer Apellido:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_ap1_barbero = ttk.Entry(form_frame, width=30)
    entry_ap1_barbero.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Segundo Apellido:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_ap2_barbero = ttk.Entry(form_frame, width=30)
    entry_ap2_barbero.grid(row=2, column=1, padx=5, pady=5)

    ttk.Button(form_frame, text="Agregar Barbero", command=agregar_barbero).grid(row=3, column=0, columnspan=2, pady=15)

    # Botones de acciones
    btn_frame = Frame(barberos_frame, bg="#f2f2f2")
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="Borrar Barbero", command=borrar_barbero).pack(pady=5)

    # Tabla de barberos
    tabla_frame = Frame(barberos_frame, bg="#f2f2f2")
    tabla_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    global tabla_barberos
    columnas = ("Nombre", "Primer Apellido", "Segundo Apellido")
    tabla_barberos = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=12)
    
    for col in columnas:
        tabla_barberos.heading(col, text=col)
        tabla_barberos.column(col, width=150, anchor="center")
    
    scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla_barberos.yview)
    scroll.pack(side="right", fill="y")
    tabla_barberos.configure(yscrollcommand=scroll.set)
    tabla_barberos.pack(fill="both", expand=True)

# ======================
# SECCIÓN SERVICIOS
# ======================
# Crea la interfaz para la sección de gestión de servicios, con formulario, botones, tabla y navegación al menú principal
def crear_seccion_servicios():
    # Botón superior izquierdo
    top_button_frame = Frame(servicios_frame, bg="#f2f2f2")
    top_button_frame.pack(fill="x", pady=(10, 0))
    ttk.Button(top_button_frame, text="← Menú Principal", 
               command=mostrar_menu).pack(side="left", padx=10, anchor="nw")
    
    mostrar_logo(servicios_frame)
    
    header_frame = Frame(servicios_frame, bg="#f2f2f2")
    header_frame.pack(fill="x", pady=10)
    
    # Eliminar el botón de aquí ↓
    Label(header_frame, text="Gestión de Servicios", 
          font=("Arial", 16, "bold"), bg="#f2f2f2", fg="#003366").pack(padx=20, pady=10)


    # Contenedor para centrar el formulario
    form_container = Frame(servicios_frame, bg="#f2f2f2")
    form_container.pack(pady=10, fill="x")
    
    # Formulario centrado
    form_frame = Frame(form_container, bg="#f2f2f2")
    form_frame.pack(anchor="center", pady=10)
    
    global entry_nombre_servicio
    
    ttk.Label(form_frame, text="Nombre del Servicio:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_nombre_servicio = ttk.Entry(form_frame, width=30)
    entry_nombre_servicio.grid(row=0, column=1, padx=5, pady=5)

    ttk.Button(form_frame, text="Agregar Servicio", command=agregar_servicio).grid(row=1, column=0, columnspan=2, pady=15)

    # Botones de acciones
    btn_frame = Frame(servicios_frame, bg="#f2f2f2")
    btn_frame.pack(pady=10)
    ttk.Button(btn_frame, text="Borrar Servicio", command=borrar_servicio).pack(pady=5)

    # Tabla de servicios
    tabla_frame = Frame(servicios_frame, bg="#f2f2f2")
    tabla_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    global tabla_servicios
    columnas = ("Nombre del Servicio",)
    tabla_servicios = ttk.Treeview(tabla_frame, columns=columnas, show="headings", height=12)
    
    for col in columnas:
        tabla_servicios.heading(col, text=col)
        tabla_servicios.column(col, width=150, anchor="center")
    
    scroll = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla_servicios.yview)
    scroll.pack(side="right", fill="y")
    tabla_servicios.configure(yscrollcommand=scroll.set)
    tabla_servicios.pack(fill="both", expand=True)


# Cargar variables del .env para la base de datos, se obtiene la base de datos barberia_peluqueria
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["barberia_peluqueria"]

# Verifica colección sino existe la crearla
if "citas" not in db.list_collection_names():
    db.create_collection("citas")
if "barberos" not in db.list_collection_names():
    db.create_collection("barberos")
if "servicios" not in db.list_collection_names():
    db.create_collection("servicios")

#obtiene cada colección de la base de datos barberia_peluqueria
citas = db["citas"]
barberos = db["barberos"]
servicios = db["servicios"]

# --- Creación de la ventana principal ---
root = tk.Tk()
root.title("Sistema de Gestión - Barbería")
root.geometry("900x700")
root.configure(bg="#f2f2f2")

# --- Frames para las diferentes secciones ---
menu_frame = Frame(root, bg="#f2f2f2")
citas_frame = Frame(root, bg="#f2f2f2")
barberos_frame = Frame(root, bg="#f2f2f2")
servicios_frame = Frame(root, bg="#f2f2f2")

# --- Estilos ---
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 11), background="#f2f2f2")
style.configure("TButton", font=("Arial", 12, "bold"), foreground="white", background="#003366", padding=10)
style.map("TButton", background=[("active", "#cc0000")])
style.configure("TCombobox", padding=5, font=("Arial", 11))
style.configure("Treeview", font=("Arial", 11), rowheight=28, background="white", fieldbackground="white", foreground="black")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#003366", foreground="white")
style.map("Treeview", background=[("selected", "#cc0000")], foreground=[("selected", "white")])

# --- Inicializar secciones ---
crear_menu()
crear_seccion_citas()
crear_seccion_barberos()
crear_seccion_servicios()

# --- Mostrar menú principal al iniciar ---
mostrar_menu()

# --- Iniciar aplicación ---
root.mainloop()