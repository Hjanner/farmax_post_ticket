# -*- coding: utf-8 -*-
import logging

from odoo import _, models

_logger = logging.getLogger(__name__)

REPORT_XMLID = 'farmax_pos_ticket.action_report_farmax_ganamax_ticket'


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _generate_pos_order_invoice(self):
        res = super()._generate_pos_order_invoice()
        for order in self:
            move = order.account_move
            if not move:
                continue
            try:
                order._farmax_generate_ticket_pdf(move)
            except Exception:  # noqa: BLE001 - no bloquear la facturacion del PdV
                _logger.exception(
                    "Farmax: no se pudo generar el ticket Gana Max para la factura %s",
                    move.name,
                )
        return res

    def _farmax_generate_ticket_pdf(self, move):
        """Renderiza el PDF de tickets y lo adjunta a la factura (una sola vez)."""
        self.ensure_one()
        count = move.farmax_ticket_count()
        if count <= 0:
            return

        attachment_name = 'Ticket Gana Max - %s.pdf' % (move.name or self.name)
        already = self.env['ir.attachment'].search_count([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', move.id),
            ('name', '=', attachment_name),
        ])
        if already:
            return

        report = self.env.ref(REPORT_XMLID)
        pdf_content, _content_type = report._render_qweb_pdf(REPORT_XMLID, move.ids)

        self.env['ir.attachment'].create({
            'name': attachment_name,
            'res_model': 'account.move',
            'res_id': move.id,
            'type': 'binary',
            'raw': pdf_content,
            'mimetype': 'application/pdf',
        })
        move.message_post(
            body=_("Se generaron %s ticket(s) CON FARMAX GANA MAX (58 mm).") % count,
        )
