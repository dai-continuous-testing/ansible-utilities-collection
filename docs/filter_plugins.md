# Filter Plugins Documentation

The DAI Continuous Testing Utilities collection includes three comprehensive filter plugin modules that enhance Ansible's string manipulation, OS detection, and version management capabilities.

## Table of Contents

- [OS Utilities Filter Plugin](#os-utilities-filter-plugin)
- [String Utilities Filter Plugin](#string-utilities-filter-plugin)  
- [Version Utilities Filter Plugin](#version-utilities-filter-plugin)
- [Integration Examples](#integration-examples)
- [Best Practices](#best-practices)

## OS Utilities Filter Plugin

### Available Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `os_family_to_os_type` | Convert OS family to standardized type | `{{ ansible_os_family \| dai_continuous_testing.utilities.os_family_to_os_type }}` |
| `normalize_os_family` | Normalize OS family names | `{{ 'centos' \| dai_continuous_testing.utilities.normalize_os_family }}` |
| `is_linux_family` | Check if OS is Linux-based | `{{ ansible_os_family \| dai_continuous_testing.utilities.is_linux_family }}` |
| `is_windows_family` | Check if OS is Windows-based | `{{ ansible_os_family \| dai_continuous_testing.utilities.is_windows_family }}` |
| `is_darwin_family` | Check if OS is Darwin/macOS-based | `{{ ansible_os_family \| dai_continuous_testing.utilities.is_darwin_family }}` |

### Usage Examples

```yaml
# Basic OS type detection
- debug:
    msg: "Running on {{ ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type }}"

# Conditional task execution
- name: Install Linux packages
  package:
    name: "{{ linux_packages }}"
  when: ansible_os_family | dai_continuous_testing.utilities.is_linux_family

- name: Configure Windows settings
  win_regedit:
    path: "{{ registry_path }}"
    name: "{{ setting_name }}"
    data: "{{ setting_value }}"
  when: ansible_os_family | dai_continuous_testing.utilities.is_windows_family

# OS-specific variable selection
- set_fact:
    package_manager: "{{ os_package_managers[ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type] }}"
  vars:
    os_package_managers:
      linux: "yum"
      darwin: "brew"
      windows: "chocolatey"
```

## String Utilities Filter Plugin

### Available Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `safe_key` | Create safe variable/key names | `{{ 'My App Name!' \| dai_continuous_testing.utilities.safe_key }}` |
| `safe_filename` | Create safe filenames | `{{ 'config<file>.txt' \| dai_continuous_testing.utilities.safe_filename }}` |
| `slugify` | Create URL-friendly slugs | `{{ 'My Title!' \| dai_continuous_testing.utilities.slugify }}` |
| `parse_url` | Parse URL into components | `{{ url \| dai_continuous_testing.utilities.parse_url }}` |
| `template_string` | Simple template interpolation | `{{ 'Hello {name}' \| dai_continuous_testing.utilities.template_string(vars) }}` |
| `join_path` | Intelligent path joining | `{{ ['/opt', 'app'] \| dai_continuous_testing.utilities.join_path }}` |
| `ensure_prefix` | Add prefix if missing | `{{ 'file.txt' \| dai_continuous_testing.utilities.ensure_prefix('app-') }}` |
| `ensure_suffix` | Add suffix if missing | `{{ 'config' \| dai_continuous_testing.utilities.ensure_suffix('.yml') }}` |
| `remove_prefix` | Remove prefix if present | `{{ 'app-file.txt' \| dai_continuous_testing.utilities.remove_prefix('app-') }}` |
| `remove_suffix` | Remove suffix if present | `{{ 'config.yml' \| dai_continuous_testing.utilities.remove_suffix('.yml') }}` |
| `camel_to_snake` | Convert camelCase to snake_case | `{{ 'myVariable' \| dai_continuous_testing.utilities.camel_to_snake }}` |
| `snake_to_camel` | Convert snake_case to camelCase | `{{ 'my_variable' \| dai_continuous_testing.utilities.snake_to_camel }}` |
| `truncate_smart` | Smart text truncation | `{{ long_text \| dai_continuous_testing.utilities.truncate_smart(50) }}` |
| `normalize_whitespace` | Normalize whitespace | `{{ '  spaced   text  ' \| dai_continuous_testing.utilities.normalize_whitespace }}` |
| `mask_sensitive` | Mask sensitive data | `{{ 'password123' \| dai_continuous_testing.utilities.mask_sensitive }}` |

### Usage Examples

```yaml
# Configuration file management
- set_fact:
    config_files:
      app_config: "{{ (app_name + '.properties') | dai_continuous_testing.utilities.safe_filename }}"
      log_config: "{{ (app_name + '-log.xml') | dai_continuous_testing.utilities.safe_filename }}"
      backup_name: "{{ (app_name + '_backup_' + ansible_date_time.epoch) | dai_continuous_testing.utilities.safe_filename }}"

# Service name generation
- set_fact:
    service_name: "{{ ('experitest-' + app_name + '-' + environment) | dai_continuous_testing.utilities.safe_key }}"

# Path construction
- set_fact:
    installation_path: "{{ [installation_root, app_name, app_version] | dai_continuous_testing.utilities.join_path }}"
    log_path: "{{ [installation_path, 'logs'] | dai_continuous_testing.utilities.join_path }}"

# URL parsing for health checks
- set_fact:
    health_url_parts: "{{ health_check_url | dai_continuous_testing.utilities.parse_url }}"

- debug:
    msg: "Health check will use port {{ health_url_parts.port }}"

# Template string interpolation
- set_fact:
    service_description: "{{ 'Service {name} v{version} on {host}' | dai_continuous_testing.utilities.template_string({'name': app_name, 'version': app_version, 'host': ansible_hostname}) }}"

# Sensitive data masking in logs
- debug:
    msg: "Database password: {{ db_password | dai_continuous_testing.utilities.mask_sensitive('*', 4) }}"
  when: debug_mode | default(false)
```

## Version Utilities Filter Plugin

### Available Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `version_compare` | Compare two versions | `{{ version1 \| dai_continuous_testing.utilities.version_compare(version2, '>=') }}` |
| `parse_version` | Parse version into components | `{{ '1.2.3-beta' \| dai_continuous_testing.utilities.parse_version }}` |
| `normalize_version` | Normalize version format | `{{ 'v1.2.3' \| dai_continuous_testing.utilities.normalize_version }}` |
| `is_stable_version` | Check if version is stable | `{{ version \| dai_continuous_testing.utilities.is_stable_version }}` |
| `bump_version` | Increment version part | `{{ '1.2.3' \| dai_continuous_testing.utilities.bump_version('minor') }}` |
| `version_in_range` | Check version range | `{{ version \| dai_continuous_testing.utilities.version_in_range('>=1.0.0,<2.0.0') }}` |
| `extract_version` | Extract version from text | `{{ 'App v1.2.3 build' \| dai_continuous_testing.utilities.extract_version }}` |
| `sort_versions` | Sort version list | `{{ versions \| dai_continuous_testing.utilities.sort_versions }}` |
| `latest_version` | Get latest version | `{{ versions \| dai_continuous_testing.utilities.latest_version }}` |
| `get_major_version` | Get major version number | `{{ '1.2.3' \| dai_continuous_testing.utilities.get_major_version }}` |
| `get_minor_version` | Get minor version number | `{{ '1.2.3' \| dai_continuous_testing.utilities.get_minor_version }}` |
| `get_patch_version` | Get patch version number | `{{ '1.2.3' \| dai_continuous_testing.utilities.get_patch_version }}` |

### Usage Examples

```yaml
# Version-based conditional logic
- name: Enable new features for recent versions
  set_fact:
    enable_advanced_features: "{{ app_version | dai_continuous_testing.utilities.version_compare('2.0.0', '>=') }}"

- name: Configure management endpoints (v25+ only)
  set_fact:
    management_endpoints: "health,info,metrics"
  when: app_version | dai_continuous_testing.utilities.version_compare('25.0.0', '>=')

# Version compatibility checks  
- name: Verify Java compatibility
  fail:
    msg: "Java 17+ required for app version {{ app_version }}"
  when: 
    - app_version | dai_continuous_testing.utilities.version_compare('25.5.0', '>=')
    - java_version | dai_continuous_testing.utilities.get_major_version < 17

# Parse version information
- set_fact:
    version_info: "{{ app_version | dai_continuous_testing.utilities.parse_version }}"

- debug:
    msg: |
      Version Details:
      Major: {{ version_info.major }}
      Minor: {{ version_info.minor }}  
      Patch: {{ version_info.patch }}
      Stable: {{ app_version | dai_continuous_testing.utilities.is_stable_version }}

# Version range validation
- name: Check supported version range
  assert:
    that:
      - app_version | dai_continuous_testing.utilities.version_in_range('>=24.0.0,<27.0.0')
    fail_msg: "App version {{ app_version }} is not in supported range (24.0.0 - 26.x.x)"

# Version sorting and selection
- name: Find latest compatible version
  set_fact:
    latest_compatible: "{{ available_versions | select('dai_continuous_testing.utilities.version_compare', '3.0.0', '<') | list | dai_continuous_testing.utilities.latest_version }}"

# Extract version from strings
- name: Parse version from filename
  set_fact:
    extracted_version: "{{ installer_filename | dai_continuous_testing.utilities.extract_version }}"
  when: app_version is not defined
```

## Integration Examples

### Complete Role Integration

```yaml
# defaults/main.yml
---
app_name: cloudserver
app_version: "25.8.24230"

# Dynamic configuration using filter plugins
service_name: "{{ ('experitest-' + app_name + '-' + ansible_hostname) | dai_continuous_testing.utilities.safe_key }}"
installation_path: "{{ [installation_root, app_name] | dai_continuous_testing.utilities.join_path }}"
config_file: "{{ (app_name + '.properties') | dai_continuous_testing.utilities.safe_filename }}"

# Version-based features
supports_management_endpoints: "{{ app_version | dai_continuous_testing.utilities.version_compare('25.0.0', '>=') }}"
requires_java_17: "{{ app_version | dai_continuous_testing.utilities.version_compare('25.5.0', '>=') }}"

# OS-specific configuration
health_check_port: "{{ 33300 if (ansible_os_family | dai_continuous_testing.utilities.is_linux_family) else server_port }}"
```

```yaml
# tasks/main.yml
---
- name: Validate version compatibility
  assert:
    that:
      - app_version | dai_continuous_testing.utilities.version_in_range('>=24.0.0,<27.0.0')
    fail_msg: "Unsupported version: {{ app_version }}"

- name: Create installation directory
  file:
    path: "{{ installation_path }}"
    state: directory
    mode: '0755'
  when: ansible_os_family | dai_continuous_testing.utilities.is_linux_family

- name: Configure application properties
  dai_continuous_testing.utilities.application_properties:
    path: "{{ [installation_path, 'conf', config_file] | dai_continuous_testing.utilities.join_path }}"
    properties:
      server.port: "{{ server_port }}"
      management.endpoints.web.exposure.include: "{{ 'health,info,metrics' if supports_management_endpoints else 'health' }}"
    backup: yes

- name: Start service with dynamic name
  systemd:
    name: "{{ service_name }}"
    state: started
    enabled: yes
  when: ansible_os_family | dai_continuous_testing.utilities.is_linux_family
```

### Multi-Environment Deployment

```yaml
# group_vars/production.yml
app_version: "25.8.24230"
environment: production
enable_debug: false

# group_vars/staging.yml  
app_version: "25.9.24250-beta.1"
environment: staging
enable_debug: true

# playbook.yml
---
- hosts: all
  vars:
    # Dynamic service configuration
    service_name: "{{ ('experitest-cloudserver-' + environment + '-' + ansible_hostname) | dai_continuous_testing.utilities.safe_key }}"
    log_level: "{{ 'DEBUG' if enable_debug else 'INFO' }}"
    
    # Version-based feature flags
    is_stable_release: "{{ app_version | dai_continuous_testing.utilities.is_stable_version }}"
    supports_new_features: "{{ app_version | dai_continuous_testing.utilities.version_compare('25.8.0', '>=') }}"
    
  tasks:
    - name: Deploy only stable versions to production
      assert:
        that: is_stable_release
        fail_msg: "Cannot deploy pre-release version {{ app_version }} to production"
      when: environment == 'production'
    
    - name: Configure based on OS type
      include_tasks: "{{ ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type }}.yml"
    
    - name: Generate deployment report
      debug:
        msg: |
          Deployment Summary:
          ==================
          Service: {{ service_name }}
          Version: {{ app_version }} ({{ 'Stable' if is_stable_release else 'Pre-release' }})
          OS Type: {{ ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type }}
          Environment: {{ environment }}
          Features: {{ 'Enhanced' if supports_new_features else 'Standard' }}
```

## Best Practices

### 1. Naming Conventions

```yaml
# Use safe_key for service and variable names
service_name: "{{ (organization + '-' + app_name + '-' + environment) | dai_continuous_testing.utilities.safe_key }}"

# Use safe_filename for configuration files
config_file: "{{ (app_name + '-' + environment + '.properties') | dai_continuous_testing.utilities.safe_filename }}"

# Use slugify for user-facing identifiers
deployment_id: "{{ (app_name + '-' + ansible_date_time.date) | dai_continuous_testing.utilities.slugify }}"
```

### 2. Path Management

```yaml
# Always use join_path for cross-platform compatibility
installation_path: "{{ [installation_root, app_name, app_version] | dai_continuous_testing.utilities.join_path }}"
config_path: "{{ [installation_path, 'conf'] | dai_continuous_testing.utilities.join_path }}"
log_path: "{{ [installation_path, 'logs'] | dai_continuous_testing.utilities.join_path }}"
```

### 3. Version Management

```yaml
# Use version comparison for feature gates
- set_fact:
    feature_flags:
      management_endpoints: "{{ app_version | dai_continuous_testing.utilities.version_compare('25.0.0', '>=') }}"
      enhanced_security: "{{ app_version | dai_continuous_testing.utilities.version_compare('25.5.0', '>=') }}"
      java_17_required: "{{ app_version | dai_continuous_testing.utilities.version_compare('26.0.0', '>=') }}"

# Use version parsing for complex logic
- set_fact:
    version_info: "{{ app_version | dai_continuous_testing.utilities.parse_version }}"
    compatibility_suffix: "{{ 'v' + (version_info.major | string) }}"
```

### 4. OS Detection

```yaml
# Use OS family detection for conditional includes
- include_tasks: "{{ ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type }}/install.yml"

# Use boolean filters for cleaner conditionals
- name: Install Linux packages
  package:
    name: "{{ packages }}"
  when: ansible_os_family | dai_continuous_testing.utilities.is_linux_family

# Use OS type for variable selection
- set_fact:
    installer_type: "{{ os_installers[ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type] }}"
  vars:
    os_installers:
      linux: "rpm"
      windows: "msi"
      darwin: "pkg"
```

### 5. Security Considerations

```yaml
# Mask sensitive data in debug output
- debug:
    msg: "Database password: {{ db_password | dai_continuous_testing.utilities.mask_sensitive('*', 4) }}"
  when: debug_mode | default(false)

# Use safe filename generation for sensitive data
- set_fact:
    credential_file: "{{ (app_name + '-credentials-' + environment) | dai_continuous_testing.utilities.safe_filename }}"
```

## Error Handling

The filter plugins include robust error handling:

```yaml
# Version filters fallback gracefully
- set_fact:
    version_check: "{{ app_version | dai_continuous_testing.utilities.version_compare('1.0.0', '>=') | default(false) }}"

# String filters handle non-string input
- set_fact:
    safe_name: "{{ (app_name | default('default')) | dai_continuous_testing.utilities.safe_key }}"

# OS filters return false for unknown OS families
- debug:
    msg: "Unknown OS family detected"
  when: not (ansible_os_family | dai_continuous_testing.utilities.is_linux_family or 
             ansible_os_family | dai_continuous_testing.utilities.is_windows_family or 
             ansible_os_family | dai_continuous_testing.utilities.is_darwin_family)
```

These filter plugins significantly enhance Ansible's capabilities for cross-platform deployments, version management, and configuration generation while maintaining clean, readable playbook code.
