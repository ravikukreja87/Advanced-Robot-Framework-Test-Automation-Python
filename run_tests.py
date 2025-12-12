"""
Main test execution script with advanced features
"""

import os
import sys
import argparse
from datetime import datetime
import subprocess


class TestRunner:
    """Advanced test runner with multiple execution modes"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_dir = f"reports/run_{self.timestamp}"
        
    def run_tests(self, args):
        """Execute tests based on arguments"""
        
        # Base robot command
        cmd = ['robot']
        
        # Output directory
        cmd.extend(['-d', self.output_dir])
        
        # Parallel execution
        if args.parallel:
            cmd = ['pabot', '--processes', str(args.processes)]
            cmd.extend(['-d', self.output_dir])
        
        # Test tags
        if args.tags:
            cmd.extend(['-i', args.tags])
        
        if args.exclude_tags:
            cmd.extend(['-e', args.exclude_tags])
        
        # Environment
        if args.env:
            cmd.extend(['-v', f'ENV:{args.env}'])
        
        # Browser
        if args.browser:
            cmd.extend(['-v', f'BROWSER:{args.browser}'])
        
        # Test suite
        if args.suite:
            cmd.extend(['-s', args.suite])
        
        # Log level
        cmd.extend(['-L', args.loglevel])
        
        # Test path
        cmd.append(args.test_path)
        
        print(f"\n{'='*80}")
        print(f"🚀 Starting Test Execution")
        print(f"{'='*80}")
        print(f"Command: {' '.join(cmd)}")
        print(f"Output: {self.output_dir}")
        print(f"{'='*80}\n")
        
        # Execute
        try:
            result = subprocess.run(cmd, check=False)
            
            print(f"\n{'='*80}")
            print(f"✅ Test Execution Completed")
            print(f"{'='*80}")
            print(f"Report: {self.output_dir}/report.html")
            print(f"Log: {self.output_dir}/log.html")
            print(f"{'='*80}\n")
            
            # Generate Allure report if requested
            if args.allure:
                self.generate_allure_report()
            
            return result.returncode
            
        except Exception as e:
            print(f"❌ Error executing tests: {e}")
            return 1
    
    def generate_allure_report(self):
        """Generate Allure HTML report"""
        try:
            print("📊 Generating Allure report...")
            subprocess.run(['allure', 'generate', self.output_dir, '-o', f'{self.output_dir}/allure-report', '--clean'])
            print(f"✅ Allure report: {self.output_dir}/allure-report/index.html")
        except Exception as e:
            print(f"⚠️  Could not generate Allure report: {e}")


def main():
    parser = argparse.ArgumentParser(description='Advanced Robot Framework Test Runner')
    
    parser.add_argument('test_path', nargs='?', default='tests/', help='Path to test files/directory')
    parser.add_argument('-p', '--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--processes', type=int, default=4, help='Number of parallel processes')
    parser.add_argument('-t', '--tags', help='Include tests with tags')
    parser.add_argument('-e', '--exclude-tags', help='Exclude tests with tags')
    parser.add_argument('--env', default='dev', choices=['dev', 'qa', 'staging', 'prod'], help='Environment')
    parser.add_argument('-b', '--browser', default='chrome', choices=['chrome', 'firefox', 'safari', 'edge'], help='Browser')
    parser.add_argument('-s', '--suite', help='Specific test suite to run')
    parser.add_argument('-L', '--loglevel', default='INFO', choices=['TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR'], help='Log level')
    parser.add_argument('--allure', action='store_true', help='Generate Allure report')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    sys.exit(runner.run_tests(args))


if __name__ == '__main__':
    main()
