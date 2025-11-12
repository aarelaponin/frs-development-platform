# Farmer Registry System - Development Platform

## Overview

Central documentation and automation platform for the Farmer Registry System (FRS) development. This repository maintains complete documentation about the overall landscape of decentralized FRS development across multiple Joget DX instances, plugins, and utilities.

## Project Goals

The FRS aims to implement a comprehensive farmer registration and subsidy management system aligned with GovStack Building Block specifications, featuring:

1. **Farmer Registration**: Citizens can register as farmers through a web portal
2. **MOA Back Office**: Ministry of Agriculture approves applications and maintains farmer registry
3. **Subsidy Management**: Ministry of Finance creates programs, allocates budgets, generates vouchers
4. **GovStack Integration**: Utilizes Registration Building Block (RBB) APIs for interoperability

## Current Status

🚧 **Phase**: Consolidation and MDM Migration
📅 **Started**: 2025-11-12
🎯 **Target Completion**: Week of 2025-12-17

See `FRS_CONSOLIDATION_PLAN.md` for detailed project plan.

## Repository Structure

```
frs-development-platform/
├── README.md                          # This file
├── FRS_CONSOLIDATION_PLAN.md          # Detailed 5-week consolidation plan
├── FRS_QUICK_START.md                 # Quick start guide for developers
│
├── docs/
│   ├── architecture/                  # System architecture and design
│   │   ├── system-overview.md
│   │   ├── data-model.md
│   │   ├── mdm-structure.md
│   │   └── mdm-integration-guide.md
│   ├── components/                    # Component documentation
│   │   ├── plugins.md                 # Joget plugin inventory
│   │   ├── utilities.md               # Utility projects inventory
│   │   └── applications.md            # Joget application catalog
│   ├── deployment/                    # Deployment procedures
│   │   ├── complete-deployment-guide.md
│   │   ├── environment-setup.md
│   │   ├── mdm-deployment.md
│   │   ├── farmers-portal-deployment.md
│   │   ├── moa-bo-deployment.md
│   │   └── testing-guide.md
│   ├── api/                          # API documentation
│   │   ├── endpoints.md
│   │   ├── govstack-integration.md
│   │   └── govstack-compliance.md
│   ├── operations/                    # Operations and maintenance
│   │   ├── monitoring.md
│   │   ├── maintenance.md
│   │   └── troubleshooting.md
│   ├── runbooks/                      # Operational runbooks
│   │   ├── mdm-update.md
│   │   ├── application-deployment.md
│   │   ├── plugin-updates.md
│   │   └── disaster-recovery.md
│   └── onboarding/                    # Developer onboarding
│       ├── developer-guide.md
│       └── architecture-walkthrough.md
│
├── scripts/
│   ├── migration/                     # MDM migration automation
│   │   ├── analyze_mdm_usage.py       # Scan apps for MDM dependencies
│   │   ├── update_form_mdm.py         # Update forms with new MDM
│   │   ├── generate_mdm_config.py     # Generate MDM configurations
│   │   └── validate_mdm_migration.py  # Validate migration accuracy
│   ├── deployment/                    # Deployment automation
│   │   ├── deploy_mdm.sh              # Deploy MDM to instance
│   │   ├── deploy_farmers_portal.sh   # Deploy farmersPortal
│   │   ├── deploy_moa_bo.sh           # Deploy farmlandRegistry
│   │   └── health_check.py            # Instance health checks
│   └── testing/                       # Test automation
│       ├── test_e2e_integration.py    # End-to-end tests
│       ├── test_mdm_connectivity.py   # MDM connection tests
│       ├── test_plugin_functionality.py # Plugin tests
│       ├── setup_test_data.py         # Populate test data
│       ├── cleanup_test_data.py       # Clean test data
│       └── generate_test_report.py    # Generate test reports
│
├── config/
│   ├── instances/                     # Instance configurations
│   │   ├── jdx1.md                    # jdx1 configuration
│   │   ├── jdx2.md                    # jdx2 configuration
│   │   ├── jdx3.md                    # jdx3 configuration
│   │   ├── jdx4.md                    # jdx4 configuration
│   │   └── jdx5.md                    # jdx5 configuration
│   └── environments/                  # Environment configs
│       ├── jdx2-to-mdm.json          # farmersPortal MDM config
│       ├── jdx1-to-mdm.json          # farmlandRegistry MDM config
│       └── test-integration.json      # Integration test config
│
├── diagrams/                          # Architecture diagrams
│   ├── system-architecture.puml
│   ├── data-flow.puml
│   └── deployment.puml
│
├── backups/                           # Database and app backups
│   └── YYYYMMDD/                     # Date-stamped backups
│
└── requirements.txt                   # Python dependencies
```

## Quick Start

### Prerequisites
- Python 3.10+
- Joget DX Enterprise 8.1.6+ or 9.0.0+
- MySQL 5.7+
- Git

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd frs-development-platform

# Set up Python environment
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Review consolidation plan
cat FRS_CONSOLIDATION_PLAN.md

# Start with quick start guide
cat FRS_QUICK_START.md
```

### First Steps
1. Read `FRS_QUICK_START.md` for immediate actions
2. Review `FRS_CONSOLIDATION_PLAN.md` for complete project plan
3. Create initial backups (see Quick Start)
4. Begin component inventory (Week 1 tasks)

## System Landscape

### Joget Instances

| Instance | Version | Web Port | DB Port | Purpose | Status |
|----------|---------|----------|---------|---------|--------|
| jdx1 | 8.1.6 | 8080 | 3306 | farmlandRegistry (MOA-BO) | Active - needs MDM migration |
| jdx2 | 8.1.6 | 9999 | 3307 | farmersPortal | Active - needs MDM migration |
| jdx3 | 9.0.0 | 8888 | 3308 | masterData, subsidyApplication | Active - reference MDM |
| jdx4 | 9.0.0 | TBD | TBD | Test: farmersPortal + MDM | Ready for setup |
| jdx5 | 9.0.0 | TBD | TBD | Test: farmlandRegistry + MDM | Ready for setup |
| jdx6 | 9.0.0 | TBD | TBD | Reserved | Available |

### Applications

#### farmersPortal (jdx2)
- **Role**: Sender of farmer applications
- **User**: Farmers
- **Plugins**: DocSubmitter, Workflow Activator
- **Sends To**: farmlandRegistry (jdx1/jdx5)
- **API Format**: GovStack Registration Building Block (RBB)

#### farmlandRegistry (jdx1)
- **Role**: Receiver of farmer applications, MOA Back Office
- **User**: Ministry of Agriculture staff
- **Plugins**: RegistrationServiceProvider
- **Receives From**: farmersPortal (jdx2/jdx4)
- **API Format**: GovStack RBB generic format

#### masterData (jdx3)
- **Role**: Central Master Data Management
- **Provides**: Reference data for dropdowns, validations
- **Used By**: farmersPortal, farmlandRegistry
- **Endpoint**: formCreator plugin

### Plugins

| Plugin | Location | Used In | Purpose |
|--------|----------|---------|---------|
| DocSubmitter | /Users/aarelaponin/IdeaProjects | jdx2 | Send applications in GovStack RBB format |
| RegistrationServiceProvider | /Users/aarelaponin/IdeaProjects | jdx1 | Receive and dispatch generic applications |
| Workflow Activator | /Users/aarelaponin/IdeaProjects | jdx2 | Trigger workflows on submission |

### Utilities

| Utility | Location | Purpose |
|---------|----------|---------|
| joget-form-generator | /Users/aarelaponin/PycharmProjects/dev | Schema-driven form generation |
| [Other utilities] | /Users/aarelaponin/PycharmProjects/dev | TBD in Phase 1 |

## Development Workflow

### Working on Documentation
```bash
# Update documentation
vim docs/components/plugins.md

# Commit changes
git add docs/
git commit -m "Update plugin documentation"
git push
```

### Running Migration Scripts
```bash
# Activate Python environment
source venv/bin/activate

# Analyze MDM usage in an application
python scripts/migration/analyze_mdm_usage.py \
  --app-export backups/20251112/jdx2_farmersPortal_20251112.zip \
  --output analysis/farmersPortal_mdm_analysis.json

# Update forms with new MDM
python scripts/migration/update_form_mdm.py \
  --app-export backups/20251112/jdx2_farmersPortal_20251112.zip \
  --config config/environments/jdx2-to-mdm.json \
  --output updated/jdx2_farmersPortal_updated.zip

# Validate migration
python scripts/migration/validate_mdm_migration.py \
  --original backups/20251112/jdx2_farmersPortal_20251112.zip \
  --updated updated/jdx2_farmersPortal_updated.zip \
  --report validation/farmersPortal_validation.html
```

### Running Tests
```bash
# Run all tests
pytest scripts/testing/

# Run specific test suite
pytest scripts/testing/test_e2e_integration.py

# Run with detailed output
pytest scripts/testing/ -v --tb=short

# Generate HTML report
pytest scripts/testing/ --html=test_report.html
```

### Deployment
```bash
# Deploy MDM to instance
./scripts/deployment/deploy_mdm.sh \
  /Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-9.0.0-4 \
  8081 \
  3309

# Check instance health
python scripts/deployment/health_check.py --instance jdx4
```

## Key Documentation

### For Developers
- 📖 [Developer Guide](docs/onboarding/developer-guide.md)
- 🏗️ [Architecture Walkthrough](docs/onboarding/architecture-walkthrough.md)
- 🔧 [Component Inventory](docs/components/)

### For Operations
- 📋 [Deployment Guide](docs/deployment/complete-deployment-guide.md)
- 🚨 [Troubleshooting](docs/operations/troubleshooting.md)
- 📓 [Runbooks](docs/runbooks/)

### For Integration
- 🔌 [API Documentation](docs/api/endpoints.md)
- 🌐 [GovStack Integration](docs/api/govstack-integration.md)
- ✅ [GovStack Compliance](docs/api/govstack-compliance.md)

## Project Phases

### Phase 1: Discovery & Documentation Foundation (Week 1)
- [x] Create documentation repository
- [ ] Complete component inventory
- [ ] Document MDM structure

### Phase 2: Analysis & Migration Planning (Week 1-2)
- [ ] Analyze MDM dependencies
- [ ] Develop migration automation
- [ ] Create validation tests

### Phase 3: MDM Integration Development (Week 2-3)
- [ ] Backup current state
- [ ] Adjust farmersPortal for new MDM
- [ ] Adjust farmlandRegistry for new MDM

### Phase 4: Clean Environment Setup (Week 3)
- [ ] Install MDM to jdx4 and jdx5
- [ ] Configure inter-instance communication

### Phase 5: Application Deployment (Week 4)
- [ ] Deploy farmersPortal to jdx4
- [ ] Deploy farmlandRegistry to jdx5
- [ ] Verify individual functionality

### Phase 6: Integration Testing (Week 4-5)
- [ ] Create test automation suite
- [ ] Execute end-to-end testing
- [ ] Plugin integration testing
- [ ] GovStack compliance testing

### Phase 7: Documentation & Finalization (Week 5)
- [ ] Complete technical documentation
- [ ] Create runbooks
- [ ] Knowledge transfer materials
- [ ] Project handoff package

## Success Criteria

✅ **Must Have**:
- [ ] Farmer can submit application from jdx4
- [ ] Application successfully received in jdx5
- [ ] MDM data correctly referenced in both instances
- [ ] All data fields correctly mapped
- [ ] No data loss or corruption
- [ ] Complete documentation

## Contributing

### Documentation Updates
- Update relevant markdown files in `docs/`
- Follow existing structure and formatting
- Include examples where helpful
- Commit with descriptive messages

### Script Development
- Add new scripts to appropriate `scripts/` subdirectory
- Include docstrings and type hints
- Add tests in `scripts/testing/`
- Update this README with usage examples

### Testing
- Write tests for all automation scripts
- Run full test suite before committing
- Document test procedures in `docs/deployment/testing-guide.md`

## Resources

### External References
- [GovStack Specifications](https://specs.govstack.global/)
- [Joget DX Documentation](https://dev.joget.org/community/)
- [Registration Building Block API](https://specs.govstack.global/)

### Internal Projects
- [joget-form-generator](../joget-form-generator/) - Form generation utility
- Plugins: `/Users/aarelaponin/IdeaProjects/`
- Utilities: `/Users/aarelaponin/PycharmProjects/dev/`

## Troubleshooting

### Can't Access Instance
```bash
# Check if Joget is running
ps aux | grep joget

# Check port availability
lsof -i :8080
lsof -i :3306

# Check logs
tail -f <joget-dir>/apache-tomcat-*/logs/catalina.out
```

### Database Connection Issues
```bash
# Test MySQL connection
mysql -P 3306 -u root -p -e "SELECT 1"

# Check MySQL service
ps aux | grep mysql
```

### Script Failures
```bash
# Check Python environment
which python
python --version

# Check dependencies
pip list

# Run with debug output
python -v script.py
```

For detailed troubleshooting, see [docs/operations/troubleshooting.md](docs/operations/troubleshooting.md).

## Contact & Support

- **Project Owner**: [Your contact]
- **Technical Lead**: [Technical contact]
- **Repository Issues**: [Link to issues]

## License

[Your license choice]

---

**Last Updated**: 2025-11-12
**Project Status**: Active Development - Consolidation Phase
**Next Milestone**: Complete Phase 1 by 2025-11-19
