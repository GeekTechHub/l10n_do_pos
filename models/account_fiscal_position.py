# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountFiscalPosition(models.Model):
    """
    Extiende la Posición Fiscal para incluir:

    - pos_invoice_journal_id: el diario que se usará en POS cuando esta
      posición fiscal esté activa (cada diario lleva su propia secuencia NCF).

    - pos_ncf_type: etiqueta corta visible en el POS (ej. 'B01', 'B02').
      Se muestra como badge informativo al cajero antes de validar el pago.

    Flujo esperado:
        Cliente → Posición Fiscal → pos_invoice_journal_id → Secuencia NCF

    Ejemplo de configuración República Dominicana:
        Posición Fiscal "Crédito Fiscal"  → Diario "Ventas B01"  → pos_ncf_type = 'B01'
        Posición Fiscal "Consumidor Final"→ Diario "Ventas B02"  → pos_ncf_type = 'B02'
        Posición Fiscal "Gubernamental"   → Diario "Ventas B14"  → pos_ncf_type = 'B14'
        Posición Fiscal "Regímenes Especiales" → Diario "B15"   → pos_ncf_type = 'B15'
    """
    _inherit = 'account.fiscal.position'

    pos_invoice_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario de Factura en POS',
        domain=[('type', '=', 'sale')],
        ondelete='set null',
        help=(
            'Diario contable que se usará al generar facturas desde el POS '
            'cuando esta posición fiscal esté activa en la orden. '
            'La secuencia de este diario determinará el tipo de NCF asignado '
            '(B01, B02, B14, B15, etc.). '
            'Si no se configura, se utilizará el diario por defecto del POS.'
        ),
    )

    pos_ncf_type = fields.Char(
        string='Tipo NCF en POS',
        size=10,
        help=(
            'Etiqueta corta que se muestra al cajero en la pantalla de pago '
            'del POS para indicar el tipo de comprobante que se generará. '
            'Ejemplos: B01, B02, B14, B15'
        ),
    )
