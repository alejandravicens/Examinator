import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import csv
import os
import random
import datetime
import time
import threading

# Función para instalar un paquete
def instalar_paquete(paquete):
    subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])

# Verificar si los módulos necesarios están instalados e instalarlos si es necesario
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
except ImportError:
    print("Instalando tkinter...")
    instalar_paquete("tkinter")

try:
    import csv
except ImportError:
    print("Instalando csv...")
    instalar_paquete("csv")

try:
    import os
    import random
    import datetime
    import time
    import threading
except ImportError as e:
    print(f"Error al importar un módulo: {e}")
    # Si alguno de estos módulos falla al importar, se puede manejar aquí, pero generalmente vienen preinstalados en Python.

# Ahora comienza el resto de tu script

class ExaminatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EXAMINATOR" )
        
        # Variables de la aplicación
        self.csv_actual = None
        self.configuracion = {'n_preguntas': 10, 'restan': False, 'tiempo': 0}
        self.preguntas = []
        self.preguntas_seleccionadas = []
        self.respuestas = []
        self.indice_pregunta = 0
        self.tiempo_restante = 0
        self.temporizador_activo = False
        self.csv_label = None
        self.config_label = None

        # Crear el menú principal
        self.create_main_menu()

    def create_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="EXAMINATOR", font=("Helvetica", 24)).pack(pady=20)
        tk.Button(self.root, text="Cargar CSV", command=self.cargar_csv).pack(pady=10)
        self.csv_label = tk.Label(self.root, text="Archivo CSV: No cargado")
        self.csv_label.pack(pady=5)
        tk.Button(self.root, text="Configurar Examen", command=self.configurar_examen).pack(pady=10)
        self.config_label = tk.Label(self.root, text="Configuración: No realizada")
        self.config_label.pack(pady=5)
        tk.Button(self.root, text="Comenzar Examen", command=self.comenzar_examen).pack(pady=10)
        tk.Button(self.root, text="Repetir Examen", command=self.repetir_examen).pack(pady=10)  # Aquí se llamará a la función correctamente
        tk.Button(self.root, text="Salir", command=self.root.quit).pack(pady=10)

    def cargar_csv(self):
        archivo_csv = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
        if archivo_csv:
            self.csv_actual = archivo_csv
            self.csv_label.config(text=f"Archivo CSV: {os.path.basename(self.csv_actual)}")
            messagebox.showinfo("Cargar CSV", f"Archivo seleccionado: {os.path.basename(self.csv_actual)}")
        else:
            messagebox.showwarning("Cargar CSV", "No se seleccionó ningún archivo.")

    def configurar_examen(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Configurar Examen")

        tk.Label(config_window, text="Número de preguntas:").pack(pady=5)
        n_preguntas_entry = tk.Entry(config_window)
        n_preguntas_entry.pack(pady=5)

        tk.Label(config_window, text="¿Los errores restan puntos? (SI/NO):").pack(pady=5)
        restan_var = tk.StringVar(value="NO")
        tk.Radiobutton(config_window, text="Sí", variable=restan_var, value="SI").pack(pady=2)
        tk.Radiobutton(config_window, text="No", variable=restan_var, value="NO").pack(pady=2)

        tk.Label(config_window, text="Tiempo en minutos (0 para sin límite):").pack(pady=5)
        tiempo_entry = tk.Entry(config_window)
        tiempo_entry.pack(pady=5)

        def guardar_configuracion():
            try:
                self.configuracion['n_preguntas'] = int(n_preguntas_entry.get())
                self.configuracion['restan'] = (restan_var.get() == "SI")
                self.configuracion['tiempo'] = int(tiempo_entry.get())
                self.config_label.config(text=f"Configuración: {self.configuracion['n_preguntas']} preguntas, "
                                            f"Errores restan: {self.configuracion['restan']}, "
                                            f"Tiempo: {self.configuracion['tiempo']} min")
                messagebox.showinfo("Configuración", "Configuración guardada con éxito.")
                config_window.destroy()
            except ValueError:
                messagebox.showwarning("Error", "Por favor, ingrese valores válidos.")

        tk.Button(config_window, text="Guardar configuración", command=guardar_configuracion).pack(pady=10)

    def comenzar_examen(self):
        if not self.csv_actual:
            messagebox.showwarning("Comenzar Examen", "Debe cargar un archivo CSV primero.")
            return

        self.preguntas = self.leer_preguntas_csv(self.csv_actual)
        if len(self.preguntas) < self.configuracion['n_preguntas']:
            messagebox.showwarning("Error", "El CSV tiene menos preguntas que las configuradas.")
            return

        self.preguntas_seleccionadas = random.sample(self.preguntas, self.configuracion['n_preguntas'])
        self.respuestas = [None] * self.configuracion['n_preguntas']
        self.indice_pregunta = 0

        if self.configuracion['tiempo'] > 0:
            self.tiempo_restante = self.configuracion['tiempo'] * 60
            self.temporizador_activo = True
            self.mostrar_pregunta(self.indice_pregunta)
            threading.Thread(target=self.iniciar_temporizador).start()
        else:
            self.mostrar_pregunta(self.indice_pregunta)

    def iniciar_temporizador(self):
        while self.tiempo_restante > 0 and self.temporizador_activo:
            mins, secs = divmod(self.tiempo_restante, 60)
            tiempo_formateado = f"Tiempo restante: {mins:02}:{secs:02}"
            self.root.title(tiempo_formateado)
            time.sleep(1)
            self.tiempo_restante -= 1

        if self.tiempo_restante <= 0:
            messagebox.showinfo("Tiempo agotado", "El tiempo ha terminado.")
            self.finalizar_examen()

    def mostrar_pregunta(self, indice):
        if indice >= len(self.preguntas_seleccionadas):
            self.finalizar_examen()
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        pregunta = self.preguntas_seleccionadas[indice]
        tk.Label(self.root, text=f"Pregunta {indice + 1}/{len(self.preguntas_seleccionadas)}", font=("Helvetica", 16)).pack(pady=20)
        tk.Label(self.root, text=pregunta[0], wraplength=500).pack(pady=20)

        opciones_frame = tk.Frame(self.root)
        opciones_frame.pack(pady=10)
        respuesta_var = tk.IntVar(value=self.respuestas[indice] if self.respuestas[indice] else 0)

        for idx in range(1, 5):
            tk.Radiobutton(opciones_frame, text=pregunta[idx], variable=respuesta_var, value=idx).pack(anchor='w')

        def guardar_respuesta():
            self.respuestas[indice] = respuesta_var.get()

        boton_anterior = tk.Button(self.root, text="Anterior", command=lambda: [guardar_respuesta(), self.mostrar_pregunta(indice - 1)])
        if indice == 0:
            boton_anterior.config(state=tk.DISABLED)
        boton_anterior.pack(side=tk.LEFT, padx=20, pady=10)

        tk.Button(self.root, text="Siguiente", command=lambda: [guardar_respuesta(), self.mostrar_pregunta(indice + 1)]).pack(side=tk.RIGHT, padx=20, pady=10)
        tk.Button(self.root, text="Finalizar Examen", command=self.finalizar_examen).pack(pady=20)

    def leer_preguntas_csv(self, archivo_csv):
        preguntas = []
        with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
            lector = csv.reader(csvfile)
            for fila in lector:
                fila = [campo.strip() for campo in fila]
                preguntas.append(fila)
        return preguntas

    def repetir_examen(self):
        carpetas = [carpeta for carpeta in os.listdir() if os.path.isdir(carpeta)]
        if not carpetas:
            messagebox.showwarning("Repetir Examen", "No hay asignaturas con exámenes guardados.")
            return

        repetir_window = tk.Toplevel(self.root)
        repetir_window.title("Repetir Examen")

        tk.Label(repetir_window, text="Seleccione una asignatura:").pack(pady=5)
        asignatura_var = tk.StringVar()
        tk.OptionMenu(repetir_window, asignatura_var, *carpetas).pack(pady=10)

        def cargar_examen_anterior():
            asignatura_seleccionada = asignatura_var.get()
            if not asignatura_seleccionada:
                messagebox.showwarning("Error", "Seleccione una asignatura.")
                return
            
            examenes_anteriores = [f for f in os.listdir(asignatura_seleccionada) if "_examen_" in f and f.endswith('.txt')]
            if not examenes_anteriores:
                messagebox.showwarning("Error", "No se encontraron exámenes anteriores.")
                return

            tk.Label(repetir_window, text="Seleccione un examen:").pack(pady=5)
            examen_var = tk.StringVar()
            tk.OptionMenu(repetir_window, examen_var, *examenes_anteriores).pack(pady=10)

            def cargar_examen():
                examen_seleccionado = examen_var.get()
                ruta_examen = os.path.join(asignatura_seleccionada, examen_seleccionado)
                self.preguntas = self.leer_preguntas_csv(ruta_examen)
                self.preguntas_seleccionadas = self.preguntas
                self.respuestas = [None] * len(self.preguntas)
                self.mostrar_pregunta(0)
                repetir_window.destroy()

            tk.Button(repetir_window, text="Cargar Examen", command=cargar_examen).pack(pady=10)

        tk.Button(repetir_window, text="Cargar Asignatura", command=cargar_examen_anterior).pack(pady=10)

    def finalizar_examen(self):
        self.temporizador_activo = False
        aciertos, fallos, respondidas, no_respondidas = 0, 0, 0, 0

        for idx, pregunta in enumerate(self.preguntas_seleccionadas):
            respuesta_correcta = pregunta[5].strip()
            seleccion_usuario = self.respuestas[idx]

            if seleccion_usuario is not None:
                respondidas += 1
                if str(seleccion_usuario) == respuesta_correcta:
                    aciertos += 1
                else:
                    fallos += 1
            else:
                no_respondidas += 1

        if self.configuracion['restan']:
            nota = aciertos - (fallos / 3)
        else:
            nota = aciertos

        # Guardar los resultados en un archivo corregido
        archivo_correccion = self.guardar_resultados()

        # Verificar si el archivo de corrección fue guardado correctamente
        if os.path.exists(archivo_correccion):
            self.mostrar_correccion_completa(archivo_correccion)
        else:
            messagebox.showerror("Error", "El archivo de corrección no se pudo guardar correctamente.")

    def guardar_resultados(self):
        # Verificar si se trata de un examen repetido (cuando self.csv_actual es None)
        if self.csv_actual is None:
            nombre_asignatura = "ExamenRepetido"  # Nombre temporal o estándar para exámenes repetidos
        else:
            nombre_asignatura = os.path.basename(os.path.splitext(self.csv_actual)[0])

        # Generar la carpeta de la asignatura y los archivos de corrección y examen
        fecha_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        carpeta_asignatura = os.path.join(os.path.dirname(self.csv_actual) if self.csv_actual else ".", nombre_asignatura)

        # Crear la carpeta de la asignatura si no existe
        if not os.path.exists(carpeta_asignatura):
            os.makedirs(carpeta_asignatura)

        archivo_correccion = f"{carpeta_asignatura}/{nombre_asignatura}_corregido_{fecha_hora}.txt"
        archivo_examen = f"{carpeta_asignatura}/{nombre_asignatura}_examen_{fecha_hora}.txt"

        try:
            with open(archivo_correccion, 'w', encoding='utf-8') as f_correccion, \
                open(archivo_examen, 'w', encoding='utf-8') as f_examen:

                # Guardar las preguntas seleccionadas en el archivo del examen
                for idx, pregunta in enumerate(self.preguntas_seleccionadas):
                    f_examen.write(','.join(pregunta) + '\n')

                    # Guardar la corrección
                    f_correccion.write(f"Pregunta {idx + 1}: {pregunta[0]}\n")
                    for opcion_idx in range(1, 5):
                        f_correccion.write(f"   {opcion_idx}. {pregunta[opcion_idx]}\n")

                    seleccion_usuario = self.respuestas[idx]
                    respuesta_correcta = pregunta[5].strip()

                    if seleccion_usuario is not None:
                        f_correccion.write(f"   -> Seleccionaste: {seleccion_usuario}. {pregunta[seleccion_usuario]}\n")
                        if str(seleccion_usuario) == respuesta_correcta:
                            f_correccion.write("   ✔ Respuesta correcta\n")
                        else:
                            f_correccion.write(f"   ✘ Respuesta incorrecta. La correcta era: {respuesta_correcta}. {pregunta[int(respuesta_correcta)]}\n")
                            f_correccion.write(f"   Explicación: {pregunta[6]}\n")
                    else:
                        f_correccion.write("   -> No respondiste esta pregunta.\n")

                # Resumen final del examen
                f_correccion.write("\n=== RESUMEN DEL EXAMEN ===\n")
                f_correccion.write(f"Preguntas respondidas: {sum([1 for r in self.respuestas if r is not None])}\n")
                f_correccion.write(f"Preguntas no respondidas: {sum([1 for r in self.respuestas if r is None])}\n")

                # Cálculo de la nota final
                aciertos = sum(1 for idx, pregunta in enumerate(self.preguntas_seleccionadas)
                            if str(self.respuestas[idx]) == pregunta[5].strip())
                fallos = sum(1 for idx, pregunta in enumerate(self.preguntas_seleccionadas)
                            if self.respuestas[idx] is not None and str(self.respuestas[idx]) != pregunta[5].strip())

                if self.configuracion['restan']:
                    nota = aciertos - (fallos / 3)
                else:
                    nota = aciertos

                f_correccion.write(f"\nNota final: {nota}/{self.configuracion['n_preguntas']}\n")

            # Devolver la ruta completa del archivo de corrección para mostrarlo más tarde
            return archivo_correccion
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el archivo: {str(e)}")
            return None




    def mostrar_correccion_completa(self, archivo_correccion):
        # Crear una ventana para mostrar el archivo corregido completo
        correccion_window = tk.Toplevel(self.root)
        correccion_window.title("Examen Corregido Completo")

        # Evitar que el menú principal se abra automáticamente después de cerrar la ventana
        correccion_window.grab_set()  # Forzar la interacción solo en la ventana de corrección

        # Mostrar el contenido del archivo corregido en una ventana de texto desplazable
        try:
            with open(archivo_correccion, 'r', encoding='utf-8') as f:
                contenido = f.read()

            scrolled_text = scrolledtext.ScrolledText(correccion_window, wrap=tk.WORD, width=100, height=30)
            scrolled_text.pack(expand=True, fill='both')
            scrolled_text.insert(tk.END, contenido)  # Mostrar todo el contenido del archivo corregido
            scrolled_text.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el archivo de corrección: {str(e)}")

        # Cuando se cierre la ventana de corrección, habilitar el menú principal
        correccion_window.protocol("WM_DELETE_WINDOW", lambda: self.create_main_menu())


# Inicialización de la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = ExaminatorApp(root)
    root.mainloop()


