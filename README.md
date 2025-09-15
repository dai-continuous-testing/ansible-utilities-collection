# DAI Continuous Testing Utilities Collection

This Ansible collection provides utility modules for DAI continuous testing projects.

## Modules

### application_properties

Manage Java application.properties files atomically, preventing race conditions.

#### Features
- Atomic file operations (no race conditions)
- Automatic backup creation
- Comment out existing properties
- Managed blocks for clear separation
- Cross-platform support

#### Usage

```yaml
- name: Update application properties
  dai_continuous_testing.utilities.application_properties:
    path: /opt/app/config/application.properties
    properties:
      server.port: "8080"
      database.url: "jdbc:mysql://localhost/mydb"
      app.name: "myapp"
    backup: true
    comment_existing: true
```

## Installation

### From Git Repository
```bash
ansible-galaxy collection install git+https://github.com/dai-continuous-testing/ansible-utilities-collection.git
```

### From Local Path (for development)
```bash
ansible-galaxy collection install /path/to/ansible_collections/dai_continuous_testing/utilities
```

### For Projects in this Repository
The collection is already available at `ansible_collections/dai_continuous_testing/utilities/` and can be used directly.

## Requirements

- Ansible >= 2.9
- Python >= 3.6

## License

GPL-3.0-or-later
