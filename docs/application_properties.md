# application_properties Module

Manage Java application.properties files atomically, preventing race conditions.

## Features

- **Atomic file operations** - No race conditions with single file write
- **Automatic backup creation** - Timestamped backups before changes
- **Comment out existing properties** - Preserves original values as comments
- **Managed blocks** - Clear separation of Ansible-managed content
- **Cross-platform support** - Works on Linux, macOS, and Windows
- **Idempotent operations** - Only changes when needed

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `path` | string | yes | - | Path to the properties file |
| `properties` | dict | yes | - | Dictionary of key-value pairs to set |
| `backup` | boolean | no | `true` | Create backup before changes |
| `comment_existing` | boolean | no | `true` | Comment out existing properties with same keys |
| `marker` | string | no | "ANSIBLE MANAGED BLOCK - Application Properties" | Block marker text |

## Return Values

| Key | Type | Description |
|-----|------|-------------|
| `changed` | boolean | Whether the file was modified |
| `properties_added` | integer | Number of properties added/updated |
| `properties_commented` | integer | Number of existing properties commented out |
| `backup_file` | string | Path to backup file (if created) |

## Examples

### Basic Usage

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

### Advanced Usage with Variables

```yaml
- name: Configure application with environment-specific properties
  dai_continuous_testing.utilities.application_properties:
    path: "{{ installation_folder }}/config/application.properties"
    properties:
      server.port: "{{ server_port | default('8080') }}"
      database.url: "{{ database_connection_string }}"
      app.name: "{{ application_name }}"
      logging.level.root: "{{ log_level | default('INFO') }}"
      spring.profiles.active: "{{ environment | default('production') }}"
    backup: yes
    comment_existing: yes
    marker: "ANSIBLE MANAGED BLOCK - {{ application_name }} Configuration"
```

### Multiple Properties Files

```yaml
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

### Disable Backup and Comments

```yaml
- name: Update properties without backup or comments
  dai_continuous_testing.utilities.application_properties:
    path: /opt/app/config/application.properties
    properties:
      server.port: "9090"
      database.timeout: "30"
    backup: false
    comment_existing: false
```

## How It Works

1. **Reads** the entire properties file into memory
2. **Comments out** existing properties that match your keys (if enabled)
3. **Removes** any previous Ansible-managed block
4. **Adds** new managed block with your properties
5. **Writes** everything back atomically
6. **Creates backup** with timestamp (if enabled)

### Example File Transformation

**Before:**
```properties
# Original application.properties
server.port=8080
database.url=jdbc:mysql://localhost/olddb
custom.setting=value
```

**After:**
```properties
# Original application.properties
# server.port=8080  # commented by ansible
# database.url=jdbc:mysql://localhost/olddb  # commented by ansible
custom.setting=value

# BEGIN ANSIBLE MANAGED BLOCK - Application Properties
server.port=9090
database.url=jdbc:mysql://newhost/newdb
app.name=myapp
# END ANSIBLE MANAGED BLOCK - Application Properties
```

## Requirements

- Ansible >= 2.9
- Python >= 3.6
- Write permissions to the target file and directory

## Error Handling

The module will fail if:
- Target file path is not writable
- Properties dictionary is empty or invalid
- Directory for the file doesn't exist and can't be created
- Backup creation fails (when backup=true)

## Best Practices

1. **Always use backup**: Keep `backup: true` for production systems
2. **Use descriptive markers**: Customize the marker text for different property files
3. **Group related properties**: Use separate tasks for logically different property groups
4. **Test with check mode**: Use `--check` flag to preview changes
5. **Validate after changes**: Add verification tasks to ensure properties were applied correctly

## Troubleshooting

### Permission Errors
Ensure the Ansible user has write permissions to the file and directory:
```yaml
- name: Ensure config directory permissions
  file:
    path: "{{ installation_folder }}/config"
    state: directory
    owner: "{{ ansible_user }}"
    mode: '0755'
  become: yes
```

### Backup Directory Full
Monitor backup directory size and clean old backups:
```yaml
- name: Clean old property backups
  find:
    paths: "{{ installation_folder }}/config"
    patterns: "*.properties.*~"
    age: "7d"
  register: old_backups

- name: Remove old backups
  file:
    path: "{{ item.path }}"
    state: absent
  loop: "{{ old_backups.files }}"
```
