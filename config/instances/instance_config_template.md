# Joget Instance Configuration: [INSTANCE_NAME]

## Instance Information

- **Instance Name**: [jdx1/jdx2/jdx3/jdx4/jdx5/jdx6]
- **Joget Version**: [8.1.6 / 9.0.0]
- **Installation Path**: `/Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-[version]`
- **Purpose**: [Brief description]
- **Status**: [Active / Staging / Test / Development]
- **Configured Date**: [YYYY-MM-DD]

## Network Configuration

### Ports
- **Web Interface**: [port]
  - URL: `http://localhost:[port]/jw`
  - Admin URL: `http://localhost:[port]/jw/web/console/home`
- **Database (MySQL)**: [port]

### Service Management
```bash
# Start instance
cd /Users/aarelaponin/joget-enterprise-linux-joget-enterprise-linux-[version]
./joget.sh start

# Stop instance
./joget.sh stop

# Check status
ps aux | grep [version]
lsof -i :[web-port]
```

## Database Configuration

### Connection Details
```properties
# Located in: wflow/app_datasource-default.properties
workflowDriver=com.mysql.cj.jdbc.Driver
workflowUrl=jdbc:mysql://localhost:[db-port]/jwdb?characterEncoding=UTF-8
workflowUser=root
workflowPassword=[password]
```

### Database Access
```bash
# Connect to database
mysql -P [db-port] -u root -p

# Common queries
USE jwdb;
SHOW TABLES;
SELECT * FROM app_app;  # List applications
SELECT * FROM app_form;  # List forms
```

### Backup Procedures
```bash
# Full database backup
mysqldump -P [db-port] -u root -p --all-databases > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
mysql -P [db-port] -u root -p < backup.sql

# Backup specific database
mysqldump -P [db-port] -u root -p jwdb > jwdb_backup.sql
```

## Applications

### Installed Applications

| App ID | App Name | Version | Purpose | Status |
|--------|----------|---------|---------|--------|
| [appId] | [appName] | [version] | [purpose] | [Active/Testing] |

### Application Details

#### [Application Name]
- **App ID**: [appId]
- **Description**: [Brief description]
- **Forms**: [Number of forms]
- **Processes**: [Number of processes]
- **Datalists**: [Number of datalists]
- **Userviews**: [Number of userviews]

**Key Forms**:
- `[formId]` - [Form name and purpose]
- `[formId]` - [Form name and purpose]

**Key Processes**:
- `[processId]` - [Process name and purpose]

**External Dependencies**:
- MDM Source: [jdx3 masterData / None]
- API Endpoints: [List of endpoints]
- Connected Instances: [List of instances]

## Plugins

### Installed Plugins

| Plugin Name | Version | Purpose | Configuration File |
|-------------|---------|---------|-------------------|
| [Plugin Name] | [version] | [purpose] | [path/to/config] |

### Plugin Details

#### [Plugin Name]
- **Plugin Class**: `[com.example.PluginClass]`
- **Purpose**: [Detailed description]
- **Configuration**:
  ```json
  {
    "property1": "value1",
    "property2": "value2"
  }
  ```
- **Dependencies**: [List dependencies]
- **API Endpoints**:
  - `POST /jw/web/json/plugin/[pluginName]/endpoint`
- **Notes**: [Any special notes]

## System Configuration

### Tomcat Settings
- **Tomcat Version**: [Version from installation]
- **Java Version**: [Output of `java -version`]
- **Memory Settings**:
  ```bash
  # Located in: apache-tomcat-*/bin/setenv.sh
  JAVA_OPTS="-Xmx2048M -Djava.awt.headless=true"
  ```

### Log Files
```bash
# Main Tomcat log
tail -f apache-tomcat-*/logs/catalina.out

# Joget application logs
tail -f wflow/*.log

# Common log locations
- apache-tomcat-*/logs/catalina.out  # Main Tomcat log
- apache-tomcat-*/logs/localhost.*.log  # Tomcat host logs
- wflow/app_formsvc.log  # Form service logs
```

### Environment Variables
```bash
# Set in: ~/.bashrc or instance-specific script
export JAVA_HOME=/path/to/java
export CATALINA_HOME=/path/to/tomcat
```

## Integration Configuration

### MDM Integration
- **MDM Instance**: [jdx3 / jdx4 / jdx5 / None]
- **MDM Endpoint**: `http://localhost:[port]/jw/web/json/plugin/formCreator/...`
- **Connection Type**: [JDBC / REST / Form Options]
- **Configuration**:
  ```json
  {
    "mdm_base_url": "http://localhost:[port]",
    "mdm_app_id": "masterData",
    "timeout": 30000
  }
  ```

### Inter-Instance Communication
- **Sends Data To**: [List of target instances]
  - Instance: [jdx5]
  - Endpoint: `http://localhost:[port]/jw/web/json/plugin/[pluginName]/receive`
  - Protocol: [HTTP/HTTPS]
  - Authentication: [Basic/OAuth/API Key]

- **Receives Data From**: [List of source instances]
  - Instance: [jdx4]
  - Plugin: [RegistrationServiceProvider]
  - Endpoint: `http://localhost:[port]/jw/web/json/plugin/[pluginName]/receive`

### API Endpoints

#### Exposed Endpoints
| Endpoint | Method | Purpose | Authentication |
|----------|--------|---------|----------------|
| `/jw/web/json/plugin/[name]/endpoint` | POST | [purpose] | [type] |

#### Consumed Endpoints
| Target | Endpoint | Purpose |
|--------|----------|---------|
| [jdx5] | `/jw/web/json/plugin/[name]/endpoint` | [purpose] |

## Monitoring

### Health Checks
```bash
# Check if Joget is responding
curl -I http://localhost:[web-port]/jw/

# Check database connectivity
mysql -P [db-port] -u root -p -e "SELECT 1"

# Check disk space
df -h

# Check memory usage
free -h
```

### Performance Metrics
- **Startup Time**: [~X seconds]
- **Average Response Time**: [X ms]
- **Memory Usage**: [X MB / Y MB]
- **Database Connections**: [X active]

### Alerts
- [ ] Web port not responding
- [ ] Database connection failed
- [ ] High memory usage (>80%)
- [ ] Disk space low (<10%)
- [ ] Application errors in logs

## Security

### User Accounts
- **Admin Username**: `admin`
- **Admin Password**: [Stored securely, not in this document]
- **Database User**: `root`
- **Database Password**: [Stored securely]

### Access Control
- Web console access: `http://localhost:[port]/jw/web/console/home`
- Required roles: [List of roles]
- IP restrictions: [None / List of allowed IPs]

### SSL/TLS
- [ ] SSL Enabled
- [ ] Certificate: [Path to certificate]
- [ ] HTTPS Port: [port]

## Maintenance

### Regular Tasks
- [ ] **Daily**: Check logs for errors
- [ ] **Weekly**: Review disk space and memory usage
- [ ] **Monthly**: Full database backup
- [ ] **Quarterly**: Review and update plugins

### Backup Schedule
- **Database Backups**: [Daily / Weekly / Before changes]
- **Application Exports**: [Weekly / Before changes]
- **Backup Location**: `/Users/aarelaponin/PycharmProjects/dev/frs-development-platform/backups/`
- **Retention Policy**: [X days/weeks]

### Update Procedures
1. Create full backup (database + applications)
2. Export all applications
3. Stop Joget instance
4. Perform update/changes
5. Start instance
6. Verify functionality
7. Document changes

## Troubleshooting

### Common Issues

#### Issue: Instance won't start
```bash
# Check if port is already in use
lsof -i :[web-port]

# Check if database is running
mysql -P [db-port] -u root -p -e "SELECT 1"

# Check logs
tail -100 apache-tomcat-*/logs/catalina.out
```

#### Issue: Database connection errors
```bash
# Verify database is running
ps aux | grep mysql

# Verify connection settings
cat wflow/app_datasource-default.properties

# Test connection
mysql -P [db-port] -u root -p
```

#### Issue: Out of memory
```bash
# Check current memory usage
ps aux | grep java

# Increase memory in setenv.sh
# Change: JAVA_OPTS="-Xmx2048M" to JAVA_OPTS="-Xmx4096M"
vim apache-tomcat-*/bin/setenv.sh

# Restart instance
./joget.sh stop
./joget.sh start
```

#### Issue: Slow performance
- Check database query performance
- Review log files for errors
- Check disk I/O
- Consider increasing memory allocation
- Review active database connections

### Debug Mode
```bash
# Enable debug logging
# Edit: apache-tomcat-*/conf/logging.properties
# Set: .level = FINE

# Restart instance
./joget.sh stop
./joget.sh start

# Monitor debug logs
tail -f apache-tomcat-*/logs/catalina.out
```

## Testing

### Test Credentials
- **Test User 1**: [username] / [password] - Role: [role]
- **Test User 2**: [username] / [password] - Role: [role]

### Test Data
- Location: [Path to test data scripts]
- Setup Script: `scripts/testing/setup_test_data.py --instance [name]`
- Cleanup Script: `scripts/testing/cleanup_test_data.py --instance [name]`

### Verification Checklist
- [ ] Instance starts successfully
- [ ] Web console accessible
- [ ] Database connection working
- [ ] All applications load
- [ ] Forms render correctly
- [ ] Workflows execute
- [ ] Plugins function correctly
- [ ] MDM integration working (if applicable)
- [ ] Inter-instance communication working (if applicable)

## Documentation

### Related Documents
- Main Plan: `../FRS_CONSOLIDATION_PLAN.md`
- Architecture: `../docs/architecture/system-overview.md`
- Deployment: `../docs/deployment/environment-setup.md`
- API Docs: `../docs/api/endpoints.md`

### Change Log

| Date | Change | Author | Notes |
|------|--------|--------|-------|
| [YYYY-MM-DD] | Initial configuration | [name] | Instance setup |
| [YYYY-MM-DD] | [Description] | [name] | [Notes] |

## Notes
[Any additional notes, quirks, or important information about this instance]

---

**Last Updated**: [YYYY-MM-DD]
**Maintained By**: [Name/Team]
**Review Frequency**: [Monthly/Quarterly]
