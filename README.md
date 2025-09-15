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

## How to Use in Other Projects

### 1. Install the Collection

#### Option A: Direct Installation
```bash
ansible-galaxy collection install git+https://github.com/dai-continuous-testing/ansible-utilities-collection.git
```

#### Option B: Requirements File
Create a `requirements.yml` file in your project:
```yaml
---
collections:
  - name: git+https://github.com/dai-continuous-testing/ansible-utilities-collection.git
    type: git
    version: main
```

Then install with:
```bash
ansible-galaxy collection install -r requirements.yml
```

### 2. Use in Playbooks

#### Basic Usage
```yaml
---
- hosts: all
  tasks:
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

#### Advanced Usage with Variables
```yaml
---
- hosts: all
  vars:
    app_properties:
      server.port: "{{ server_port | default('8080') }}"
      database.url: "{{ db_url }}"
      app.name: "{{ application_name }}"
      logging.level.root: "INFO"
      
  tasks:
    - name: Update application properties
      dai_continuous_testing.utilities.application_properties:
        path: "{{ installation_folder }}/config/application.properties"
        properties: "{{ app_properties }}"
        backup: yes
        comment_existing: yes
        marker: "ANSIBLE MANAGED BLOCK - {{ application_name }} Properties"
```

#### Multiple Properties Files
```yaml
---
- hosts: all
  tasks:
    - name: Update application properties
      dai_continuous_testing.utilities.application_properties:
        path: "{{ installation_folder }}/config/application.properties"
        properties: "{{ application_properties }}"
        backup: yes
        comment_existing: yes
        marker: "ANSIBLE MANAGED BLOCK - Application Properties"

    - name: Update logback properties
      dai_continuous_testing.utilities.application_properties:
        path: "{{ installation_folder }}/config/logback.properties"
        properties: "{{ logback_properties }}"
        backup: yes
        comment_existing: yes
        marker: "ANSIBLE MANAGED BLOCK - Logback Properties"
```

### 3. Use in Roles

Add to your role's `tasks/main.yml`:
```yaml
- name: Configure application properties
  dai_continuous_testing.utilities.application_properties:
    path: "{{ config_file_path }}"
    properties: "{{ role_properties }}"
    backup: "{{ create_backup | default(true) }}"
    comment_existing: "{{ comment_existing_props | default(true) }}"
```

### 4. Module Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | yes | - | Path to the properties file |
| `properties` | dict | yes | - | Dictionary of key-value pairs to set |
| `backup` | boolean | no | `true` | Create backup before changes |
| `comment_existing` | boolean | no | `true` | Comment out existing properties |
| `marker` | string | no | "ANSIBLE MANAGED BLOCK - Application Properties" | Block marker text |

### 5. Return Values

The module returns:
- `changed`: Whether the file was modified
- `properties_added`: Number of properties added/updated
- `properties_commented`: Number of existing properties commented out
- `backup_file`: Path to backup file (if created)

## Requirements

- Ansible >= 2.9
- Python >= 3.6

## License

GPL-3.0-or-later
