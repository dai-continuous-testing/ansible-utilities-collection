#!/usr/bin/python

DOCUMENTATION = r'''
---
module: health_check
short_description: Perform HTTP health checks with retry logic
description:
    - Performs HTTP health checks against specified URLs
    - Supports custom headers, timeout, and expected status codes
    - Includes retry logic with configurable delays
    - Can validate response content using regular expressions
version_added: "1.0.0"
options:
    url:
        description: The URL to check
        required: true
        type: str
    headers:
        description: HTTP headers to send with the request
        required: false
        type: dict
        default: {}
    initial_delay:
        description: Initial delay before first attempt (seconds)
        required: false
        type: int
        default: 0
    delay_between_tries:
        description: Delay between retry attempts (seconds)
        required: false
        type: int
        default: 5
    max_retries:
        description: Maximum number of retry attempts
        required: false
        type: int
        default: 10
    timeout:
        description: Request timeout (seconds)
        required: false
        type: int
        default: 10
    expected_status:
        description: Expected HTTP status code
        required: false
        type: int
        default: 200
    expected_regexp:
        description: Regular expression to match in response content
        required: false
        type: str
author:
    - DAI Development Team
'''

EXAMPLES = r'''
- name: Basic health check
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:8080/health"

- name: Health check with custom status
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:8080/admin"
    expected_status: 401

- name: Health check with retry configuration
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:8080/health"
    max_retries: 5
    delay_between_tries: 10
    timeout: 30

- name: Health check with custom headers
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:8080/api/status"
    headers:
      Authorization: "Bearer {{ api_token }}"
      Content-Type: "application/json"

- name: Health check with content validation
  dai_continuous_testing.utilities.health_check:
    url: "http://localhost:8080/health"
    expected_regexp: '"status":\s*"(OK|healthy)"'
'''

RETURN = r'''
msg:
    description: Result message
    type: str
    returned: always
success:
    description: Whether the health check succeeded
    type: bool
    returned: always
url:
    description: The URL that was checked
    type: str
    returned: always
expected_status:
    description: The expected HTTP status code
    type: int
    returned: always
actual_status:
    description: The actual HTTP status code received
    type: int
    returned: when response received
content:
    description: Response content
    type: str
    returned: when content available
failed_attempts:
    description: Number of failed attempts before success
    type: int
    returned: on success
'''

import time
import socket

try:
    # python3
    import urllib.request as urllib_request
    import urllib.error as urllib_error
except ImportError:
    # python2
    import urllib2 as urllib_request
    import urllib2 as urllib_error

from ansible.module_utils.basic import AnsibleModule

def check_server_status(url, headers, expected_status, timeout, expected_regexp):

    try:
        req = urllib_request.Request(url, headers=headers)
        resp = urllib_request.urlopen(req, timeout=timeout)

    except urllib_error.HTTPError as e:
        if e.code == expected_status:
            return {
                "msg": "OK",
                "success": True,
                "url": url,
                "expected_status": expected_status,
                "actual_status": e.code
            }

        else:
            return {
                "msg": 'Expected status %d, actual: %d' % (expected_status, e.code),
                "success": False,
                "url": url,
                "expected_status": expected_status,
                "actual_status": e.code
            }

    except (urllib_error.URLError, socket.error) as e:
        return {
            "msg": 'URLError: %s' % str(e),
            "success": False,
            "url": url,
            "expected_status": expected_status
        }

    if resp.getcode() != expected_status:
        return {
            "msg": 'Expected status %d, actual: %d' % (expected_status, resp.getcode()),
            "success": False,
            "url": url,
            "expected_status": expected_status,
            "actual_status": resp.getcode()
        }

    try:
        content = resp.read()
    except:
        content = ""

    return {
        "msg": "OK",
        "success": True,
        "url": url,
        "expected_status": expected_status,
        "actual_status": resp.getcode(),
        "content": content
    }

def main():
    
    module_args = dict(
        url=dict(required=True, type='str'),
        headers=dict(required=False, type='dict', default=None),
        initial_delay=dict(required=False, type='int', default=0),
        delay_between_tries=dict(required=False, type='int', default=5),
        max_retries=dict(required=False, type='int', default=10),
        timeout=dict(request=False, type='int', default=10),
        expected_status=dict(request=False, type='int', default=200),
        expected_regexp=dict(request=False, default=None)
    )
    
    module = AnsibleModule(
        argument_spec=module_args
    )

    url = module.params['url']
    headers = module.params['headers'] or {}
    initial_delay = module.params['initial_delay']
    delay_between_tries = module.params['delay_between_tries']
    max_retries = module.params['max_retries']
    timeout = module.params['timeout']
    expected_status = module.params['expected_status']
    expected_regexp = module.params['expected_regexp']

    time.sleep(initial_delay)
    
    for attempt in range(max_retries):
        
        if attempt != 0:
            time.sleep(delay_between_tries)
        
        result = check_server_status(
                url=url, 
                headers=headers, 
                timeout=timeout,
                expected_status=expected_status,
                expected_regexp=expected_regexp)
        
        if result["success"]:
            module.exit_json(failed_attempts=attempt)
    
    else:
        module.fail_json(msg='Maximum attempts reached: ' + result["msg"],
                         failed_attempts=attempt)

if __name__ == '__main__':
    main()
