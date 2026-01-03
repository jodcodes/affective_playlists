# Documentation

This folder contains all documentation for the affective_playlists project.

## Folder Structure

```
docs/
├── README.md                         # This file
├── OVERVIEW.md                       # Project summary and architecture
├── requirements/                     # Specifications and technical requirements
│   ├── README.md                     # Requirements index
│   ├── SPEC_TEMPERAMENT_ANALYZER.md  # Functional spec for 4tempers
│   ├── SPEC_METADATA_ENRICHMENT.md   # Functional spec for metadata enrichment
│   ├── SPEC_PLAYLIST_ORGANIZATION.md # Functional spec for playlist organization
│   └── TECH_REQ_SYSTEM_ARCHITECTURE.md # Technical system architecture
├── rules/                            # Documentation rules and standards
│   ├── DOCUMENTATION_STANDARDS.md    # Standards for writing specifications
│   └── TEST_ORGANIZATION_RULE.md     # Test file organization rules
└── summary/                          # Reports, summaries, and quick references
    ├── README.md                     # Summary index
    ├── IMPLEMENTATION_REPORTS/       # Implementation reports
    │   └── METADATA_ENRICHMENT_REPORT.md
    ├── PROJECT_SUMMARIES/            # Project status and roadmaps
    │   ├── UPDATE_SUMMARY.md         # Documentation updates summary
    │   └── ROADMAP_SUMMARY.md        # Development roadmap
    └── QUICK_REFERENCE/              # Quick reference guides
        └── TESTING_QUICK_REFERENCE.md
```

## Key Documents

### Overview
- **OVERVIEW.md** - Project summary, architecture overview, and features

### Requirements (docs/requirements/)
Detailed functional and technical specifications for each component.

**Functional Specifications:**
- **SPEC_TEMPERAMENT_ANALYZER.md** - 4tempers AI emotion classification
- **SPEC_METADATA_ENRICHMENT.md** - Metadata enrichment functionality
- **SPEC_PLAYLIST_ORGANIZATION.md** - Playlist organization by genre

**Technical Requirements:**
- **TECH_REQ_SYSTEM_ARCHITECTURE.md** - System design, APIs, and integration

### Rules (docs/rules/)
Guidelines and standards for the project.

- **README.md** - Overview of all rules
- **SETUP_RULE.md** - Virtual environment setup and activation (⚠️ Start here)
- **DOCUMENTATION_STANDARDS.md** - How to create and maintain specifications
- **TEST_ORGANIZATION_RULE.md** - Test file organization requirements

### Summary (docs/summary/)
Reports, implementation guides, quick references, and architecture guides.

- **SRC_ARCHITECTURE_GUIDE.md** - Source code organization and architecture overview
- **PROJECT_SUMMARIES/** - Status summaries and roadmaps
  - **SETUP_STATUS_SUMMARY.md** - Current setup and configuration status
  - **UPDATE_SUMMARY.md** - Recent documentation updates
  - **ROADMAP_SUMMARY.md** - Development roadmap and next steps
- **IMPLEMENTATION_REPORTS/** - Feature implementation analysis
  - **METADATA_ENRICHMENT_REPORT.md** - Detailed implementation report
- **QUICK_REFERENCE/** - Quick lookup guides
  - **SSL_CERTIFICATE_FIX_QUICK_REFERENCE.md** - SSL troubleshooting
  - **TESTING_QUICK_REFERENCE.md** - Quick testing guide

## Quick Links

- **Main README**: See `../README.md`
- **Quick Start**: See `../QUICKSTART.md`
- **Main Entry Point**: See `../main.py`
- **Source Code**: See `../src/`

## Creating New Documentation

Follow the standards in `rules/DOCUMENTATION_STANDARDS.md`:

1. Create functional specs and technical requirements as separate `.md` files
2. Store specs in `requirements/` folder with naming convention:
   - Functional specs: `SPEC_*.md`
   - Technical requirements: `TECH_REQ_*.md`
3. Store reports in `summary/IMPLEMENTATION_REPORTS/*.md`
4. Store summaries in `summary/PROJECT_SUMMARIES/*.md`
5. Store quick references in `summary/QUICK_REFERENCE/*_QUICK_REFERENCE.md`
6. Include references to related source files from `src/` and `main.py`

See `rules/DOCUMENTATION_STANDARDS.md` for complete guidelines.
