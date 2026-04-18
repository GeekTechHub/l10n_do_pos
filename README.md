# l10n_do_pos — RD POS: Diario NCF por Posición Fiscal

**Versión:** 19.0.1.0.0  
**Compatibilidad:** Odoo 19.0 Community (build 20260209+)  
**Licencia:** LGPL-3  
**Dependencias:** `point_of_sale`, `account`, `l10n_do`

---

## ¿Qué hace este módulo?

Cuando un cajero selecciona un cliente en el **Punto de Venta**, este módulo:

1. **Lee la Posición Fiscal** del cliente (configurada en su ficha de contacto).
2. **Selecciona automáticamente el Diario contable correcto** al generar la factura (y con él, la secuencia NCF: B01, B02, B14, B15…).
3. **Muestra un badge visual** en la pantalla de pago indicando el tipo de NCF que se generará.

No hay intervención manual del cajero para elegir el tipo de comprobante.

---

## Problema que resuelve

En la República Dominicana, la DGII exige secuencias de NCF distintas según el tipo de transacción:

| Tipo de Cliente       | NCF  | Descripción                  |
|-----------------------|------|------------------------------|
| Con RNC (empresa)     | B01  | Crédito Fiscal               |
| Persona física / sin  | B02  | Consumidor Final             |
| Gobierno              | B14  | Gubernamental                |
| Regímenes especiales  | B15  | Regímenes Especiales         |

En Odoo, **cada diario (journal) lleva su propia secuencia**. Este módulo conecta:

```
Cliente → Posición Fiscal → Diario → Secuencia NCF
```

---

## Componentes del módulo

### Python — Backend

#### `models/account_fiscal_position.py`
Extiende `account.fiscal.position` con dos campos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `pos_invoice_journal_id` | Many2one → `account.journal` | Diario a usar en POS al facturar con esta posición fiscal |
| `pos_ncf_type` | Char(10) | Etiqueta visual en POS (ej: `B01`, `B02`) |

#### `models/pos_order.py`
Extiende `pos.order` con dos overrides:

- **`_get_l10n_do_invoice_journal()`** — Método auxiliar que busca el diario correcto según la posición fiscal de la orden o del partner.
- **`_prepare_invoice_vals()`** — Override del método estándar de Odoo 17/18/19 que prepara el dict para crear `account.move`. Aquí se inyecta el `journal_id` correcto.
- **`_create_invoice()`** — Override de respaldo por si otro módulo sobreescribe `_prepare_invoice_vals`.

#### `models/pos_session.py`
Extiende `pos.session` para incluir los campos `pos_invoice_journal_id` y `pos_ncf_type` en los datos enviados al frontend POS al iniciar la sesión.

Override del método:
```python
_loader_params_account_fiscal_position()
```

### OWL — Frontend (JavaScript / XML / SCSS)

#### `static/src/js/ncf_badge.js`
Usa el patrón `patch()` de Odoo 19 para extender `PaymentScreen.prototype` con el getter reactivo `currentNcfInfo`.

```javascript
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    get currentNcfInfo() { ... }
});
```

El getter retorna `{ ncfType, journalName, fpName }` o `null` si no hay posición fiscal configurada.

#### `static/src/xml/ncf_badge.xml`
Extiende el template QWeb de `PaymentScreen` usando:

```xml
<t t-name="l10n_do_pos.PaymentScreen"
   t-inherit="point_of_sale.PaymentScreen"
   t-inherit-mode="extension">
```

Inserta el badge después del botón `partner-button` (selector de cliente).

#### `static/src/scss/ncf_badge.scss`
Estilos del badge con colores diferenciados por tipo NCF.

---

## Instalación

### Requisitos previos

1. Odoo 19.0 Community instalado con `l10n_do` activo en la base de datos.
2. Los diarios NCF (B01, B02, etc.) deben estar creados y con sus secuencias configuradas en `Contabilidad → Configuración → Diarios`.

### Método 1: Docker (recomendado)

Ver sección **Dockerfile** al final de este README.

### Método 2: Addons manual

```bash
# Copiar la carpeta del módulo al directorio de addons
cp -r l10n_do_pos /opt/odoo/custom-addons/

# Reiniciar Odoo
systemctl restart odoo   # o docker restart <nombre_contenedor>
```

Luego en Odoo:
1. Activar **Modo Desarrollador** (`Ajustes → Activar modo de desarrollador`).
2. Ir a `Aplicaciones → Actualizar lista de aplicaciones`.
3. Buscar `l10n_do_pos` e instalar.

---

## Configuración paso a paso

### Paso 1: Crear/verificar los Diarios NCF

Ir a `Contabilidad → Configuración → Diarios` y confirmar que existen:

| Nombre sugerido       | Tipo  | Secuencia configurada |
|-----------------------|-------|-----------------------|
| Ventas Crédito Fiscal | Venta | B01XXXXXXXX           |
| Ventas Consumidor     | Venta | B02XXXXXXXX           |

### Paso 2: Vincular el Diario a la Posición Fiscal

Ir a `Contabilidad → Configuración → Posiciones Fiscales` y en cada posición:

1. Abrir la posición fiscal (ej: "Crédito Fiscal B01").
2. Bajar hasta la sección **"Configuración Punto de Venta (NCF)"**.
3. Seleccionar el **Diario de Factura en POS** → ej: `Ventas Crédito Fiscal`.
4. Escribir el **Tipo NCF en POS** → ej: `B01`.
5. Guardar.

### Paso 3: Asignar la Posición Fiscal al Cliente

Ir a `Contabilidad → Clientes → Clientes` (o `Contactos`):

1. Abrir la ficha del cliente.
2. Pestaña **"Ventas y Compras"**.
3. Campo **"Posición Fiscal"** → seleccionar `Crédito Fiscal B01` o `Consumidor Final B02`.
4. Guardar.

### Paso 4: Verificar en el POS

1. Abrir una sesión POS.
2. Agregar productos al carrito.
3. Seleccionar un cliente que tenga posición fiscal configurada.
4. Ir a la pantalla de pago.
5. Se debería ver el badge **"NCF: B01"** (o B02) junto al botón del cliente.
6. Validar el pago con factura → la factura se crea en el diario B01/B02 correcto.

---

## Lógica de prioridad del diario

```
1. Posición Fiscal de la ORDEN POS (fiscal_position_id)
   └── Si tiene pos_invoice_journal_id → usar ese diario

2. Si no hay posición fiscal en la orden:
   Posición Fiscal del PARTNER (property_account_position_id)
   └── Si tiene pos_invoice_journal_id → usar ese diario

3. Si ninguna posición fiscal tiene diario configurado:
   → Usar el diario por defecto del POS (config_id.invoice_journal_id)
   → Comportamiento estándar de Odoo sin cambios
```

---

## Compatibilidad con l10n_do

Este módulo es **complementario** a `l10n_do`. No sobreescribe ni reemplaza su funcionalidad — únicamente agrega dos campos a `account.fiscal.position` y un override en la creación de facturas desde POS.

La secuencia NCF real (B01XXXXXXXX, B02XXXXXXXX) es gestionada íntegramente por `l10n_do` a través del diario. Este módulo solo asegura que **el diario correcto sea seleccionado**.

---

## Dockerfile

```dockerfile
FROM odoo:19.0

# Copiar la localización dominicana (si no la tienes ya)
# COPY l10n-dominicana /mnt/extra-addons/l10n-dominicana

# Copiar este módulo
COPY l10n_do_pos /mnt/extra-addons/l10n_do_pos

USER root
RUN chown -R odoo:odoo /mnt/extra-addons/l10n_do_pos
USER odoo
```

---

## Solución de problemas

### Badge no aparece en el POS

- Verificar que el módulo está instalado y la sesión POS fue **reiniciada** (no solo recargada).
- Confirmar que la posición fiscal tiene `pos_ncf_type` y `pos_invoice_journal_id` configurados.
- Confirmar que el cliente tiene la posición fiscal asignada en su ficha.
- Revisar la consola del navegador (F12) por errores JS.

### La factura sigue usando el diario incorrecto

- Verificar que el `pos_invoice_journal_id` en la posición fiscal apunta al diario correcto.
- Activar el log de Python: en los logs de Odoo buscar líneas con `l10n_do_pos:`.
- Si otro módulo también sobreescribe `_prepare_invoice_vals`, puede haber conflicto de prioridad.

### Error de bundle al instalar

- Asegurarse de que los archivos JS y XML usan el patrón correcto de Odoo 19 (`@odoo-module`, `t-inherit`).
- Verificar que el `__manifest__.py` lista los assets bajo `point_of_sale._assets_pos`.
- Borrar caché del navegador y reiniciar el servidor Odoo.

---

## Contribuir

Pull requests bienvenidos. Por favor seguir las guías de contribución de OCA.
