# Biblioteca Personal (CLI) - Python + SQLite

Aplicación de **línea de comandos** para gestionar una biblioteca personal.
Permite **agregar, actualizar, eliminar, listar y buscar** libros almacenados en SQLite.

## Requisitos
- Python 3.9+
- No requiere paquetes externos (usa `sqlite3` de la librería estándar).

## Ejecución
```bash
python main.py
```

> La primera ejecución crea automáticamente la base `biblioteca.db` y la tabla `libros` si no existen.

## Estructura de la base
Tabla `libros`:
- id (INTEGER, PK AUTOINCREMENT)
- titulo (TEXT, NOT NULL)
- autor (TEXT, NOT NULL)
- genero (TEXT, NOT NULL)
- leido (INTEGER 0/1, NOT NULL, por defecto 0)

## Funcionalidades
- Agregar nuevo libro (título, autor, género, leído/no leído).
- Actualizar libro por ID (cualquier campo).
- Eliminar libro por ID (confirmación).
- Listar todos los libros (formato tabular).
- Buscar por título, autor o género.
- Salir del programa.

## Notas
- El estado **leído** se guarda como `0` (No leído) o `1` (Leído).
- Las consultas usan **parámetros** para evitar inyecciones SQL.
