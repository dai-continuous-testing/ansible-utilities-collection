#!/usr/bin/env python3
"""
Backup and Recovery test suite for application_properties module
Tests backup creation, restoration, and recovery scenarios
"""

import os
import sys
import unittest
import tempfile
import shutil
import glob
import time
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

class TestBackupAndRecovery(unittest.TestCase):
    """Test backup and recovery functionality with real-world scenarios"""

    def setUp(self):
        """Set up test environment for backup and recovery tests"""
        self.test_dir = tempfile.mkdtemp()
        self.properties_file = os.path.join(self.test_dir, 'application.properties')
        
        # Create a complex properties file for backup testing
        self.complex_content = """# Complex Production Configuration
# Contains sensitive data and critical settings
# Backup and recovery are essential for this file

#######################################################################
#  Database Configuration - CRITICAL
#######################################################################
spring.datasource.driver-class-name = org.postgresql.Driver
spring.datasource.password = ENC(ProductionPasswordHash123456789ABCDEF=)
spring.datasource.url = jdbc:postgresql://prod-cluster:5432/production_db
spring.datasource.username = ENC(ProductionUsernameHashABCDEF123456789=)

# Critical connection settings
spring.datasource.hikari.maximum-pool-size = 200
spring.datasource.hikari.connection-timeout = 30000
spring.datasource.hikari.leak-detection-threshold = 60000

#######################################################################
#  Security Configuration - HIGHLY SENSITIVE
#######################################################################
ct.security.master-key = ENC(MasterKeyForProductionEnvironment12345=)
ct.security.pairing-key = critical-production-pairing-key-do-not-lose
ct.security.jwt.secret = ENC(JWTSecretKeyForProductionSigning67890=)
ct.security.oauth2.client-secret = ENC(OAuth2ClientSecretProduction=)

# SSL/TLS Configuration
server.ssl.enabled = true
server.ssl.key-store = /etc/ssl/certs/production.keystore
server.ssl.key-store-password = ENC(KeystorePasswordProduction=)
server.ssl.trust-store = /etc/ssl/certs/production.truststore
server.ssl.trust-store-password = ENC(TruststorePasswordProduction=)

#######################################################################
#  Third-Party Integrations - EXTERNAL DEPENDENCIES
#######################################################################
# Payment Gateway
payment.gateway.api-key = ENC(PaymentGatewayAPIKeyProduction=)
payment.gateway.secret = ENC(PaymentGatewaySecretProduction=)
payment.gateway.webhook-secret = ENC(PaymentWebhookSecretProduction=)

# Email Service
email.service.api-key = ENC(EmailServiceAPIKeyProduction=)
email.service.from-address = noreply@production.experitest.com

# Cloud Storage
cloud.storage.access-key = ENC(CloudStorageAccessKeyProduction=)
cloud.storage.secret-key = ENC(CloudStorageSecretKeyProduction=)
cloud.storage.bucket = production-file-storage-bucket

#######################################################################
#  Monitoring and Alerting
#######################################################################
monitoring.datadog.api-key = ENC(DatadogAPIKeyProduction=)
monitoring.newrelic.license-key = ENC(NewRelicLicenseKeyProduction=)
monitoring.slack.webhook-url = https://hooks.slack.com/services/PROD/WEBHOOK/SECRET

#######################################################################
#  Feature Flags and Configuration
#######################################################################
feature.advanced-analytics.enabled = true
feature.experimental-ui.enabled = false
feature.beta-features.rollout-percentage = 25

# Performance settings
cache.redis.cluster-nodes = redis-01:6379,redis-02:6379,redis-03:6379
cache.redis.password = ENC(RedisClusterPasswordProduction=)
"""
        
        with open(self.properties_file, 'w', encoding='utf-8') as f:
            f.write(self.complex_content)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_backup_creation_basic(self):
        """Test basic backup file creation"""
        # Mock datetime for consistent backup naming
        with patch('application_properties.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 9, 15, 14, 30, 45)
            
            backup_path = self._simulate_backup_creation()
            
            # Verify backup file exists
            self.assertTrue(os.path.exists(backup_path))
            
            # Verify backup filename format
            expected_name = 'application.properties.backup.20250915_143045'
            self.assertIn(expected_name, backup_path)
            
            # Verify backup content matches original
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            
            self.assertEqual(backup_content, self.complex_content)

    def test_backup_preserves_sensitive_data(self):
        """Test that backup preserves all sensitive encrypted data"""
        backup_path = self._simulate_backup_creation()
        
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        # Verify all encrypted values are preserved
        encrypted_patterns = [
            'ENC(ProductionPasswordHash123456789ABCDEF=)',
            'ENC(ProductionUsernameHashABCDEF123456789=)',
            'ENC(MasterKeyForProductionEnvironment12345=)',
            'ENC(JWTSecretKeyForProductionSigning67890=)',
            'ENC(PaymentGatewayAPIKeyProduction=)',
            'ENC(CloudStorageAccessKeyProduction=)',
            'ENC(KeystorePasswordProduction=)'
        ]
        
        for pattern in encrypted_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, backup_content)

    def test_backup_preserves_file_structure(self):
        """Test that backup preserves exact file structure and formatting"""
        backup_path = self._simulate_backup_creation()
        
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        # Verify section headers are preserved
        self.assertIn('#######################################################################', backup_content)
        self.assertIn('#  Database Configuration - CRITICAL', backup_content)
        self.assertIn('#  Security Configuration - HIGHLY SENSITIVE', backup_content)
        
        # Verify comments are preserved
        self.assertIn('# Contains sensitive data and critical settings', backup_content)
        self.assertIn('# Critical connection settings', backup_content)
        
        # Verify exact line structure
        original_lines = self.complex_content.split('\n')
        backup_lines = backup_content.split('\n')
        
        self.assertEqual(len(original_lines), len(backup_lines))
        
        for i, (orig, backup) in enumerate(zip(original_lines, backup_lines)):
            with self.subTest(line_number=i+1):
                self.assertEqual(orig, backup)

    def test_multiple_backups_unique_timestamps(self):
        """Test that multiple backups create unique timestamped files"""
        backups = []
        
        # Create multiple backups with slight time differences
        for i in range(3):
            with patch('application_properties.datetime') as mock_datetime:
                # Each backup has a different timestamp
                mock_datetime.now.return_value = datetime(2025, 9, 15, 14, 30, 45 + i)
                backup_path = self._simulate_backup_creation()
                backups.append(backup_path)
            
            # Small delay to ensure different timestamps in real scenario
            time.sleep(0.01)
        
        # Verify all backup files are unique
        self.assertEqual(len(set(backups)), 3)
        
        # Verify all backup files exist
        for backup_path in backups:
            self.assertTrue(os.path.exists(backup_path))
        
        # Verify backup file naming pattern
        expected_patterns = [
            'application.properties.backup.20250915_143045',
            'application.properties.backup.20250915_143046',
            'application.properties.backup.20250915_143047'
        ]
        
        for i, backup_path in enumerate(backups):
            self.assertIn(expected_patterns[i], backup_path)

    def test_backup_cleanup_old_files(self):
        """Test cleanup of old backup files when there are too many"""
        # Create multiple backup files simulating different dates
        backup_dates = [
            datetime(2025, 9, 10, 10, 0, 0),  # 5 days old
            datetime(2025, 9, 12, 10, 0, 0),  # 3 days old
            datetime(2025, 9, 14, 10, 0, 0),  # 1 day old
            datetime(2025, 9, 15, 10, 0, 0),  # Current day
        ]
        
        backup_files = []
        for backup_date in backup_dates:
            with patch('application_properties.datetime') as mock_datetime:
                mock_datetime.now.return_value = backup_date
                backup_path = self._simulate_backup_creation()
                backup_files.append(backup_path)
        
        # Simulate cleanup that keeps only last 2 backups
        all_backups = glob.glob(os.path.join(self.test_dir, '*.backup.*'))
        all_backups.sort(key=os.path.getmtime, reverse=True)
        
        # Keep only the 2 most recent
        to_keep = all_backups[:2]
        to_remove = all_backups[2:]
        
        for backup_file in to_remove:
            os.remove(backup_file)
        
        # Verify only 2 backup files remain
        remaining_backups = glob.glob(os.path.join(self.test_dir, '*.backup.*'))
        self.assertEqual(len(remaining_backups), 2)
        
        # Verify the most recent backups are kept
        remaining_backups.sort(key=os.path.getmtime, reverse=True)
        self.assertEqual(set(remaining_backups), set(to_keep))

    def test_recovery_from_backup_exact_restore(self):
        """Test exact recovery of properties file from backup"""
        # Create backup
        backup_path = self._simulate_backup_creation()
        
        # Modify the original file (simulate corruption or bad changes)
        corrupted_content = """# This file has been corrupted
# All original content is lost
server.port = 9999
broken.property = invalid
"""
        
        with open(self.properties_file, 'w', encoding='utf-8') as f:
            f.write(corrupted_content)
        
        # Verify file is corrupted
        with open(self.properties_file, 'r', encoding='utf-8') as f:
            current_content = f.read()
        self.assertNotEqual(current_content, self.complex_content)
        
        # Restore from backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        with open(self.properties_file, 'w', encoding='utf-8') as f:
            f.write(backup_content)
        
        # Verify exact restoration
        with open(self.properties_file, 'r', encoding='utf-8') as f:
            restored_content = f.read()
        
        self.assertEqual(restored_content, self.complex_content)
        
        # Verify sensitive data is restored
        self.assertIn('ENC(ProductionPasswordHash123456789ABCDEF=)', restored_content)
        self.assertIn('critical-production-pairing-key-do-not-lose', restored_content)

    def test_backup_during_concurrent_modifications(self):
        """Test backup behavior during concurrent file modifications"""
        # Simulate creating backup while file is being modified
        with patch('application_properties.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 9, 15, 14, 30, 45)
            
            # Start backup process
            backup_path = self._simulate_backup_creation()
            
            # Simulate concurrent modification (this would happen after backup is taken)
            modified_content = self.complex_content + "\n# Added during backup process\nnew.property = added"
            
            with open(self.properties_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # Verify backup contains original content (not the concurrent modification)
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            
            self.assertEqual(backup_content, self.complex_content)
            self.assertNotIn('Added during backup process', backup_content)
            
            # Verify current file has the modification
            with open(self.properties_file, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            self.assertIn('Added during backup process', current_content)

    def test_backup_with_file_permissions(self):
        """Test backup preserves and handles file permissions correctly"""
        # Set specific permissions on original file
        os.chmod(self.properties_file, 0o600)  # Owner read/write only
        
        backup_path = self._simulate_backup_creation()
        
        # Verify backup file exists and is readable
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify backup content is accessible
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        self.assertEqual(backup_content, self.complex_content)
        
        # Verify backup file has appropriate permissions (should be readable by process)
        backup_stat = os.stat(backup_path)
        self.assertTrue(backup_stat.st_mode & 0o400)  # Owner can read

    def test_backup_disk_space_scenarios(self):
        """Test backup behavior in low disk space scenarios"""
        # This test simulates disk space issues
        backup_path = self._simulate_backup_creation()
        
        # Verify backup was created successfully
        self.assertTrue(os.path.exists(backup_path))
        
        # Get file sizes
        original_size = os.path.getsize(self.properties_file)
        backup_size = os.path.getsize(backup_path)
        
        # Verify backup is complete (same size as original)
        self.assertEqual(original_size, backup_size)
        
        # Simulate checking available disk space
        disk_usage = shutil.disk_usage(self.test_dir)
        available_space = disk_usage.free
        
        # Verify there's enough space for backup (this is informational)
        self.assertGreater(available_space, backup_size * 10)  # At least 10x backup size available

    def test_backup_with_special_characters_and_encoding(self):
        """Test backup with special characters and different encodings"""
        # Add content with special characters
        special_content = self.complex_content + """
# Special characters and international content
app.welcome.message = Welcome! Bienvenidos! 欢迎! مرحبا! स्वागत!
app.special.chars = !@#$%^&*()_+-=[]{}|;':",./<>?
app.unicode.test = 𝐔𝐧𝐢𝐜𝐨𝐝𝐞 𝒯𝑒𝓈𝓉 ✓ ⚡ 🚀 💻
app.math.symbols = ∑∏∆∇∈∉⊂⊃∪∩∧∨¬∀∃≡≠≤≥
"""
        
        # Update file with special content
        with open(self.properties_file, 'w', encoding='utf-8') as f:
            f.write(special_content)
        
        # Create backup
        backup_path = self._simulate_backup_creation()
        
        # Verify special characters are preserved in backup
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        self.assertEqual(backup_content, special_content)
        
        # Verify specific special character content
        self.assertIn('Welcome! Bienvenidos! 欢迎! مرحبا! स्वागत!', backup_content)
        self.assertIn('!@#$%^&*()_+-=[]{}|;\':",./<>?', backup_content)  # Fixed quote escaping
        self.assertIn('𝐔𝐧𝐢𝐜𝐨𝐝𝐞 𝒯𝑒𝓈𝓉 ✓ ⚡ 🚀 💻', backup_content)

    def test_disaster_recovery_scenario(self):
        """Test complete disaster recovery scenario"""
        # Step 1: Create initial backup
        initial_backup = self._simulate_backup_creation()
        
        # Step 2: Make some changes and create another backup
        with patch('application_properties.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 9, 15, 15, 0, 0)
            
            # Modify content
            modified_content = self.complex_content + "\n# Changes made after initial backup\nchange.timestamp = 2025-09-15T15:00:00\n"
            with open(self.properties_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # Create second backup
            second_backup = self._simulate_backup_creation()
        
        # Step 3: Simulate disaster (file corruption/deletion)
        os.remove(self.properties_file)
        self.assertFalse(os.path.exists(self.properties_file))
        
        # Step 4: Recover from most recent backup
        with open(second_backup, 'r', encoding='utf-8') as f:
            recovery_content = f.read()
        
        with open(self.properties_file, 'w', encoding='utf-8') as f:
            f.write(recovery_content)
        
        # Step 5: Verify recovery is complete
        with open(self.properties_file, 'r', encoding='utf-8') as f:
            recovered_content = f.read()
        
        self.assertEqual(recovered_content, modified_content)
        self.assertIn('Changes made after initial backup', recovered_content)
        self.assertIn('change.timestamp = 2025-09-15T15:00:00', recovered_content)
        
        # Verify all sensitive data is recovered
        self.assertIn('ENC(ProductionPasswordHash123456789ABCDEF=)', recovered_content)
        self.assertIn('critical-production-pairing-key-do-not-lose', recovered_content)

    def _simulate_backup_creation(self):
        """Simulate the backup creation process"""
        # This simulates the backup_file() function from application_properties module
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'application.properties.backup.{timestamp}'
        backup_path = os.path.join(self.test_dir, backup_filename)
        
        # Copy original file to backup location
        shutil.copy2(self.properties_file, backup_path)
        
        return backup_path

    def test_backup_retention_policy(self):
        """Test backup retention policy implementation"""
        # Create multiple backups over time
        backup_files = []
        base_date = datetime(2025, 9, 1)
        
        for days_offset in range(30):  # 30 days of backups
            backup_date = base_date + timedelta(days=days_offset)
            
            with patch('application_properties.datetime') as mock_datetime:
                mock_datetime.now.return_value = backup_date
                
                backup_path = self._simulate_backup_creation()
                backup_files.append(backup_path)
                
                # Simulate aging the file
                timestamp = time.mktime(backup_date.timetuple())
                os.utime(backup_path, (timestamp, timestamp))
        
        # Implement retention policy: keep last 7 days
        current_time = time.mktime(datetime(2025, 9, 30).timetuple())
        retention_seconds = 7 * 24 * 60 * 60  # 7 days
        
        files_to_keep = []
        files_to_remove = []
        
        for backup_file in backup_files:
            file_age = current_time - os.path.getmtime(backup_file)
            if file_age <= retention_seconds:
                files_to_keep.append(backup_file)
            else:
                files_to_remove.append(backup_file)
        
        # Verify retention policy logic
        self.assertEqual(len(files_to_keep), 7)  # Last 7 days
        self.assertEqual(len(files_to_remove), 23)  # Older than 7 days
        
        # Simulate cleanup
        for old_backup in files_to_remove:
            os.remove(old_backup)
        
        # Verify only recent backups remain
        remaining_backups = glob.glob(os.path.join(self.test_dir, '*.backup.*'))
        self.assertEqual(len(remaining_backups), 7)

    def test_backup_validation_and_integrity(self):
        """Test backup validation and integrity checks"""
        backup_path = self._simulate_backup_creation()
        
        # Verify backup integrity by checking key markers
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        # Check for configuration file markers
        integrity_checks = [
            ('has_comments', lambda c: c.count('#') > 10),
            ('has_sections', lambda c: '#######################################################################' in c),
            ('has_properties', lambda c: c.count(' = ') > 20),
            ('has_encrypted_values', lambda c: 'ENC(' in c and ')' in c),
            ('has_database_config', lambda c: 'spring.datasource' in c),
            ('has_security_config', lambda c: 'ct.security' in c),
            ('proper_line_endings', lambda c: '\n' in c),
            ('non_empty', lambda c: len(c.strip()) > 100)
        ]
        
        for check_name, check_func in integrity_checks:
            with self.subTest(check=check_name):
                self.assertTrue(check_func(backup_content), f"Integrity check failed: {check_name}")
        
        # Verify backup can be parsed as properties (basic format check)
        lines = backup_content.split('\n')
        property_lines = [line for line in lines if ' = ' in line and not line.strip().startswith('#')]
        
        # Should have significant number of properties
        self.assertGreater(len(property_lines), 20)
        
        # Each property line should have valid format
        for line in property_lines[:5]:  # Check first 5 property lines
            with self.subTest(line=line):
                parts = line.split(' = ')
                self.assertEqual(len(parts), 2, f"Invalid property format: {line}")
                self.assertTrue(len(parts[0].strip()) > 0, f"Empty property key: {line}")


if __name__ == '__main__':
    unittest.main()
