# SML AI Router - Roadmap

## Overview

- Total phases: 1
- Total mapped requirements: 13
- Focus: End-to-end brownfield improvement to make deployment and operation simple, reliable, and safe across Local, Docker, and Coolify.

## Phase Plan

| Phase | Name | Goal | Requirements |
|------:|------|------|--------------|
| 1 | Architecture Reset and Deployment Simplification | Consolidate runtime architecture, standardize configuration/security, and deliver verified deployment flows and operator UX improvements for all target environments | ARCH-01, ARCH-02, CONF-01, CONF-02, SEC-01, DEP-01, DEP-02, DEP-03, OPS-01, DASH-01, DASH-02, API-01, QUAL-01 |

---

## Phase 1: Architecture Reset and Deployment Simplification

### Goal

Deliver a simplified, production-usable SML AI Router that can be deployed and operated consistently in Local, Docker, and Coolify modes, while preserving OpenClaw compatibility and Thai-first operator experience.

### Requirements Mapped

- ARCH-01, ARCH-02
- CONF-01, CONF-02, SEC-01
- DEP-01, DEP-02, DEP-03, OPS-01
- DASH-01, DASH-02
- API-01, QUAL-01

### Success Criteria

1. A new maintainer can follow one documented path per environment (Local, Docker, Coolify) and obtain a healthy system without undocumented steps.
2. Service boundaries, startup sequence, and configuration contracts are explicit and consistent across code and docs.
3. Dashboard exposes provider health and key operational signals for troubleshooting.
4. OpenAI-compatible endpoints required by OpenClaw function after refactor.
5. A repeatable verification checklist/test flow confirms deployment and routing readiness.
