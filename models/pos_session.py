# -*- coding: utf-8 -*-
from odoo import models


class PosSession(models.Model):
    """
    Extiende pos.session para incluir los campos personalizados de
    posición fiscal (pos_invoice_journal_id y pos_ncf_type) en los
    datos que se cargan al abrir una sesión POS.

    En Odoo 17/18/19, el método _loader_params_account_fiscal_position()
    define qué campos de account.fiscal.position se envían al frontend.
    Al extenderlo, el OWL frontend puede acceder a nuestros campos y
    mostrar el badge informativo del tipo NCF.
    """
    _inherit = 'pos.session'

    def _loader_params_account_fiscal_position(self):
        """
        Extiende los campos cargados para account.fiscal.position
        en la sesión POS, añadiendo nuestros campos personalizados.

        Campos añadidos:
        - pos_invoice_journal_id: [id, nombre] del diario de factura
        - pos_ncf_type: etiqueta del tipo NCF (ej: 'B01', 'B02')
        """
        result = super()._loader_params_account_fiscal_position()

        # Aseguramos que 'fields' existe en search_params
        if 'search_params' not in result:
            result['search_params'] = {}
        if 'fields' not in result['search_params']:
            result['search_params']['fields'] = []

        extra_fields = ['pos_invoice_journal_id', 'pos_ncf_type']
        for field in extra_fields:
            if field not in result['search_params']['fields']:
                result['search_params']['fields'].append(field)

        return result
