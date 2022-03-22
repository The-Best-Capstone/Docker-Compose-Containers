FROM grafana/grafana-enterprise:8.2.0

WORKDIR ~/Docker-Compose-Containers/grafana/

COPY ./defaults.ini /usr/share/grafana/conf/defaults.ini
COPY ./provisioning/datasources /etc/grafana/provisioning/datasources/
COPY ./provisioning/dashboards /etc/grafana/provisioning/dashboards/