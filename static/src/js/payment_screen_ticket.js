/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    async afterOrderValidation(suggestToSync = true) {
        await this._farmaxOpenGanaMaxTickets();
        return super.afterOrderValidation(...arguments);
    },

    async _farmaxOpenGanaMaxTickets() {
        try {
            const order = this.currentOrder;
            if (!order || !order.is_to_invoice()) {
                return;
            }
            // Misma regla que el servidor: 1 ticket por cada $10, minimo $10.
            if (order.get_total_with_tax() < 10) {
                return;
            }
            const orderId = order.server_id || order.backendId;
            if (!orderId) {
                return;
            }
            const [rec] = await this.orm.read(
                "pos.order",
                [orderId],
                ["account_move"],
                { load: false }
            );
            if (rec && rec.account_move) {
                await this.report.doAction(
                    "farmax_pos_ticket.action_report_farmax_ganamax_ticket",
                    [rec.account_move]
                );
            }
        } catch (error) {
            // No bloquear el cierre de la venta si falla la apertura del PDF.
            console.warn("Farmax: no se pudieron abrir los tickets Gana Max", error);
        }
    },
});
