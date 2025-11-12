#!/usr/bin/env python3
"""
Joget Instance Health Check Tool

Performs health checks on Joget DX instances to verify they are running correctly.
Checks web interface availability, database connectivity, and application status.

Usage:
    python health_check.py --instance jdx4
    python health_check.py --config config/instances/jdx4.json
    python health_check.py --all

Author: FRS Development Team
Created: 2025-11-12
"""

import argparse
import json
import requests
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "✅ HEALTHY"
    DEGRADED = "⚠️  DEGRADED"
    UNHEALTHY = "❌ UNHEALTHY"
    UNKNOWN = "❓ UNKNOWN"


@dataclass
class CheckResult:
    """Result of a single health check"""
    check_name: str
    status: HealthStatus
    message: str
    details: Dict = None


class InstanceHealthChecker:
    """Performs health checks on a Joget instance"""

    # Default instance configurations
    INSTANCES = {
        'jdx1': {'web_port': 8080, 'db_port': 3306, 'version': '8.1.6'},
        'jdx2': {'web_port': 9999, 'db_port': 3307, 'version': '8.1.6'},
        'jdx3': {'web_port': 8888, 'db_port': 3308, 'version': '9.0.0'},
        'jdx4': {'web_port': 8081, 'db_port': 3309, 'version': '9.0.0'},
        'jdx5': {'web_port': 8082, 'db_port': 3310, 'version': '9.0.0'},
        'jdx6': {'web_port': 8083, 'db_port': 3311, 'version': '9.0.0'},
    }

    def __init__(self, instance_name: str, config: Dict = None):
        """
        Initialize health checker

        Args:
            instance_name: Name of instance (e.g., 'jdx4')
            config: Optional custom configuration
        """
        self.instance_name = instance_name
        self.config = config or self.INSTANCES.get(instance_name, {})

        if not self.config:
            raise ValueError(f"Unknown instance: {instance_name}")

        self.web_port = self.config['web_port']
        self.db_port = self.config['db_port']
        self.base_url = f"http://localhost:{self.web_port}/jw"

        self.results: List[CheckResult] = []

    def run_all_checks(self) -> Tuple[HealthStatus, List[CheckResult]]:
        """
        Run all health checks

        Returns:
            Tuple of (overall_status, list of check results)
        """
        print(f"Running health checks for {self.instance_name}...")
        print(f"  Web Port: {self.web_port}")
        print(f"  DB Port: {self.db_port}")
        print()

        # Run checks
        self._check_web_interface()
        self._check_database_connection()
        self._check_admin_console()
        self._check_process_running()
        self._check_disk_space()
        self._check_memory_usage()

        # Determine overall status
        overall_status = self._calculate_overall_status()

        return overall_status, self.results

    def _check_web_interface(self):
        """Check if web interface is accessible"""
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=10,
                allow_redirects=True
            )

            if response.status_code == 200:
                self.results.append(CheckResult(
                    check_name="Web Interface",
                    status=HealthStatus.HEALTHY,
                    message=f"Web interface responding (HTTP {response.status_code})",
                    details={'url': self.base_url, 'response_time': response.elapsed.total_seconds()}
                ))
            else:
                self.results.append(CheckResult(
                    check_name="Web Interface",
                    status=HealthStatus.DEGRADED,
                    message=f"Web interface returned HTTP {response.status_code}",
                    details={'url': self.base_url}
                ))

        except requests.exceptions.ConnectionError:
            self.results.append(CheckResult(
                check_name="Web Interface",
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot connect to web interface on port {self.web_port}",
                details={'url': self.base_url}
            ))
        except requests.exceptions.Timeout:
            self.results.append(CheckResult(
                check_name="Web Interface",
                status=HealthStatus.DEGRADED,
                message="Web interface timeout (>10s)",
                details={'url': self.base_url}
            ))
        except Exception as e:
            self.results.append(CheckResult(
                check_name="Web Interface",
                status=HealthStatus.UNHEALTHY,
                message=f"Error checking web interface: {str(e)}",
                details={'error': str(e)}
            ))

    def _check_database_connection(self):
        """Check if database is accessible"""
        try:
            # Try to connect using mysql client
            result = subprocess.run(
                ['mysql', '-P', str(self.db_port), '-u', 'root', '-e', 'SELECT 1'],
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0:
                self.results.append(CheckResult(
                    check_name="Database Connection",
                    status=HealthStatus.HEALTHY,
                    message=f"Database accessible on port {self.db_port}",
                    details={'port': self.db_port}
                ))
            else:
                # Try without password (might work if no password set)
                result = subprocess.run(
                    ['mysql', '-P', str(self.db_port), '-u', 'root', '-e', 'SELECT 1'],
                    capture_output=True,
                    timeout=10,
                    input=b'\n'
                )

                if result.returncode == 0:
                    self.results.append(CheckResult(
                        check_name="Database Connection",
                        status=HealthStatus.HEALTHY,
                        message=f"Database accessible on port {self.db_port}",
                        details={'port': self.db_port}
                    ))
                else:
                    self.results.append(CheckResult(
                        check_name="Database Connection",
                        status=HealthStatus.DEGRADED,
                        message=f"Database connection requires authentication (port {self.db_port})",
                        details={'port': self.db_port, 'note': 'Unable to verify without password'}
                    ))

        except subprocess.TimeoutExpired:
            self.results.append(CheckResult(
                check_name="Database Connection",
                status=HealthStatus.DEGRADED,
                message="Database connection timeout",
                details={'port': self.db_port}
            ))
        except FileNotFoundError:
            self.results.append(CheckResult(
                check_name="Database Connection",
                status=HealthStatus.UNKNOWN,
                message="MySQL client not found (cannot verify database)",
                details={'port': self.db_port, 'note': 'Install mysql-client to enable this check'}
            ))
        except Exception as e:
            self.results.append(CheckResult(
                check_name="Database Connection",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking database: {str(e)}",
                details={'error': str(e)}
            ))

    def _check_admin_console(self):
        """Check if admin console is accessible"""
        try:
            response = requests.get(
                f"{self.base_url}/web/console/home",
                timeout=10,
                allow_redirects=False
            )

            # Admin console typically redirects to login if not authenticated
            if response.status_code in [200, 302, 401]:
                self.results.append(CheckResult(
                    check_name="Admin Console",
                    status=HealthStatus.HEALTHY,
                    message="Admin console accessible",
                    details={'url': f"{self.base_url}/web/console/home"}
                ))
            else:
                self.results.append(CheckResult(
                    check_name="Admin Console",
                    status=HealthStatus.DEGRADED,
                    message=f"Admin console returned HTTP {response.status_code}",
                    details={'url': f"{self.base_url}/web/console/home"}
                ))

        except Exception as e:
            self.results.append(CheckResult(
                check_name="Admin Console",
                status=HealthStatus.DEGRADED,
                message=f"Cannot access admin console: {str(e)}",
                details={'error': str(e)}
            ))

    def _check_process_running(self):
        """Check if Joget process is running"""
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Look for Joget process (contains version number)
            version = self.config.get('version', '')
            joget_processes = [
                line for line in result.stdout.split('\n')
                if 'joget' in line.lower() and version in line
            ]

            if joget_processes:
                self.results.append(CheckResult(
                    check_name="Process Status",
                    status=HealthStatus.HEALTHY,
                    message=f"Joget process running (version {version})",
                    details={'process_count': len(joget_processes)}
                ))
            else:
                self.results.append(CheckResult(
                    check_name="Process Status",
                    status=HealthStatus.UNHEALTHY,
                    message="Joget process not found",
                    details={'version': version}
                ))

        except Exception as e:
            self.results.append(CheckResult(
                check_name="Process Status",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking process: {str(e)}",
                details={'error': str(e)}
            ))

    def _check_disk_space(self):
        """Check available disk space"""
        try:
            result = subprocess.run(
                ['df', '-h', '/'],
                capture_output=True,
                text=True,
                timeout=5
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                # Parse output (format: Filesystem Size Used Avail Use% Mounted)
                parts = lines[1].split()
                if len(parts) >= 5:
                    used_percent = int(parts[4].rstrip('%'))

                    if used_percent < 80:
                        status = HealthStatus.HEALTHY
                        message = f"Disk space OK ({used_percent}% used)"
                    elif used_percent < 90:
                        status = HealthStatus.DEGRADED
                        message = f"Disk space low ({used_percent}% used)"
                    else:
                        status = HealthStatus.UNHEALTHY
                        message = f"Disk space critical ({used_percent}% used)"

                    self.results.append(CheckResult(
                        check_name="Disk Space",
                        status=status,
                        message=message,
                        details={
                            'used_percent': used_percent,
                            'available': parts[3],
                            'total': parts[1]
                        }
                    ))
                    return

            # Fallback if parsing fails
            self.results.append(CheckResult(
                check_name="Disk Space",
                status=HealthStatus.UNKNOWN,
                message="Could not parse disk space information",
                details={}
            ))

        except Exception as e:
            self.results.append(CheckResult(
                check_name="Disk Space",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking disk space: {str(e)}",
                details={'error': str(e)}
            ))

    def _check_memory_usage(self):
        """Check system memory usage"""
        try:
            # Use free command on Linux/Mac
            result = subprocess.run(
                ['free', '-m'],
                capture_output=True,
                text=True,
                timeout=5
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                # Parse memory line
                parts = lines[1].split()
                if len(parts) >= 3:
                    total = int(parts[1])
                    used = int(parts[2])
                    used_percent = int((used / total) * 100)

                    if used_percent < 80:
                        status = HealthStatus.HEALTHY
                        message = f"Memory usage OK ({used_percent}%)"
                    elif used_percent < 90:
                        status = HealthStatus.DEGRADED
                        message = f"Memory usage high ({used_percent}%)"
                    else:
                        status = HealthStatus.UNHEALTHY
                        message = f"Memory usage critical ({used_percent}%)"

                    self.results.append(CheckResult(
                        check_name="Memory Usage",
                        status=status,
                        message=message,
                        details={
                            'used_percent': used_percent,
                            'used_mb': used,
                            'total_mb': total
                        }
                    ))
                    return

            # Fallback
            self.results.append(CheckResult(
                check_name="Memory Usage",
                status=HealthStatus.UNKNOWN,
                message="Could not parse memory information",
                details={}
            ))

        except FileNotFoundError:
            # free command not available (might be on Mac)
            self.results.append(CheckResult(
                check_name="Memory Usage",
                status=HealthStatus.UNKNOWN,
                message="Memory check not available on this platform",
                details={}
            ))
        except Exception as e:
            self.results.append(CheckResult(
                check_name="Memory Usage",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking memory: {str(e)}",
                details={'error': str(e)}
            ))

    def _calculate_overall_status(self) -> HealthStatus:
        """
        Calculate overall health status from individual checks

        Returns:
            HealthStatus: Overall status
        """
        unhealthy_count = sum(1 for r in self.results if r.status == HealthStatus.UNHEALTHY)
        degraded_count = sum(1 for r in self.results if r.status == HealthStatus.DEGRADED)
        unknown_count = sum(1 for r in self.results if r.status == HealthStatus.UNKNOWN)

        if unhealthy_count > 0:
            return HealthStatus.UNHEALTHY
        elif degraded_count > 0:
            return HealthStatus.DEGRADED
        elif unknown_count > 0:
            return HealthStatus.UNKNOWN
        else:
            return HealthStatus.HEALTHY


def print_results(instance_name: str, overall_status: HealthStatus, results: List[CheckResult]):
    """Print health check results"""
    print("\n" + "="*70)
    print(f"HEALTH CHECK RESULTS: {instance_name}")
    print("="*70)
    print(f"\nOverall Status: {overall_status.value}\n")

    for result in results:
        print(f"{result.status.value} {result.check_name}")
        print(f"    {result.message}")
        if result.details:
            for key, value in result.details.items():
                print(f"      {key}: {value}")
        print()

    print("="*70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Check health of Joget DX instances'
    )
    parser.add_argument(
        '--instance',
        type=str,
        choices=['jdx1', 'jdx2', 'jdx3', 'jdx4', 'jdx5', 'jdx6'],
        help='Instance name to check'
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to instance configuration file (JSON)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Check all instances'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )

    args = parser.parse_args()

    # Validate arguments
    if not (args.instance or args.config or args.all):
        parser.error("Must specify --instance, --config, or --all")

    # Determine instances to check
    instances_to_check = []

    if args.all:
        instances_to_check = ['jdx1', 'jdx2', 'jdx3', 'jdx4', 'jdx5', 'jdx6']
    elif args.config:
        # Load custom config
        with open(args.config) as f:
            config = json.load(f)
        instances_to_check = [(config.get('instance_name', 'custom'), config)]
    else:
        instances_to_check = [args.instance]

    # Run checks
    all_results = {}

    for instance in instances_to_check:
        if isinstance(instance, tuple):
            name, config = instance
            checker = InstanceHealthChecker(name, config)
        else:
            checker = InstanceHealthChecker(instance)

        overall_status, results = checker.run_all_checks()
        all_results[instance if isinstance(instance, str) else name] = {
            'status': overall_status,
            'results': results
        }

        if not args.json:
            print_results(
                instance if isinstance(instance, str) else name,
                overall_status,
                results
            )

    # JSON output if requested
    if args.json:
        json_output = {}
        for instance_name, data in all_results.items():
            json_output[instance_name] = {
                'overall_status': data['status'].name,
                'checks': [
                    {
                        'check_name': r.check_name,
                        'status': r.status.name,
                        'message': r.message,
                        'details': r.details
                    }
                    for r in data['results']
                ]
            }
        print(json.dumps(json_output, indent=2))

    # Exit with appropriate code
    if all(r['status'] == HealthStatus.HEALTHY for r in all_results.values()):
        sys.exit(0)
    elif any(r['status'] == HealthStatus.UNHEALTHY for r in all_results.values()):
        sys.exit(2)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
