# win_drive_letter_to_disk_info Module

Get disk space information for Windows drives by drive letter.

## Features

- **Drive letter lookup** - Query specific drives (C:, D:, etc.)
- **Multiple size formats** - Returns bytes, MiB, and GiB values
- **Disk validation** - Ensures drive exists and is accessible
- **Free and total space** - Complete disk usage information
- **Windows-native** - Uses Windows disk management APIs

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `disks` | list | yes | - | List of disk information (from ansible_facts.disks) |
| `drive_letter` | string | yes | - | Drive letter to query (e.g., "C", "D", "E") |

## Return Values

| Key | Type | Description |
|-----|------|-------------|
| `disk_found` | boolean | Whether the specified drive was found |
| `free_disk_space` | object | Free space in bytes, MiB, and GiB |
| `total_disk_space` | object | Total space in bytes, MiB, and GiB |

### Disk Space Object Structure

```json
{
  "bytes": 107374182400,
  "mib": 102400,
  "gib": 100
}
```

## Examples

### Basic Disk Space Check

```yaml
- name: Get C: drive information
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    disks: "{{ ansible_facts.disks }}"
    drive_letter: "C"
  register: c_drive_info

- name: Display disk space
  debug:
    msg: "C: drive has {{ c_drive_info.free_disk_space.gib }}GB free of {{ c_drive_info.total_disk_space.gib }}GB total"
```

### Pre-Installation Disk Space Validation

```yaml
- name: Gather disk facts
  setup:
    gather_subset:
      - hardware

- name: Check available space on installation drive
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    disks: "{{ ansible_facts.disks }}"
    drive_letter: "{{ installation_drive | default('C') }}"
  register: install_drive

- name: Fail if insufficient disk space
  fail:
    msg: "Insufficient disk space. Available: {{ install_drive.free_disk_space.gib }}GB, Required: {{ required_space_gb }}GB"
  when: 
    - install_drive.disk_found
    - install_drive.free_disk_space.gib < (required_space_gb | int)

- name: Fail if drive not found
  fail:
    msg: "Installation drive {{ installation_drive }} not found"
  when: not install_drive.disk_found
```

### Multiple Drive Space Check

```yaml
- name: Check space on multiple drives
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    disks: "{{ ansible_facts.disks }}"
    drive_letter: "{{ item }}"
  loop:
    - "C"
    - "D"
    - "E"
  register: drive_spaces
  ignore_errors: yes

- name: Report drive space status
  debug:
    msg: "Drive {{ item.item }}: {% if item.disk_found %}{{ item.free_disk_space.gib }}GB free{% else %}Not found{% endif %}"
  loop: "{{ drive_spaces.results }}"
```

### Application Deployment Space Check

```yaml
- name: Check space before application installation
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    disks: "{{ ansible_facts.disks }}"
    drive_letter: "{{ app_install_drive }}"
  register: app_drive_space

- name: Calculate space requirements
  set_fact:
    space_needed_mb: "{{ (app_size_mb | int) + (temp_space_mb | int) + (log_space_mb | int) }}"

- name: Verify sufficient space exists
  assert:
    that:
      - app_drive_space.disk_found
      - app_drive_space.free_disk_space.mib >= (space_needed_mb | int)
    fail_msg: "Insufficient space on {{ app_install_drive }}: drive. Need {{ space_needed_mb }}MB, have {{ app_drive_space.free_disk_space.mib }}MB"
    success_msg: "Sufficient space available for installation"
```

### Database Storage Planning

```yaml
- name: Check database drive space
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    disks: "{{ ansible_facts.disks }}"
    drive_letter: "{{ db_drive_letter }}"
  register: db_drive

- name: Calculate database space allocation
  set_fact:
    max_db_size_gb: "{{ (db_drive.free_disk_space.gib * 0.8) | int }}"  # Use 80% of available space
  when: db_drive.disk_found

- name: Configure database with space limits
  win_template:
    src: database_config.j2
    dest: "{{ db_config_path }}"
  vars:
    max_database_size: "{{ max_db_size_gb }}GB"
  when: db_drive.disk_found
```

### System Monitoring

```yaml
- name: Monitor system drives
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    disks: "{{ ansible_facts.disks }}"
    drive_letter: "{{ item.drive }}"
  loop:
    - { drive: "C", threshold: 10 }  # System drive - 10GB minimum
    - { drive: "D", threshold: 50 }  # Data drive - 50GB minimum
    - { drive: "E", threshold: 20 }  # Backup drive - 20GB minimum
  register: system_drives

- name: Alert on low disk space
  win_eventlog:
    log: System
    source: DiskMonitoring
    event_id: 2001
    message: "Low disk space warning: Drive {{ item.item.drive }}: has {{ item.free_disk_space.gib }}GB free (threshold: {{ item.item.threshold }}GB)"
    level: warning
  loop: "{{ system_drives.results }}"
  when: 
    - item.disk_found
    - item.free_disk_space.gib < item.item.threshold
```

### Backup Space Verification

```yaml
- name: Check backup drive space before backup
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    disks: "{{ ansible_facts.disks }}"
    drive_letter: "{{ backup_drive }}"
  register: backup_space

- name: Get source data size
  win_stat:
    path: "{{ source_directory }}"
    get_size: yes
  register: source_size

- name: Calculate backup space requirements
  set_fact:
    backup_needed_gb: "{{ (source_size.stat.size / 1024 / 1024 / 1024) | round(1) }}"
    safety_margin_gb: 5

- name: Verify backup space availability
  assert:
    that:
      - backup_space.disk_found
      - backup_space.free_disk_space.gib >= ((backup_needed_gb | float) + safety_margin_gb)
    fail_msg: "Insufficient backup space. Need {{ backup_needed_gb }}GB + {{ safety_margin_gb }}GB margin, have {{ backup_space.free_disk_space.gib }}GB"
```

## Common Use Cases

### Application Installation

```yaml
- name: Pre-installation space check
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    disks: "{{ ansible_facts.disks }}"
    drive_letter: "C"
  register: system_drive

- name: Install application only if space available
  win_package:
    path: "{{ installer_path }}"
    state: present
  when: system_drive.free_disk_space.gib >= 5  # Require 5GB free
```

### Log File Management

```yaml
- name: Check log drive space
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    disks: "{{ ansible_facts.disks }}"
    drive_letter: "{{ log_drive }}"
  register: log_space

- name: Clean old logs if space is low
  win_find:
    paths: "{{ log_directory }}"
    patterns: "*.log"
    age: "7d"
  register: old_logs
  when: log_space.free_disk_space.gib < 5

- name: Remove old log files
  win_file:
    path: "{{ item.path }}"
    state: absent
  loop: "{{ old_logs.files }}"
  when: 
    - log_space.free_disk_space.gib < 5
    - old_logs.files is defined
```

## Error Handling

The module will fail if:
- Specified drive letter is not found
- Multiple drives have the same letter (rare)
- Disk information is not accessible

### Example Error Handling

```yaml
- name: Check drive with error handling
  dai_continuous_testing.utilities.win_drive_letter_to_disk_info:
    disks: "{{ ansible_facts.disks }}"
    drive_letter: "{{ target_drive }}"
  register: drive_check
  ignore_errors: yes

- name: Handle missing drive
  debug:
    msg: "Drive {{ target_drive }}: not found, using default C: drive"
  when: not drive_check.disk_found

- name: Use alternative drive
  set_fact:
    actual_drive: "C"
  when: not drive_check.disk_found
```

## Requirements

- Windows operating system
- PowerShell access
- Ansible facts gathering enabled
- Read permissions to disk information

## Limitations

- Requires `ansible_facts.disks` to be populated
- Only works with lettered drives (A-Z)
- Cannot query network drives or UNC paths
- No support for mount points or volume GUIDs

## Best Practices

1. **Always gather facts first**: Ensure `setup` module runs before using this module
2. **Handle missing drives**: Check `disk_found` before using space information
3. **Use appropriate thresholds**: Leave safety margins for disk space checks
4. **Consider different units**: Use GiB for large applications, MiB for smaller checks
5. **Monitor regularly**: Implement recurring space checks for critical systems

## Troubleshooting

### Facts Not Available

```yaml
- name: Ensure hardware facts are gathered
  setup:
    gather_subset:
      - hardware
  when: ansible_facts.disks is not defined
```

### Permission Issues

```yaml
- name: Test disk access
  win_stat:
    path: "{{ target_drive }}:\\"
  register: drive_access
  ignore_errors: yes

- name: Report access issues
  debug:
    msg: "Cannot access drive {{ target_drive }}:"
  when: drive_access.failed
```

### Drive Letter Validation

```yaml
- name: Validate drive letter format
  assert:
    that:
      - target_drive | length == 1
      - target_drive | regex_match('^[A-Za-z]$')
    fail_msg: "Invalid drive letter: {{ target_drive }}. Must be a single letter A-Z"
```
