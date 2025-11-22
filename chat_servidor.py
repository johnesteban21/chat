import socket
import threading
import json
from datetime import datetime

class Sala:
    def __init__(self, nombre):
        self.nombre = nombre
        self.usuarios = {}  # {socket: nombre_usuario}
        self.lock = threading.Lock()
    
    def agregar_usuario(self, cliente_socket, nombre_usuario):
        with self.lock:
            self.usuarios[cliente_socket] = nombre_usuario
    
    def eliminar_usuario(self, cliente_socket):
        with self.lock:
            if cliente_socket in self.usuarios:
                nombre = self.usuarios[cliente_socket]
                del self.usuarios[cliente_socket]
                return nombre
        return None
    
    def obtener_usuarios(self):
        with self.lock:
            return list(self.usuarios.values())
    
    def broadcast(self, mensaje, excluir_socket=None):
        with self.lock:
            usuarios_desconectados = []
            for sock in self.usuarios.keys():
                if sock != excluir_socket:
                    try:
                        sock.send(mensaje.encode('utf-8'))
                    except:
                        usuarios_desconectados.append(sock)
            
            # Limpiar usuarios desconectados
            for sock in usuarios_desconectados:
                self.eliminar_usuario(sock)


class ServidorChat:
    def __init__(self, host='127.0.0.1', puerto=5555):
        self.host = host
        self.puerto = puerto
        self.servidor_socket = None
        self.salas = {}  # {nombre_sala: Sala}
        self.clientes = {}  # {socket: {'nombre': str, 'sala': str}}
        self.lock = threading.Lock()
        self.ejecutando = True
        
    def iniciar(self):
        self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.servidor_socket.bind((self.host, self.puerto))
        self.servidor_socket.listen()
        
        print(f"[SERVIDOR] Iniciado en {self.host}:{self.puerto}")
        print("[SERVIDOR] Esperando conexiones...")
        
        # Crear sala por defecto
        self.crear_sala("General")
        
        while self.ejecutando:
            try:
                cliente_socket, direccion = self.servidor_socket.accept()
                print(f"[NUEVA CONEXIÓN] {direccion}")
                
                thread = threading.Thread(target=self.manejar_cliente, args=(cliente_socket,))
                thread.start()
            except:
                break
    
    def crear_sala(self, nombre_sala):
        with self.lock:
            if nombre_sala not in self.salas:
                self.salas[nombre_sala] = Sala(nombre_sala)
                print(f"[SALA CREADA] {nombre_sala}")
                return True
            return False
    
    def obtener_salas(self):
        with self.lock:
            return list(self.salas.keys())
    
    def manejar_cliente(self, cliente_socket):
        nombre_usuario = None
        sala_actual = None
        
        try:
            while True:
                mensaje = cliente_socket.recv(4096).decode('utf-8')
                if not mensaje:
                    break
                
                datos = json.loads(mensaje)
                tipo = datos.get('tipo')
                
                if tipo == 'conectar':
                    nombre_usuario = datos.get('nombre')
                    with self.lock:
                        self.clientes[cliente_socket] = {'nombre': nombre_usuario, 'sala': None}
                    
                    respuesta = {
                        'tipo': 'conexion_exitosa',
                        'mensaje': f'Bienvenido {nombre_usuario}!'
                    }
                    cliente_socket.send(json.dumps(respuesta).encode('utf-8'))
                    print(f"[CONECTADO] {nombre_usuario}")
                
                elif tipo == 'listar_salas':
                    salas = self.obtener_salas()
                    respuesta = {
                        'tipo': 'lista_salas',
                        'salas': salas
                    }
                    cliente_socket.send(json.dumps(respuesta).encode('utf-8'))
                
                elif tipo == 'crear_sala':
                    nombre_sala = datos.get('sala')
                    if self.crear_sala(nombre_sala):
                        respuesta = {
                            'tipo': 'sala_creada',
                            'sala': nombre_sala,
                            'mensaje': f'Sala "{nombre_sala}" creada exitosamente'
                        }
                    else:
                        respuesta = {
                            'tipo': 'error',
                            'mensaje': f'La sala "{nombre_sala}" ya existe'
                        }
                    cliente_socket.send(json.dumps(respuesta).encode('utf-8'))
                
                elif tipo == 'unirse_sala':
                    nueva_sala = datos.get('sala')
                    
                    # Salir de sala anterior si existe
                    if sala_actual and sala_actual in self.salas:
                        nombre_salida = self.salas[sala_actual].eliminar_usuario(cliente_socket)
                        notificacion = {
                            'tipo': 'notificacion',
                            'mensaje': f'{nombre_salida} ha salido de la sala'
                        }
                        self.salas[sala_actual].broadcast(json.dumps(notificacion))
                    
                    # Unirse a nueva sala
                    if nueva_sala in self.salas:
                        self.salas[nueva_sala].agregar_usuario(cliente_socket, nombre_usuario)
                        sala_actual = nueva_sala
                        
                        with self.lock:
                            self.clientes[cliente_socket]['sala'] = nueva_sala
                        
                        # Obtener usuarios en la sala
                        usuarios = self.salas[nueva_sala].obtener_usuarios()
                        
                        respuesta = {
                            'tipo': 'sala_unida',
                            'sala': nueva_sala,
                            'usuarios': usuarios,
                            'mensaje': f'Te has unido a la sala "{nueva_sala}"'
                        }
                        cliente_socket.send(json.dumps(respuesta).encode('utf-8'))
                        
                        # Notificar a otros usuarios
                        notificacion = {
                            'tipo': 'notificacion',
                            'mensaje': f'{nombre_usuario} se ha unido a la sala'
                        }
                        self.salas[nueva_sala].broadcast(json.dumps(notificacion), excluir_socket=cliente_socket)
                        
                        print(f"[SALA] {nombre_usuario} se unió a {nueva_sala}")
                
                elif tipo == 'mensaje':
                    if sala_actual and sala_actual in self.salas:
                        contenido = datos.get('contenido')
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        
                        mensaje_broadcast = {
                            'tipo': 'mensaje',
                            'usuario': nombre_usuario,
                            'contenido': contenido,
                            'timestamp': timestamp
                        }
                        
                        self.salas[sala_actual].broadcast(json.dumps(mensaje_broadcast))
                        print(f"[{sala_actual}] {nombre_usuario}: {contenido}")
                
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            # Limpiar al desconectar
            if sala_actual and sala_actual in self.salas:
                nombre_salida = self.salas[sala_actual].eliminar_usuario(cliente_socket)
                if nombre_salida:
                    notificacion = {
                        'tipo': 'notificacion',
                        'mensaje': f'{nombre_salida} se ha desconectado'
                    }
                    self.salas[sala_actual].broadcast(json.dumps(notificacion))
            
            with self.lock:
                if cliente_socket in self.clientes:
                    del self.clientes[cliente_socket]
            
            cliente_socket.close()
            print(f"[DESCONECTADO] {nombre_usuario}")
    
    def detener(self):
        self.ejecutando = False
        if self.servidor_socket:
            self.servidor_socket.close()


if __name__ == '__main__':
    servidor = ServidorChat()
    try:
        servidor.iniciar()
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Deteniendo servidor...")
        servidor.detener()
        print("[SERVIDOR] Servidor detenido")