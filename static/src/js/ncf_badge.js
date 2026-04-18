/** @odoo-module */
/**
 * l10n_do_pos - NCF Badge en PaymentScreen
 *
 * Patcha el componente PaymentScreen de Odoo 19 POS para añadir
 * un getter reactivo `currentNcfInfo` que expone el tipo de NCF
 * (B01, B02, etc.) según la posición fiscal del cliente seleccionado.
 *
 * El getter es un computed property que se re-evalúa automáticamente
 * cuando cambia el partner de la orden gracias a OWL reactivity.
 *
 * Patrón Odoo 19:
 *   - import { patch } from "@web/core/utils/patch"
 *   - patch(Component.prototype, { getter/method overrides })
 *   - El template usa t-inherit para extender PaymentScreen
 *
 * NO se sobreescribe setup() porque this.pos ya existe en PaymentScreen.
 */

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {

    /**
     * Computed getter: retorna info del NCF según posición fiscal del partner.
     *
     * Accede a:
     *   - this.pos           → POS store (ya disponible en PaymentScreen)
     *   - this.pos.get_order()    → orden actual
     *   - order.get_partner()     → partner seleccionado
     *   - partner.property_account_position_id → [id, name] o id
     *   - this.pos.fiscal_positions → array de posiciones fiscales cargadas
     *
     * Los campos pos_ncf_type y pos_invoice_journal_id son cargados
     * en la sesión gracias al override de _loader_params_account_fiscal_position
     * en pos.session (Python).
     *
     * @returns {Object|null} { ncfType, journalName, fpName } o null
     */
    get currentNcfInfo() {
        // Obtener la orden activa
        const order = this.pos.get_order ? this.pos.get_order() : null;
        if (!order) {
            return null;
        }

        // Obtener el partner seleccionado
        const partner = order.get_partner ? order.get_partner() : null;
        if (!partner) {
            return null;
        }

        // Extraer el ID de la posición fiscal del partner
        // En POS, property_account_position_id puede ser [id, name] o id directo
        const fpRaw = partner.property_account_position_id;
        if (!fpRaw) {
            return null;
        }
        const fpId = Array.isArray(fpRaw) ? fpRaw[0] : fpRaw;
        if (!fpId) {
            return null;
        }

        // Buscar la posición fiscal en las cargadas en la sesión POS
        const fiscalPositions = this.pos.fiscal_positions || [];
        const fp = fiscalPositions.find((f) => f.id === fpId);

        // Solo mostrar badge si la posición fiscal tiene tipo NCF configurado
        if (!fp || !fp.pos_ncf_type) {
            return null;
        }

        // Extraer nombre del diario (pos_invoice_journal_id es [id, name] en POS)
        let journalName = "";
        if (fp.pos_invoice_journal_id) {
            journalName = Array.isArray(fp.pos_invoice_journal_id)
                ? fp.pos_invoice_journal_id[1] || ""
                : "";
        }

        return {
            ncfType: fp.pos_ncf_type,
            journalName: journalName,
            fpName: fp.name || "",
        };
    },
});
