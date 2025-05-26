# LiteLLM Engine Synchronization

BudConnect serves as the centralized registry for engines, models and their versions across deployments. Each BudServe instance communicates with BudConnect to discover compatible providers and models based on a chosen engine version. This document explains how the LiteLLM engine is maintained and how deployments retrieve the latest model details.

## Overview

BudServe supports multiple proprietary engines. For inference with certain provider offerings, the **LiteLLM** engine is used. The LiteLLM engine packages model and provider details in JSON files. BudConnect ingests these files through a seeder and exposes an API so that deployments can stay synchronized.

At a high level the workflow is:

1. LiteLLM publishes provider and model details in a versioned JSON file.
2. A seeder reads the file and upserts records into BudConnect's database.
3. Each record is tagged with the engine version that produced it.
4. Deployments query the API to receive all providers and models matching the engine version they run.

The following sections expand on each step, accompanied by diagrams and usage examples.

## Seeder Design

The seeder is responsible for ingesting provider and model data. It runs whenever a new engine version is released or when additional providers and models are added. The seeder operates idempotently; running it multiple times with the same data does not create duplicates.

```
flowchart TD
    A[LiteLLM JSON files] --> B[Seeder process]
    B --> C{Parse providers and models}
    C --> D[Provider DB table]
    C --> E[Model DB table]
    D --> F[Engine version association]
    E --> F
```

The data files are located under `budconnect/seeders/data/litellm/` and are named according to the engine version (for example `0.2.0.json`). When executed, the seeder opens the matching file and processes it entry by entry. Existing rows are updated and new rows are inserted.

## Data Model

BudConnect maintains two main tables for this feature:

- `engine_version` – stores all available engine versions.
- `provider` – references the `engine_version` table and contains each provider's metadata.
- `model_info` – models offered by a provider under a specific engine version.

```
classDiagram
    class EngineVersion {
        string name
        string version
        datetime created
    }
    class Provider {
        string name
        string icon
        EngineVersion version
    }
    class ModelInfo {
        string name
        Provider provider
        EngineVersion version
    }
    Provider --> EngineVersion : many-to-one
    ModelInfo --> Provider : many-to-one
    ModelInfo --> EngineVersion : many-to-one
```

## API Endpoints

BudConnect exposes endpoints to retrieve the seeded data. The main endpoint for synchronization is:

```
GET /model/get-compatible-models
```

Query parameters:

- `engine` – the engine key, e.g., `litellm`.
- `engine_version` – the version string, e.g., `0.2.0`.

## Typical Synchronization Flow

The following sequence diagram illustrates how BudServe syncs with BudConnect:

```
sequenceDiagram
    participant BudServe
    participant BudConnect
    BudServe->>BudConnect: Request provider + model info
    BudConnect-->>BudServe: Return JSON payload
    BudServe->>BudServe: Update local configuration
```

BudServe periodically polls this endpoint. This enables BudServe deployments to stay current with the latest provider and model definitions. By associating each provider and model with a specific engine version, BudConnect ensures compatibility across multiple deployments running different versions. The approach allows the ecosystem to grow over time while giving operators confidence that they are using the correct models.