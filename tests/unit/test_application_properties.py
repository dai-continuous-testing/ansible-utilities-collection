#!/usr/bin/env python3
"""
Unit tests for application_properties module
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../plugins/modules'))

try:
    from application_properties import (
        backup_file,
        read_properties_file,
        write_properties_file,
        comment_existing_properties,
        remove_existing_ansible_block,
        add_ansible_block
    )
except ImportError:
    # If direct import fails, we'll skip these tests in CI
    backup_file = None
    read_properties_file = None
    write_properties_file = None
    comment_existing_properties = None
    remove_existing_ansible_block = None
    add_ansible_block = None


class TestApplicationPropertiesModule(unittest.TestCase):
    """Test cases for application_properties module functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test.properties')
        self.test_properties = {
            'server.port': '8080',
            'database.url': 'jdbc:mysql://localhost/test',
            'app.name': 'test-app'
        }
        self.test_marker = 'ANSIBLE MANAGED BLOCK - Test Properties'

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @unittest.skipIf(backup_file is None, "Module not available")
    def test_backup_file(self):
        """Test backup file creation"""
        # Create a test file
        with open(self.test_file, 'w') as f:
            f.write('test content\n')

        # Create backup
        with patch('application_properties.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20250915_123456'
            backup_path = backup_file(self.test_file)

        # Verify backup path format
        expected_path = f"{self.test_file}.backup_20250915_123456"
        self.assertEqual(backup_path, expected_path)

        # Verify backup file exists and has same content
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, 'test content\n')

    @unittest.skipIf(read_properties_file is None, "Module not available")
    def test_read_properties_file_existing(self):
        """Test reading existing properties file"""
        content = 'server.port=8080\ndatabase.url=jdbc:mysql://localhost/db\n'
        with open(self.test_file, 'w') as f:
            f.write(content)

        lines = read_properties_file(self.test_file)
        expected = ['server.port=8080\n', 'database.url=jdbc:mysql://localhost/db\n']
        self.assertEqual(lines, expected)

    @unittest.skipIf(read_properties_file is None, "Module not available")
    def test_read_properties_file_nonexistent(self):
        """Test reading non-existent properties file"""
        lines = read_properties_file('/nonexistent/file.properties')
        self.assertEqual(lines, [])

    @unittest.skipIf(write_properties_file is None, "Module not available")
    def test_write_properties_file(self):
        """Test writing properties file"""
        lines = ['server.port=8080\n', 'database.url=jdbc:mysql://localhost/db\n']
        write_properties_file(self.test_file, lines)

        # Verify file was written correctly
        with open(self.test_file, 'r') as f:
            content = f.read()
        expected = 'server.port=8080\ndatabase.url=jdbc:mysql://localhost/db\n'
        self.assertEqual(content, expected)

    @unittest.skipIf(comment_existing_properties is None, "Module not available")
    def test_comment_existing_properties(self):
        """Test commenting existing properties"""
        lines = [
            'server.port=9090\n',
            'database.url=jdbc:mysql://old/db\n',
            'other.property=value\n'
        ]
        properties = {'server.port': '8080', 'database.url': 'jdbc:mysql://new/db'}
        marker = 'TEST BLOCK'

        new_lines, commented_count = comment_existing_properties(lines, properties, marker)

        # Should comment out matching properties
        self.assertEqual(commented_count, 2)
        self.assertIn('# server.port=9090  # commented by ansible\n', new_lines)
        self.assertIn('# database.url=jdbc:mysql://old/db  # commented by ansible\n', new_lines)
        self.assertIn('other.property=value\n', new_lines)  # Should remain unchanged

    @unittest.skipIf(comment_existing_properties is None, "Module not available")
    def test_comment_existing_properties_skip_ansible_block(self):
        """Test that properties inside Ansible blocks are not commented"""
        lines = [
            'server.port=9090\n',
            '# BEGIN TEST BLOCK\n',
            'server.port=8080\n',
            '# END TEST BLOCK\n',
            'database.url=jdbc:mysql://old/db\n'
        ]
        properties = {'server.port': '8080', 'database.url': 'jdbc:mysql://new/db'}
        marker = 'TEST BLOCK'

        new_lines, commented_count = comment_existing_properties(lines, properties, marker)

        # Should only comment the first server.port (outside block) and database.url
        self.assertEqual(commented_count, 2)
        self.assertIn('# server.port=9090  # commented by ansible\n', new_lines)
        self.assertIn('server.port=8080\n', new_lines)  # Inside block, unchanged
        self.assertIn('# database.url=jdbc:mysql://old/db  # commented by ansible\n', new_lines)

    @unittest.skipIf(remove_existing_ansible_block is None, "Module not available")
    def test_remove_existing_ansible_block(self):
        """Test removing existing Ansible managed block"""
        lines = [
            'server.port=9090\n',
            '# BEGIN TEST BLOCK\n',
            'database.url=jdbc:mysql://old/db\n',
            '# END TEST BLOCK\n',
            'other.property=value\n'
        ]
        marker = 'TEST BLOCK'

        new_lines = remove_existing_ansible_block(lines, marker)

        expected = [
            'server.port=9090\n',
            'other.property=value\n'
        ]
        self.assertEqual(new_lines, expected)

    @unittest.skipIf(add_ansible_block is None, "Module not available")
    def test_add_ansible_block_empty_file(self):
        """Test adding Ansible block to empty file"""
        lines = []
        properties = {'server.port': '8080', 'app.name': 'test'}
        marker = 'TEST BLOCK'

        result_lines = add_ansible_block(lines, properties, marker)

        self.assertIn('# BEGIN TEST BLOCK\n', result_lines)
        self.assertIn('# END TEST BLOCK\n', result_lines)
        self.assertIn('server.port=8080\n', result_lines)
        self.assertIn('app.name=test\n', result_lines)

    @unittest.skipIf(add_ansible_block is None, "Module not available")
    def test_add_ansible_block_with_content(self):
        """Test adding Ansible block to file with existing content"""
        lines = ['existing.property=value\n']
        properties = {'server.port': '8080'}
        marker = 'TEST BLOCK'

        result_lines = add_ansible_block(lines, properties, marker)

        # Should add blank line before block
        self.assertEqual(result_lines[0], 'existing.property=value\n')
        self.assertEqual(result_lines[1], '\n')  # Blank line
        self.assertEqual(result_lines[2], '# BEGIN TEST BLOCK\n')

    @unittest.skipIf(add_ansible_block is None, "Module not available")
    def test_add_ansible_block_already_blank_line(self):
        """Test adding block when file already ends with blank line"""
        lines = ['existing.property=value\n', '\n']
        properties = {'server.port': '8080'}
        marker = 'TEST BLOCK'

        result_lines = add_ansible_block(lines, properties, marker)

        # Should not add extra blank line
        self.assertEqual(result_lines[0], 'existing.property=value\n')
        self.assertEqual(result_lines[1], '\n')  # Existing blank line
        self.assertEqual(result_lines[2], '# BEGIN TEST BLOCK\n')


class TestApplicationPropertiesIntegration(unittest.TestCase):
    """Integration tests for the full module workflow"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'application.properties')

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @unittest.skipIf(read_properties_file is None, "Module not available")
    def test_full_workflow(self):
        """Test the complete workflow of the module"""
        # Create initial properties file
        initial_content = '''# Application Configuration
server.port=9090
database.url=jdbc:mysql://old-host/olddb
app.name=old-app
other.setting=keep-this
'''
        with open(self.test_file, 'w') as f:
            f.write(initial_content)

        # New properties to apply
        new_properties = {
            'server.port': '8080',
            'database.url': 'jdbc:mysql://new-host/newdb',
            'app.version': '2.0.0'
        }
        marker = 'ANSIBLE MANAGED BLOCK - Application Properties'

        # Simulate the module workflow
        original_lines = read_properties_file(self.test_file)
        working_lines = original_lines.copy()

        # Comment existing properties
        working_lines, commented_count = comment_existing_properties(
            working_lines, new_properties, marker
        )

        # Remove any existing Ansible block
        working_lines = remove_existing_ansible_block(working_lines, marker)

        # Add new Ansible block
        working_lines = add_ansible_block(working_lines, new_properties, marker)

        # Write the result
        write_properties_file(self.test_file, working_lines)

        # Verify the result
        with open(self.test_file, 'r') as f:
            result_content = f.read()

        # Check that old properties were commented
        self.assertIn('# server.port=9090  # commented by ansible', result_content)
        self.assertIn('# database.url=jdbc:mysql://old-host/olddb  # commented by ansible', result_content)

        # Check that non-matching properties were preserved
        self.assertIn('other.setting=keep-this', result_content)

        # Check that new Ansible block was added
        self.assertIn('# BEGIN ANSIBLE MANAGED BLOCK - Application Properties', result_content)
        self.assertIn('server.port=8080', result_content)
        self.assertIn('database.url=jdbc:mysql://new-host/newdb', result_content)
        self.assertIn('app.version=2.0.0', result_content)
        self.assertIn('# END ANSIBLE MANAGED BLOCK - Application Properties', result_content)

        # Verify commented count
        self.assertEqual(commented_count, 2)


if __name__ == '__main__':
    unittest.main()
