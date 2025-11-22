# Image de base : Odoo 17 officielle
FROM odoo:17.0

# On passe en root pour copier fichiers + permissions
USER root

# Copier les modules custom dans /mnt/extra-addons
COPY ./addons /mnt/extra-addons

# Copier la config Odoo
COPY ./config/odoo.conf /etc/odoo/odoo.conf

# Fixer les permissions
RUN chown -R odoo:odoo /mnt/extra-addons /etc/odoo/odoo.conf

# Retour à l'utilisateur odoo
USER odoo

# Le ENTRYPOINT/CMD de l'image odoo:17.0 reste le même
