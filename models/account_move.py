# -*- coding: utf-8 -*-
from odoo import models

# Cada cuantos USD del total de la factura se emite un ticket.
FARMAX_TICKET_STEP = 10.0
# Tope de seguridad para no bloquear el servidor generando miles de paginas.
# Se puede ajustar con el parametro de sistema 'farmax_pos_ticket.max_tickets'.
FARMAX_TICKET_MAX_DEFAULT = 100


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _farmax_ticket_max(self):
        value = self.env['ir.config_parameter'].sudo().get_param(
            'farmax_pos_ticket.max_tickets', FARMAX_TICKET_MAX_DEFAULT)
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return FARMAX_TICKET_MAX_DEFAULT

    def farmax_ticket_count(self):
        """Numero de tickets a imprimir para esta factura.

        < 10  -> 0 tickets
        10-19 -> 1 ticket
        20-29 -> 2 tickets ... (uno por cada FARMAX_TICKET_STEP USD)

        Se limita al tope de seguridad 'farmax_pos_ticket.max_tickets'.
        """
        self.ensure_one()
        total = self.amount_total or 0.0
        if total < FARMAX_TICKET_STEP:
            return 0
        return min(int(total // FARMAX_TICKET_STEP), self._farmax_ticket_max())

    def farmax_ticket_range(self):
        """Iterable para el t-foreach del QWeb: [1, 2, ..., n]."""
        self.ensure_one()
        return range(1, self.farmax_ticket_count() + 1)

    def farmax_partner_data(self):
        """Datos del cliente para el ticket."""
        self.ensure_one()
        partner = self.partner_id
        firstname = lastname = ''
        # Compatibilidad con partner_firstname (OCA) si estuviera instalado.
        if 'firstname' in partner._fields and (partner.firstname or partner.lastname):
            firstname = partner.firstname or ''
            lastname = partner.lastname or ''
        else:
            parts = (partner.name or '').split()
            if parts:
                firstname = parts[0]
                lastname = ' '.join(parts[1:])
        return {
            'firstname': firstname,
            'lastname': lastname,
            'vat': partner.vat or '',
            'phone': partner.phone or partner.mobile or '',
            # Numero REAL de la factura para la trazabilidad de la compra.
            'invoice_number': self.name or '',
        }
