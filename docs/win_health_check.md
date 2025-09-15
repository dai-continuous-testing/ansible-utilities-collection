# win_health_check Module

Perform HTTP health checks with retry logic for Windows systems using PowerShell.

## Features

- **PowerShell-based HTTP checks** - Native Windows implementation
- **Retry logic with backoff** - Configurable retries and delays
- **Expected status validation** - Verify specific HTTP status codes
- **Timeout control** - Prevent hanging requests
- **Windows-optimized** - Uses Invoke-WebRequest cmdlet

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | yes | - | URL to perform health check against |
| `timeout` | integer | no | `10` | Request timeout in seconds |
| `expected_status` | integer | no | `200` | Expected HTTP status code |
| `max_retries` | integer | no | `10` | Maximum number of retry attempts |
| `initial_delay` | integer | no | `0` | Seconds to wait before first attempt |
| `delay_between_tries` | integer | no | `5` | Seconds between retry attempts |

## Return Values

| Key | Type | Description |
|-----|------|-------------|
| `changed` | boolean | Always false (read-only operation) |
| `success` | boolean | Whether the health check succeeded |
| `url` | string | The URL that was checked |
| `failed_attempts` | integer | Number of failed attempts |
| `msg` | string | Status message describing the result |

## Examples

### Basic Health Check

```yaml
- name: Check if web service is running on Windows
  dai_continuous_testing.utilities.win_health_check:
    url: "http://localhost:8080/health"
    expected_status: 200
    max_retries: 5
    delay_between_tries: 3
```

### Application Startup Verification

```yaml
- name: Wait for Windows service to start
  dai_continuous_testing.utilities.win_health_check:
    url: "http://{{ ansible_default_ipv4.address }}:{{ server_port }}/health"
    expected_status: 200
    initial_delay: 30  # Wait 30 seconds before first check
    max_retries: 20    # Try for up to 5+ minutes
    delay_between_tries: 10
    timeout: 15
  register: service_health

- name: Display startup results
  debug:
    msg: "Service started successfully after {{ service_health.failed_attempts }} failed attempts"
  when: service_health.success
```

### Multiple Service Health Checks

```yaml
- name: Check multiple Windows services
  dai_continuous_testing.utilities.win_health_check:
    url: "{{ item.url }}"
    expected_status: "{{ item.status | default(200) }}"
    max_retries: 3
    delay_between_tries: 5
    timeout: 10
  loop:
    - { url: "http://localhost:8080/api/health" }
    - { url: "http://localhost:8081/status" }
    - { url: "http://localhost:9090/metrics" }
  register: windows_services

- name: Report service status
  debug:
    msg: "Service {{ item.item.url }} - Success: {{ item.success }}, Attempts: {{ item.failed_attempts }}"
  loop: "{{ windows_services.results }}"
```

### HTTPS Health Check

```yaml
- name: Check HTTPS endpoint on Windows
  dai_continuous_testing.utilities.win_health_check:
    url: "https://{{ inventory_hostname }}:{{ ssl_port }}/secure/health"
    expected_status: 200
    timeout: 20
    max_retries: 5
    delay_between_tries: 8
```

### Service Deployment Verification

```yaml
- name: Deploy Windows service
  win_service:
    name: "{{ service_name }}"
    state: started
    start_mode: auto

- name: Verify service is responding
  dai_continuous_testing.utilities.win_health_check:
    url: "http://localhost:{{ service_port }}/health"
    expected_status: 200
    initial_delay: 15
    max_retries: 15
    delay_between_tries: 6
    timeout: 12
  register: deployment_health

- name: Handle deployment failure
  fail:
    msg: "Service deployment failed - health check unsuccessful"
  when: not deployment_health.success
```

### Different Status Code Checks

```yaml
- name: Check service returns maintenance status
  dai_continuous_testing.utilities.win_health_check:
    url: "http://localhost:8080/maintenance"
    expected_status: 503  # Service Unavailable
    max_retries: 2
    delay_between_tries: 3

- name: Check API requires authentication
  dai_continuous_testing.utilities.win_health_check:
    url: "http://localhost:8080/api/protected"
    expected_status: 401  # Unauthorized
    max_retries: 1
    timeout: 5
```

## Common Use Cases

### IIS Application Health Checks

```yaml
- name: Restart IIS application pool
  win_iis_webapppool:
    name: "{{ app_pool_name }}"
    state: restarted

- name: Wait for IIS application to be ready
  dai_continuous_testing.utilities.win_health_check:
    url: "http://localhost/{{ app_name }}/health"
    expected_status: 200
    initial_delay: 10
    max_retries: 12
    delay_between_tries: 5
    timeout: 15
```

### Windows Service Health Monitoring

```yaml
- name: Check Windows service health endpoints
  dai_continuous_testing.utilities.win_health_check:
    url: "http://{{ item.host }}:{{ item.port }}/{{ item.endpoint }}"
    expected_status: 200
    max_retries: 3
    delay_between_tries: 4
    timeout: 8
  loop:
    - { host: "localhost", port: 8080, endpoint: "health" }
    - { host: "localhost", port: 8081, endpoint: "status" }
    - { host: "localhost", port: 9090, endpoint: "metrics" }
  register: service_checks

- name: Alert on unhealthy services
  debug:
    msg: "WARNING: Service at {{ item.item.host }}:{{ item.item.port }} is unhealthy"
  loop: "{{ service_checks.results }}"
  when: not item.success
```

### Load Balancer Backend Verification

```yaml
- name: Check backend servers from Windows load balancer
  dai_continuous_testing.utilities.win_health_check:
    url: "http://{{ item }}:{{ backend_port }}/health"
    expected_status: 200
    max_retries: 2
    delay_between_tries: 3
    timeout: 6
  loop: "{{ backend_servers }}"
  register: backend_health

- name: Update load balancer configuration
  # Remove unhealthy backends from rotation
  win_lineinfile:
    path: "{{ lb_config_path }}"
    regexp: "^server {{ item.item }}:"
    state: absent
  loop: "{{ backend_health.results }}"
  when: not item.success
```

## Error Handling

The module will fail if:
- URL is unreachable after all retries
- Received status code doesn't match expected
- PowerShell execution errors occur
- Network connectivity issues

### Example Error Handling

```yaml
- name: Health check with error handling
  dai_continuous_testing.utilities.win_health_check:
    url: "http://localhost:8080/health"
    expected_status: 200
    max_retries: 3
    delay_between_tries: 5
  register: health_result
  ignore_errors: yes

- name: Log health check failure
  win_eventlog:
    log: Application
    source: Ansible
    event_id: 1001
    message: "Health check failed for service: {{ health_result.msg }}"
    level: warning
  when: health_result.failed

- name: Restart service on health check failure
  win_service:
    name: "{{ service_name }}"
    state: restarted
  when: health_result.failed
```

## PowerShell Implementation Details

The module uses PowerShell's `Invoke-WebRequest` cmdlet with:
- `-UseBasicParsing` for compatibility
- `-Method 'GET'` for health checks
- `-TimeoutSec` for request timeout
- Error handling for WebExceptions

## Requirements

- Windows PowerShell 3.0+
- Network connectivity to target URL
- Appropriate firewall rules for outbound HTTP/HTTPS

## Limitations

- No custom headers support (compared to Linux version)
- Limited to GET requests
- No regex pattern matching for response content
- PowerShell execution policy must allow script execution

## Best Practices

1. **Use appropriate timeouts**: Windows services may take longer to respond
2. **Account for Windows startup times**: Use longer initial delays
3. **Monitor Windows Event Log**: Log health check results for troubleshooting
4. **Test firewall rules**: Ensure outbound connectivity is allowed
5. **Handle service dependencies**: Check dependent services first

## Troubleshooting

### PowerShell Execution Policy

```yaml
- name: Check PowerShell execution policy
  win_shell: Get-ExecutionPolicy
  register: exec_policy

- name: Set execution policy if needed
  win_shell: Set-ExecutionPolicy RemoteSigned -Force
  when: exec_policy.stdout.strip() == "Restricted"
```

### Windows Firewall Issues

```yaml
- name: Check Windows firewall rule
  win_firewall_rule:
    name: "Allow HTTP Out"
    direction: out
    action: allow
    protocol: tcp
    localport: any
    remoteport: 80,443,8080
    state: present
```

### Network Connectivity Test

```yaml
- name: Test network connectivity before health check
  win_shell: Test-NetConnection -ComputerName {{ target_host }} -Port {{ target_port }}
  register: connectivity_test
  ignore_errors: yes

- name: Skip health check if no connectivity
  debug:
    msg: "Skipping health check - no connectivity to {{ target_host }}:{{ target_port }}"
  when: connectivity_test.failed
```
