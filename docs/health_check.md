# health_check Module

Perform HTTP health checks with retry logic for Linux/Unix systems.

## Features

- **HTTP/HTTPS health checks** - Support for both protocols
- **Retry logic with backoff** - Configurable retries and delays
- **Custom headers support** - Send authentication or custom headers
- **Expected status validation** - Verify specific HTTP status codes
- **Timeout control** - Prevent hanging requests
- **Python 2/3 compatible** - Works with both Python versions

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | yes | - | URL to perform health check against |
| `headers` | dict | no | `{}` | HTTP headers to send with request |
| `initial_delay` | integer | no | `0` | Seconds to wait before first attempt |
| `delay_between_tries` | integer | no | `5` | Seconds between retry attempts |
| `max_retries` | integer | no | `10` | Maximum number of retry attempts |
| `timeout` | integer | no | `10` | Request timeout in seconds |
| `expected_status` | integer | no | `200` | Expected HTTP status code |
| `expected_regexp` | string | no | `null` | Expected response pattern (not implemented) |

## Return Values

| Key | Type | Description |
|-----|------|-------------|
| `failed_attempts` | integer | Number of failed attempts before success |
| `msg` | string | Status message describing the result |
| `success` | boolean | Whether the health check succeeded |
| `url` | string | The URL that was checked |
| `expected_status` | integer | Expected HTTP status code |
| `actual_status` | integer | Actual HTTP status code received |

## Examples

### Basic Health Check

```yaml
- name: Check if web service is running
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:8080/health"
    expected_status: 200
    max_retries: 5
    delay_between_tries: 3
```

### Advanced Health Check with Headers

```yaml
- name: Health check with authentication
  dai_continuous_testing.utilities.health_check:
    url: "https://api.example.com/health"
    headers:
      Authorization: "Bearer {{ api_token }}"
      Content-Type: "application/json"
      User-Agent: "Ansible Health Check"
    expected_status: 200
    timeout: 15
    max_retries: 10
    delay_between_tries: 5
```

### Wait for Application Startup

```yaml
- name: Wait for application to start after deployment
  dai_continuous_testing.utilities.health_check:
    url: "http://{{ ansible_default_ipv4.address }}:{{ server_port }}/actuator/health"
    expected_status: 200
    initial_delay: 30  # Wait 30 seconds before first check
    max_retries: 30    # Try for up to 5 minutes
    delay_between_tries: 10
    timeout: 5
  register: health_result

- name: Display health check results
  debug:
    msg: "Health check succeeded after {{ health_result.failed_attempts }} failed attempts"
```

### Multiple Service Health Checks

```yaml
- name: Check multiple services
  dai_continuous_testing.utilities.health_check:
    url: "{{ item.url }}"
    expected_status: "{{ item.status | default(200) }}"
    max_retries: 5
    delay_between_tries: 3
  loop:
    - { url: "http://localhost:8080/health", status: 200 }
    - { url: "http://localhost:8081/status", status: 200 }
    - { url: "http://localhost:8082/ping", status: 200 }
  register: service_health

- name: Report any failed health checks
  fail:
    msg: "Service health check failed for {{ item.item.url }}"
  when: item.failed_attempts is defined
  loop: "{{ service_health.results }}"
```

### Check Different Status Codes

```yaml
- name: Check service returns maintenance mode
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:8080/maintenance"
    expected_status: 503  # Service Unavailable during maintenance
    max_retries: 3
    delay_between_tries: 2

- name: Check API endpoint requires authentication
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:8080/api/protected"
    expected_status: 401  # Unauthorized without credentials
    max_retries: 1
```

## Common Use Cases

### Application Deployment Verification

```yaml
- name: Deploy application
  # ... deployment tasks ...

- name: Verify application is responding
  dai_continuous_testing.utilities.health_check:
    url: "http://{{ inventory_hostname }}:{{ app_port }}/health"
    expected_status: 200
    initial_delay: 15
    max_retries: 20
    delay_between_tries: 5
    timeout: 10
```

### Load Balancer Health Checks

```yaml
- name: Check all backend servers
  dai_continuous_testing.utilities.health_check:
    url: "http://{{ item }}:{{ backend_port }}/health"
    expected_status: 200
    max_retries: 3
    delay_between_tries: 2
  loop: "{{ backend_servers }}"
  register: backend_health

- name: Remove unhealthy backends from load balancer
  # ... load balancer configuration ...
  when: backend_health.results[ansible_loop.index0].failed_attempts is defined
```

### Service Restart Verification

```yaml
- name: Restart service
  systemd:
    name: "{{ service_name }}"
    state: restarted
  become: yes

- name: Wait for service to be healthy after restart
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:{{ service_port }}/health"
    expected_status: 200
    initial_delay: 10
    max_retries: 15
    delay_between_tries: 4
    timeout: 8
```

## Error Handling

The module will fail if:
- URL is unreachable after all retries
- Received status code doesn't match expected status
- Request times out repeatedly
- Network connectivity issues

### Example Error Handling

```yaml
- name: Check service health with error handling
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:8080/health"
    expected_status: 200
    max_retries: 5
    delay_between_tries: 3
  register: health_check
  ignore_errors: yes

- name: Handle health check failure
  debug:
    msg: "Health check failed after {{ health_check.failed_attempts }} attempts: {{ health_check.msg }}"
  when: health_check.failed

- name: Take corrective action
  systemd:
    name: "{{ service_name }}"
    state: restarted
  become: yes
  when: health_check.failed
```

## Requirements

- Python 2.7+ or Python 3.6+
- Network connectivity to target URL
- `urllib2` (Python 2) or `urllib.request` (Python 3)

## Limitations

- The `expected_regexp` parameter is defined but not implemented
- Only supports basic HTTP methods (GET)
- Limited to HTTP/HTTPS protocols
- No support for client certificates

## Best Practices

1. **Set appropriate timeouts**: Balance between reliability and speed
2. **Use initial delays**: Allow time for services to start before checking
3. **Monitor retry counts**: Log failed attempts for troubleshooting
4. **Check different endpoints**: Use specific health check endpoints when available
5. **Handle failures gracefully**: Plan for health check failures in your playbooks

## Troubleshooting

### DNS Resolution Issues
```yaml
- name: Check if hostname resolves
  command: nslookup {{ target_hostname }}
  ignore_errors: yes
  register: dns_check

- name: Use IP address if DNS fails
  set_fact:
    health_check_url: "http://{{ ansible_default_ipv4.address }}:{{ port }}/health"
  when: dns_check.failed
```

### Certificate Issues (HTTPS)
For HTTPS endpoints with self-signed certificates, consider using HTTP for health checks or implementing certificate validation bypass.
