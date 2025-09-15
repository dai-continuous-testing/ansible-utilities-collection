#!powershell

<#
.SYNOPSIS
    Performs HTTP health checks on Windows systems with retry logic

.DESCRIPTION
    This PowerShell-based Ansible module performs HTTP health checks against specified URLs.
    It supports custom timeout, expected status codes, and retry logic with configurable delays.
    
    This is the Windows-specific version of the health_check module, designed to work
    with Windows systems where PowerShell is the preferred scripting environment.

.PARAMETER url
    The URL to check (required)

.PARAMETER timeout
    Request timeout in seconds (default: 10)

.PARAMETER expected_status
    Expected HTTP status code (default: 200)

.PARAMETER max_retries
    Maximum number of retry attempts (default: 10)

.PARAMETER initial_delay
    Initial delay before first attempt in seconds (default: 0)

.PARAMETER delay_between_tries
    Delay between retry attempts in seconds (default: 5)

.EXAMPLE
    win_health_check -url "http://localhost:8080/health"

.EXAMPLE
    win_health_check -url "http://localhost:8080/admin" -expected_status 401

.NOTES
    Author: DAI Development Team
    Version: 1.0.0
    
    This module requires PowerShell and the Ansible.ModuleUtils.Legacy module.
    It's specifically designed for Windows environments.
#>

#Requires -Module Ansible.ModuleUtils.Legacy

$ErrorActionPreference = 'Stop'

$params = Parse-Args $args -supports_check_mode $true
$check_mode = Get-AnsibleParam -obj $params -name "_ansible_check_mode" -type "bool" -default $false
$_remote_tmp = Get-AnsibleParam $params "_ansible_remote_tmp" -type "path" -default $env:TMP


$url = Get-AnsibleParam -obj $params -name "url" -type "str" -failifempty $true
$timeout = Get-AnsibleParam -obj $params -name "timeout" -type "int" -default 10
$expected_status = Get-AnsibleParam -obj $params -name "expected_status" -type "int" -default 200
$max_retries = Get-AnsibleParam -obj $params -name "max_retries" -type "int" -default 10
$initial_delay = Get-AnsibleParam -obj $params -name "initial_delay" -type "int" -default 0
$delay_between_tries = Get-AnsibleParam -obj $params -name "delay_between_tries" -type "int" -default 5

# $headers = Get-AnsibleParam -obj $params -name "headers" -type "dict" -default @{}
# $expected_regexp = Get-AnsibleParam -obj $params -name "expected_regexp" -type "str" -default @{}

Function Request-Url($url, $timeout, $expected_status) {

    try { 
        $response = Invoke-WebRequest `
            -Uri $url `
            -ErrorAction Stop `
            -UseBasicParsing `
            -Method 'GET' `
            -TimeoutSec $timeout
    } catch [System.Net.WebException] { 
        # Write-Debug $_
        $response = $_.Exception.Response
        $the_error = $_.Exception.Message
    }
    
    if (!$response) {
        return @{
            msg = "Error is $($the_error)"
            success = $false
        }
    }

    if ($response.StatusCode -eq $expected_status) {
        return @{
            msg = "Success: $($response.StatusCode) = $($expected_status)"
            success = $true
        }
    } 
    else {
        return @{
            msg = "Result is $($response.StatusCode.value__), Error is $($the_error)"
            success = $false
        }
    }
}

$result = @{
    changed = $false
    success = $false
    url = $url
    failed_attempts = 0
    msg = ""
}

Start-Sleep -s $initial_delay

For ($i=0; $i -lt $max_retries; $i++) {

    $res = Request-Url -url $url -timeout $timeout -expected_status $expected_status
    
    $result.success = $res.success
    $result.msg = $res.msg

    if ($result.success) {
        Exit-Json -obj $result
    } else {
        $result.failed_attempts = $i + 1
    }

    Start-Sleep -s $delay_between_tries
}

Fail-Json -obj $result
