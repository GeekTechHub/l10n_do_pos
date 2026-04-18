# -*- coding: utf-8 -*-
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    """
    Extiende pos.order para seleccionar automáticamente el diario
    correcto al generar la factura, basándose en la posición fiscal
    del cliente.

    Lógica de selección del diario (prioridad descendiente):
    1. Posición fiscal de la ORDEN (fiscal_position_id en el POS)
    2. Posición fiscal del PARTNER (property_account_position_id)
    3. Diario por defecto del POS (config_id.invoice_journal_id)

    El punto de override es _prepare_invoice_vals(), que es el método
    estándar de pos.order en Odoo 14-19 para preparar los valores
    antes de crear el account.move (factura).
    """
    _inherit = 'pos.order'

    # -------------------------------------------------------------------------
    # Método auxiliar público (puede sobreescribirse por otros módulos)
    # -------------------------------------------------------------------------

    def _get_l10n_do_invoice_journal(self):
        """
        Devuelve el diario correcto para la factura según la posición fiscal.

        Returns:
            account.journal: el diario a usar, o False si no hay configuración
        """
        self.ensure_one()

        # 1. Leer la posición fiscal de la orden POS
        fiscal_position = self.fiscal_position_id

        # 2. Si no hay en la orden, usar la del partner
        if not fiscal_position and self.partner_id:
            fiscal_position = self.partner_id.property_account_position_id

        # 3. Si la posición fiscal tiene un diario POS configurado, usarlo
        if fiscal_position and fiscal_position.pos_invoice_journal_id:
            journal = fiscal_position.pos_invoice_journal_id
            _logger.info(
                "l10n_do_pos: Orden %s → Posición Fiscal '%s' → "
                "Diario '%s' (NCF: %s)",
                self.name,
                fiscal_position.name,
                journal.name,
                fiscal_position.pos_ncf_type or 'N/A',
            )
            return journal

        return False

    # -------------------------------------------------------------------------
    # Override del método de preparación de factura (Odoo 17/18/19)
    # -------------------------------------------------------------------------

    def _prepare_invoice_vals(self):
        """
        Override para inyectar el journal_id correcto según posición fiscal.

        En Odoo 17/18/19, pos.order._prepare_invoice_vals() retorna el dict
        de valores para crear el account.move. El journal_id por defecto
        viene de self.config_id.invoice_journal_id.

        Aquí lo sobreescribimos para usar el diario configurado en la
        posición fiscal cuando existe.
        """
        vals = super()._prepare_invoice_vals()

        journal = self._get_l10n_do_invoice_journal()
        if journal:
            vals['journal_id'] = journal.id

        return vals

    # -------------------------------------------------------------------------
    # Override adicional de _create_invoice como respaldo
    # (cubre casos donde _prepare_invoice_vals no sea llamado directamente)
    # -------------------------------------------------------------------------

    def _create_invoice(self, move_vals):
        """
        Respaldo: si por alguna razón _prepare_invoice_vals no capturó
        el diario correcto, lo inyectamos aquí también en move_vals.

        Nota: move_vals.update() en el super() sobreescribiría nuestros
        valores de _prepare_invoice_vals, así que agregamos el journal
        a move_vals ANTES del super() solo si no viene ya configurado.
        """
        # Solo actuar si no hay ya un journal_id explícito en move_vals
        if not move_vals.get('journal_id'):
            journal = self._get_l10n_do_invoice_journal()
            if journal:
                move_vals['journal_id'] = journal.id

        return super()._create_invoice(move_vals)
