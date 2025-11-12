# FRS Consolidation - Quick Start Guide

## Overview
This quick start guide helps you begin the Farmer Registry System (FRS) consolidation project. For complete details, see `FRS_CONSOLIDATION_PLAN.md`.

## Immediate Next Steps (Day 1)

### 1. Create Central Documentation Repository
```bash
# Create new repository
cd /Users/aarelaponin/PycharmProjects/dev
mkdir frs-development-platform
cd frs-development-platform
git init

# Create directory structure
mkdir -p docs/{architecture,components,deployment,api,operations,runbooks,onboarding}
mkdir -p scripts/{migration,deployment,testing}
mkdir -p config/{instances,environments}
mkdir -p diagrams
mkdir -p backups

# Copy the plan
cp ../joget-form-generator/FRS_CONSOLIDATION_PLAN.md .

# Create initial README (see template below)
touch README.md

# First commit
git add .
git commit -m "Initial FRS development platform structure"

# Optional: Create GitHub repository and push
# gh repo create frs-development-platform --private
# git remote add origin <repo-url>
# git push -u origin main
```

### 2. Create Backups Immediately
```bash
# Backup databases
cd /Users/aarelaponin/PycharmProjects/dev/frs-development-platform/backups
mkdir -p $(date +%Y%m%d)
cd $(date +%Y%m%d)

# jdx1 backup (port 3306)
mysqldump -P 3306 -u root -p --all-databases > jdx1_backup.sql

# jdx2 backup (port 3307)
mysqldump -P 3307 -u root -p --all-databases > jdx2_backup.sql

# jdx3 backup (port 3308)
mysqldump -P 3308 -u root -p --all-databases > jdx3_backup.sql

# Create backup log
echo "Backup Date: $(date)" > backup_log.txt
echo "jdx1 size: $(du -h jdx1_backup.sql | cut -f1)" >> backup_log.txt
echo "jdx2 size: $(du -h jdx2_backup.sql | cut -f1)" >> backup_log.txt
echo "jdx3 size: $(du -h jdx3_backup.sql | cut -f1)" >> backup_log.txt

cd ../../
git add backups/
git commit -m "Initial database backups"
```

### 3. Export Current Applications
```bash
cd /Users/aarelaponin/PycharmProjects/dev/frs-development-platform/backups/$(date +%Y%m%d)

# Export via Joget UI:
# jdx1: http://localhost:8080 → App Center → farmlandRegistry → Export
# jdx2: http://localhost:9999 → App Center → farmersPortal → Export
# jdx3: http://localhost:8888 → App Center → masterData, subsidyApplication → Export

# Save to this directory with naming convention:
# jdx1_farmlandRegistry_$(date +%Y%m%d).zip
# jdx2_farmersPortal_$(date +%Y%m%d).zip
# jdx3_masterData_$(date +%Y%m%d).zip
# jdx3_subsidyApplication_$(date +%Y%m%d).zip

# Commit exports
cd ../../
git add backups/
git commit -m "Application exports - baseline"
```

### 4. Start Component Inventory

Create initial component documentation:

```bash
cd /Users/aarelaponin/PycharmProjects/dev/frs-development-platform/docs/components

# Create initial component files
cat > plugins.md << 'EOF'
# FRS Plugin Inventory

## Overview
This document catalogs all Joget plugins used in the FRS.

## Plugins

### DocSubmitter
- **Location**: /Users/aarelaponin/IdeaProjects/[plugin-folder]
- **Version**: TBD
- **Used In**: jdx2 (farmersPortal)
- **Purpose**: Send farmer applications via GovStack RBB API format
- **Dependencies**: TBD
- **Configuration**:
  - Target endpoint: jdx5 RegistrationServiceProvider
  - API format: GovStack Registration Building Block
- **Status**: Needs documentation update

### RegistrationServiceProvider
- **Location**: /Users/aarelaponin/IdeaProjects/[plugin-folder]
- **Version**: TBD
- **Used In**: jdx1 (farmlandRegistry)
- **Purpose**: Receive generic applications and dispatch to specific forms
- **Dependencies**: TBD
- **Configuration**: TBD
- **Status**: Needs documentation update

### Workflow Activator
- **Location**: /Users/aarelaponin/IdeaProjects/[plugin-folder]
- **Version**: TBD
- **Used In**: jdx2 (farmersPortal)
- **Purpose**: Trigger workflows on form submission
- **Dependencies**: TBD
- **Configuration**: TBD
- **Status**: Needs documentation update

## Action Items
- [ ] Document plugin versions
- [ ] Document configuration parameters
- [ ] Document API endpoints
- [ ] Document build procedures
- [ ] Document dependencies
EOF

cat > utilities.md << 'EOF'
# FRS Utility Projects Inventory

## Overview
This document catalogs all utility projects in the FRS development ecosystem.

## Utilities

### joget-form-generator
- **Location**: /Users/aarelaponin/PycharmProjects/dev/joget-form-generator
- **Purpose**: Schema-driven Joget form generation from YAML
- **Status**: Active development
- **Documentation**: See CLAUDE.md, README.md
- **Related Components**: Form definitions for all FRS applications

### [Other Utilities - TBD]
- [ ] Inventory all projects in /Users/aarelaponin/PycharmProjects/dev
- [ ] Document each utility
- [ ] Map relationships to FRS

## Action Items
- [ ] Complete inventory of all utilities
- [ ] Document usage examples
- [ ] Document dependencies
EOF

cat > applications.md << 'EOF'
# FRS Joget Applications Inventory

## Overview
This document catalogs all Joget applications in the FRS.

## Applications

### farmersPortal (jdx2)
- **Instance**: jdx2 (:9999, DB :3307)
- **App ID**: farmersPortal
- **Version**: TBD
- **Purpose**: Farmer-facing application for registration
- **Forms**: TBD
- **Processes**: TBD
- **Plugins**: DocSubmitter, Workflow Activator
- **Database Tables**: TBD
- **MDM Dependencies**: TBD (Phase 2 analysis)
- **Status**: Active, needs MDM migration

### farmlandRegistry (jdx1)
- **Instance**: jdx1 (:8080, DB :3306)
- **App ID**: farmlandRegistry
- **Version**: TBD
- **Purpose**: MOA Back Office for application approval
- **Forms**: TBD
- **Processes**: TBD
- **Plugins**: RegistrationServiceProvider
- **Database Tables**: TBD
- **MDM Dependencies**: TBD (Phase 2 analysis)
- **Status**: Active, needs MDM migration

### masterData (jdx3)
- **Instance**: jdx3 (:8888, DB :3308)
- **App ID**: masterData
- **Version**: TBD
- **Purpose**: Central Master Data Management
- **Forms**: TBD (needs detailed documentation)
- **MDM Lists**: TBD (Phase 1.3 analysis)
- **Status**: Reference MDM for migration

### subsidyApplication (jdx3)
- **Instance**: jdx3 (:8888, DB :3308)
- **App ID**: subsidyApplication
- **Version**: TBD
- **Purpose**: Subsidy program management
- **Forms**: TBD
- **Status**: Future integration

## Action Items
- [ ] Document all forms for each application
- [ ] Document all processes and workflows
- [ ] Map data flows between applications
- [ ] Create entity-relationship diagrams
- [ ] Document database schemas
EOF

git add docs/
git commit -m "Initial component inventory templates"
```

## Week 1 Focus Areas

### Days 1-2: Documentation Foundation
- ✅ Create repository structure (completed above)
- ✅ Create backups (completed above)
- ✅ Export applications (completed above)
- 📝 Complete plugin inventory
- 📝 Complete utilities inventory
- 📝 Document current MDM structure from jdx3

### Days 3-5: Analysis & Tool Development
- 📝 Analyze MDM usage in farmersPortal (jdx2)
- 📝 Analyze MDM usage in farmlandRegistry (jdx1)
- 📝 Start building migration analysis tool
- 📝 Document MDM migration mapping

## Key Commands Reference

### Start/Stop Joget Instances
```bash
# jdx1
cd /Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-8.1.6
./joget.sh start
./joget.sh stop

# jdx2
cd /Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-8.1.6-2
./joget.sh start
./joget.sh stop

# jdx3
cd /Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-9.0.0
./joget.sh start
./joget.sh stop
```

### Access URLs
- jdx1: http://localhost:8080/jw
- jdx2: http://localhost:9999/jw
- jdx3: http://localhost:8888/jw
- jdx4: TBD (after configuration)
- jdx5: TBD (after configuration)
- jdx6: TBD (reserved)

### Database Connections
```bash
# jdx1 database
mysql -P 3306 -u root -p

# jdx2 database
mysql -P 3307 -u root -p

# jdx3 database
mysql -P 3308 -u root -p
```

### Check Joget Logs
```bash
# jdx1
tail -f /Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-8.1.6/apache-tomcat-9.0.80/logs/catalina.out

# jdx2
tail -f /Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-8.1.6-2/apache-tomcat-9.0.80/logs/catalina.out

# jdx3
tail -f /Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-9.0.0/apache-tomcat-9.0.80/logs/catalina.out
```

## Development Environment Setup

### Python Environment for Automation Tools
```bash
cd /Users/aarelaponin/PycharmProjects/dev/frs-development-platform

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install \
  pytest \
  pytest-cov \
  requests \
  pyyaml \
  jsonschema \
  rich \
  typer

# Create requirements.txt
pip freeze > requirements.txt

git add requirements.txt
git commit -m "Python environment dependencies"
```

### joget-form-generator Integration
```bash
# Link to existing form generator project
cd /Users/aarelaponin/PycharmProjects/dev/frs-development-platform
ln -s ../joget-form-generator/src/joget_form_generator ./scripts/lib/joget_form_generator

# Or install as development dependency
pip install -e ../joget-form-generator[dev]
```

## Critical Success Factors

### Must Complete in Week 1
1. ✅ Backups of all instances
2. ✅ Repository structure created
3. 📝 Complete component inventory
4. 📝 Document MDM structure from jdx3
5. 📝 Create MDM analysis tool (basic version)

### Red Flags to Watch For
- ⚠️ Can't connect to any instance → Check if services running
- ⚠️ Export fails → Check disk space, permissions
- ⚠️ Database backup fails → Check MySQL service, credentials
- ⚠️ MDM structure unclear → Schedule time to explore jdx3 thoroughly

## Getting Help

### Documentation References
- **Main Plan**: `FRS_CONSOLIDATION_PLAN.md`
- **Joget Docs**: https://dev.joget.org/community/
- **GovStack Specs**: https://specs.govstack.global/

### Internal Documentation
As you complete each phase, update documentation in:
- `docs/components/` - Component details
- `docs/architecture/` - Architecture decisions
- `docs/deployment/` - Deployment procedures

## Daily Checklist Template

```markdown
## Day [N] - [Date]

### Planned
- [ ] Task 1
- [ ] Task 2

### Completed
- [x] Completed task

### Blockers
- Issue description and resolution needed

### Notes
- Important observations
- Decisions made
- Questions for next day
```

## Contact Points

- **Project Owner**: [Your contact info]
- **Technical Questions**: [Team contact]
- **Documentation**: frs-development-platform repository

---

Last Updated: 2025-11-12
