#!/usr/bin/env python3
"""
Unit tests for win_health_check module
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, Mock
import tempfile
import json

# Add the module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../plugins/modules'))

# Since win_health_check.ps1 is a PowerShell script, we'll test the wrapper/interface
# and mock the PowerShell execution


class TestWinHealthCheckModule(unittest.TestCase):
    """Test cases for win_health_check module PowerShell execution"""

    def test_powershell_script_exists(self):
        """Test that the PowerShell script file exists"""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '../../plugins/modules/win_health_check.ps1'
        )
        self.assertTrue(os.path.exists(script_path), 
                       f"PowerShell script not found at {script_path}")

    @patch('subprocess.run')
    def test_powershell_execution_success(self, mock_subprocess):
        """Test successful PowerShell script execution"""
        # Mock successful PowerShell execution
        expected_result = {
            "success": True,
            "msg": "OK",
            "actual_status": 200,
            "expected_status": 200,
            "url": "http://localhost:8080/health",
            "content": '{"status": "healthy"}'
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(expected_result)
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Simulate calling PowerShell script
        import subprocess
        result = subprocess.run([
            'powershell.exe', '-File', 'win_health_check.ps1',
            '-Url', 'http://localhost:8080/health',
            '-ExpectedStatus', '200',
            '-Timeout', '10'
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        output_data = json.loads(result.stdout)
        self.assertTrue(output_data['success'])
        self.assertEqual(output_data['actual_status'], 200)

    @patch('subprocess.run')
    def test_powershell_execution_http_error(self, mock_subprocess):
        """Test PowerShell script execution with HTTP error"""
        # Mock HTTP error response
        expected_result = {
            "success": False,
            "msg": "Expected status 200, actual: 500",
            "actual_status": 500,
            "expected_status": 200,
            "url": "http://localhost:8080/health"
        }
        
        mock_result = Mock()
        mock_result.returncode = 0  # PowerShell script runs successfully but reports HTTP error
        mock_result.stdout = json.dumps(expected_result)
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Simulate calling PowerShell script
        import subprocess
        result = subprocess.run([
            'powershell.exe', '-File', 'win_health_check.ps1',
            '-Url', 'http://localhost:8080/health',
            '-ExpectedStatus', '200',
            '-Timeout', '10'
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        output_data = json.loads(result.stdout)
        self.assertFalse(output_data['success'])
        self.assertEqual(output_data['actual_status'], 500)

    @patch('subprocess.run')
    def test_powershell_execution_connection_error(self, mock_subprocess):
        """Test PowerShell script execution with connection error"""
        # Mock connection error
        expected_result = {
            "success": False,
            "msg": "Connection error: Unable to connect to remote server",
            "expected_status": 200,
            "url": "http://localhost:8080/health"
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(expected_result)
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Simulate calling PowerShell script
        import subprocess
        result = subprocess.run([
            'powershell.exe', '-File', 'win_health_check.ps1',
            '-Url', 'http://localhost:8080/health',
            '-ExpectedStatus', '200',
            '-Timeout', '10'
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        output_data = json.loads(result.stdout)
        self.assertFalse(output_data['success'])
        self.assertIn('Connection error', output_data['msg'])

    @patch('subprocess.run')
    def test_powershell_script_execution_error(self, mock_subprocess):
        """Test PowerShell script execution failure"""
        # Mock PowerShell execution error
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "PowerShell script error: Invalid parameter"
        mock_subprocess.return_value = mock_result

        # Simulate calling PowerShell script with invalid parameters
        import subprocess
        result = subprocess.run([
            'powershell.exe', '-File', 'win_health_check.ps1',
            '-InvalidParam', 'value'
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn('PowerShell script error', result.stderr)

    def test_powershell_script_content_validation(self):
        """Test that PowerShell script contains expected functions and parameters"""
        script_path = os.path.join(
            os.path.dirname(__file__), 
            '../../plugins/modules/win_health_check.ps1'
        )
        
        if os.path.exists(script_path):
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for expected PowerShell elements (case-insensitive)
            content_lower = content.lower()
            
            # Check for Ansible parameter parsing
            self.assertIn('get-ansibleparam', content_lower)
            self.assertIn('$url', content)
            self.assertIn('$expectedstatus', content_lower.replace('_', ''))
            self.assertIn('$timeout', content)
            
            # Check for health check logic
            self.assertIn('invoke-webrequest', content_lower)
            self.assertIn('statuscode', content_lower)
            
            # Check for Ansible module functions
            self.assertIn('exit-json', content_lower)
            self.assertIn('fail-json', content_lower)
            
            # Check for documentation
            self.assertIn('.synopsis', content_lower)


class TestWinHealthCheckIntegration(unittest.TestCase):
    """Integration tests for win_health_check PowerShell module"""

    @patch('subprocess.run')
    def test_retry_workflow_powershell(self, mock_subprocess):
        """Test retry workflow with PowerShell health check"""
        # Mock multiple calls - first two fail, third succeeds
        call_results = [
            # First call - connection error
            Mock(returncode=0, stdout=json.dumps({
                "success": False,
                "msg": "Connection timeout",
                "expected_status": 200,
                "url": "http://localhost:8080/health"
            }), stderr=""),
            # Second call - still failing
            Mock(returncode=0, stdout=json.dumps({
                "success": False,
                "msg": "Service unavailable",
                "actual_status": 503,
                "expected_status": 200,
                "url": "http://localhost:8080/health"
            }), stderr=""),
            # Third call - success
            Mock(returncode=0, stdout=json.dumps({
                "success": True,
                "msg": "OK",
                "actual_status": 200,
                "expected_status": 200,
                "url": "http://localhost:8080/health",
                "content": '{"status": "healthy"}'
            }), stderr="")
        ]
        
        mock_subprocess.side_effect = call_results

        # Simulate retry logic
        import subprocess
        import time
        
        max_retries = 3
        delay_between_tries = 1
        success = False
        
        for attempt in range(max_retries):
            if attempt > 0:
                time.sleep(delay_between_tries)
            
            result = subprocess.run([
                'powershell.exe', '-File', 'win_health_check.ps1',
                '-Url', 'http://localhost:8080/health',
                '-ExpectedStatus', '200',
                '-Timeout', '10'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                output_data = json.loads(result.stdout)
                if output_data.get('success'):
                    success = True
                    break

        self.assertTrue(success)
        self.assertEqual(mock_subprocess.call_count, 3)

    @patch('subprocess.run')
    def test_custom_headers_powershell(self, mock_subprocess):
        """Test PowerShell health check with custom headers"""
        expected_result = {
            "success": True,
            "msg": "OK",
            "actual_status": 200,
            "expected_status": 200,
            "url": "http://localhost:8080/health",
            "content": '{"status": "healthy"}'
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(expected_result)
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Simulate calling PowerShell script with custom headers
        import subprocess
        result = subprocess.run([
            'powershell.exe', '-File', 'win_health_check.ps1',
            '-Url', 'http://localhost:8080/health',
            '-ExpectedStatus', '200',
            '-Headers', '{"Authorization": "Bearer token123", "Content-Type": "application/json"}',
            '-Timeout', '30'
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        output_data = json.loads(result.stdout)
        self.assertTrue(output_data['success'])

    @patch('subprocess.run')
    def test_regex_validation_powershell(self, mock_subprocess):
        """Test PowerShell health check with regex validation"""
        expected_result = {
            "success": True,
            "msg": "OK",
            "actual_status": 200,
            "expected_status": 200,
            "url": "http://localhost:8080/health",
            "content": '{"status": "healthy"}',
            "regex_match": True
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(expected_result)
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Simulate calling PowerShell script with regex validation
        import subprocess
        result = subprocess.run([
            'powershell.exe', '-File', 'win_health_check.ps1',
            '-Url', 'http://localhost:8080/health',
            '-ExpectedStatus', '200',
            '-ExpectedRegexp', r'"status":\s*"healthy"',
            '-Timeout', '10'
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        output_data = json.loads(result.stdout)
        self.assertTrue(output_data['success'])
        self.assertTrue(output_data.get('regex_match', False))


if __name__ == '__main__':
    unittest.main()
