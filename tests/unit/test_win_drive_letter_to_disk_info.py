#!/usr/bin/env python3
"""
Unit tests for win_drive_letter_to_disk_info module
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, Mock
import tempfile
import json

# Add the module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../plugins/modules'))

try:
    from win_drive_letter_to_disk_info import get_disk_info, parse_drive_letter
except ImportError:
    get_disk_info = None
    parse_drive_letter = None


class TestWinDriveLetterToDiskInfo(unittest.TestCase):
    """Test cases for win_drive_letter_to_disk_info module functions"""

    @unittest.skipIf(parse_drive_letter is None, "Module not available")
    def test_parse_drive_letter_valid_formats(self):
        """Test parsing valid drive letter formats"""
        test_cases = [
            ('C:', 'C'),
            ('c:', 'C'),
            ('C', 'C'),
            ('c', 'C'),
            ('D:', 'D'),
            ('Z:', 'Z')
        ]
        
        for input_drive, expected_output in test_cases:
            with self.subTest(input_drive=input_drive):
                result = parse_drive_letter(input_drive)
                self.assertEqual(result, expected_output)

    @unittest.skipIf(parse_drive_letter is None, "Module not available")
    def test_parse_drive_letter_invalid_formats(self):
        """Test parsing invalid drive letter formats"""
        test_cases = [
            '',  # Empty string
            'CC',  # Two letters
            '1',  # Number
            'C:/',  # With slash
            'C:\\',  # With backslash
            'invalid',  # Word
            None  # None value
        ]
        
        for invalid_input in test_cases:
            with self.subTest(invalid_input=invalid_input):
                with self.assertRaises((ValueError, TypeError)):
                    parse_drive_letter(invalid_input)

    @unittest.skipIf(get_disk_info is None, "Module not available")
    @patch('win_drive_letter_to_disk_info.subprocess.run')
    def test_get_disk_info_success(self, mock_subprocess):
        """Test successful disk info retrieval"""
        # Mock successful PowerShell execution
        powershell_output = '''
[
    {
        "DriveLetter": "C",
        "Size": 500107862016,
        "FreeSpace": 250053931008,
        "FileSystem": "NTFS",
        "DriveType": 3,
        "DeviceID": "C:",
        "VolumeLabel": "System",
        "DiskNumber": 0,
        "PartitionNumber": 2,
        "DiskSize": 500107862016,
        "DiskModel": "Samsung SSD 970 EVO 500GB",
        "DiskInterface": "NVMe"
    }
]
        '''
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = powershell_output.strip()
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = get_disk_info('C')

        self.assertTrue(result['success'])
        self.assertEqual(result['msg'], 'OK')
        self.assertIn('disk_info', result)
        
        disk_info = result['disk_info']
        self.assertEqual(disk_info['DriveLetter'], 'C')
        self.assertEqual(disk_info['Size'], 500107862016)
        self.assertEqual(disk_info['FileSystem'], 'NTFS')
        self.assertEqual(disk_info['DiskNumber'], 0)

    @unittest.skipIf(get_disk_info is None, "Module not available")
    @patch('win_drive_letter_to_disk_info.subprocess.run')
    def test_get_disk_info_drive_not_found(self, mock_subprocess):
        """Test disk info retrieval when drive is not found"""
        # Mock PowerShell execution with empty result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "[]"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = get_disk_info('Z')

        self.assertFalse(result['success'])
        self.assertIn('Drive Z: not found', result['msg'])
        self.assertEqual(result['drive_letter'], 'Z')

    @unittest.skipIf(get_disk_info is None, "Module not available")
    @patch('win_drive_letter_to_disk_info.subprocess.run')
    def test_get_disk_info_powershell_error(self, mock_subprocess):
        """Test disk info retrieval when PowerShell command fails"""
        # Mock PowerShell execution error
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Access denied"
        mock_subprocess.return_value = mock_result

        result = get_disk_info('C')

        self.assertFalse(result['success'])
        self.assertIn('PowerShell command failed', result['msg'])
        self.assertIn('Access denied', result['msg'])

    @unittest.skipIf(get_disk_info is None, "Module not available")
    @patch('win_drive_letter_to_disk_info.subprocess.run')
    def test_get_disk_info_invalid_json(self, mock_subprocess):
        """Test disk info retrieval when PowerShell returns invalid JSON"""
        # Mock PowerShell execution with invalid JSON
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Invalid JSON output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = get_disk_info('C')

        self.assertFalse(result['success'])
        self.assertIn('Failed to parse PowerShell output', result['msg'])

    @unittest.skipIf(get_disk_info is None, "Module not available")
    @patch('win_drive_letter_to_disk_info.subprocess.run')
    def test_get_disk_info_multiple_drives(self, mock_subprocess):
        """Test disk info retrieval with multiple drives in output"""
        # Mock PowerShell execution with multiple drives
        powershell_output = '''
[
    {
        "DriveLetter": "C",
        "Size": 500107862016,
        "FreeSpace": 250053931008,
        "FileSystem": "NTFS",
        "DriveType": 3,
        "DeviceID": "C:",
        "VolumeLabel": "System",
        "DiskNumber": 0,
        "PartitionNumber": 2
    },
    {
        "DriveLetter": "D",
        "Size": 1000204886016,
        "FreeSpace": 500102443008,
        "FileSystem": "NTFS",
        "DriveType": 3,
        "DeviceID": "D:",
        "VolumeLabel": "Data",
        "DiskNumber": 1,
        "PartitionNumber": 1
    }
]
        '''
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = powershell_output.strip()
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = get_disk_info('D')

        self.assertTrue(result['success'])
        disk_info = result['disk_info']
        self.assertEqual(disk_info['DriveLetter'], 'D')
        self.assertEqual(disk_info['VolumeLabel'], 'Data')
        self.assertEqual(disk_info['DiskNumber'], 1)

    @unittest.skipIf(get_disk_info is None, "Module not available")
    @patch('win_drive_letter_to_disk_info.subprocess.run')
    def test_get_disk_info_network_drive(self, mock_subprocess):
        """Test disk info retrieval for network drive"""
        # Mock PowerShell execution for network drive
        powershell_output = '''
[
    {
        "DriveLetter": "Z",
        "Size": null,
        "FreeSpace": null,
        "FileSystem": "Network",
        "DriveType": 4,
        "DeviceID": "Z:",
        "VolumeLabel": "NetworkShare",
        "DiskNumber": null,
        "PartitionNumber": null,
        "DiskSize": null,
        "DiskModel": null,
        "DiskInterface": null
    }
]
        '''
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = powershell_output.strip()
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = get_disk_info('Z')

        self.assertTrue(result['success'])
        disk_info = result['disk_info']
        self.assertEqual(disk_info['DriveLetter'], 'Z')
        self.assertEqual(disk_info['DriveType'], 4)  # Network drive
        self.assertEqual(disk_info['FileSystem'], 'Network')
        self.assertIsNone(disk_info['DiskNumber'])


class TestWinDriveLetterToDiskInfoIntegration(unittest.TestCase):
    """Integration tests for win_drive_letter_to_disk_info module workflow"""

    @unittest.skipIf(get_disk_info is None, "Module not available")
    @patch('win_drive_letter_to_disk_info.subprocess.run')
    def test_full_workflow_with_valid_drive(self, mock_subprocess):
        """Test complete workflow with valid drive letter"""
        # Mock successful PowerShell execution
        powershell_output = '''
[
    {
        "DriveLetter": "C",
        "Size": 500107862016,
        "FreeSpace": 250053931008,
        "FileSystem": "NTFS",
        "DriveType": 3,
        "DeviceID": "C:",
        "VolumeLabel": "System",
        "DiskNumber": 0,
        "PartitionNumber": 2,
        "DiskSize": 500107862016,
        "DiskModel": "Samsung SSD 970 EVO 500GB",
        "DiskInterface": "NVMe"
    }
]
        '''
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = powershell_output.strip()
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Test with different input formats
        test_cases = ['C:', 'c:', 'C', 'c']
        
        for drive_input in test_cases:
            with self.subTest(drive_input=drive_input):
                # Parse drive letter
                parsed_drive = parse_drive_letter(drive_input)
                self.assertEqual(parsed_drive, 'C')
                
                # Get disk info
                result = get_disk_info(parsed_drive)
                
                self.assertTrue(result['success'])
                self.assertEqual(result['drive_letter'], 'C')
                
                disk_info = result['disk_info']
                self.assertEqual(disk_info['DriveLetter'], 'C')
                self.assertIsInstance(disk_info['Size'], int)
                self.assertIsInstance(disk_info['FreeSpace'], int)

    @unittest.skipIf(get_disk_info is None, "Module not available")
    def test_error_handling_workflow(self):
        """Test error handling in the complete workflow"""
        # Test invalid drive letter parsing
        with self.assertRaises((ValueError, TypeError)):
            invalid_drive = parse_drive_letter('invalid')

        # Test handling of None values
        with self.assertRaises((ValueError, TypeError)):
            none_drive = parse_drive_letter(None)

    @unittest.skipIf(get_disk_info is None, "Module not available")
    @patch('win_drive_letter_to_disk_info.subprocess.run')
    def test_disk_size_calculations(self, mock_subprocess):
        """Test disk size and usage calculations"""
        # Mock PowerShell execution with specific sizes
        total_size = 1000000000000  # 1TB
        free_space = 250000000000   # 250GB
        used_space = total_size - free_space
        
        powershell_output = f'''
[
    {{
        "DriveLetter": "D",
        "Size": {total_size},
        "FreeSpace": {free_space},
        "FileSystem": "NTFS",
        "DriveType": 3,
        "DeviceID": "D:",
        "VolumeLabel": "Data",
        "DiskNumber": 1,
        "PartitionNumber": 1
    }}
]
        '''
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = powershell_output.strip()
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = get_disk_info('D')

        self.assertTrue(result['success'])
        disk_info = result['disk_info']
        
        # Verify size calculations
        self.assertEqual(disk_info['Size'], total_size)
        self.assertEqual(disk_info['FreeSpace'], free_space)
        
        # Calculate used space
        calculated_used = disk_info['Size'] - disk_info['FreeSpace']
        self.assertEqual(calculated_used, used_space)
        
        # Calculate usage percentage
        usage_percent = (calculated_used / disk_info['Size']) * 100
        self.assertAlmostEqual(usage_percent, 75.0, places=1)  # 75% usage

    @unittest.skipIf(get_disk_info is None, "Module not available")
    @patch('win_drive_letter_to_disk_info.subprocess.run')
    def test_drive_type_detection(self, mock_subprocess):
        """Test detection of different drive types"""
        drive_types = [
            (3, "Fixed disk"),      # Local hard drive
            (4, "Network drive"),   # Network mapped drive
            (5, "CD-ROM"),          # Optical drive
            (2, "Removable disk")   # USB/floppy
        ]
        
        for drive_type_code, drive_description in drive_types:
            with self.subTest(drive_type=drive_description):
                powershell_output = f'''
[
    {{
        "DriveLetter": "X",
        "Size": 100000000,
        "FreeSpace": 50000000,
        "FileSystem": "NTFS",
        "DriveType": {drive_type_code},
        "DeviceID": "X:",
        "VolumeLabel": "Test",
        "DiskNumber": 0,
        "PartitionNumber": 1
    }}
]
                '''
                
                mock_result = Mock()
                mock_result.returncode = 0
                mock_result.stdout = powershell_output.strip()
                mock_result.stderr = ""
                mock_subprocess.return_value = mock_result

                result = get_disk_info('X')

                self.assertTrue(result['success'])
                disk_info = result['disk_info']
                self.assertEqual(disk_info['DriveType'], drive_type_code)


if __name__ == '__main__':
    unittest.main()
