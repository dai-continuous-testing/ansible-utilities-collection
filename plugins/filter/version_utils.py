#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, DAI Continuous Testing
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
from packaging import version

DOCUMENTATION = '''
---
name: version_utils
short_description: Version comparison and manipulation utilities
description:
  - Provides version comparison and manipulation functions
  - Supports semantic versioning (SemVer) and custom version schemes
  - Useful for deployment logic and compatibility checks
version_added: "1.0.0"
author:
  - DAI Continuous Testing
'''

EXAMPLES = '''
# Version comparison
- debug:
    msg: "Upgrade needed"
  when: "'1.2.3' | dai_continuous_testing.utilities.version_compare('1.2.5', '<')"

# Parse version components
- set_fact:
    version_info: "{{ '2.1.3-beta.1+build.123' | dai_continuous_testing.utilities.parse_version }}"
  # Returns: {"major": 2, "minor": 1, "patch": 3, "prerelease": "beta.1", "build": "build.123"}

# Check if version is stable
- debug:
    msg: "This is a stable release"
  when: "'1.2.3' | dai_continuous_testing.utilities.is_stable_version"

# Get next version
- set_fact:
    next_patch: "{{ '1.2.3' | dai_continuous_testing.utilities.bump_version('patch') }}"
  # Returns: 1.2.4

# Version range checking
- debug:
    msg: "Version is compatible"
  when: "'2.1.5' | dai_continuous_testing.utilities.version_in_range('>=2.0.0,<3.0.0')"
'''


class FilterModule(object):
    """Version utilities filter plugin"""
    
    def filters(self):
        return {
            'version_compare': self.version_compare,
            'parse_version': self.parse_version,
            'normalize_version': self.normalize_version,
            'is_stable_version': self.is_stable_version,
            'bump_version': self.bump_version,
            'version_in_range': self.version_in_range,
            'extract_version': self.extract_version,
            'sort_versions': self.sort_versions,
            'latest_version': self.latest_version,
            'version_satisfies': self.version_satisfies,
            'get_major_version': self.get_major_version,
            'get_minor_version': self.get_minor_version,
            'get_patch_version': self.get_patch_version,
        }

    def version_compare(self, version1, version2, operator):
        """
        Compare two versions using specified operator
        
        Args:
            version1 (str): First version
            version2 (str): Second version  
            operator (str): Comparison operator (<, <=, ==, !=, >=, >)
            
        Returns:
            bool: Comparison result
        """
        try:
            v1 = version.parse(str(version1))
            v2 = version.parse(str(version2))
            
            if operator == '<':
                return v1 < v2
            elif operator == '<=':
                return v1 <= v2
            elif operator == '==':
                return v1 == v2
            elif operator == '!=':
                return v1 != v2
            elif operator == '>=':
                return v1 >= v2
            elif operator == '>':
                return v1 > v2
            else:
                raise ValueError(f"Invalid operator: {operator}")
        except Exception:
            # Fallback to string comparison
            return self._string_version_compare(str(version1), str(version2), operator)

    def _string_version_compare(self, version1, version2, operator):
        """Fallback string-based version comparison"""
        v1_parts = [int(x) for x in re.findall(r'\d+', version1)]
        v2_parts = [int(x) for x in re.findall(r'\d+', version2)]
        
        # Pad shorter version with zeros
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        if operator == '<':
            return v1_parts < v2_parts
        elif operator == '<=':
            return v1_parts <= v2_parts
        elif operator == '==':
            return v1_parts == v2_parts
        elif operator == '!=':
            return v1_parts != v2_parts
        elif operator == '>=':
            return v1_parts >= v2_parts
        elif operator == '>':
            return v1_parts > v2_parts
        else:
            return False

    def parse_version(self, version_string):
        """
        Parse version string into components
        
        Args:
            version_string (str): Version string to parse
            
        Returns:
            dict: Version components
        """
        version_string = str(version_string).strip()
        
        # SemVer pattern: major.minor.patch[-prerelease][+build]
        semver_pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$'
        match = re.match(semver_pattern, version_string)
        
        if match:
            major, minor, patch, prerelease, build = match.groups()
            return {
                'major': int(major),
                'minor': int(minor),
                'patch': int(patch),
                'prerelease': prerelease,
                'build': build,
                'is_semver': True,
                'original': version_string
            }
        
        # Fallback: extract numbers
        numbers = re.findall(r'\d+', version_string)
        if numbers:
            result = {
                'major': int(numbers[0]) if len(numbers) > 0 else 0,
                'minor': int(numbers[1]) if len(numbers) > 1 else 0,
                'patch': int(numbers[2]) if len(numbers) > 2 else 0,
                'prerelease': None,
                'build': None,
                'is_semver': False,
                'original': version_string
            }
            
            # Check for prerelease indicators
            if any(keyword in version_string.lower() for keyword in ['alpha', 'beta', 'rc', 'pre', 'dev', 'snapshot']):
                result['prerelease'] = version_string
                
            return result
        
        return {
            'major': 0,
            'minor': 0,
            'patch': 0,
            'prerelease': version_string if version_string else None,
            'build': None,
            'is_semver': False,
            'original': version_string
        }

    def normalize_version(self, version_string):
        """
        Normalize version string to standard format
        
        Args:
            version_string (str): Version string to normalize
            
        Returns:
            str: Normalized version string
        """
        parsed = self.parse_version(version_string)
        
        base = f"{parsed['major']}.{parsed['minor']}.{parsed['patch']}"
        
        if parsed['prerelease']:
            base += f"-{parsed['prerelease']}"
        
        if parsed['build']:
            base += f"+{parsed['build']}"
            
        return base

    def is_stable_version(self, version_string):
        """
        Check if version is a stable release
        
        Args:
            version_string (str): Version string to check
            
        Returns:
            bool: True if stable, False if prerelease
        """
        parsed = self.parse_version(version_string)
        return parsed['prerelease'] is None

    def bump_version(self, version_string, part='patch'):
        """
        Bump version by specified part
        
        Args:
            version_string (str): Current version
            part (str): Part to bump (major, minor, patch)
            
        Returns:
            str: Bumped version
        """
        parsed = self.parse_version(version_string)
        
        if part == 'major':
            return f"{parsed['major'] + 1}.0.0"
        elif part == 'minor':
            return f"{parsed['major']}.{parsed['minor'] + 1}.0"
        elif part == 'patch':
            return f"{parsed['major']}.{parsed['minor']}.{parsed['patch'] + 1}"
        else:
            raise ValueError(f"Invalid part: {part}")

    def version_in_range(self, version_string, range_spec):
        """
        Check if version is within specified range
        
        Args:
            version_string (str): Version to check
            range_spec (str): Range specification (e.g., ">=1.0.0,<2.0.0")
            
        Returns:
            bool: True if version is in range
        """
        try:
            v = version.parse(str(version_string))
            
            # Split range by comma
            constraints = [c.strip() for c in range_spec.split(',')]
            
            for constraint in constraints:
                # Parse constraint
                match = re.match(r'([<>=!]+)(.+)', constraint)
                if not match:
                    continue
                
                operator, target_version = match.groups()
                target_v = version.parse(target_version.strip())
                
                if not self._check_constraint(v, target_v, operator):
                    return False
            
            return True
        except Exception:
            return False

    def _check_constraint(self, version_obj, target_version_obj, operator):
        """Helper method to check version constraint"""
        if operator == '>=':
            return version_obj >= target_version_obj
        elif operator == '>':
            return version_obj > target_version_obj
        elif operator == '<=':
            return version_obj <= target_version_obj
        elif operator == '<':
            return version_obj < target_version_obj
        elif operator == '==':
            return version_obj == target_version_obj
        elif operator == '!=':
            return version_obj != target_version_obj
        else:
            return True

    def extract_version(self, text):
        """
        Extract version string from text
        
        Args:
            text (str): Text containing version
            
        Returns:
            str: Extracted version or None
        """
        text = str(text)
        
        # Common version patterns
        patterns = [
            r'v?(\d+\.\d+\.\d+(?:-[a-zA-Z0-9\-\.]+)?(?:\+[a-zA-Z0-9\-\.]+)?)',  # SemVer
            r'version[:\s]+(\d+\.\d+\.\d+)',  # "version: 1.2.3"
            r'(\d+\.\d+\.\d+)',  # Simple x.y.z
            r'(\d+\.\d+)',  # x.y
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None

    def sort_versions(self, version_list, reverse=False):
        """
        Sort list of versions
        
        Args:
            version_list (list): List of version strings
            reverse (bool): Sort in descending order
            
        Returns:
            list: Sorted version list
        """
        try:
            return sorted(version_list, key=lambda v: version.parse(str(v)), reverse=reverse)
        except Exception:
            # Fallback to string sorting
            return sorted(version_list, reverse=reverse)

    def latest_version(self, version_list):
        """
        Get the latest version from list
        
        Args:
            version_list (list): List of version strings
            
        Returns:
            str: Latest version
        """
        if not version_list:
            return None
        
        sorted_versions = self.sort_versions(version_list, reverse=True)
        return sorted_versions[0]

    def version_satisfies(self, version_string, requirement):
        """
        Check if version satisfies requirement (npm-style)
        
        Args:
            version_string (str): Version to check
            requirement (str): Requirement string (e.g., "^1.2.0", "~1.2.3")
            
        Returns:
            bool: True if version satisfies requirement
        """
        requirement = requirement.strip()
        
        if requirement.startswith('^'):
            # Caret range: ^1.2.3 := >=1.2.3 <2.0.0
            target = requirement[1:]
            parsed_target = self.parse_version(target)
            return self.version_in_range(
                version_string,
                f">={target},<{parsed_target['major'] + 1}.0.0"
            )
        elif requirement.startswith('~'):
            # Tilde range: ~1.2.3 := >=1.2.3 <1.3.0
            target = requirement[1:]
            parsed_target = self.parse_version(target)
            return self.version_in_range(
                version_string,
                f">={target},<{parsed_target['major']}.{parsed_target['minor'] + 1}.0"
            )
        else:
            # Exact match or range
            return self.version_in_range(version_string, requirement)

    def get_major_version(self, version_string):
        """Get major version number"""
        return self.parse_version(version_string)['major']

    def get_minor_version(self, version_string):
        """Get minor version number"""
        return self.parse_version(version_string)['minor']

    def get_patch_version(self, version_string):
        """Get patch version number"""
        return self.parse_version(version_string)['patch']
