#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, DAI Continuous Testing
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
import base64
import json
from urllib.parse import urlparse, quote, unquote

DOCUMENTATION = '''
---
name: string_utils
short_description: String manipulation utilities for Ansible
description:
  - Provides enhanced string manipulation functions
  - Includes URL handling, encoding, formatting utilities
  - Useful for configuration management and data processing
version_added: "1.0.0"
author:
  - DAI Continuous Testing
'''

EXAMPLES = '''
# Safe key generation
- set_fact:
    safe_key: "{{ 'My Application Name!' | dai_continuous_testing.utilities.safe_key }}"
  # Returns: my_application_name

# URL parsing
- set_fact:
    parsed_url: "{{ 'https://example.com:8080/path?param=value' | dai_continuous_testing.utilities.parse_url }}"
  # Returns: {"scheme": "https", "hostname": "example.com", "port": 8080, "path": "/path"}

# Template string interpolation
- set_fact:
    message: "{{ 'Hello {name}, you have {count} messages' | dai_continuous_testing.utilities.template_string({'name': 'John', 'count': 5}) }}"
  # Returns: Hello John, you have 5 messages

# Join with conditional
- set_fact:
    path: "{{ ['/opt', 'experitest', app_name] | dai_continuous_testing.utilities.join_path }}"
  # Returns: /opt/experitest/cloudserver

# Slugify for filenames
- set_fact:
    filename: "{{ 'Cloud Server Config!' | dai_continuous_testing.utilities.slugify }}"
  # Returns: cloud-server-config
'''


class FilterModule(object):
    """String utilities filter plugin"""
    
    def filters(self):
        return {
            'safe_key': self.safe_key,
            'safe_filename': self.safe_filename,
            'slugify': self.slugify,
            'parse_url': self.parse_url,
            'template_string': self.template_string,
            'join_path': self.join_path,
            'ensure_prefix': self.ensure_prefix,
            'ensure_suffix': self.ensure_suffix,
            'remove_prefix': self.remove_prefix,
            'remove_suffix': self.remove_suffix,
            'camel_to_snake': self.camel_to_snake,
            'snake_to_camel': self.snake_to_camel,
            'truncate_smart': self.truncate_smart,
            'encode_base64_safe': self.encode_base64_safe,
            'decode_base64_safe': self.decode_base64_safe,
            'normalize_whitespace': self.normalize_whitespace,
            'extract_numbers': self.extract_numbers,
            'mask_sensitive': self.mask_sensitive,
        }

    def safe_key(self, text):
        """
        Convert text to safe key format (lowercase, alphanumeric, underscores)
        
        Args:
            text (str): Input text
            
        Returns:
            str: Safe key format
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Convert to lowercase and replace non-alphanumeric with underscores
        safe = re.sub(r'[^a-zA-Z0-9]+', '_', text.lower())
        # Remove leading/trailing underscores and collapse multiple underscores
        safe = re.sub(r'^_+|_+$', '', safe)
        safe = re.sub(r'_+', '_', safe)
        
        return safe or 'default'

    def safe_filename(self, text, max_length=255):
        """
        Convert text to safe filename
        
        Args:
            text (str): Input text
            max_length (int): Maximum filename length
            
        Returns:
            str: Safe filename
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Remove or replace unsafe characters
        safe = re.sub(r'[<>:"/\\|?*]', '', text)
        safe = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', safe)  # Remove control characters
        safe = safe.strip('. ')  # Remove leading/trailing dots and spaces
        
        # Truncate if necessary
        if len(safe) > max_length:
            safe = safe[:max_length].rstrip('. ')
        
        return safe or 'file'

    def slugify(self, text, separator='-'):
        """
        Convert text to URL-friendly slug
        
        Args:
            text (str): Input text
            separator (str): Separator character
            
        Returns:
            str: URL-friendly slug
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Convert to lowercase and replace non-alphanumeric with separator
        slug = re.sub(r'[^a-zA-Z0-9]+', separator, text.lower())
        # Remove leading/trailing separators and collapse multiple separators
        slug = re.sub(f'^{re.escape(separator)}+|{re.escape(separator)}+$', '', slug)
        slug = re.sub(f'{re.escape(separator)}+', separator, slug)
        
        return slug or 'item'

    def parse_url(self, url):
        """
        Parse URL into components
        
        Args:
            url (str): URL to parse
            
        Returns:
            dict: URL components
        """
        parsed = urlparse(url)
        return {
            'scheme': parsed.scheme,
            'hostname': parsed.hostname,
            'port': parsed.port,
            'path': parsed.path,
            'query': parsed.query,
            'fragment': parsed.fragment,
            'username': parsed.username,
            'password': parsed.password,
            'netloc': parsed.netloc
        }

    def template_string(self, template, variables):
        """
        Simple string template interpolation
        
        Args:
            template (str): Template string with {key} placeholders
            variables (dict): Variables to substitute
            
        Returns:
            str: Interpolated string
        """
        if not isinstance(template, str):
            template = str(template)
        
        if not isinstance(variables, dict):
            return template
        
        try:
            return template.format(**variables)
        except (KeyError, ValueError):
            # Fallback to manual replacement for missing keys
            result = template
            for key, value in variables.items():
                result = result.replace(f'{{{key}}}', str(value))
            return result

    def join_path(self, path_parts, separator='/'):
        """
        Join path parts intelligently
        
        Args:
            path_parts (list): List of path parts
            separator (str): Path separator
            
        Returns:
            str: Joined path
        """
        if not isinstance(path_parts, list):
            return str(path_parts)
        
        # Filter out None and empty strings
        parts = [str(part).strip() for part in path_parts if part is not None and str(part).strip()]
        
        if not parts:
            return ''
        
        # Join parts and normalize separators
        path = separator.join(parts)
        # Remove duplicate separators
        while separator + separator in path:
            path = path.replace(separator + separator, separator)
        
        return path

    def ensure_prefix(self, text, prefix):
        """
        Ensure text starts with prefix
        
        Args:
            text (str): Input text
            prefix (str): Required prefix
            
        Returns:
            str: Text with prefix
        """
        text = str(text)
        prefix = str(prefix)
        
        if not text.startswith(prefix):
            return prefix + text
        return text

    def ensure_suffix(self, text, suffix):
        """
        Ensure text ends with suffix
        
        Args:
            text (str): Input text
            suffix (str): Required suffix
            
        Returns:
            str: Text with suffix
        """
        text = str(text)
        suffix = str(suffix)
        
        if not text.endswith(suffix):
            return text + suffix
        return text

    def remove_prefix(self, text, prefix):
        """
        Remove prefix from text if present
        
        Args:
            text (str): Input text
            prefix (str): Prefix to remove
            
        Returns:
            str: Text without prefix
        """
        text = str(text)
        prefix = str(prefix)
        
        if text.startswith(prefix):
            return text[len(prefix):]
        return text

    def remove_suffix(self, text, suffix):
        """
        Remove suffix from text if present
        
        Args:
            text (str): Input text
            suffix (str): Suffix to remove
            
        Returns:
            str: Text without suffix
        """
        text = str(text)
        suffix = str(suffix)
        
        if text.endswith(suffix):
            return text[:-len(suffix)]
        return text

    def camel_to_snake(self, text):
        """
        Convert camelCase to snake_case
        
        Args:
            text (str): CamelCase text
            
        Returns:
            str: snake_case text
        """
        text = str(text)
        # Insert underscore before uppercase letters (except at start)
        snake = re.sub(r'(?<!^)([A-Z])', r'_\1', text)
        return snake.lower()

    def snake_to_camel(self, text, capitalize_first=False):
        """
        Convert snake_case to camelCase
        
        Args:
            text (str): snake_case text
            capitalize_first (bool): Whether to capitalize first letter
            
        Returns:
            str: camelCase text
        """
        text = str(text)
        parts = text.split('_')
        
        if not parts:
            return text
        
        if capitalize_first:
            return ''.join(part.capitalize() for part in parts)
        else:
            return parts[0] + ''.join(part.capitalize() for part in parts[1:])

    def truncate_smart(self, text, max_length, suffix='...'):
        """
        Smart truncation that tries to break at word boundaries
        
        Args:
            text (str): Text to truncate
            max_length (int): Maximum length
            suffix (str): Suffix for truncated text
            
        Returns:
            str: Truncated text
        """
        text = str(text)
        
        if len(text) <= max_length:
            return text
        
        # Try to break at word boundary
        truncated = text[:max_length - len(suffix)]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.7:  # If we found a reasonable break point
            truncated = truncated[:last_space]
        
        return truncated + suffix

    def encode_base64_safe(self, text):
        """
        Safely encode text to base64
        
        Args:
            text (str): Text to encode
            
        Returns:
            str: Base64 encoded text
        """
        try:
            return base64.b64encode(str(text).encode('utf-8')).decode('ascii')
        except Exception:
            return text

    def decode_base64_safe(self, encoded_text):
        """
        Safely decode base64 text
        
        Args:
            encoded_text (str): Base64 encoded text
            
        Returns:
            str: Decoded text
        """
        try:
            return base64.b64decode(str(encoded_text)).decode('utf-8')
        except Exception:
            return encoded_text

    def normalize_whitespace(self, text):
        """
        Normalize whitespace in text
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with normalized whitespace
        """
        text = str(text)
        # Replace multiple whitespace with single space
        normalized = re.sub(r'\s+', ' ', text)
        return normalized.strip()

    def extract_numbers(self, text):
        """
        Extract all numbers from text
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of numbers found
        """
        text = str(text)
        numbers = re.findall(r'-?\d+\.?\d*', text)
        return [float(n) if '.' in n else int(n) for n in numbers]

    def mask_sensitive(self, text, mask_char='*', visible_chars=4):
        """
        Mask sensitive information
        
        Args:
            text (str): Sensitive text
            mask_char (str): Character to use for masking
            visible_chars (int): Number of characters to keep visible
            
        Returns:
            str: Masked text
        """
        text = str(text)
        
        if len(text) <= visible_chars:
            return mask_char * len(text)
        
        visible_start = visible_chars // 2
        visible_end = visible_chars - visible_start
        
        if visible_end == 0:
            return text[:visible_start] + mask_char * (len(text) - visible_start)
        else:
            return text[:visible_start] + mask_char * (len(text) - visible_chars) + text[-visible_end:]
