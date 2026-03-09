# Documentation

This folder contains all documentation for the affective_playlists project, organized around the spec-driven brownfield workflow.

## Folder Structure

```
docs/
├── README.md                          # This file
├── OVERVIEW.md                        # Project summary and quick-start guide
├── domain-guides/                     # DEPRECATED: Content migrated to openspec/specs/
│   ├── README.md                      # Domain guides index
│   ├── metadata/                      # Metadata enrichment domain (metad_enr)
│   ├── playlists/                     # Playlist organization domain (plsort)
│   └── temperament/                   # Temperament analysis domain (4tempers)
├── architecture/                      # System architecture and technical design
│   └── README.md                      # High-level system overview
├── project-management/                # Operational planning and prioritization
│   ├── README.md                      # Planning docs index
│   ├── fix_plan.md                    # Priority-based task list
│   ├── spec_debt.md                   # Specification coverage gaps
│   └── NEXT_STEPS.md                  # 30-90 day development directions
├── legacy-specs/                      # Brownfield migration reference
│   ├── README.md                      # Legacy specs index and traceability
│   ├── SPEC_METADATA_ENRICHMENT.md    # Original spec (reference only)
│   ├── SPEC_PLAYLIST_ORGANIZATION.md  # Original spec (reference only)
│   ├── SPEC_TEMPERAMENT_ANALYZER.md   # Original spec (reference only)
│   └── TECH_REQ_SYSTEM_ARCHITECTURE.md # Original architecture spec
├── archived-reports/                  # Historical project status reports
│   ├── README.md                      # Archive index and timeline
│   ├── WORK_SUMMARY_JAN4_2026.md      # January development summary
│   ├── DOCUMENTATION_REORGANIZATION_SUMMARY.md # Brownfield bootstrap summary
│   ├── FINAL_IMPLEMENTATION_SUMMARY.md # Complete implementation snapshot
│   └── GITHUB_CLONEABLE.md            # GitHub distribution readiness
├── reference-reports/                 # Implementation analysis and metrics
│   ├── README.md                      # Reports index
│   └── IMPLEMENTATION_REPORTS/        # Detailed feature analysis
│       ├── METADATA_ENRICHMENT_REPORT.md
│       └── ...
├── rules/                             # Coding and documentation standards
│   ├── CODE_QUALITY_STANDARDS.md      # Python code quality requirements
│   ├── DOCUMENTATION_STANDARDS.md     # Documentation authoring standards
│   ├── MARKDOWN_FILE_ORGANIZATION.md  # Markdown structure guidelines
│   ├── SETUP_RULE.md                  # Setup and installation rules
│   ├── TEST_ORGANIZATION_RULE.md      # Test file organization rules
│   └── README.md                      # Rules index
└── summary/                           # Quick references and project resources
    ├── README.md                      # Summary index
    ├── SRC_ARCHITECTURE_GUIDE.md      # Source code organization reference
    ├── PROJECT_SUMMARIES/             # Project status resources
    ├── QUICK_REFERENCE/               # Quick reference guides
    └── QUICK_REFERENCE/
        ├── CLI_UI_QUICK_REFERENCE.md
        ├── TESTING_QUICK_REFERENCE.md
        └── ...
```

## Navigation Guide

### For Feature Implementation

Start with **OpenSpec Specifications** — these contain authoritative requirements with implementation context:

- [Metadata Enrichment](../openspec/specs/metadata/spec.md) — `metad_enr` feature
- [Playlist Organization](../openspec/specs/playlists/spec.md) — `plsort` feature  
- [Temperament Analysis](../openspec/specs/temperament/spec.md) — `4tempers` feature

### For System Design
See [Architecture](architecture/) for high-level system design, component organization, and data flow.

### For Development Planning
Check [Project Management](project-management/) for operational priorities:
- [fix_plan.md](project-management/fix_plan.md) — Priority-based task list
- [spec_debt.md](project-management/spec_debt.md) — Specification gaps to address
- [NEXT_STEPS.md](project-management/NEXT_STEPS.md) — 30-90 day roadmap

### For Technical Analysis
Reference [Reports](reference-reports/) for implementation analysis with metrics:
- Feature implementation compliance reports
- Performance baselines and metrics
- Test coverage and passing rates

### For Historical Context
[Archived Reports](archived-reports/) contains project snapshots from January 2026 brownfield phase.

### For Coding & Documentation Standards
[Rules](rules/) defines project standards:
- [CODE_QUALITY_STANDARDS.md](rules/CODE_QUALITY_STANDARDS.md) — Python code requirements
- [DOCUMENTATION_STANDARDS.md](rules/DOCUMENTATION_STANDARDS.md) — How to write specs
- [TEST_ORGANIZATION_RULE.md](rules/TEST_ORGANIZATION_RULE.md) — Test file structure

### For Quick References
[Summary](summary/) contains quick-lookup guides and project resources:
- SRC_ARCHITECTURE_GUIDE.md — Source code organization
- QUICK_REFERENCE/ — CLI, testing, and troubleshooting guides
- PROJECT_SUMMARIES/ — Status and roadmap information

## Source of Truth Hierarchy

1. **OpenSpec Specs** (`openspec/specs/`) — Authoritative requirements with implementation context
2. **Architecture** (`architecture/`) — System-level design
3. **Code Quality Standards** (`rules/CODE_QUALITY_STANDARDS.md`) — Development standards
4. **Legacy Specs** (`legacy-specs/`) — Historical reference only

## Project Overview

For project introduction and setup, see:
- **[OVERVIEW.md](OVERVIEW.md)** — Project summary, features, and quick start
- **[INSTALLATION.md](INSTALLATION.md)** — Detailed installation instructions

