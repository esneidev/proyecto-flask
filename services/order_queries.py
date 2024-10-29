from models.pedidos import Pedidos
from models.detalle_pedido import Detalle_pedido
from models.productos import Productos
from models.estado import Estado
from models.usuarios import Usuarios
from models.historial_pedidos import Historial_pedidos
from utils.db import db
from utils.historial import Historial
import datetime

class OrderQueries:
    @staticmethod
    def obtener_pedidos():
        return Pedidos.query.all()

    @staticmethod
    def buscar_producto_por_id(id_prod):
        return Productos.query.get(id_prod)

    @staticmethod
    def actualizar_total_pedido(pedido_id, subtotal):
        pedido = Pedidos.query.get(pedido_id)
        if pedido:
            pedido.total = subtotal
            db.session.commit()

    @staticmethod
    def marcar_producto_inactivo(producto):
        producto.fk_estado = 1
        db.session.commit()

    @staticmethod
    def filtrar_pedidos(estado_id=None, fecha=None):
        query = Pedidos.query
        if estado_id:
            query = query.filter(Pedidos.fk_estado == estado_id)
        if fecha:
            query = query.filter(db.func.date(Pedidos.fecha) == fecha)
        return query.all()

    @staticmethod
    def obtener_detalles_pedido(pedido_id):
        return (Detalle_pedido.query
                .join(Productos)
                .filter(Detalle_pedido.fk_pedido == pedido_id)
                .add_columns(Productos.nombre, Productos.precio, Detalle_pedido.cantidad, Detalle_pedido.subtotal)
                .all())

    @staticmethod
    def finalizar_pedido(productos):
        try:
            Historial.historial_categorias()
            total = sum(item['subtotal'] for item in productos)
            nuevo_pedido = Pedidos(fk_estado=3, total=total, fecha=datetime.datetime.utcnow())
            
            db.session.add(nuevo_pedido)
            db.session.commit()

            for item in productos:
                detalle = Detalle_pedido(
                    fk_pedido=nuevo_pedido.id,
                    fk_producto=item['id'],
                    cantidad=item['cantidad'],
                    subtotal=item['subtotal']
                )
                db.session.add(detalle)
            db.session.commit()

            return nuevo_pedido
        except Exception as e:
            print(f'Ocurrio un error{e}')

    @staticmethod
    def actualizar_estado_pedido(pedido_id):
        try:
            Historial.historial_categorias()
            pedido = Pedidos.query.get(pedido_id)
            if pedido:
                pedido.fk_estado += 1
                db.session.commit()
                return pedido
            return None
        except Exception as e:
            print(f'Ocurrio un error {e}')

    @staticmethod
    def detalle_cambios(pedido_id):
        try:
            result = (
                db.query(
                    Pedidos.id,
                    Historial_pedidos.fecha_cambio,
                    Historial_pedidos.fk_estado,
                    Usuarios.username
                )
                .join(Historial_pedidos, Historial_pedidos.fk_pedido == Pedidos.id)
                .join(Estado, Historial_pedidos.fk_estado == Estado.id)
                .join(Usuarios, Usuarios.id == Historial_pedidos.fk_user)
                .filter(Pedidos.id == pedido_id)
                .all()
            )

            return result
        except Exception as e:
            print(f'Ocurrio un error: {e}')
            return None