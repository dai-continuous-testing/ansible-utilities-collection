#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, DAI Continuous Testing
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
name: os_family_to_os_type
short_description: Convert Ansible OS family to standardized OS type
description:
  - Converts Ansible's ansible_os_family values to standardized OS types
  - Useful for cross-platform playbooks and role logic
version_added: "1.0.0"
author:
  - DAI Continuous Testing
options:
  _input:
    description: The OS family name to convert
    type: str
    required: true
notes:
  - Supported OS families: RedHat, Debian, Suse, Darwin, Windows
  - Returns lowercase standardized types: linux, darwin, windows
examples:
  - name: Convert RedHat to linux
    debug:
      msg: "{{ 'RedHat' | dai_continuous_testing.utilities.os_family_to_os_type }}"
    # Returns: linux
    
  - name: Use in conditional logic
    debug:
      msg: "This is a Linux system"
    when: ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type == 'linux'
'''

EXAMPLES = '''
# Convert various OS families
- debug:
    msg: "{{ ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type }}"

# Use in conditional tasks
- name: Install Linux packages
  package:
    name: "{{ linux_packages }}"
  when: ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type == 'linux'

- name: Configure Windows settings
  win_regedit:
    path: "{{ registry_path }}"
    name: "{{ setting_name }}"
    data: "{{ setting_value }}"
  when: ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type == 'windows'

# Use in variable selection
- set_fact:
    package_manager: "{{ os_package_managers[ansible_os_family | dai_continuous_testing.utilities.os_family_to_os_type] }}"
  vars:
    os_package_managers:
      linux: "yum"
      darwin: "brew"
      windows: "chocolatey"
'''

RETURN = '''
_value:
  description: Standardized OS type
  type: str
  returned: always
  sample: "linux"
'''


class FilterModule(object):
    """Ansible filter plugin for OS utilities"""
    
    def filters(self):
        return {
            'os_family_to_os_type': self.os_family_to_os_type,
            'normalize_os_family': self.normalize_os_family,
            'is_linux_family': self.is_linux_family,
            'is_windows_family': self.is_windows_family,
            'is_darwin_family': self.is_darwin_family,
        }

    def os_family_to_os_type(self, os_family):
        """
        Convert Ansible OS family to standardized OS type
        
        Args:
            os_family (str): The OS family from ansible_os_family
            
        Returns:
            str: Standardized OS type (linux, darwin, windows)
            
        Raises:
            KeyError: If the OS family is not supported
        """
        if not isinstance(os_family, str):
            raise TypeError("OS family must be a string")
            
        os_family_mapping = {
            "redhat": "linux",
            "debian": "linux", 
            "ubuntu": "linux",
            "suse": "linux",
            "archlinux": "linux",
            "gentoo": "linux",
            "alpine": "linux",
            "amazon": "linux",
            "rocky": "linux",
            "almalinux": "linux",
            "darwin": "darwin",
            "macosx": "darwin",
            "windows": "windows"
        }
        
        normalized_family = os_family.lower().strip()
        
        if normalized_family not in os_family_mapping:
            raise KeyError(f"Unsupported OS family: {os_family}")
            
        return os_family_mapping[normalized_family]

    def normalize_os_family(self, os_family):
        """
        Normalize OS family name to consistent format
        
        Args:
            os_family (str): The OS family name
            
        Returns:
            str: Normalized OS family name
        """
        if not isinstance(os_family, str):
            return os_family
            
        # Common normalizations
        normalizations = {
            "redhat": "RedHat",
            "red hat": "RedHat", 
            "rhel": "RedHat",
            "centos": "RedHat",
            "fedora": "RedHat",
            "ubuntu": "Debian",
            "debian": "Debian",
            "mint": "Debian",
            "suse": "Suse",
            "opensuse": "Suse",
            "sles": "Suse",
            "darwin": "Darwin",
            "macos": "Darwin",
            "macosx": "Darwin",
            "osx": "Darwin",
            "windows": "Windows",
            "win32": "Windows",
            "cygwin": "Windows"
        }
        
        return normalizations.get(os_family.lower().strip(), os_family)

    def is_linux_family(self, os_family):
        """
        Check if OS family is Linux-based
        
        Args:
            os_family (str): The OS family name
            
        Returns:
            bool: True if Linux-based, False otherwise
        """
        try:
            return self.os_family_to_os_type(os_family) == "linux"
        except (KeyError, TypeError):
            return False

    def is_windows_family(self, os_family):
        """
        Check if OS family is Windows-based
        
        Args:
            os_family (str): The OS family name
            
        Returns:
            bool: True if Windows-based, False otherwise
        """
        try:
            return self.os_family_to_os_type(os_family) == "windows"
        except (KeyError, TypeError):
            return False

    def is_darwin_family(self, os_family):
        """
        Check if OS family is Darwin/macOS-based
        
        Args:
            os_family (str): The OS family name
            
        Returns:
            bool: True if Darwin-based, False otherwise
        """
        try:
            return self.os_family_to_os_type(os_family) == "darwin"
        except (KeyError, TypeError):
            return False
