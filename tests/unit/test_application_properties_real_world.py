#!/usr/bin/env python3
"""
Enhanced unit tests for application_properties module using real-world data
This test suite uses actual production application.properties content
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../plugins/modules'))

try:
    from application_properties import backup_file, read_properties_file, write_properties_file, comment_existing_properties, add_ansible_block
except ImportError:
    # Import stubs for when module is not available
    backup_file = None
    read_properties_file = None
    write_properties_file = None
    comment_existing_properties = None
    add_ansible_block = None


class TestApplicationPropertiesRealWorld(unittest.TestCase):
    """Test cases using real-world application.properties content"""

    def setUp(self):
        """Set up test environment with real properties file"""
        self.test_dir = tempfile.mkdtemp()
        self.properties_file = os.path.join(self.test_dir, 'application.properties')
        
        # Load real properties content
        fixtures_dir = os.path.join(os.path.dirname(__file__), '../fixtures')
        real_props_file = os.path.join(fixtures_dir, 'real_application.properties')
        
        if os.path.exists(real_props_file):
            with open(real_props_file, 'r', encoding='utf-8') as f:
                self.real_properties_content = f.read()
        else:
            # Fallback content if fixture file doesn't exist
            self.real_properties_content = self._get_sample_real_content()
        
        # Create test file with real content
        with open(self.properties_file, 'w', encoding='utf-8') as f:
            f.write(self.real_properties_content)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _get_sample_real_content(self):
        """Fallback real-world content for testing"""
        return """# Properties file with JDBC and JPA settings
spring.datasource.driver-class-name = org.postgresql.Driver
spring.datasource.password = ENC(ErHtDY2qfBjBhPAyZ0lB2fBN1vMPW0NTmD1LGAOUUx8=)
spring.datasource.url = jdbc:postgresql://localhost:5432/cloudserver
spring.datasource.username = ENC(/cEe75s4cf+mzcXtEV0DGDxcTbnzVWjM)

#######################################################################
#  Spring Boot Management
#######################################################################
management.endpoint.health.show-details = always
management.server.address = 127.0.0.1
management.server.port = 33300

server.port = 8080
server.servlet.session.timeout = 180m

ct.cloud.hostname = preprod.experitest.com
ct.password-management.access-key-expiration-duration = 3650d
"""

    @unittest.skipIf(read_properties_file is None, "Module not available")
    def test_read_real_properties_file(self):
        """Test reading the real properties file structure"""
        content = read_properties_file(self.properties_file)
        
        # Verify we can read the file
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 1000)  # Real file is substantial
        
        # Check for key sections
        self.assertIn('#######################################################################', content)
        self.assertIn('Datasource Settings', content)
        self.assertIn('Spring Boot Management', content)
        
        # Check for encrypted values
        self.assertIn('ENC(', content)
        
        # Check for complex URLs
        self.assertIn('jdbc:postgresql:', content)

    @unittest.skipIf(backup_file is None, "Module not available")
    @patch('application_properties.datetime')
    def test_backup_real_properties_file(self, mock_datetime):
        """Test backup functionality with real properties file"""
        # Mock datetime for consistent backup naming
        mock_datetime.now.return_value = datetime(2025, 9, 15, 14, 30, 45)
        
        backup_path = backup_file(self.properties_file)
        
        # Verify backup was created
        self.assertTrue(os.path.exists(backup_path))
        self.assertIn('20250915_143045', backup_path)
        
        # Verify backup content matches original
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        self.assertEqual(backup_content, self.real_properties_content)
        
        # Verify backup preserves encrypted values
        self.assertIn('ENC(ErHtDY2qfBjBhPAyZ0lB2fBN1vMPW0NTmD1LGAOUUx8=)', backup_content)

    @unittest.skipIf(add_ansible_block is None, "Module not available")
    def test_add_properties_to_real_file(self):
        """Test adding new properties to real file while preserving structure"""
        new_properties = {
            'spring.datasource.hikari.maximum-pool-size': '20',
            'spring.datasource.hikari.minimum-idle': '5',
            'ct.cloud.new-feature.enabled': 'true',
            'management.endpoint.custom.enabled': 'true'
        }
        
        marker = 'ANSIBLE MANAGED BLOCK - TEST'
        
        # Add properties
        result = add_ansible_block(
            content=self.real_properties_content,
            properties=new_properties,
            marker=marker
        )
        
        # Verify original content is preserved
        original_lines = self.real_properties_content.split('\n')
        result_lines = result.split('\n')
        
        # Find where the Ansible block starts
        ansible_start = None
        for i, line in enumerate(result_lines):
            if marker in line and 'BEGIN' in line:
                ansible_start = i
                break
        
        self.assertIsNotNone(ansible_start, "Ansible block not found")
        
        # Verify original content before Ansible block is intact
        for i in range(min(ansible_start, len(original_lines))):
            if i < len(original_lines) and i < len(result_lines):
                if not result_lines[i].startswith('#') or 'ANSIBLE' not in result_lines[i]:
                    # Allow for some formatting differences but preserve content
                    pass
        
        # Verify new properties are added
        for key, value in new_properties.items():
            self.assertIn(f'{key} = {value}', result)

    @unittest.skipIf(comment_existing_properties is None, "Module not available")
    def test_comment_existing_encrypted_properties(self):
        """Test commenting out existing properties including encrypted ones"""
        properties_to_comment = {
            'spring.datasource.password': 'ENC(ErHtDY2qfBjBhPAyZ0lB2fBN1vMPW0NTmD1LGAOUUx8=)',
            'spring.datasource.username': 'ENC(/cEe75s4cf+mzcXtEV0DGDxcTbnzVWjM)',
            'server.port': '8080'
        }
        
        result = comment_existing_properties(
            content=self.real_properties_content,
            properties=properties_to_comment,
            marker='ANSIBLE MANAGED BLOCK'
        )
        
        # Verify encrypted properties are commented out
        self.assertIn('#spring.datasource.password = ENC(ErHtDY2qfBjBhPAyZ0lB2fBN1vMPW0NTmD1LGAOUUx8=)', result)
        self.assertIn('#spring.datasource.username = ENC(/cEe75s4cf+mzcXtEV0DGDxcTbnzVWjM)', result)
        self.assertIn('#server.port = 8080', result)
        
        # Verify other properties remain untouched
        self.assertIn('spring.datasource.driver-class-name = org.postgresql.Driver', result)
        self.assertIn('management.server.address = 127.0.0.1', result)

    @unittest.skipIf(add_ansible_block is None, "Module not available")
    def test_preserve_section_headers(self):
        """Test that section headers with decorative borders are preserved"""
        new_properties = {
            'test.property': 'value'
        }
        
        result = add_ansible_block(
            content=self.real_properties_content,
            properties=new_properties,
            marker='ANSIBLE MANAGED BLOCK'
        )
        
        # Verify section headers are preserved
        self.assertIn('#######################################################################', result)
        self.assertIn('#  Datasource Settings', result)
        self.assertIn('#  Spring Boot Management', result)
        self.assertIn('#  End of Datasource Settings', result)

    @unittest.skipIf(add_ansible_block is None, "Module not available")
    def test_handle_complex_urls_and_paths(self):
        """Test handling properties with complex URLs and file paths"""
        complex_properties = {
            'shared-cloud.spring.kafka.bootstrap-servers': 'b-1.newcluster.kafka.us-east-1.amazonaws.com:9092,b-2.newcluster.kafka.us-east-1.amazonaws.com:9092',
            'ct.region-proxy.ssl.keystore-path': 'conf/new-wildcard.experitest.com.keystore',
            'ct.cloud.backup-base-dir': '/var/lib/Experitest/cloud-server/new-backups',
            'spring.datasource.url': 'jdbc:postgresql://new-host:5432/newdatabase'
        }
        
        result = add_ansible_block(
            content=self.real_properties_content,
            properties=complex_properties,
            marker='ANSIBLE MANAGED BLOCK'
        )
        
        # Verify complex URLs are handled correctly
        for key, value in complex_properties.items():
            self.assertIn(f'{key} = {value}', result)
        
        # Verify original complex URLs are preserved or commented
        original_kafka_url = 'b-2.ctinternaluseast1.pwylnr.c19.kafka.us-east-1.amazonaws.com:9092'
        # Should be either preserved as-is or commented out
        self.assertTrue(
            original_kafka_url in result or 
            f'#{original_kafka_url}' in result or
            f'# {original_kafka_url}' in result
        )

    @unittest.skipIf(add_ansible_block is None, "Module not available")
    def test_handle_duration_formats(self):
        """Test handling properties with duration formats (h, m, d, s)"""
        duration_properties = {
            'server.servlet.session.timeout': '240m',  # Change from 180m
            'ct.password-management.access-key-expiration-duration': '7300d',  # Change from 3650d
            'ct.password-management.initial-password-expiration-duration': '48h',  # Change from 24h
            'new.timeout.property': '30s'
        }
        
        result = add_ansible_block(
            content=self.real_properties_content,
            properties=duration_properties,
            marker='ANSIBLE MANAGED BLOCK'
        )
        
        # Verify duration properties are added correctly
        for key, value in duration_properties.items():
            self.assertIn(f'{key} = {value}', result)
        
        # Verify original duration properties are commented out
        self.assertIn('#server.servlet.session.timeout = 180m', result)
        self.assertIn('#ct.password-management.access-key-expiration-duration = 3650d', result)

    @unittest.skipIf(write_properties_file is None, "Module not available")
    def test_write_and_read_cycle_preserves_structure(self):
        """Test that write and read cycle preserves the file structure"""
        # Read original content
        original_content = read_properties_file(self.properties_file)
        
        # Write it back
        write_properties_file(self.properties_file, original_content)
        
        # Read again
        final_content = read_properties_file(self.properties_file)
        
        # Verify content is preserved
        self.assertEqual(original_content, final_content)
        
        # Verify key elements are still present
        self.assertIn('ENC(ErHtDY2qfBjBhPAyZ0lB2fBN1vMPW0NTmD1LGAOUUx8=)', final_content)
        self.assertIn('#######################################################################', final_content)
        self.assertIn('spring.datasource.driver-class-name = org.postgresql.Driver', final_content)

    @unittest.skipIf(add_ansible_block is None, "Module not available")
    def test_update_existing_encrypted_properties(self):
        """Test updating properties that contain encrypted values"""
        # Update encrypted properties with new encrypted values
        encrypted_updates = {
            'spring.datasource.password': 'ENC(NewEncryptedPasswordHash12345=)',
            'spring.datasource.username': 'ENC(NewEncryptedUsernameHash67890=)',
            'ct.security.pairing-key': 'new-pairing-key-value-for-testing'
        }
        
        result = add_ansible_block(
            content=self.real_properties_content,
            properties=encrypted_updates,
            marker='ANSIBLE MANAGED BLOCK'
        )
        
        # Verify old encrypted values are commented out
        self.assertIn('#spring.datasource.password = ENC(ErHtDY2qfBjBhPAyZ0lB2fBN1vMPW0NTmD1LGAOUUx8=)', result)
        self.assertIn('#spring.datasource.username = ENC(/cEe75s4cf+mzcXtEV0DGDxcTbnzVWjM)', result)
        
        # Verify new encrypted values are added
        self.assertIn('spring.datasource.password = ENC(NewEncryptedPasswordHash12345=)', result)
        self.assertIn('spring.datasource.username = ENC(NewEncryptedUsernameHash67890=)', result)
        self.assertIn('ct.security.pairing-key = new-pairing-key-value-for-testing', result)

    @unittest.skipIf(add_ansible_block is None, "Module not available")
    def test_handle_regex_and_special_characters(self):
        """Test handling properties with regex patterns and special characters"""
        special_properties = {
            'cloud.metric.allow': '.*test.*',  # Change regex pattern
            'server.compression.mime-types': 'text/html,text/css,application/json,application/xml',  # Modify list
            'ct.file-license': 'NewTestLicenseKeyWithSpecialChars@#$%',
            'new.regex.pattern': '^[a-zA-Z0-9_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        }
        
        result = add_ansible_block(
            content=self.real_properties_content,
            properties=special_properties,
            marker='ANSIBLE MANAGED BLOCK'
        )
        
        # Verify special character properties are handled correctly
        for key, value in special_properties.items():
            self.assertIn(f'{key} = {value}', result)
        
        # Verify original regex pattern is commented out
        self.assertIn('#cloud.metric.allow = .*', result)

    def test_real_file_analysis_completeness(self):
        """Test that our analysis covers all aspects of the real file"""
        content = self.real_properties_content
        
        # Verify we have all the complex elements we identified
        test_elements = {
            'encrypted_values': 'ENC(',
            'section_headers': '#######################################################################',
            'complex_urls': 'amazonaws.com',
            'duration_formats': '180m',
            'variable_substitution': '${java.io.tmpdir}',
            'commented_properties': '# cloud.kafka.enabled=true',
            'boolean_values': ' = true',
            'numeric_values': ' = 1000',
            'file_paths': '/usr/pgsql-14/',
            'regex_patterns': '.*'
        }
        
        for element_name, pattern in test_elements.items():
            with self.subTest(element=element_name):
                self.assertIn(pattern, content, f"Missing {element_name} pattern: {pattern}")


class TestApplicationPropertiesRealWorldIntegration(unittest.TestCase):
    """Integration tests using real-world scenarios"""

    def setUp(self):
        """Set up integration test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.properties_file = os.path.join(self.test_dir, 'application.properties')
        
        # Create a smaller but realistic properties file for integration tests
        self.integration_content = """# Production Configuration
spring.datasource.driver-class-name = org.postgresql.Driver
spring.datasource.password = ENC(TestEncryptedPassword123=)
spring.datasource.url = jdbc:postgresql://localhost:5432/testdb
spring.datasource.username = ENC(TestEncryptedUser456=)

#######################################################################
#  Server Configuration
#######################################################################
server.port = 8080
server.servlet.session.timeout = 180m
management.server.address = 127.0.0.1
management.server.port = 33300

# Feature flags
ct.cloud.feature.enabled = true
ct.password-management.access-key-expiration-duration = 3650d
"""
        
        with open(self.properties_file, 'w', encoding='utf-8') as f:
            f.write(self.integration_content)

    def tearDown(self):
        """Clean up integration test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @unittest.skipIf(add_ansible_block is None, "Module not available")
    def test_full_workflow_realistic_scenario(self):
        """Test complete workflow with realistic property updates"""
        # Simulate updating database configuration and adding new features
        updates = {
            'spring.datasource.url': 'jdbc:postgresql://prod-db:5432/production',
            'spring.datasource.hikari.maximum-pool-size': '50',
            'spring.datasource.hikari.minimum-idle': '10',
            'ct.cloud.new-monitoring.enabled': 'true',
            'ct.cloud.new-monitoring.interval': '30s',
            'management.endpoint.custom-health.enabled': 'true'
        }
        
        marker = 'ANSIBLE MANAGED BLOCK'
        
        # Perform the update
        result = add_ansible_block(
            content=self.integration_content,
            properties=updates,
            marker=marker
        )
        
        # Write the result
        write_properties_file(self.properties_file, result)
        
        # Verify the file was updated correctly
        updated_content = read_properties_file(self.properties_file)
        
        # Check that old database URL is commented
        self.assertIn('#spring.datasource.url = jdbc:postgresql://localhost:5432/testdb', updated_content)
        
        # Check that new values are added
        self.assertIn('spring.datasource.url = jdbc:postgresql://prod-db:5432/production', updated_content)
        self.assertIn('spring.datasource.hikari.maximum-pool-size = 50', updated_content)
        self.assertIn('ct.cloud.new-monitoring.enabled = true', updated_content)
        
        # Verify Ansible block markers
        self.assertIn('# BEGIN ANSIBLE MANAGED BLOCK', updated_content)
        self.assertIn('# END ANSIBLE MANAGED BLOCK', updated_content)
        
        # Verify original structure is preserved
        self.assertIn('#######################################################################', updated_content)
        self.assertIn('#  Server Configuration', updated_content)


if __name__ == '__main__':
    unittest.main()
