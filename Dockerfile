# =============================================================================
# Dockerfile — Odoo 19.0 Community + l10n_do_pos
# =============================================================================
# Uso:
#   docker build -t odoo19-l10n-do .
#   docker run -d -p 8069:8069 --name odoo19 \
#     -e HOST=db -e USER=odoo -e PASSWORD=odoo \
#     odoo19-l10n-do
#
# Variables de entorno requeridas en producción:
#   HOST       → hostname del servidor PostgreSQL
#   USER       → usuario de PostgreSQL
#   PASSWORD   → contraseña de PostgreSQL
# =============================================================================

FROM odoo:19.0

# ---------------------------------------------------------------------------
# Metadatos
# ---------------------------------------------------------------------------
LABEL maintainer="tu-email@dominio.com" \
      description="Odoo 19 Community con l10n_do_pos (NCF por Posición Fiscal en POS)" \
      version="19.0.1.0.0"

# ---------------------------------------------------------------------------
# Copiar el módulo personalizado al directorio de addons extras
# ---------------------------------------------------------------------------
USER root

# Crear directorio para addons extra si no existe
RUN mkdir -p /mnt/extra-addons

# Copiar el módulo l10n_do_pos
COPY l10n_do_pos /mnt/extra-addons/l10n_do_pos

# Ajustar permisos
RUN chown -R odoo:odoo /mnt/extra-addons

# ---------------------------------------------------------------------------
# Configuración de Odoo para incluir el directorio de addons extra
# ---------------------------------------------------------------------------
# Sobreescribir odoo.conf para añadir addons_path correcto
RUN echo "[options]" > /etc/odoo/odoo.conf && \
    echo "addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons" >> /etc/odoo/odoo.conf && \
    echo "data_dir = /var/lib/odoo" >> /etc/odoo/odoo.conf && \
    echo "logfile = /var/log/odoo/odoo.log" >> /etc/odoo/odoo.conf && \
    echo "log_level = info" >> /etc/odoo/odoo.conf && \
    chown odoo:odoo /etc/odoo/odoo.conf

# ---------------------------------------------------------------------------
# Volver al usuario odoo para seguridad
# ---------------------------------------------------------------------------
USER odoo

# ---------------------------------------------------------------------------
# Exponer puerto
# ---------------------------------------------------------------------------
EXPOSE 8069 8071 8072

# ---------------------------------------------------------------------------
# Comando por defecto
# ---------------------------------------------------------------------------
CMD ["odoo"]
