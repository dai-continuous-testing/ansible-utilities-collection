#!/usr/bin/env python3
"""
Test runner for DAI Continuous Testing Utilities Collection

This script runs all unit tests and integration tests for the collection modules.
It provides comprehensive test coverage reporting and validation.
"""

import os
import sys
import unittest
import importlib.util
import subprocess
import argparse
from pathlib import Path


class TestRunner:
    """Test runner for the utilities collection"""
    
    def __init__(self):
        self.collection_root = Path(__file__).parent.parent
        self.tests_dir = self.collection_root / 'tests'
        self.modules_dir = self.collection_root / 'plugins' / 'modules'
        
    def discover_tests(self, test_type='all'):
        """Discover and return test suites"""
        test_suites = []
        
        if test_type in ('all', 'unit'):
            unit_tests_dir = self.tests_dir / 'unit'
            if unit_tests_dir.exists():
                unit_suite = unittest.TestLoader().discover(
                    str(unit_tests_dir),
                    pattern='test_*.py'
                )
                test_suites.append(('Unit Tests', unit_suite))
        
        if test_type in ('all', 'integration'):
            integration_tests_dir = self.tests_dir / 'integration'
            if integration_tests_dir.exists():
                integration_suite = unittest.TestLoader().discover(
                    str(integration_tests_dir),
                    pattern='test_*.py'
                )
                test_suites.append(('Integration Tests', integration_suite))
        
        return test_suites
    
    def run_tests(self, test_type='all', verbose=True):
        """Run the discovered tests"""
        print(f"Running {test_type} tests for DAI Continuous Testing Utilities Collection")
        print("=" * 70)
        
        test_suites = self.discover_tests(test_type)
        
        if not test_suites:
            print(f"No {test_type} tests found!")
            return False
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        
        for suite_name, suite in test_suites:
            print(f"\n{suite_name}")
            print("-" * len(suite_name))
            
            runner = unittest.TextTestRunner(
                verbosity=2 if verbose else 1,
                stream=sys.stdout
            )
            
            result = runner.run(suite)
            
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            total_skipped += len(result.skipped)
            
            print(f"\nTests run: {result.testsRun}")
            print(f"Failures: {len(result.failures)}")
            print(f"Errors: {len(result.errors)}")
            print(f"Skipped: {len(result.skipped)}")
        
        print("\n" + "=" * 70)
        print("OVERALL TEST SUMMARY")
        print(f"Total tests run: {total_tests}")
        print(f"Total failures: {total_failures}")
        print(f"Total errors: {total_errors}")
        print(f"Total skipped: {total_skipped}")
        
        success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
        return total_failures == 0 and total_errors == 0
    
    def validate_modules(self):
        """Validate that all modules are present and have basic structure"""
        print("\nValidating module structure...")
        print("-" * 30)
        
        expected_modules = [
            'application_properties.py',
            'health_check.py',
            'win_health_check.ps1',
            'win_drive_letter_to_disk_info.py'
        ]
        
        validation_results = {}
        
        for module_name in expected_modules:
            module_path = self.modules_dir / module_name
            validation_results[module_name] = {
                'exists': module_path.exists(),
                'readable': False,
                'has_documentation': False,
                'python_syntax_valid': False
            }
            
            if validation_results[module_name]['exists']:
                try:
                    with open(module_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        validation_results[module_name]['readable'] = True
                        
                        # Check for documentation
                        if module_name.endswith('.ps1'):
                            # PowerShell documentation
                            if '.synopsis' in content.lower() or '.description' in content.lower():
                                validation_results[module_name]['has_documentation'] = True
                        else:
                            # Python documentation
                            if 'DOCUMENTATION' in content:
                                validation_results[module_name]['has_documentation'] = True
                        
                        # Check Python syntax (for .py files)
                        if module_name.endswith('.py'):
                            try:
                                compile(content, str(module_path), 'exec')
                                validation_results[module_name]['python_syntax_valid'] = True
                            except SyntaxError:
                                pass
                        else:
                            # For non-Python files, assume syntax is valid if readable
                            validation_results[module_name]['python_syntax_valid'] = True
                            
                except Exception as e:
                    print(f"Error reading {module_name}: {e}")
        
        # Print validation results
        for module_name, results in validation_results.items():
            status = "✓" if all(results.values()) else "✗"
            print(f"{status} {module_name}")
            for check, passed in results.items():
                indicator = "✓" if passed else "✗"
                print(f"  {indicator} {check.replace('_', ' ').title()}")
        
        return all(all(results.values()) for results in validation_results.values())
    
    def check_test_coverage(self):
        """Check test coverage for modules"""
        print("\nChecking test coverage...")
        print("-" * 25)
        
        module_files = [f.stem for f in self.modules_dir.glob('*.py')]
        test_files = [f.stem for f in (self.tests_dir / 'unit').glob('test_*.py')]
        
        # Extract module names from test files
        tested_modules = []
        for test_file in test_files:
            if test_file.startswith('test_'):
                module_name = test_file[5:]  # Remove 'test_' prefix
                tested_modules.append(module_name)
        
        print("Module coverage:")
        for module in module_files:
            has_test = module in tested_modules
            indicator = "✓" if has_test else "✗"
            print(f"  {indicator} {module}.py")
        
        coverage_percentage = (len([m for m in module_files if m in tested_modules]) / len(module_files) * 100) if module_files else 0
        print(f"\nTest coverage: {coverage_percentage:.1f}%")
        
        return coverage_percentage >= 80  # Require at least 80% coverage
    
    def run_linting(self):
        """Run linting checks on Python modules"""
        print("\nRunning linting checks...")
        print("-" * 24)
        
        python_modules = list(self.modules_dir.glob('*.py'))
        test_files = list(self.tests_dir.rglob('*.py'))
        
        all_files = python_modules + test_files
        
        # Basic Python syntax checking (since we might not have external linters)
        syntax_errors = []
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(file_path), 'exec')
                print(f"✓ {file_path.name}")
            except SyntaxError as e:
                syntax_errors.append((file_path, e))
                print(f"✗ {file_path.name}: {e}")
        
        if syntax_errors:
            print(f"\nFound {len(syntax_errors)} syntax errors!")
            return False
        else:
            print(f"\nAll {len(all_files)} Python files passed syntax check!")
            return True


def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(description='Run tests for DAI Continuous Testing Utilities Collection')
    parser.add_argument('--type', choices=['all', 'unit', 'integration'], default='all',
                       help='Type of tests to run (default: all)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--validate', action='store_true',
                       help='Run module validation checks')
    parser.add_argument('--coverage', action='store_true',
                       help='Check test coverage')
    parser.add_argument('--lint', action='store_true',
                       help='Run linting checks')
    parser.add_argument('--all-checks', action='store_true',
                       help='Run all validation checks and tests')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    success = True
    
    if args.all_checks:
        args.validate = True
        args.coverage = True
        args.lint = True
    
    if args.validate:
        if not runner.validate_modules():
            print("❌ Module validation failed!")
            success = False
        else:
            print("✅ Module validation passed!")
    
    if args.coverage:
        if not runner.check_test_coverage():
            print("⚠️  Test coverage below recommended threshold!")
        else:
            print("✅ Test coverage meets requirements!")
    
    if args.lint:
        if not runner.run_linting():
            print("❌ Linting checks failed!")
            success = False
        else:
            print("✅ Linting checks passed!")
    
    # Run tests
    if not runner.run_tests(args.type, args.verbose):
        print("❌ Tests failed!")
        success = False
    else:
        print("✅ All tests passed!")
    
    if success:
        print("\n🎉 All checks passed! The collection is ready for use.")
        sys.exit(0)
    else:
        print("\n💥 Some checks failed. Please review the output above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
