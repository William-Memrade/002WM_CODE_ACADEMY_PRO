---
source_file: "BA/DevOps/NU1098018_ReposUtils_DevOps/pipelines/BuildValidationPipeline.yml"
type: "code"
community: "Community 237"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Community_237
---

# Build Validation Pipeline

## Connections
- [[Code Scan IaC Stage]] - `calls` [EXTRACTED]
- [[Compilacion Sonar Stage]] - `calls` [EXTRACTED]
- [[Escaneos Seguridad Stage]] - `calls` [EXTRACTED]
- [[Freeze Date Validation Policy]] - `references` [EXTRACTED]
- [[Freeze Validation Exception Flow]] - `references` [EXTRACTED]
- [[Recoleccion Datos Stage]] - `calls` [EXTRACTED]
- [[Select Pool Stage]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Community_237