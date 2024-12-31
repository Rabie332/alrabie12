FROM registry.hadooc.com/devops/ci:intermediate as intermediate

RUN git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/base.git \
    && rm -rf base/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/web.git \
    && rm -rf web/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/tools.git \
    && rm -rf tools/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/account.git \
    && rm -rf account/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo-sa/account.git account-sa \
    && rm -rf account-sa/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/payroll.git \
    && rm -rf payroll/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo-sa/payroll.git payroll-sa \
    && rm -rf payroll-sa/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo-sa/theme.git \
    && rm -rf theme/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo-sa/fleet.git \
    && rm -rf fleet/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/crm.git \
    && rm -rf crm/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/dms.git \
    && rm -rf dms/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo-sa/custom/hms.git \
    && rm -rf hms/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/pos.git \
    && rm -rf pos/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo-sa/pos.git pos-sa\
    && rm -rf pos-sa/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/real_estate.git \
    && rm -rf real_estate/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo-sa/hr.git hr-sa \
    && rm -rf hr-sa/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo-sa/purchase.git purchase-sa\
    && rm -rf purchase-sa/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/dashboard_ninja.git dashboard_ninja\
    && rm -rf dashboard_ninja/.git \
    && git clone --depth 1 --branch 14.0 git@gitlab.hadooc.com:odoo/sale.git \
    && rm -rf sale/.git

# Final image
FROM registry.hadooc.com/docker/odoo:14.0
MAINTAINER Hadooc <contact@hadooc.com>
COPY --from=intermediate /base /mnt/extra-addons/
COPY --from=intermediate /web /mnt/extra-addons/
COPY --from=intermediate /tools /mnt/extra-addons/
COPY --from=intermediate /account /mnt/extra-addons/
COPY --from=intermediate /payroll /mnt/extra-addons/
COPY --from=intermediate /dms /mnt/extra-addons/
COPY --from=intermediate /hms /mnt/extra-addons/
COPY --from=intermediate /real_estate /mnt/extra-addons/
COPY --from=intermediate /account-sa /mnt/extra-addons/
COPY --from=intermediate /hr-sa /mnt/extra-addons/
COPY --from=intermediate /payroll-sa /mnt/extra-addons/
COPY --from=intermediate /theme /mnt/extra-addons/
COPY --from=intermediate /fleet /mnt/extra-addons/
COPY --from=intermediate /crm /mnt/extra-addons/
COPY --from=intermediate /pos /mnt/extra-addons/
COPY --from=intermediate /pos-sa /mnt/extra-addons/
COPY --from=intermediate /purchase-sa /mnt/extra-addons/
COPY --from=intermediate /sale /mnt/extra-addons/
COPY --from=intermediate /dashboard_ninja /mnt/extra-addons/
COPY . /mnt/extra-addons
USER root
RUN set -x; \
         pip3 install -r /mnt/extra-addons/requirements.txt \
         && rm -rf /root/.cache/pip/*  \
         && rm -rf /var/lib/apt/lists/*
USER odoo
