import socket
import threading
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from datetime import datetime

class ClienteChat:
    def __init__(self, root):
        self.root = root
        self.root.title("💬 Chat Colaborativo")
        self.root.geometry("900x650")
        self.root.configure(bg='#1a1a2e')
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        # Configurar estilo
        self.color_primary = '#0f3460'
        self.color_secondary = '#16213e'
        self.color_accent = '#e94560'
        self.color_success = '#00d9ff'
        self.color_bg = '#1a1a2e'
        self.color_text = '#ffffff'
        
        self.socket = None
        self.nombre_usuario = None
        self.sala_actual = None
        self.conectado = False
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # ==================== PANTALLA DE CONEXIÓN ====================
        self.frame_conexion = tk.Frame(self.root, bg=self.color_bg)
        self.frame_conexion.pack(fill=tk.BOTH, expand=True)
        
        # Container central
        container = tk.Frame(self.frame_conexion, bg=self.color_secondary, 
                            relief=tk.RAISED, borderwidth=2)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=450, height=500)
        
        # Título con emoji
        tk.Label(container, text="💬", font=('Arial', 60), 
                bg=self.color_secondary, fg=self.color_success).pack(pady=(30, 10))
        
        tk.Label(container, text="Chat Colaborativo", 
                font=('Arial', 28, 'bold'), bg=self.color_secondary, 
                fg=self.color_text).pack(pady=(0, 5))
        
        tk.Label(container, text="Conecta y chatea en tiempo real", 
                font=('Arial', 11), bg=self.color_secondary, 
                fg='#a0a0a0').pack(pady=(0, 30))
        
        # Nombre de usuario
        tk.Label(container, text="👤 Nombre de usuario", 
                font=('Arial', 11, 'bold'), bg=self.color_secondary, 
                fg=self.color_text).pack(pady=(0, 8))
        
        frame_nombre = tk.Frame(container, bg=self.color_primary, relief=tk.FLAT)
        frame_nombre.pack(pady=(0, 20), padx=40, fill=tk.X)
        
        self.entry_nombre = tk.Entry(frame_nombre, font=('Arial', 13), 
                                     bg=self.color_primary, fg=self.color_text,
                                     relief=tk.FLAT, insertbackground=self.color_text,
                                     borderwidth=0)
        self.entry_nombre.pack(padx=15, pady=12, fill=tk.X)
        self.entry_nombre.bind('<Return>', lambda e: self.conectar())
        
        # Configuración del servidor
        tk.Label(container, text="🌐 Configuración del servidor", 
                font=('Arial', 11, 'bold'), bg=self.color_secondary, 
                fg=self.color_text).pack(pady=(10, 8))
        
        frame_server = tk.Frame(container, bg=self.color_secondary)
        frame_server.pack(pady=(0, 30), padx=40)
        
        # Host
        frame_host = tk.Frame(frame_server, bg=self.color_primary, relief=tk.FLAT)
        frame_host.pack(side=tk.LEFT, padx=(0, 10))
        
        self.entry_host = tk.Entry(frame_host, font=('Arial', 11), width=14,
                                   bg=self.color_primary, fg=self.color_text,
                                   relief=tk.FLAT, insertbackground=self.color_text)
        self.entry_host.insert(0, "127.0.0.1")
        self.entry_host.pack(padx=12, pady=10)
        
        # Puerto
        frame_puerto = tk.Frame(frame_server, bg=self.color_primary, relief=tk.FLAT)
        frame_puerto.pack(side=tk.LEFT)
        
        self.entry_puerto = tk.Entry(frame_puerto, font=('Arial', 11), width=8,
                                     bg=self.color_primary, fg=self.color_text,
                                     relief=tk.FLAT, insertbackground=self.color_text)
        self.entry_puerto.insert(0, "5555")
        self.entry_puerto.pack(padx=12, pady=10)
        
        # Botón conectar
        btn_conectar = tk.Button(container, text="CONECTAR", 
                                command=self.conectar,
                                font=('Arial', 13, 'bold'), 
                                bg=self.color_accent, fg=self.color_text,
                                relief=tk.FLAT, cursor='hand2',
                                activebackground='#d63850',
                                activeforeground=self.color_text,
                                borderwidth=0, padx=60, pady=15)
        btn_conectar.pack(pady=(0, 20))
        
        # Efecto hover en botón
        btn_conectar.bind('<Enter>', lambda e: btn_conectar.config(bg='#d63850'))
        btn_conectar.bind('<Leave>', lambda e: btn_conectar.config(bg=self.color_accent))
        
        # Footer
        tk.Label(container, text="Desarrollado con Python + Sockets", 
                font=('Arial', 9), bg=self.color_secondary, 
                fg='#666666').pack(side=tk.BOTTOM, pady=15)
        
        # ==================== PANTALLA DE SALAS ====================
        self.frame_salas = tk.Frame(self.root, bg=self.color_bg)
        
        # Header
        header_salas = tk.Frame(self.frame_salas, bg=self.color_secondary, height=80)
        header_salas.pack(fill=tk.X)
        header_salas.pack_propagate(False)
        
        tk.Label(header_salas, text="🏠 Salas Disponibles", 
                font=('Arial', 24, 'bold'), bg=self.color_secondary, 
                fg=self.color_text).pack(side=tk.LEFT, padx=30, pady=20)
        
        self.label_usuario_salas = tk.Label(header_salas, text="", 
                                           font=('Arial', 11), 
                                           bg=self.color_secondary, 
                                           fg=self.color_success)
        self.label_usuario_salas.pack(side=tk.RIGHT, padx=30)
        
        # Contenedor principal de salas
        container_salas = tk.Frame(self.frame_salas, bg=self.color_bg)
        container_salas.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        # Lista de salas con estilo
        frame_lista = tk.Frame(container_salas, bg=self.color_secondary, 
                              relief=tk.FLAT, borderwidth=0)
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        tk.Label(frame_lista, text="Selecciona una sala o crea una nueva", 
                font=('Arial', 11), bg=self.color_secondary, 
                fg='#a0a0a0').pack(pady=(15, 10))
        
        # Scrollbar personalizado
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        
        self.listbox_salas = tk.Listbox(frame_lista, font=('Arial', 13), 
                                        height=10, bg=self.color_primary,
                                        fg=self.color_text, relief=tk.FLAT,
                                        selectbackground=self.color_accent,
                                        selectforeground=self.color_text,
                                        borderwidth=0, highlightthickness=0,
                                        yscrollcommand=scrollbar.set)
        self.listbox_salas.pack(pady=(0, 15), padx=20, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox_salas.yview)
        
        # Doble clic para unirse
        self.listbox_salas.bind('<Double-Button-1>', lambda e: self.unirse_sala())
        
        # Botones de acción
        frame_botones_sala = tk.Frame(container_salas, bg=self.color_bg)
        frame_botones_sala.pack(fill=tk.X)
        
        btn_unirse = tk.Button(frame_botones_sala, text="✓ UNIRSE", 
                              command=self.unirse_sala,
                              bg=self.color_success, fg='#000000',
                              font=('Arial', 12, 'bold'), relief=tk.FLAT,
                              cursor='hand2', padx=40, pady=12)
        btn_unirse.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        btn_crear = tk.Button(frame_botones_sala, text="+ CREAR SALA", 
                             command=self.crear_sala,
                             bg=self.color_accent, fg=self.color_text,
                             font=('Arial', 12, 'bold'), relief=tk.FLAT,
                             cursor='hand2', padx=40, pady=12)
        btn_crear.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        btn_actualizar = tk.Button(frame_botones_sala, text="🔄 ACTUALIZAR", 
                                  command=self.actualizar_salas,
                                  bg=self.color_primary, fg=self.color_text,
                                  font=('Arial', 12, 'bold'), relief=tk.FLAT,
                                  cursor='hand2', padx=40, pady=12)
        btn_actualizar.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # ==================== PANTALLA DE CHAT ====================
        self.frame_chat = tk.Frame(self.root, bg=self.color_bg)
        
        # Header del chat
        header_chat = tk.Frame(self.frame_chat, bg=self.color_secondary, height=70)
        header_chat.pack(fill=tk.X)
        header_chat.pack_propagate(False)
        
        info_frame = tk.Frame(header_chat, bg=self.color_secondary)
        info_frame.pack(side=tk.LEFT, padx=25, pady=15)
        
        self.label_sala = tk.Label(info_frame, text="# General", 
                                   font=('Arial', 20, 'bold'), 
                                   bg=self.color_secondary, fg=self.color_text)
        self.label_sala.pack(anchor=tk.W)
        
        self.label_usuario_chat = tk.Label(info_frame, text="", 
                                          font=('Arial', 10), 
                                          bg=self.color_secondary, 
                                          fg=self.color_success)
        self.label_usuario_chat.pack(anchor=tk.W)
        
        btn_salir = tk.Button(header_chat, text="← Volver", 
                            command=self.volver_salas,
                            bg=self.color_accent, fg=self.color_text,
                            font=('Arial', 11, 'bold'), relief=tk.FLAT,
                            cursor='hand2', padx=20, pady=8)
        btn_salir.pack(side=tk.RIGHT, padx=25)
        
        # Panel principal - chat y usuarios
        frame_principal = tk.Frame(self.frame_chat, bg=self.color_bg)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Panel de mensajes
        frame_mensajes = tk.Frame(frame_principal, bg=self.color_bg)
        frame_mensajes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Área de chat con estilo
        chat_container = tk.Frame(frame_mensajes, bg=self.color_secondary, 
                                 relief=tk.FLAT)
        chat_container.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(chat_container, text="💬 Mensajes", 
                font=('Arial', 12, 'bold'), bg=self.color_secondary,
                fg=self.color_text).pack(anchor=tk.W, padx=20, pady=(15, 10))
        
        self.text_chat = scrolledtext.ScrolledText(chat_container, 
                                                   wrap=tk.WORD, 
                                                   font=('Consolas', 10),
                                                   state=tk.DISABLED,
                                                   bg=self.color_primary,
                                                   fg=self.color_text,
                                                   relief=tk.FLAT,
                                                   borderwidth=0,
                                                   highlightthickness=0,
                                                   padx=15, pady=10)
        self.text_chat.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Configurar tags para colores
        self.text_chat.tag_config('usuario', foreground=self.color_success, 
                                 font=('Consolas', 10, 'bold'))
        self.text_chat.tag_config('timestamp', foreground='#888888', 
                                 font=('Consolas', 9))
        self.text_chat.tag_config('sistema', foreground='#ffaa00', 
                                 font=('Consolas', 9, 'italic'))
        
        # Panel de usuarios
        frame_usuarios = tk.Frame(frame_principal, bg=self.color_secondary,
                                 width=220, relief=tk.FLAT)
        frame_usuarios.pack(side=tk.RIGHT, fill=tk.Y)
        frame_usuarios.pack_propagate(False)
        
        tk.Label(frame_usuarios, text="👥 Usuarios", 
                font=('Arial', 12, 'bold'), bg=self.color_secondary,
                fg=self.color_text).pack(anchor=tk.W, padx=20, pady=(15, 10))
        
        self.listbox_usuarios = tk.Listbox(frame_usuarios, font=('Arial', 11),
                                          bg=self.color_primary, fg=self.color_text,
                                          relief=tk.FLAT, borderwidth=0,
                                          highlightthickness=0,
                                          selectbackground=self.color_accent)
        self.listbox_usuarios.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Panel de entrada de mensaje
        frame_entrada = tk.Frame(self.frame_chat, bg=self.color_bg, height=80)
        frame_entrada.pack(fill=tk.X, padx=20, pady=(0, 20))
        frame_entrada.pack_propagate(False)
        
        input_container = tk.Frame(frame_entrada, bg=self.color_secondary,
                                  relief=tk.FLAT)
        input_container.pack(fill=tk.BOTH, expand=True)
        
        entrada_frame = tk.Frame(input_container, bg=self.color_primary)
        entrada_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.entry_mensaje = tk.Entry(entrada_frame, font=('Arial', 12),
                                      bg=self.color_primary, fg=self.color_text,
                                      relief=tk.FLAT, insertbackground=self.color_text,
                                      borderwidth=0)
        self.entry_mensaje.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, 
                               padx=15, pady=10)
        self.entry_mensaje.bind('<Return>', lambda e: self.enviar_mensaje())
        
        btn_enviar = tk.Button(entrada_frame, text="➤", 
                              command=self.enviar_mensaje,
                              bg=self.color_accent, fg=self.color_text,
                              font=('Arial', 16, 'bold'), relief=tk.FLAT,
                              cursor='hand2', width=4, borderwidth=0)
        btn_enviar.pack(side=tk.RIGHT, padx=10)
    
    def conectar(self):
        nombre = self.entry_nombre.get().strip()
        host = self.entry_host.get().strip()
        puerto = self.entry_puerto.get().strip()
        
        if not nombre:
            messagebox.showerror("❌ Error", "Ingresa un nombre de usuario")
            return
        
        try:
            puerto = int(puerto)
        except:
            messagebox.showerror("❌ Error", "Puerto inválido")
            return
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, puerto))
            
            self.nombre_usuario = nombre
            self.conectado = True
            
            # Enviar solicitud de conexión
            mensaje = {
                'tipo': 'conectar',
                'nombre': nombre
            }
            self.socket.send(json.dumps(mensaje).encode('utf-8'))
            
            # Iniciar hilo de recepción
            thread = threading.Thread(target=self.recibir_mensajes, daemon=True)
            thread.start()
            
            # Actualizar labels
            self.label_usuario_salas.config(text=f"👤 {nombre}")
            self.label_usuario_chat.config(text=f"Conectado como {nombre}")
            
            # Cambiar a vista de salas
            self.frame_conexion.pack_forget()
            self.frame_salas.pack(fill=tk.BOTH, expand=True)
            self.actualizar_salas()
            
        except Exception as e:
            messagebox.showerror("❌ Error de Conexión", 
                               f"No se pudo conectar al servidor\n{e}")
    
    def recibir_mensajes(self):
        while self.conectado:
            try:
                mensaje = self.socket.recv(4096).decode('utf-8')
                if not mensaje:
                    break
                
                datos = json.loads(mensaje)
                self.procesar_mensaje(datos)
                
            except Exception as e:
                if self.conectado:
                    print(f"Error al recibir: {e}")
                break
    
    def procesar_mensaje(self, datos):
        tipo = datos.get('tipo')
        
        if tipo == 'conexion_exitosa':
            print(datos.get('mensaje'))
        
        elif tipo == 'lista_salas':
            self.listbox_salas.delete(0, tk.END)
            for sala in datos.get('salas', []):
                self.listbox_salas.insert(tk.END, f"  # {sala}")
        
        elif tipo == 'sala_creada':
            messagebox.showinfo("✓ Éxito", datos.get('mensaje'))
            self.actualizar_salas()
        
        elif tipo == 'sala_unida':
            self.sala_actual = datos.get('sala')
            self.label_sala.config(text=f"# {self.sala_actual}")
            
            # Mostrar chat
            self.frame_salas.pack_forget()
            self.frame_chat.pack(fill=tk.BOTH, expand=True)
            
            # Limpiar chat anterior
            self.text_chat.config(state=tk.NORMAL)
            self.text_chat.delete(1.0, tk.END)
            self.text_chat.config(state=tk.DISABLED)
            
            # Actualizar usuarios
            self.listbox_usuarios.delete(0, tk.END)
            for usuario in datos.get('usuarios', []):
                self.listbox_usuarios.insert(tk.END, f"  • {usuario}")
            
            # Mostrar mensaje de bienvenida
            self.mostrar_mensaje_sistema(datos.get('mensaje'))
        
        elif tipo == 'mensaje':
            usuario = datos.get('usuario')
            contenido = datos.get('contenido')
            timestamp = datos.get('timestamp')
            self.mostrar_mensaje(usuario, contenido, timestamp)
        
        elif tipo == 'notificacion':
            self.mostrar_mensaje_sistema(datos.get('mensaje'))
            # Actualizar lista de usuarios después de una notificación
            self.root.after(100, self.actualizar_usuarios_en_sala)
        
        elif tipo == 'error':
            messagebox.showerror("❌ Error", datos.get('mensaje'))
    
    def actualizar_usuarios_en_sala(self):
        # Esta función puede mejorarse solicitando la lista actualizada al servidor
        pass
    
    def actualizar_salas(self):
        if self.conectado:
            mensaje = {'tipo': 'listar_salas'}
            self.socket.send(json.dumps(mensaje).encode('utf-8'))
    
    def crear_sala(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Crear Nueva Sala")
        dialog.geometry("400x200")
        dialog.configure(bg=self.color_secondary)
        dialog.resizable(False, False)
        dialog.grab_set()
        
        tk.Label(dialog, text="🏠 Nombre de la sala", 
                font=('Arial', 14, 'bold'), bg=self.color_secondary,
                fg=self.color_text).pack(pady=(30, 15))
        
        entry = tk.Entry(dialog, font=('Arial', 12), width=30,
                        bg=self.color_primary, fg=self.color_text,
                        relief=tk.FLAT, insertbackground=self.color_text)
        entry.pack(pady=(0, 20), padx=40)
        entry.focus()
        
        def crear():
            nombre_sala = entry.get().strip()
            if nombre_sala:
                mensaje = {
                    'tipo': 'crear_sala',
                    'sala': nombre_sala
                }
                self.socket.send(json.dumps(mensaje).encode('utf-8'))
                dialog.destroy()
        
        entry.bind('<Return>', lambda e: crear())
        
        btn_frame = tk.Frame(dialog, bg=self.color_secondary)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Crear", command=crear,
                 bg=self.color_accent, fg=self.color_text,
                 font=('Arial', 11, 'bold'), relief=tk.FLAT,
                 cursor='hand2', padx=30, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancelar", command=dialog.destroy,
                 bg=self.color_primary, fg=self.color_text,
                 font=('Arial', 11, 'bold'), relief=tk.FLAT,
                 cursor='hand2', padx=30, pady=8).pack(side=tk.LEFT, padx=5)
    
    def unirse_sala(self):
        seleccion = self.listbox_salas.curselection()
        if seleccion:
            sala_texto = self.listbox_salas.get(seleccion[0])
            sala = sala_texto.replace('  # ', '').strip()
            mensaje = {
                'tipo': 'unirse_sala',
                'sala': sala
            }
            self.socket.send(json.dumps(mensaje).encode('utf-8'))
        else:
            messagebox.showwarning("⚠ Advertencia", "Selecciona una sala primero")
    
    def volver_salas(self):
        self.frame_chat.pack_forget()
        self.frame_salas.pack(fill=tk.BOTH, expand=True)
        self.actualizar_salas()
    
    def enviar_mensaje(self):
        contenido = self.entry_mensaje.get().strip()
        if contenido and self.conectado and self.sala_actual:
            mensaje = {
                'tipo': 'mensaje',
                'contenido': contenido
            }
            self.socket.send(json.dumps(mensaje).encode('utf-8'))
            self.entry_mensaje.delete(0, tk.END)
    
    def mostrar_mensaje(self, usuario, contenido, timestamp):
        self.text_chat.config(state=tk.NORMAL)
        
        # Timestamp
        self.text_chat.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Usuario
        self.text_chat.insert(tk.END, f"{usuario}: ", 'usuario')
        
        # Contenido
        self.text_chat.insert(tk.END, f"{contenido}\n")
        
        self.text_chat.config(state=tk.DISABLED)
        self.text_chat.see(tk.END)
    
    def mostrar_mensaje_sistema(self, mensaje):
        self.text_chat.config(state=tk.NORMAL)
        self.text_chat.insert(tk.END, f">>> {mensaje}\n", 'sistema')
        self.text_chat.config(state=tk.DISABLED)
        self.text_chat.see(tk.END)
    
    def cerrar_aplicacion(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro que deseas salir?"):
            self.conectado = False
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
            self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = ClienteChat(root)
    root.mainloop()