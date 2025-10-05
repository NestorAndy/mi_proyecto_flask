import sqlite3
from dataclasses import dataclass, asdict
from typing import Dict, List
import os

@dataclass
class Producto:
    id: int = None
    nombre: str = ''
    cantidad: int = 0
    precio: float = 0.0

    def to_dict(self):
        return {'id': self.id, 'nombre': self.nombre, 'cantidad': self.cantidad, 'precio': self.precio}

class Inventario:
    def __init__(self):
        # uso de diccionario para búsquedas rápidas por id
        self.productos: Dict[int, Producto] = {}
        # mantener contador local si es necesario
        self._next_id = 1

    def _assign_id(self, producto: Producto):
        if producto.id is None:
            producto.id = self._next_id
            self._next_id += 1

    def add_producto(self, producto: Producto, save_db=True):
        self._assign_id(producto)
        self.productos[producto.id] = producto
        return producto

    def eliminar_producto(self, id_producto: int):
        return self.productos.pop(id_producto, None)

    def update_producto(self, id_producto: int, nombre=None, cantidad=None, precio=None):
        p = self.productos.get(id_producto)
        if not p:
            return None
        if nombre is not None: p.nombre = nombre
        if cantidad is not None: p.cantidad = cantidad
        if precio is not None: p.precio = precio
        return p

    def buscar_por_nombre(self, nombre: str) -> List[Producto]:
        nombre_lower = nombre.lower()
        return [p for p in self.productos.values() if nombre_lower in p.nombre.lower()]

    def mostrar_todos(self) -> List[Producto]:
        return list(self.productos.values())

# Interfaz de consola (menú)
def menu_console(inventario: Inventario):
    while True:
        print("\n--- MENU INVENTARIO ---")
        print("1) Añadir producto")
        print("2) Eliminar producto por ID")
        print("3) Actualizar producto")
        print("4) Buscar por nombre")
        print("5) Mostrar todos")
        print("0) Salir")
        op = input("Opción: ").strip()
        if op == '1':
            nombre = input("Nombre: ")
            cantidad = int(input("Cantidad: "))
            precio = float(input("Precio: "))
            p = Producto(nombre=nombre, cantidad=cantidad, precio=precio)
            inventario.add_producto(p)
            print("Añadido:", p)
        elif op == '2':
            idp = int(input("ID a eliminar: "))
            removed = inventario.eliminar_producto(idp)
            print("Eliminado:", removed)
        elif op == '3':
            idp = int(input("ID a actualizar: "))
            nombre = input("Nombre (dejar vacío para no cambiar): ")
            cantidad = input("Cantidad (vacío para no cambiar): ")
            precio = input("Precio (vacío para no cambiar): ")
            cantidad = int(cantidad) if cantidad else None
            precio = float(precio) if precio else None
            updated = inventario.update_producto(idp, nombre=nombre or None, cantidad=cantidad, precio=precio)
            print("Actualizado:", updated)
        elif op == '4':
            q = input("Nombre a buscar: ")
            res = inventario.buscar_por_nombre(q)
            print("Resultados:", res)
        elif op == '5':
            print("Todos:", inventario.mostrar_todos())
        elif op == '0':
            break
        else:
            print("Opción inválida.")