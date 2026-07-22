[![flake8](https://github.com/EOEPCA/resource-catalogue-metrics/workflows/flake8/badge.svg)](https://github.com/EOEPCA/resource-catalogue-metrics/actions)

# resource-catalogue-metrics

EOEPCA Resource Catalogue metrics service.


## Workflow

- runs on a schedule (per `resource-catalogue-metrics-management/dockekr/resource-catalogue-metrics-management.cron`) to analyze a resource catalogue instance (as defined in `$RESOURCE_CATALOGUE_METRICS_CATALOGUE_URL`)
- queries catalogue to derive metrics
- publishes to broker service (MQTT)
- sends metrics to a Prometheus collector
- collect real-time and offline Resource Catalogue metrics and makes them available as [OpenMetrics](https://openmetrics.io)
- provides analytics and visualization via [Prometheus](https://prometheus.io) and [Grafana](https://grafana.com)

## Installation

### Requirements
- Docker

### Dependencies
Dependencies are embedded in service definitions and orchestrated by Docker.

## Running

### Docker

The Docker setup uses Docker and Docker Compose to manage the following services:

- **resource-catalogue-metrics-monitoring**: monitoring
  - **resource-catalogue-metrics-metrics-collector**: metrics collector
  - **resource-catalogue-metrics-prometheus**: metrics scraper
  - **resource-catalogue-metrics-grafana**: analytics and visualization
- **resource-catalogue-metrics-broker**: MQTT broker
- **resource-catalogue-metrics-management**: management service to publich metrics from a Resource Catalogue instance (as defined in `$RESOURCE_CATALOGUE_METRICS_CATALOGUE_URL`)

See [`resource-catalogue-metrics.env`](resource-catalogue-metrics.env) for default environment variable settings.

To adjust service ports, edit [`docker-compose.override.yml`](docker-compose.override.yml) accordingly.

The [`Makefile`](Makefile) in the root directory provides options to manage the Docker Compose setup.

```bash
# build all images
make build

# build all images (no cache)
make force-build

# start all containers
make up

# reinitialize backend
make reinit-backend

# start all containers in dev mode
make dev

# view all container logs in realtime
make logs

# login to the resource-catalogue-metrics-management container
make login

# restart all containers
make restart

# shutdown all containers
make down

# remove all volumes
make rm
```

## Development

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/EOEPCA/resource-catalogue-metrics/issues).

## Contact

* [Angelos Tzotsos](https://github.com/kalxas)
