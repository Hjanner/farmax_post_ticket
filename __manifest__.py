# -*- coding: utf-8 -*-
{
    'name': "Farmax POS - Ticket Gana Max (58mm)",
    'summary': "Genera tickets de 58mm al facturar en el Punto de Venta "
               "(1 ticket por cada $10 facturados).",
    'description': """
Al facturar una orden en el Punto de Venta, este modulo genera un PDF con
tickets de 58 x 58 mm (una pagina cuadrada por ticket). Se emite un ticket
por cada 10 del total de la factura (>= 10 => 1 ticket, >= 20 => 2 tickets,
etc.), con un tope de seguridad configurable. Cada ticket contiene:

    CON FARMAX GANA MAX
    NOMBRE
    APELLIDO
    CEDULA
    TELEFONO
    NUMERO DE FACTURA (el numero real del asiento para la trazabilidad)

El PDF se adjunta a la factura, se anota en el chatter y, al validar la venta
en el TPV, se abre automaticamente en el navegador para imprimirlo. Tambien
esta disponible en el menu Imprimir de la factura.
    """,
    'author': "Farmax",
    'category': 'Point of Sale',
    'version': '17.0.1.1.0',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'point_of_sale',
        'account',
    ],
    'data': [
        'report/paperformat.xml',
        'report/farmax_ticket_report.xml',
        'report/farmax_ticket_templates.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'farmax_pos_ticket/static/src/js/payment_screen_ticket.js',
        ],
    },
}
