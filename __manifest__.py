# -*- coding: utf-8 -*-
{
    'name': 'RD - POS Diario por Posición Fiscal (NCF)',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Selecciona automáticamente el diario NCF (B01/B02) en POS según la posición fiscal del cliente',
    'description': """
RD POS NCF Journal by Fiscal Position
======================================
Este módulo permite que, al generar una factura desde el Punto de Venta,
se seleccione automáticamente el diario contable correcto (y su secuencia NCF)
según la posición fiscal configurada en el cliente.

Funcionalidades:
- Campo 'Diario de Factura en POS' en cada Posición Fiscal
- Campo 'Tipo NCF' (ej: B01, B02) visible como etiqueta en POS
- Lógica Python que inyecta el diario correcto al crear la factura
- Indicador visual en la pantalla de pago del POS
- Compatible con l10n_do y Odoo 19 Community

Dependencias requeridas:
- l10n_do (localización dominicana)
    """,
    'author': 'Localización RD Community',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'account',
        'l10n_do',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_position_views.xml',
    ],
    'assets': {
        # Bundle de assets del POS en Odoo 17/18/19
        'point_of_sale._assets_pos': [
            'l10n_do_pos/static/src/js/ncf_badge.js',
            'l10n_do_pos/static/src/xml/ncf_badge.xml',
            'l10n_do_pos/static/src/scss/ncf_badge.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
