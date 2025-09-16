#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import sys
import os

# Add the plugins directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../../plugins/filter'))

from os_utils import FilterModule as OSUtilsFilterModule
from string_utils import FilterModule as StringUtilsFilterModule
from version_utils import FilterModule as VersionUtilsFilterModule


class TestOSUtilsFilters:
    """Test OS utilities filters"""
    
    def setup_method(self):
        self.filter_module = OSUtilsFilterModule()
        self.filters = self.filter_module.filters()
    
    def test_os_family_to_os_type(self):
        """Test OS family to OS type conversion"""
        assert self.filters['os_family_to_os_type']('RedHat') == 'linux'
        assert self.filters['os_family_to_os_type']('Debian') == 'linux'
        assert self.filters['os_family_to_os_type']('Ubuntu') == 'linux'
        assert self.filters['os_family_to_os_type']('Darwin') == 'darwin'
        assert self.filters['os_family_to_os_type']('Windows') == 'windows'
        
        # Test case insensitivity
        assert self.filters['os_family_to_os_type']('redhat') == 'linux'
        assert self.filters['os_family_to_os_type']('WINDOWS') == 'windows'
    
    def test_os_family_to_os_type_invalid(self):
        """Test invalid OS family"""
        with pytest.raises(KeyError):
            self.filters['os_family_to_os_type']('InvalidOS')
    
    def test_normalize_os_family(self):
        """Test OS family normalization"""
        assert self.filters['normalize_os_family']('redhat') == 'RedHat'
        assert self.filters['normalize_os_family']('centos') == 'RedHat'
        assert self.filters['normalize_os_family']('ubuntu') == 'Debian'
        assert self.filters['normalize_os_family']('macos') == 'Darwin'
    
    def test_is_linux_family(self):
        """Test Linux family detection"""
        assert self.filters['is_linux_family']('RedHat') is True
        assert self.filters['is_linux_family']('Debian') is True
        assert self.filters['is_linux_family']('Ubuntu') is True
        assert self.filters['is_linux_family']('Darwin') is False
        assert self.filters['is_linux_family']('Windows') is False
    
    def test_is_windows_family(self):
        """Test Windows family detection"""
        assert self.filters['is_windows_family']('Windows') is True
        assert self.filters['is_windows_family']('RedHat') is False
        assert self.filters['is_windows_family']('Darwin') is False
    
    def test_is_darwin_family(self):
        """Test Darwin family detection"""
        assert self.filters['is_darwin_family']('Darwin') is True
        assert self.filters['is_darwin_family']('RedHat') is False
        assert self.filters['is_darwin_family']('Windows') is False


class TestStringUtilsFilters:
    """Test string utilities filters"""
    
    def setup_method(self):
        self.filter_module = StringUtilsFilterModule()
        self.filters = self.filter_module.filters()
    
    def test_safe_key(self):
        """Test safe key generation"""
        assert self.filters['safe_key']('My Application Name!') == 'my_application_name'
        assert self.filters['safe_key']('test-123_value') == 'test_123_value'
        assert self.filters['safe_key']('!!!') == 'default'
        assert self.filters['safe_key']('') == 'default'
    
    def test_safe_filename(self):
        """Test safe filename generation"""
        assert self.filters['safe_filename']('file<>name.txt') == 'filename.txt'
        assert self.filters['safe_filename']('path/to/file') == 'pathtofile'
        assert self.filters['safe_filename']('') == 'file'
    
    def test_slugify(self):
        """Test slugification"""
        assert self.filters['slugify']('My Great Title!') == 'my-great-title'
        assert self.filters['slugify']('Test   123') == 'test-123'
        assert self.filters['slugify']('') == 'item'
    
    def test_parse_url(self):
        """Test URL parsing"""
        result = self.filters['parse_url']('https://example.com:8080/path?param=value')
        assert result['scheme'] == 'https'
        assert result['hostname'] == 'example.com'
        assert result['port'] == 8080
        assert result['path'] == '/path'
        assert result['query'] == 'param=value'
    
    def test_template_string(self):
        """Test string templating"""
        template = 'Hello {name}, you have {count} messages'
        variables = {'name': 'John', 'count': 5}
        result = self.filters['template_string'](template, variables)
        assert result == 'Hello John, you have 5 messages'
    
    def test_join_path(self):
        """Test path joining"""
        assert self.filters['join_path'](['/opt', 'experitest', 'app']) == '/opt/experitest/app'
        assert self.filters['join_path'](['', 'path', '', 'to', 'file']) == 'path/to/file'
    
    def test_ensure_prefix(self):
        """Test prefix ensuring"""
        assert self.filters['ensure_prefix']('test', 'pre-') == 'pre-test'
        assert self.filters['ensure_prefix']('pre-test', 'pre-') == 'pre-test'
    
    def test_ensure_suffix(self):
        """Test suffix ensuring"""
        assert self.filters['ensure_suffix']('test', '.txt') == 'test.txt'
        assert self.filters['ensure_suffix']('test.txt', '.txt') == 'test.txt'
    
    def test_remove_prefix(self):
        """Test prefix removal"""
        assert self.filters['remove_prefix']('pre-test', 'pre-') == 'test'
        assert self.filters['remove_prefix']('test', 'pre-') == 'test'
    
    def test_remove_suffix(self):
        """Test suffix removal"""
        assert self.filters['remove_suffix']('test.txt', '.txt') == 'test'
        assert self.filters['remove_suffix']('test', '.txt') == 'test'
    
    def test_camel_to_snake(self):
        """Test camelCase to snake_case conversion"""
        assert self.filters['camel_to_snake']('myVariableName') == 'my_variable_name'
        assert self.filters['camel_to_snake']('HTTPSConnection') == 'h_t_t_p_s_connection'
    
    def test_snake_to_camel(self):
        """Test snake_case to camelCase conversion"""
        assert self.filters['snake_to_camel']('my_variable_name') == 'myVariableName'
        assert self.filters['snake_to_camel']('my_variable_name', True) == 'MyVariableName'
    
    def test_truncate_smart(self):
        """Test smart truncation"""
        text = 'This is a long sentence that needs truncation'
        result = self.filters['truncate_smart'](text, 20)
        assert len(result) <= 20
        assert result.endswith('...')
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization"""
        assert self.filters['normalize_whitespace']('  test   value  ') == 'test value'
        assert self.filters['normalize_whitespace']('test\n\tvalue') == 'test value'
    
    def test_extract_numbers(self):
        """Test number extraction"""
        result = self.filters['extract_numbers']('test 123 and 45.6 values')
        assert result == [123, 45.6]
    
    def test_mask_sensitive(self):
        """Test sensitive data masking"""
        result = self.filters['mask_sensitive']('secretpassword123', '*', 4)
        assert len(result) == len('secretpassword123')
        assert result.count('*') > 0


class TestVersionUtilsFilters:
    """Test version utilities filters"""
    
    def setup_method(self):
        self.filter_module = VersionUtilsFilterModule()
        self.filters = self.filter_module.filters()
    
    def test_version_compare(self):
        """Test version comparison"""
        assert self.filters['version_compare']('1.2.3', '1.2.4', '<') is True
        assert self.filters['version_compare']('1.2.3', '1.2.3', '==') is True
        assert self.filters['version_compare']('1.2.4', '1.2.3', '>') is True
        assert self.filters['version_compare']('2.0.0', '1.9.9', '>=') is True
    
    def test_parse_version(self):
        """Test version parsing"""
        result = self.filters['parse_version']('2.1.3-beta.1+build.123')
        assert result['major'] == 2
        assert result['minor'] == 1
        assert result['patch'] == 3
        assert result['prerelease'] == 'beta.1'
        assert result['build'] == 'build.123'
        assert result['is_semver'] is True
    
    def test_normalize_version(self):
        """Test version normalization"""
        assert self.filters['normalize_version']('v1.2.3') == '1.2.3'
        assert self.filters['normalize_version']('1.2.3-beta+build') == '1.2.3-beta+build'
    
    def test_is_stable_version(self):
        """Test stable version detection"""
        assert self.filters['is_stable_version']('1.2.3') is True
        assert self.filters['is_stable_version']('1.2.3-beta') is False
        assert self.filters['is_stable_version']('1.2.3-alpha.1') is False
    
    def test_bump_version(self):
        """Test version bumping"""
        assert self.filters['bump_version']('1.2.3', 'major') == '2.0.0'
        assert self.filters['bump_version']('1.2.3', 'minor') == '1.3.0'
        assert self.filters['bump_version']('1.2.3', 'patch') == '1.2.4'
    
    def test_version_in_range(self):
        """Test version range checking"""
        assert self.filters['version_in_range']('1.5.0', '>=1.0.0,<2.0.0') is True
        assert self.filters['version_in_range']('2.0.0', '>=1.0.0,<2.0.0') is False
        assert self.filters['version_in_range']('0.9.0', '>=1.0.0,<2.0.0') is False
    
    def test_extract_version(self):
        """Test version extraction"""
        assert self.filters['extract_version']('version: 1.2.3') == '1.2.3'
        assert self.filters['extract_version']('v2.1.0-beta') == '2.1.0-beta'
        assert self.filters['extract_version']('no version here') is None
    
    def test_sort_versions(self):
        """Test version sorting"""
        versions = ['1.2.3', '1.10.0', '2.0.0', '1.2.10']
        sorted_versions = self.filters['sort_versions'](versions)
        assert sorted_versions == ['1.2.3', '1.2.10', '1.10.0', '2.0.0']
    
    def test_latest_version(self):
        """Test latest version selection"""
        versions = ['1.2.3', '1.10.0', '2.0.0', '1.2.10']
        assert self.filters['latest_version'](versions) == '2.0.0'
    
    def test_get_version_parts(self):
        """Test getting version parts"""
        assert self.filters['get_major_version']('1.2.3') == 1
        assert self.filters['get_minor_version']('1.2.3') == 2
        assert self.filters['get_patch_version']('1.2.3') == 3


if __name__ == '__main__':
    pytest.main([__file__])
