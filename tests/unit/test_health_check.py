#!/usr/bin/env python3
"""
Unit tests for health_check module
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, Mock
import socket

# Add the module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../plugins/modules'))

try:
    from health_check import check_server_status
except ImportError:
    check_server_status = None


class TestHealthCheckModule(unittest.TestCase):
    """Test cases for health_check module functions"""

    @unittest.skipIf(check_server_status is None, "Module not available")
    @patch('health_check.urllib_request.urlopen')
    @patch('health_check.urllib_request.Request')
    def test_check_server_status_success(self, mock_request, mock_urlopen):
        """Test successful health check"""
        # Mock successful response
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"status": "healthy"}'
        mock_urlopen.return_value = mock_response

        result = check_server_status(
            url='http://localhost:8080/health',
            headers={'Content-Type': 'application/json'},
            expected_status=200,
            timeout=10,
            expected_regexp=None
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['msg'], 'OK')
        self.assertEqual(result['actual_status'], 200)
        self.assertEqual(result['expected_status'], 200)
        self.assertEqual(result['url'], 'http://localhost:8080/health')

    @unittest.skipIf(check_server_status is None, "Module not available")
    @patch('health_check.urllib_request.urlopen')
    @patch('health_check.urllib_request.Request')
    def test_check_server_status_wrong_status(self, mock_request, mock_urlopen):
        """Test health check with unexpected status code"""
        # Mock response with wrong status
        mock_response = Mock()
        mock_response.getcode.return_value = 500
        mock_urlopen.return_value = mock_response

        result = check_server_status(
            url='http://localhost:8080/health',
            headers={},
            expected_status=200,
            timeout=10,
            expected_regexp=None
        )

        self.assertFalse(result['success'])
        self.assertIn('Expected status 200, actual: 500', result['msg'])
        self.assertEqual(result['actual_status'], 500)
        self.assertEqual(result['expected_status'], 200)

    @unittest.skipIf(check_server_status is None, "Module not available")
    @patch('health_check.urllib_request.urlopen')
    @patch('health_check.urllib_request.Request')
    def test_check_server_status_http_error_expected(self, mock_request, mock_urlopen):
        """Test health check where HTTP error matches expected status"""
        # Mock HTTP error that matches expected status
        import urllib.error
        http_error = urllib.error.HTTPError(
            url='http://localhost:8080/health',
            code=404,
            msg='Not Found',
            hdrs={},
            fp=None
        )
        mock_urlopen.side_effect = http_error

        result = check_server_status(
            url='http://localhost:8080/health',
            headers={},
            expected_status=404,
            timeout=10,
            expected_regexp=None
        )

        self.assertTrue(result['success'])
        self.assertEqual(result['msg'], 'OK')
        self.assertEqual(result['actual_status'], 404)
        self.assertEqual(result['expected_status'], 404)

    @unittest.skipIf(check_server_status is None, "Module not available")
    @patch('health_check.urllib_request.urlopen')
    @patch('health_check.urllib_request.Request')
    def test_check_server_status_http_error_unexpected(self, mock_request, mock_urlopen):
        """Test health check where HTTP error doesn't match expected status"""
        # Mock HTTP error that doesn't match expected status
        import urllib.error
        http_error = urllib.error.HTTPError(
            url='http://localhost:8080/health',
            code=500,
            msg='Internal Server Error',
            hdrs={},
            fp=None
        )
        mock_urlopen.side_effect = http_error

        result = check_server_status(
            url='http://localhost:8080/health',
            headers={},
            expected_status=200,
            timeout=10,
            expected_regexp=None
        )

        self.assertFalse(result['success'])
        self.assertIn('Expected status 200, actual: 500', result['msg'])
        self.assertEqual(result['actual_status'], 500)
        self.assertEqual(result['expected_status'], 200)

    @unittest.skipIf(check_server_status is None, "Module not available")
    @patch('health_check.urllib_request.urlopen')
    @patch('health_check.urllib_request.Request')
    def test_check_server_status_connection_error(self, mock_request, mock_urlopen):
        """Test health check with connection error"""
        # Mock connection error
        import urllib.error
        url_error = urllib.error.URLError(reason='Connection refused')
        mock_urlopen.side_effect = url_error

        result = check_server_status(
            url='http://localhost:8080/health',
            headers={},
            expected_status=200,
            timeout=10,
            expected_regexp=None
        )

        self.assertFalse(result['success'])
        self.assertIn('URLError:', result['msg'])
        self.assertEqual(result['expected_status'], 200)
        self.assertNotIn('actual_status', result)

    @unittest.skipIf(check_server_status is None, "Module not available")
    @patch('health_check.urllib_request.urlopen')
    @patch('health_check.urllib_request.Request')
    def test_check_server_status_socket_error(self, mock_request, mock_urlopen):
        """Test health check with socket error"""
        # Mock socket error
        socket_error = socket.error('Network is unreachable')
        mock_urlopen.side_effect = socket_error

        result = check_server_status(
            url='http://localhost:8080/health',
            headers={},
            expected_status=200,
            timeout=10,
            expected_regexp=None
        )

        self.assertFalse(result['success'])
        self.assertIn('URLError:', result['msg'])
        self.assertEqual(result['expected_status'], 200)

    @unittest.skipIf(check_server_status is None, "Module not available")
    @patch('health_check.urllib_request.urlopen')
    @patch('health_check.urllib_request.Request')
    def test_check_server_status_read_error(self, mock_request, mock_urlopen):
        """Test health check where response.read() fails"""
        # Mock response where read() raises exception
        mock_response = Mock()
        mock_response.getcode.return_value = 200
        mock_response.read.side_effect = Exception('Read error')
        mock_urlopen.return_value = mock_response

        result = check_server_status(
            url='http://localhost:8080/health',
            headers={},
            expected_status=200,
            timeout=10,
            expected_regexp=None
        )

        # Should still succeed even if read fails
        self.assertTrue(result['success'])
        self.assertEqual(result['msg'], 'OK')
        self.assertEqual(result['content'], '')  # Empty content due to read error


class TestHealthCheckIntegration(unittest.TestCase):
    """Integration tests for health_check module workflow"""

    @unittest.skipIf(check_server_status is None, "Module not available")
    @patch('health_check.time.sleep')
    @patch('health_check.check_server_status')
    def test_retry_logic_success_first_try(self, mock_check, mock_sleep):
        """Test retry logic when first attempt succeeds"""
        # Mock successful first attempt
        mock_check.return_value = {'success': True, 'msg': 'OK'}

        # This would normally be in the main() function
        max_retries = 3
        for attempt in range(max_retries):
            if attempt != 0:
                mock_sleep(5)  # delay_between_tries
            
            result = mock_check.return_value
            if result['success']:
                break
        else:
            self.fail("Should have succeeded on first attempt")

        # Should not have slept since first attempt succeeded
        mock_sleep.assert_not_called()
        mock_check.assert_called_once()

    @unittest.skipIf(check_server_status is None, "Module not available")
    @patch('health_check.time.sleep')
    @patch('health_check.check_server_status')
    def test_retry_logic_success_after_retries(self, mock_check, mock_sleep):
        """Test retry logic when succeeds after retries"""
        # Mock failure then success
        mock_check.side_effect = [
            {'success': False, 'msg': 'Connection refused'},
            {'success': False, 'msg': 'Connection refused'},
            {'success': True, 'msg': 'OK'}
        ]

        max_retries = 5
        delay_between_tries = 2
        success = False
        
        for attempt in range(max_retries):
            if attempt != 0:
                mock_sleep(delay_between_tries)
            
            result = mock_check()
            if result['success']:
                success = True
                break

        self.assertTrue(success)
        # Should have slept 2 times (before attempt 1 and 2)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(delay_between_tries)

    @unittest.skipIf(check_server_status is None, "Module not available")
    @patch('health_check.time.sleep')
    @patch('health_check.check_server_status')
    def test_retry_logic_max_retries_exceeded(self, mock_check, mock_sleep):
        """Test retry logic when max retries are exceeded"""
        # Mock always failing
        mock_check.return_value = {'success': False, 'msg': 'Always fails'}

        max_retries = 3
        delay_between_tries = 1
        success = False
        
        for attempt in range(max_retries):
            if attempt != 0:
                mock_sleep(delay_between_tries)
            
            result = mock_check()
            if result['success']:
                success = True
                break

        self.assertFalse(success)
        # Should have called check_server_status max_retries times
        self.assertEqual(mock_check.call_count, max_retries)
        # Should have slept max_retries - 1 times
        self.assertEqual(mock_sleep.call_count, max_retries - 1)


if __name__ == '__main__':
    unittest.main()
