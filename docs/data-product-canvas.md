# Data Product Canvas - Berlin LOR Daycare Centers

## Input Ports

**Input ports define the format and protocol in which data can be read (database, file, API, visualizations)**

This data product uses LOR geodata provided by data
product [open-lifeworlds-data-product-berlin-lor-geodata](https://github.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-geodata)
published under the following URLs

* [berlin-lor-districts/berlin-lor-districts.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-geodata/main/data/berlin-lor-districts/berlin-lor-districts.geojson)
* [berlin-lor-forecast-areas-until-2020/berlin-lor-forecast-areas-until-2020.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-geodata/main/data/berlin-lor-forecast-areas-until-2020/berlin-lor-forecast-areas-until-2020.geojson)
* [berlin-lor-forecast-areas-from-2021/berlin-lor-forecast-areas-from-2021.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-geodata/main/data/berlin-lor-forecast-areas-from-2021/berlin-lor-forecast-areas-from-2021.geojson)
* [berlin-lor-district-regions-until-2020/berlin-lor-district-regions-until-2020.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-geodata/main/data/berlin-lor-district-regions-until-2020/berlin-lor-district-regions-until-2020.geojson)
* [berlin-lor-district-regions-from-2021/berlin-lor-district-regions-from-2021.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-geodata/main/data/berlin-lor-district-regions-from-2021/berlin-lor-district-regions-from-2021.geojson)
* [berlin-lor-planning-areas-until-2020/berlin-lor-planning-areas-until-2020.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-geodata/main/data/berlin-lor-planning-areas-until-2020/berlin-lor-planning-areas-until-2020.geojson)
* [berlin-lor-planning-areas-from-2021/berlin-lor-planning-areas-from-2021.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-geodata/main/data/berlin-lor-planning-areas-from-2021/berlin-lor-planning-areas-from-2021.geojson)

and detailed daycare center data provided by data product [open-lifeworlds-data-product-berlin-lor-daycare-centers-source-aligned](https://github.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-daycare-centers-source-aligned) published under the following URLs

* [berlin-lor-daycare-centers-2024-01-details.csv](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-daycare-centers-source-aligned/main/data/berlin-lor-daycare-centers-2024-01/berlin-lor-daycare-centers-2024-01-details.csv)

and statistical population data provided by data
product [open-lifeworlds-data-product-berlin-lor-population](https://github.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-population)
published under the following URLs

* [berlin-lor-population-statistics/berlin-lor-population-statistics.json](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-population/main/data/berlin-lor-population-statistics/berlin-lor-population-statistics.json)

## Data Product Design

**Describe everything you need to design a data product on a conceptual level.**
**Ingestion, storage, transport, wrangling, cleaning, transformations, enrichment, augmentation, analytics, SQL
statements, or used data platform services.**

* [assign LOR area to daycare center](../lib/transform/data_lor_area_assigner.py)
* [aggregates daycare centers](../lib/transform/data_aggregator.py) on LOR area level
* [blends statistical data into geojson](../lib/transform/data_blender.py) on different LOR area hierarchy levels
* [aggregates statistical data into json](../lib/transform/data_blender.py) on different LOR area hierarchy levels

## Output Ports

**Output ports define the format and protocol in which data can be exposed (db, file, API, visualizations)**

The data of this data product is available under the following URLs

* [berlin-lor-daycare-centers-2024-01/berlin-lor-daycare-centers-2024-01-district-regions.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-daycare-centers/main/data/berlin-lor-daycare-centers-2024-01/berlin-lor-daycare-centers-2024-01-district-regions.geojson)
* [berlin-lor-daycare-centers-2024-01/berlin-lor-daycare-centers-2024-01-districts.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-daycare-centers/main/data/berlin-lor-daycare-centers-2024-01/berlin-lor-daycare-centers-2024-01-districts.geojson)
* [berlin-lor-daycare-centers-2024-01/berlin-lor-daycare-centers-2024-01-forecast-areas.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-daycare-centers/main/data/berlin-lor-daycare-centers-2024-01/berlin-lor-daycare-centers-2024-01-forecast-areas.geojson)
* [berlin-lor-daycare-centers-2024-01/berlin-lor-daycare-centers-2024-01-planning-areas.geojson](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-daycare-centers/main/data/berlin-lor-daycare-centers-2024-01/berlin-lor-daycare-centers-2024-01-planning-areas.geojson)

Additionally, statistics are available under the following URLs

* [berlin-lor-daycare-centers-statistics/berlin-lor-daycare-centers-statistics.json](https://raw.githubusercontent.com/open-lifeworlds/open-lifeworlds-data-product-berlin-lor-daycare-centers/main/data/berlin-lor-daycare-centers-statistics/berlin-lor-daycare-centers-statistics.json)

## Metadata

### Ownership

**Domain, data product owner, organizational unit, license, version and expiration date**

* ownership: Open Lifeworlds
* domain: geodata
* license: CC-BY-4.0

### Schema

**Attributes, data types, constraints, and relationships to other elements**

* `daycare_centers`: number of daycare centers
* `places`: number of places in daycare centers

### Semantics

**Description, logical model**

### Security

**Security rules applied to the data product usage e.g. public org, internal, personally identifiable information (PII)
attributes**

## Observability

### Quality metrics

**Requirements and metrics such as accuracy, completeness, integrity, or compliance to Data Governance policies**

Completeness of this data product is verified via [data_metrics.py](../lib/metrics/data_completeness.py).

### Operational metrics

**Interval of change, freshness, usage statistics, availability, number of users, data versioning, etc.**

### SLOs

**Thresholds for service level objectives to up alerting**

## Consumer

**Who is the consumer of the Data Product?**

Consumers of this data product may include  projects that display statistical data based on LOR areas on maps or graphs.

## Use Case

**We believe that ...**
**We help achieving ...**
**We know, we are getting there based on ..., ..., ...**

We believe that this data product can be used to display statistical data related to LOR areas in Berlin on an interactive map.

## Classification

**The nature of the exposed data (source-aligned, aggregate, consumer-aligned)**

This data product is consumer-aligned since it is meant to be used for display on maps or graphs.

## Ubiquitous Language

**Context-specific domain terminology (relevant for Data Product), Data Product polysemes which are used to create the
current Data Product**

* **LOR**: (German: Lebensweltlich orientierte Räume) life-world oriented spaces
* **district**: (German: Bezirk)
* **forecast area**: (German: Prognoseraum)
* **district region**: (German: Bezirksregion)
* **planning area**: a spatial unit whose spatial development is planned by the public authorities

---
This data product canvas uses the template
of [datamesh-architecture.com](https://www.datamesh-architecture.com/data-product-canvas).
