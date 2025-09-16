# DAI Continuous Testing Utilities Collection

This Ansible collection provides utility modules and filter plugins for DAI continuous testing projects.

## Modules

| Module | Platform | Description | Documentation |
|--------|----------|-------------|---------------|
| **application_properties** | Cross-platform | Manage Java application.properties files atomically | [📖 Docs](docs/application_properties.md) |
| **health_check** | Linux/Unix | HTTP health checks with retry logic | [📖 Docs](docs/health_check.md) |
| **win_health_check** | Windows | HTTP health checks for Windows systems | [📖 Docs](docs/win_health_check.md) |
| **win_drive_letter_to_disk_info** | Windows | Get disk space information by drive letter | [📖 Docs](docs/win_drive_letter_to_disk_info.md) |

## Filter Plugins

| Filter Plugin | Description | Example Usage |
|---------------|-------------|---------------|
| **os_utils** | OS family detection and normalization | `{{ ansible_os_family \| dai_continuous_testing.utilities.os_family_to_os_type }}` |
| **string_utils** | String manipulation and formatting | `{{ app_name \| dai_continuous_testing.utilities.safe_key }}` |
| **version_utils** | Version comparison and parsing | `{{ version \| dai_continuous_testing.utilities.version_compare('1.0.0', '>=') }}` |

## Quick Start

### Module Usage Examples

```yaml
# Update application properties
- name: Configure application
  dai_continuous_testing.utilities.application_properties:
    path: /opt/app/config/application.properties
    properties:
      server.port: "8080"
      database.url: "jdbc:mysql://localhost/mydb"

# Health check on Linux
- name: Check service health
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:8080/health"
    max_retries: 10

# Health check on Windows  
- name: Check Windows service
  dai_continuous_testing.utilities.win_health_check:
    url: "http://localhost:8080/health"
    max_retries: 10

# Check Windows disk space
- name: Verify disk space
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    drive_letter: "C:"
```

### Filter Plugin Usage Examples

```yaml
# OS utilities
- debug:
    msg: "This is a {{ ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type }} system"

# String utilities  
- set_fact:
    service_name: "{{ 'My Service Name!' | dai_continuous_testing.utilities.safe_key }}"
    config_file: "{{ app_name | dai_continuous_testing.utilities.safe_filename }}"

# Version utilities
- debug:
    msg: "Upgrade needed"
  when: current_version | dai_continuous_testing.utilities.version_compare(required_version, '<')
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

### 1. 📦 Installation Methods

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

### 2. 🛠️ Basic Usage in Playbooks

```yaml
---
- hosts: all
  tasks:
    - name: Configure application properties
      dai_continuous_testing.utilities.application_properties:
        path: "{{ app_config_path }}"
        properties: "{{ app_properties }}"
        backup: yes

    - name: Wait for service to be healthy  
      dai_continuous_testing.utilities.health_check:
        url: "http://{{ inventory_hostname }}:{{ service_port }}/health"
        max_retries: 20
        delay_between_tries: 5
      when: ansible_os_family != "Windows"

    - name: Wait for Windows service to be healthy
      dai_continuous_testing.utilities.win_health_check:
        url: "http://{{ inventory_hostname }}:{{ service_port }}/health"
        max_retries: 20
        delay_between_tries: 5
      when: ansible_os_family == "Windows"

    - name: Check disk space (Windows only)
      dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
        disks: "{{ ansible_facts.disks }}"
        drive_letter: "C"
      register: disk_info
      when: ansible_os_family == "Windows"
```

### 3. 📚 Detailed Documentation

Each module has comprehensive documentation with examples, parameters, and best practices:

- **[application_properties](docs/application_properties.md)** - Complete guide for properties file management
- **[health_check](docs/health_check.md)** - Linux/Unix health checking examples and use cases
- **[win_health_check](docs/win_health_check.md)** - Windows health checking guide
- **[win_drive_letter_to_disk_info](docs/win_drive_letter_to_disk_info.md)** - Windows disk space management
