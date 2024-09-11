# COMPILADOR - SSPTL2

Compilador contruido como parte del producto integrador requerido para la materia de Seminario de Solución de Problemas de Traductores de Lenguaje 2 impartido por el profesor Roberto Patiño Ruiz

## Descarga del proyecto

Clonar  repositorio

```bash
git clone
```

## Settear ambiente local
(Version de python: 3.12.1)

1. Crear un entorno virtual con **venv** dentro de la nueva carpeta que se creo al clonar el proyecto.

```bash
python -m venv nombre-entorno-virtual
```

2. Activar el entorno virtual creado.
```bash
nombre-entorno-virtual\Scripts\activate
```

3. Instalar los paquetes necesarios que requiere el proyecto para funcionan que vienen indicados en el archivo **requirements.txt**.
```bash
pip install -r requirements.txt
```

Nota: la aplicación para realizar y editar la interfaz del proyecto (Qt Design - design.exe) lo podras encontrar dentro de tu entorno virtual en la siguiente ruta
```bash
entorno-virtual-creado/Lib/Pyside6/
```

## Antes de realizar tu primer push.......
Asegurate que en tu archivo **.gitignore** aparezca por lo menos el siguiente renglon:

nombre-entorno-virtual-creado/  <------------ para que al momento de subir tus cambios no subas paquetes innecesarios a la repo
