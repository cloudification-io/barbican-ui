#!/bin/bash
# devstack/plugin.sh - DevStack plugin for barbican-ui

BARBICAN_UI_DIR=${BARBICAN_UI_DIR:-$DEST/barbican-ui}
HORIZON_DIR=${HORIZON_DIR:-$DEST/horizon}
HORIZON_ENABLED=${HORIZON_DIR}/openstack_dashboard/local/enabled
HORIZON_LOCAL_SETTINGS=${HORIZON_DIR}/openstack_dashboard/local/local_settings.d

function install_barbican_ui {
    setup_develop $BARBICAN_UI_DIR
}

function configure_barbican_ui {
    for f in \
        _91_barbican_secrets.py \
        _92_barbican_containers.py \
        _93_barbican_orders.py \
        _94_barbican_certificates.py
    do
        cp -a ${BARBICAN_UI_DIR}/barbican_ui/enabled/${f} ${HORIZON_ENABLED}/
    done
    cp -a ${BARBICAN_UI_DIR}/barbican_ui/local_settings/d/_91_barbican_settings.py \
          ${HORIZON_LOCAL_SETTINGS}/
}

function cleanup_barbican_ui {
    for f in \
        _91_barbican_secrets.py \
        _92_barbican_containers.py \
        _93_barbican_orders.py \
        _94_barbican_certificates.py
    do
        rm -f ${HORIZON_ENABLED}/${f}
    done
    rm -f ${HORIZON_LOCAL_SETTINGS}/_91_barbican_settings.py
}

if is_service_enabled horizon && is_service_enabled barbican && is_service_enabled barbican-ui; then

    if [[ "$1" == "stack" && "$2" == "pre-install" ]]; then
        :
    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing barbican-ui"
        install_barbican_ui
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring barbican-ui"
        configure_barbican_ui
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        restart_service apache2 || restart_service httpd || true
    fi

    if [[ "$1" == "unstack" ]]; then cleanup_barbican_ui; fi
    if [[ "$1" == "clean" ]];   then cleanup_barbican_ui; fi
fi
