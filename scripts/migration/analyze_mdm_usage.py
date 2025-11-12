#!/usr/bin/env python3
"""
MDM Usage Analysis Tool

Scans a Joget application export to identify all Master Data Management (MDM) dependencies.
This tool helps with planning MDM migration by finding all fields that use master data sources.

Usage:
    python analyze_mdm_usage.py --app-export path/to/app.zip --output analysis.json

Author: FRS Development Team
Created: 2025-11-12
"""

import argparse
import json
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Set
from dataclasses import dataclass, asdict
import sys


@dataclass
class MDMDependency:
    """Represents a single MDM dependency found in the application"""
    form_id: str
    form_name: str
    field_id: str
    field_label: str
    field_type: str  # selectBox, checkBox, radio
    options_source: str  # formOptions, jdbcOptions, etc.
    options_config: Dict[str, Any]  # Full options binder configuration
    has_ajax_cascade: bool
    cascade_config: Dict[str, Any] = None


@dataclass
class AnalysisReport:
    """Complete analysis report of MDM usage"""
    application_id: str
    application_name: str
    total_forms: int
    total_mdm_fields: int
    dependencies: List[MDMDependency]
    warnings: List[str]
    statistics: Dict[str, Any]


class JogetAppAnalyzer:
    """Analyzes Joget application exports for MDM dependencies"""

    # Field types that commonly use MDM
    MDM_FIELD_TYPES = {'selectBox', 'checkBox', 'radio', 'multiselect'}

    # Options binder types that indicate external data source
    EXTERNAL_BINDERS = {
        'formOptions': 'Form Options Binder',
        'jdbcOptions': 'JDBC Options Binder',
        'restOptions': 'REST Options Binder'
    }

    def __init__(self, app_export_path: Path):
        self.app_export_path = app_export_path
        self.dependencies: List[MDMDependency] = []
        self.warnings: List[str] = []
        self.app_data: Dict = {}

    def analyze(self) -> AnalysisReport:
        """
        Main analysis method

        Returns:
            AnalysisReport: Complete analysis of MDM dependencies
        """
        print(f"Analyzing application export: {self.app_export_path}")

        # Extract and parse application
        self.app_data = self._load_app_export()

        # Analyze forms
        forms = self._get_forms()
        print(f"Found {len(forms)} forms to analyze")

        for form in forms:
            self._analyze_form(form)

        # Generate statistics
        stats = self._generate_statistics()

        # Create report
        report = AnalysisReport(
            application_id=self.app_data.get('appId', 'unknown'),
            application_name=self.app_data.get('appName', 'unknown'),
            total_forms=len(forms),
            total_mdm_fields=len(self.dependencies),
            dependencies=self.dependencies,
            warnings=self.warnings,
            statistics=stats
        )

        print(f"\nAnalysis complete:")
        print(f"  - Forms analyzed: {report.total_forms}")
        print(f"  - MDM dependencies found: {report.total_mdm_fields}")
        print(f"  - Warnings: {len(report.warnings)}")

        return report

    def _load_app_export(self) -> Dict:
        """
        Load and parse Joget application export (ZIP file)

        Returns:
            Dict: Parsed application data
        """
        try:
            with zipfile.ZipFile(self.app_export_path, 'r') as zip_file:
                # Joget app exports typically contain appDefinition.xml or JSON files
                # This is a simplified version - adjust based on actual export structure

                # Find the main application definition file
                json_files = [f for f in zip_file.namelist() if f.endswith('.json')]

                if not json_files:
                    raise ValueError("No JSON files found in export")

                # Load the main app definition (usually first JSON file)
                with zip_file.open(json_files[0]) as f:
                    return json.load(f)

        except Exception as e:
            print(f"Error loading application export: {e}")
            sys.exit(1)

    def _get_forms(self) -> List[Dict]:
        """
        Extract all forms from application data

        Returns:
            List[Dict]: List of form definitions
        """
        forms = []

        # Navigate application structure to find forms
        # Adjust this based on actual Joget export structure
        if 'forms' in self.app_data:
            forms = self.app_data['forms']
        elif 'formDefinitionList' in self.app_data:
            forms = self.app_data['formDefinitionList']
        else:
            self.warnings.append("Could not find forms in application structure")

        return forms

    def _analyze_form(self, form: Dict):
        """
        Analyze a single form for MDM dependencies

        Args:
            form: Form definition dictionary
        """
        form_id = form.get('id', 'unknown')
        form_name = form.get('name', 'unknown')

        print(f"  Analyzing form: {form_id}")

        # Get form JSON definition
        form_json = form.get('json', {})
        if isinstance(form_json, str):
            form_json = json.loads(form_json)

        # Recursively search for MDM field types
        self._search_elements(form_json, form_id, form_name)

    def _search_elements(self, element: Dict, form_id: str, form_name: str):
        """
        Recursively search form elements for MDM dependencies

        Args:
            element: Current element in form structure
            form_id: Form identifier
            form_name: Form display name
        """
        if not isinstance(element, dict):
            return

        # Check if this element is an MDM field
        class_name = element.get('className', '')
        field_type = self._get_field_type(class_name)

        if field_type in self.MDM_FIELD_TYPES:
            self._analyze_mdm_field(element, form_id, form_name, field_type)

        # Recursively search child elements
        if 'elements' in element:
            for child in element.get('elements', []):
                self._search_elements(child, form_id, form_name)

        # Search in properties (some elements nest configs here)
        if 'properties' in element:
            props = element['properties']
            if isinstance(props, dict) and 'elements' in props:
                for child in props['elements']:
                    self._search_elements(child, form_id, form_name)

    def _get_field_type(self, class_name: str) -> str:
        """
        Extract field type from className

        Args:
            class_name: Java class name

        Returns:
            str: Field type (e.g., 'selectBox')
        """
        # Example: org.joget.apps.form.lib.SelectBox -> selectBox
        if '.' in class_name:
            return class_name.split('.')[-1].replace('SelectBox', 'selectBox')
        return class_name

    def _analyze_mdm_field(self, element: Dict, form_id: str, form_name: str, field_type: str):
        """
        Analyze a specific MDM field

        Args:
            element: Field element definition
            form_id: Form identifier
            form_name: Form display name
            field_type: Type of field
        """
        properties = element.get('properties', {})
        field_id = properties.get('id', 'unknown')
        field_label = properties.get('label', 'unknown')

        # Check options configuration
        options_config = {}
        options_source = 'static'  # default

        # Look for options binder configuration
        if 'options' in properties:
            options_config = properties['options']
            options_source = 'static'

        if 'optionsBinder' in properties:
            binder_config = properties['optionsBinder']
            if isinstance(binder_config, dict):
                binder_class = binder_config.get('className', '')
                options_source = self._identify_binder_type(binder_class)
                options_config = binder_config.get('properties', {})

        # Check for AJAX cascade
        has_ajax_cascade = False
        cascade_config = {}
        if properties.get('controlField') or properties.get('cascadeOptions'):
            has_ajax_cascade = True
            cascade_config = {
                'controlField': properties.get('controlField'),
                'cascadeOptions': properties.get('cascadeOptions', {})
            }

        # Only record if using external data source
        if options_source != 'static' or has_ajax_cascade:
            dependency = MDMDependency(
                form_id=form_id,
                form_name=form_name,
                field_id=field_id,
                field_label=field_label,
                field_type=field_type,
                options_source=options_source,
                options_config=options_config,
                has_ajax_cascade=has_ajax_cascade,
                cascade_config=cascade_config if has_ajax_cascade else None
            )

            self.dependencies.append(dependency)
            print(f"    Found MDM field: {field_id} ({options_source})")

    def _identify_binder_type(self, binder_class: str) -> str:
        """
        Identify options binder type from class name

        Args:
            binder_class: Java class name of binder

        Returns:
            str: Binder type identifier
        """
        for key, name in self.EXTERNAL_BINDERS.items():
            if key in binder_class.lower():
                return key
        return 'unknown'

    def _generate_statistics(self) -> Dict[str, Any]:
        """
        Generate statistics about MDM usage

        Returns:
            Dict: Statistics summary
        """
        stats = {
            'by_field_type': {},
            'by_options_source': {},
            'ajax_cascade_count': 0,
            'unique_forms_with_mdm': len(set(d.form_id for d in self.dependencies))
        }

        for dep in self.dependencies:
            # Count by field type
            stats['by_field_type'][dep.field_type] = \
                stats['by_field_type'].get(dep.field_type, 0) + 1

            # Count by options source
            stats['by_options_source'][dep.options_source] = \
                stats['by_options_source'].get(dep.options_source, 0) + 1

            # Count AJAX cascades
            if dep.has_ajax_cascade:
                stats['ajax_cascade_count'] += 1

        return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Analyze Joget application for MDM dependencies'
    )
    parser.add_argument(
        '--app-export',
        type=Path,
        required=True,
        help='Path to Joget application export (ZIP file)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output path for analysis report (JSON)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Validate input file exists
    if not args.app_export.exists():
        print(f"Error: Application export not found: {args.app_export}")
        sys.exit(1)

    # Create analyzer and run analysis
    analyzer = JogetAppAnalyzer(args.app_export)
    report = analyzer.analyze()

    # Save report
    output_data = asdict(report)

    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nAnalysis report saved to: {args.output}")

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Application: {report.application_name} ({report.application_id})")
    print(f"Total Forms: {report.total_forms}")
    print(f"Forms with MDM: {report.statistics['unique_forms_with_mdm']}")
    print(f"Total MDM Fields: {report.total_mdm_fields}")
    print(f"AJAX Cascades: {report.statistics['ajax_cascade_count']}")

    print("\nBy Field Type:")
    for field_type, count in report.statistics['by_field_type'].items():
        print(f"  {field_type}: {count}")

    print("\nBy Options Source:")
    for source, count in report.statistics['by_options_source'].items():
        print(f"  {source}: {count}")

    if report.warnings:
        print(f"\nWarnings ({len(report.warnings)}):")
        for warning in report.warnings:
            print(f"  ⚠️  {warning}")

    print("\n" + "="*60)


if __name__ == '__main__':
    main()
