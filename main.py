
"""
Biblioteca personal - Aplicación CLI en Python + SQLite
Autor: (coloca tu nombre)
Descripción: CRUD y búsqueda de libros almacenados en SQLite.
Requisitos: Python 3.9+ (stdlib) - no necesita dependencias externas.

Uso rápido:
    python main.py
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Tuple

DB_PATH = "biblioteca.db"

# ---------- Modelo ----------
@dataclass
class Libro:
    titulo: str
    autor: str
    genero: str
    leido: bool = False

# ---------- Capa de datos ----------
def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_bd():
    with conectar() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS libros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                genero TEXT NOT NULL,
                leido INTEGER NOT NULL DEFAULT 0 CHECK (leido IN (0,1))
            );
            """
        )

# ---------- Utilidades de UI ----------
def limpiar():
    # Minimal para Windows/Linux/macOS sin borrar la consola (evita dependencias).
    print("\n" + "-"*70 + "\n")

def bool_a_texto(b: int | bool) -> str:
    return "Leído" if int(b) == 1 else "No leído"

def pedir_si_no(mensaje: str, default: Optional[bool] = None) -> bool:
    sufijo = " [s/n]"
    if default is True:
        sufijo = " [S/n]"
    elif default is False:
        sufijo = " [s/N]"
    while True:
        resp = input(mensaje + sufijo + ": ").strip().lower()
        if not resp and default is not None:
            return default
        if resp in ("s", "si", "sí", "y", "yes"):
            return True
        if resp in ("n", "no"):
            return False
        print("→ Respuesta inválida. Intenta con s/n.")

def pedir_no_vacio(msg: str, default: Optional[str] = None) -> str:
    while True:
        val = input(f"{msg}" + (f" [{default}]" if default else "") + ": ").strip()
        if not val and default is not None:
            return default
        if val:
            return val
        print("→ No puede estar vacío.")

def pedir_estado(default: Optional[bool] = None) -> bool:
    return pedir_si_no("¿El libro está leído?", default=default)

# ---------- Operaciones CRUD ----------
def agregar_libro(libro: Libro) -> int:
    with conectar() as conn:
        cur = conn.execute(
            "INSERT INTO libros (titulo, autor, genero, leido) VALUES (?, ?, ?, ?);",
            (libro.titulo, libro.autor, libro.genero, 1 if libro.leido else 0),
        )
        return cur.lastrowid

def actualizar_libro(id_libro: int, titulo: str, autor: str, genero: str, leido: bool) -> bool:
    with conectar() as conn:
        cur = conn.execute(
            """
            UPDATE libros
               SET titulo = ?, autor = ?, genero = ?, leido = ?
             WHERE id = ?;
            """,
            (titulo, autor, genero, 1 if leido else 0, id_libro),
        )
        return cur.rowcount > 0

def eliminar_libro(id_libro: int) -> bool:
    with conectar() as conn:
        cur = conn.execute("DELETE FROM libros WHERE id = ?;", (id_libro,))
        return cur.rowcount > 0

def obtener_libros() -> List[Tuple]:
    with conectar() as conn:
        cur = conn.execute("SELECT id, titulo, autor, genero, leido FROM libros ORDER BY id;")
        return cur.fetchall()

def buscar_libros(termino: str, campo: str) -> List[Tuple]:
    if campo not in {"titulo", "autor", "genero"}:
        raise ValueError("Campo inválido para búsqueda.")
    q = f"SELECT id, titulo, autor, genero, leido FROM libros WHERE {campo} LIKE ? ORDER BY id;"
    with conectar() as conn:
        cur = conn.execute(q, (f"%{termino}%",))
        return cur.fetchall()

def obtener_libro_por_id(id_libro: int) -> Optional[Tuple]:
    with conectar() as conn:
        cur = conn.execute("SELECT id, titulo, autor, genero, leido FROM libros WHERE id = ?;", (id_libro,))
        return cur.fetchone()

# ---------- Interfaz CLI ----------
def mostrar_libros(filas: List[Tuple]):
    if not filas:
        print("No hay libros para mostrar.")
        return
    print(f"{'ID':<4} {'TÍTULO':<30} {'AUTOR':<22} {'GÉNERO':<15} ESTADO")
    print("-"*85)
    for (id_, titulo, autor, genero, leido) in filas:
        print(f"{id_:<4} {titulo[:29]:<30} {autor[:21]:<22} {genero[:14]:<15} {bool_a_texto(leido)}")

def accion_agregar():
    limpiar()
    print("➕ Agregar nuevo libro")
    titulo = pedir_no_vacio("Título")
    autor = pedir_no_vacio("Autor")
    genero = pedir_no_vacio("Género")
    leido = pedir_estado(default=False)
    libro = Libro(titulo=titulo, autor=autor, genero=genero, leido=leido)
    nuevo_id = agregar_libro(libro)
    print(f"✔ Libro agregado con ID {nuevo_id}")

def accion_actualizar():
    limpiar()
    print("✏️  Actualizar libro")
    try:
        id_libro = int(pedir_no_vacio("ID del libro a actualizar"))
    except ValueError:
        print("→ ID inválido.")
        return
    actual = obtener_libro_por_id(id_libro)
    if not actual:
        print("→ No existe un libro con ese ID.")
        return
    _, t, a, g, l = actual
    print("Deja en blanco para mantener el valor actual.")
    titulo = pedir_no_vacio("Título", default=t)
    autor  = pedir_no_vacio("Autor", default=a)
    genero = pedir_no_vacio("Género", default=g)
    leido  = pedir_estado(default=bool(l))
    ok = actualizar_libro(id_libro, titulo, autor, genero, leido)
    print("✔ Libro actualizado" if ok else "→ No se pudo actualizar.")

def accion_eliminar():
    limpiar()
    print("🗑  Eliminar libro")
    try:
        id_libro = int(pedir_no_vacio("ID del libro a eliminar"))
    except ValueError:
        print("→ ID inválido.")
        return
    if not obtener_libro_por_id(id_libro):
        print("→ No existe un libro con ese ID.")
        return
    if pedir_si_no("¿Seguro que deseas eliminarlo?"):
        ok = eliminar_libro(id_libro)
        print("✔ Libro eliminado" if ok else "→ No se pudo eliminar.")
    else:
        print("Operación cancelada.")

def accion_listar():
    limpiar()
    print("📚 Listado de libros")
    filas = obtener_libros()
    mostrar_libros(filas)

def accion_buscar():
    limpiar()
    print("🔎 Buscar libros")
    print("Buscar por: 1) Título  2) Autor  3) Género")
    opcion = input("Elige (1-3): ").strip()
    mapa = {"1": "titulo", "2": "autor", "3": "genero"}
    campo = mapa.get(opcion)
    if not campo:
        print("→ Opción inválida.")
        return
    termino = pedir_no_vacio(f"Término a buscar en {campo}")
    filas = buscar_libros(termino, campo)
    mostrar_libros(filas)

def menu_principal():
    inicializar_bd()
    while True:
        limpiar()
        print("=== Biblioteca Personal ===")
        print("1) Agregar libro")
        print("2) Actualizar libro")
        print("3) Eliminar libro")
        print("4) Ver listado de libros")
        print("5) Buscar libros")
        print("0) Salir")
        opcion = input("Selecciona una opción: ").strip()
        if opcion == "1":
            accion_agregar()
        elif opcion == "2":
            accion_actualizar()
        elif opcion == "3":
            accion_eliminar()
        elif opcion == "4":
            accion_listar()
        elif opcion == "5":
            accion_buscar()
        elif opcion == "0":
            print("¡Hasta luego!")
            break
        else:
            print("→ Opción no válida.")
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    menu_principal()
