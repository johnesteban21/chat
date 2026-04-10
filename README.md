# Chat

Aplicación de chat colaborativo en tiempo real desarrollada en Python, basada en arquitectura cliente-servidor con sockets, soporte para salas de conversación y una interfaz gráfica de escritorio construida con Tkinter.

## Descripción

**Chat** es un proyecto de comunicación en tiempo real que implementa un sistema de mensajería colaborativa mediante una arquitectura cliente-servidor. La aplicación permite a varios usuarios conectarse a un servidor, visualizar salas disponibles, crear nuevas salas de conversación, unirse a ellas y enviar mensajes en tiempo real.

El proyecto incluye una interfaz gráfica amigable desarrollada con **Tkinter** para el cliente, mientras que el servidor administra conexiones concurrentes utilizando **sockets**, **threads** y mensajería estructurada en **JSON**.

## Objetivos del proyecto

- Implementar un sistema de chat en tiempo real basado en sockets.
- Aplicar conceptos de comunicación cliente-servidor.
- Gestionar múltiples usuarios y salas de conversación.
- Desarrollar una interfaz gráfica funcional para mejorar la experiencia de uso.
- Fortalecer conocimientos en concurrencia, redes y estructuración de aplicaciones en Python.

## Funcionalidades principales

- Conexión de usuarios a un servidor TCP.
- Creación y listado de salas de chat.
- Unión dinámica a salas disponibles.
- Envío y recepción de mensajes en tiempo real.
- Gestión de múltiples clientes mediante hilos.
- Notificaciones de conexión, desconexión y cambios de sala.
- Interfaz gráfica de escritorio para la experiencia del usuario.

## Tecnologías utilizadas

- Python
- Socket Programming
- Threading
- Tkinter
- JSON

## Estructura del proyecto

```bash
chat_cliente.py    # Cliente gráfico de chat
chat_servidor.py   # Servidor de mensajería en tiempo real
```

## Valor del proyecto

Este proyecto demuestra experiencia en desarrollo con Python, programación de redes, comunicación en tiempo real, concurrencia con hilos y construcción de interfaces gráficas para aplicaciones de escritorio.

## Estado del proyecto

Finalizado como proyecto funcional y abierto a mejoras.

## Autor

**John Esteban**