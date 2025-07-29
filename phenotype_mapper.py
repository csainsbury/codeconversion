#!/usr/bin/env python3
"""
Medical Code to Phenotype Conversion Tool

This tool converts ICD9, ICD10, and SNOMED codes to broader phenotyping diagnoses
based on the available phenotype categories in the Medical conditions folder.

Author: Generated with Claude Code
"""

import csv
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import argparse

class PhenotypeMapper:
    """
    Main class for mapping medical codes to phenotype categories.
    """
    
    def __init__(self, data_dir: str = "Medical conditions", mapping_file: str = "icd10toicd9gem.csv"):
        """
        Initialize the phenotype mapper.
        
        Args:  
            data_dir: Path to the directory containing phenotype CSV files
            mapping_file: Path to ICD9-ICD10 mapping file
        """
        self.data_dir = Path(data_dir)
        self.mapping_file = Path(mapping_file)
        self.phenotype_index = {
            'icd10': defaultdict(set),
            'snomed': defaultdict(set), 
            'icd9': defaultdict(set)  # Will be populated from mapping files
        }
        self.phenotype_descriptions = {}
        self.code_descriptions = {}
        self.icd9_to_icd10_map = {}  # ICD9 -> ICD10 mapping
        self.icd10_to_icd9_map = defaultdict(set)  # ICD10 -> set of ICD9 codes
        
        # Load existing phenotype data
        self._build_phenotype_index()
        # Load ICD9-ICD10 mapping
        self._load_icd9_mapping()
    
    def _extract_phenotype_name(self, folder_name: str) -> str:
        """
        Extract clean phenotype name from folder name by removing _birm_cam suffix.
        
        Args:
            folder_name: The folder name containing phenotype data
            
        Returns:
            Clean phenotype name
        """
        return re.sub(r'_birm_cam.*$', '', folder_name)
    
    def _build_phenotype_index(self):
        """
        Build comprehensive index of all medical codes to phenotype mappings
        from existing CSV files.
        """
        print("Building phenotype index from existing data...")
        
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory {self.data_dir} not found")
        
        # Find all phenotype folders
        phenotype_folders = [d for d in self.data_dir.iterdir() 
                           if d.is_dir() and '_birm_cam' in d.name]
        
        for folder in phenotype_folders:
            phenotype_name = self._extract_phenotype_name(folder.name)
            
            # Process ICD10 files
            icd10_file = folder / f"{folder.name}_ICD10.csv"
            if icd10_file.exists():
                self._process_csv_file(icd10_file, phenotype_name, 'icd10')
            
            # Process SNOMED files (CPRD_AURUM contains SNOMED codes)
            snomed_files = [
                folder / f"{folder.name}_CPRD_AURUM.csv",
                folder / f"{folder.name}_CPRD_GOLD.csv",
                folder / f"{folder.name}_IMRD.csv"
            ]
            
            for snomed_file in snomed_files:
                if snomed_file.exists():
                    self._process_csv_file(snomed_file, phenotype_name, 'snomed')
        
        print(f"Indexed {len(self.phenotype_index['icd10'])} ICD10 codes")
        print(f"Indexed {len(self.phenotype_index['snomed'])} SNOMED codes")
        print(f"Found {len(set(self.phenotype_descriptions.values()))} phenotype categories")
    
    def _load_icd9_mapping(self):
        """
        Load ICD9 to ICD10 mapping file and create bidirectional mappings.
        """
        if not self.mapping_file.exists():
            print(f"Warning: ICD9-ICD10 mapping file {self.mapping_file} not found")
            return
        
        print("Loading ICD9-ICD10 mapping...")
        
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    icd10_code = row.get('icd10cm', '').strip()
                    icd9_code = row.get('icd9cm', '').strip()
                    approximate = int(row.get('approximate', 0))
                    no_map = int(row.get('no_map', 0))
                    
                    # Skip if no mapping exists
                    if no_map or not icd9_code or not icd10_code:
                        continue
                    
                    # Format codes properly 
                    icd9_formatted = self._format_icd9_code(icd9_code)
                    icd10_formatted = self._format_icd10_code(icd10_code)
                    
                    # Store mappings
                    self.icd9_to_icd10_map[icd9_formatted] = {
                        'icd10': icd10_formatted,
                        'approximate': bool(approximate)
                    }
                    self.icd10_to_icd9_map[icd10_formatted].add(icd9_formatted)
                    
                    # If there's a corresponding phenotype for the ICD10 code,
                    # add the ICD9 code to the phenotype index
                    if icd10_formatted in self.phenotype_index['icd10']:
                        phenotypes = self.phenotype_index['icd10'][icd10_formatted]
                        self.phenotype_index['icd9'][icd9_formatted].update(phenotypes)
                        
                        # Also inherit the description
                        if icd10_formatted in self.code_descriptions:
                            self.code_descriptions[icd9_formatted] = self.code_descriptions[icd10_formatted]
            
            print(f"Loaded {len(self.icd9_to_icd10_map)} ICD9-ICD10 mappings")
            print(f"Indexed {len(self.phenotype_index['icd9'])} ICD9 codes with phenotype mappings")
            
        except Exception as e:
            print(f"Error loading ICD9-ICD10 mapping: {e}")
    
    def _format_icd9_code(self, code: str) -> str:
        """
        Format ICD9 code to standard format.
        
        Args:
            code: Raw ICD9 code
            
        Returns:
            Formatted ICD9 code
        """
        code = code.strip()
        
        # Handle V and E codes
        if code.startswith(('V', 'E')):
            return code
        
        # Add decimal point for numeric codes if needed
        if len(code) >= 4 and '.' not in code:
            return f"{code[:3]}.{code[3:]}"
        elif len(code) == 3:
            return code
        else:
            return code
    
    def _format_icd10_code(self, code: str) -> str:
        """
        Format ICD10 code to standard format.
        
        Args:
            code: Raw ICD10 code
            
        Returns:
            Formatted ICD10 code  
        """
        code = code.strip().upper()
        
        # Add decimal point if needed and code is long enough
        if len(code) >= 4 and '.' not in code:
            return f"{code[:3]}.{code[3:]}"
        else:
            return code
    
    def _process_csv_file(self, file_path: Path, phenotype_name: str, code_type: str):
        """
        Process a single CSV file and extract medical codes.
        
        Args:
            file_path: Path to the CSV file
            phenotype_name: Name of the phenotype category
            code_type: Type of medical code (icd10, snomed, etc.)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Extract the main medical code
                    medical_code = row.get('MEDICAL_CODE_ID', '').strip()
                    description = row.get('DESCRIPTION', '').strip()
                    snomed_code = row.get('SNOMED_CT_CODE', '').strip()
                    
                    if medical_code:
                        # Add to appropriate index
                        self.phenotype_index[code_type][medical_code].add(phenotype_name)
                        self.code_descriptions[medical_code] = description
                        self.phenotype_descriptions[medical_code] = phenotype_name
                        
                        # For SNOMED files, also index the SNOMED code if present
                        if code_type == 'snomed' and snomed_code:
                            self.phenotype_index['snomed'][snomed_code].add(phenotype_name)
                            self.code_descriptions[snomed_code] = description
                            self.phenotype_descriptions[snomed_code] = phenotype_name
                            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def map_code(self, medical_code: str, code_type: str = 'auto') -> Dict:
        """
        Map a medical code to phenotype categories.
        
        Args:
            medical_code: The medical code to map
            code_type: Type of code ('icd9', 'icd10', 'snomed', or 'auto')
            
        Returns:
            Dictionary containing mapping results
        """
        original_code = medical_code.strip()
        
        # Auto-detect code type if not specified
        if code_type == 'auto':
            code_type = self._detect_code_type(original_code)
        
        # Format the code based on its type
        if code_type == 'icd9':
            formatted_code = self._format_icd9_code(original_code)
        elif code_type == 'icd10':
            formatted_code = self._format_icd10_code(original_code)
        else:
            formatted_code = original_code.upper()
        
        # Initialize result structure
        result = {
            'input_code': original_code,
            'formatted_code': formatted_code,
            'detected_type': code_type,
            'phenotypes': [],
            'description': '',
            'match_type': 'none',
            'confidence': 0.0,
            'mapping_path': '',
            'approximate_match': False
        }
        
        # Try direct lookup first
        phenotypes = self.phenotype_index[code_type].get(formatted_code, set())
        
        if phenotypes:
            result.update({
                'phenotypes': list(phenotypes),
                'description': self.code_descriptions.get(formatted_code, ''),
                'match_type': 'direct',
                'confidence': 1.0,
                'mapping_path': f"{code_type} -> phenotype"
            })
            return result
        
        # For ICD9 codes, try mapping through ICD10
        if code_type == 'icd9' and formatted_code in self.icd9_to_icd10_map:
            mapping_info = self.icd9_to_icd10_map[formatted_code]
            icd10_code = mapping_info['icd10']
            approximate = mapping_info['approximate']
            
            # Look up phenotypes for the mapped ICD10 code
            icd10_phenotypes = self.phenotype_index['icd10'].get(icd10_code, set())
            
            if icd10_phenotypes:
                result.update({
                    'phenotypes': list(icd10_phenotypes),
                    'description': self.code_descriptions.get(icd10_code, ''),
                    'match_type': 'mapped',
                    'confidence': 0.9 if not approximate else 0.7,
                    'mapping_path': f"icd9 -> icd10 ({icd10_code}) -> phenotype",
                    'approximate_match': approximate
                })
                return result
        
        # Try partial matches if no direct or mapped match found
        partial_phenotypes = self._find_partial_matches(formatted_code, code_type)
        if partial_phenotypes:
            result.update({
                'phenotypes': list(partial_phenotypes),
                'description': self.code_descriptions.get(formatted_code, ''),
                'match_type': 'partial',
                'confidence': 0.5,
                'mapping_path': f"{code_type} -> phenotype (partial match)"
            })
        
        return result
    
    def _detect_code_type(self, medical_code: str) -> str:
        """
        Auto-detect the type of medical code based on format patterns.
        
        Args:
            medical_code: The medical code to analyze
            
        Returns:
            Detected code type
        """
        medical_code = medical_code.strip()
        
        # ICD10 patterns: Letter followed by numbers with optional decimal
        if re.match(r'^[A-Z]\d{2}(\.\d+)?$', medical_code):
            return 'icd10'
        
        # ICD9 patterns: Numbers with optional decimal, or V/E codes
        if re.match(r'^(\d{3}(\.\d+)?|[VE]\d{2}(\.\d+)?)$', medical_code):
            return 'icd9'
        
        # SNOMED codes are typically long numeric strings
        if re.match(r'^\d{6,18}$', medical_code):
            return 'snomed'
        
        # Default fallback - try all types
        return 'unknown'
    
    def _find_partial_matches(self, medical_code: str, code_type: str) -> Set[str]:
        """
        Find partial matches for a medical code.
        
        Args:
            medical_code: The medical code to match
            code_type: Type of medical code
            
        Returns:
            Set of matching phenotype names
        """
        matches = set()
        
        # Try matching without decimal points
        code_base = medical_code.split('.')[0]
        if code_base in self.phenotype_index[code_type]:
            matches.update(self.phenotype_index[code_type][code_base])
        
        # Try prefix matching for hierarchical codes
        for length in [4, 3, 2]:
            if len(code_base) > length:
                prefix = code_base[:length]
                for indexed_code in self.phenotype_index[code_type]:
                    if indexed_code.startswith(prefix):
                        matches.update(self.phenotype_index[code_type][indexed_code])
        
        return matches
    
    def map_codes_batch(self, codes: List[str], code_type: str = 'auto') -> List[Dict]:
        """
        Map multiple medical codes to phenotypes.
        
        Args:
            codes: List of medical codes to map
            code_type: Type of codes or 'auto' for auto-detection
            
        Returns:
            List of mapping results
        """
        results = []
        for code in codes:
            result = self.map_code(code, code_type)
            results.append(result)
        
        return results
    
    def get_phenotype_stats(self) -> Dict:
        """
        Get statistics about the loaded phenotype data.
        
        Returns:
            Dictionary containing statistics
        """
        all_phenotypes = set()
        for code_dict in self.phenotype_index.values():
            for phenotype_set in code_dict.values():
                all_phenotypes.update(phenotype_set)
        
        return {
            'total_phenotypes': len(all_phenotypes),
            'icd10_codes': len(self.phenotype_index['icd10']),
            'snomed_codes': len(self.phenotype_index['snomed']),
            'icd9_codes': len(self.phenotype_index['icd9']),
            'phenotype_list': sorted(list(all_phenotypes))
        }
    
    def export_mappings(self, output_file: str, format: str = 'json'):
        """
        Export all mappings to a file.
        
        Args:
            output_file: Path to output file
            format: Export format ('json' or 'csv')
        """
        if format == 'json':
            # Convert sets to lists for JSON serialization
            export_data = {}
            for code_type, code_dict in self.phenotype_index.items():
                export_data[code_type] = {
                    code: list(phenotypes) 
                    for code, phenotypes in code_dict.items()
                }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Code', 'Code_Type', 'Phenotype', 'Description'])
                
                for code_type, code_dict in self.phenotype_index.items():
                    for code, phenotypes in code_dict.items():
                        description = self.code_descriptions.get(code, '')
                        for phenotype in phenotypes:
                            writer.writerow([code, code_type, phenotype, description])

def main():
    """Command line interface for the phenotype mapper."""
    parser = argparse.ArgumentParser(description='Map medical codes to phenotype categories')
    parser.add_argument('--data-dir', default='Medical conditions', 
                       help='Directory containing phenotype CSV files')
    parser.add_argument('--code', help='Single medical code to map')
    parser.add_argument('--code-type', choices=['icd9', 'icd10', 'snomed', 'auto'], 
                       default='auto', help='Type of medical code')
    parser.add_argument('--batch-file', help='File containing codes to map (one per line)')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--format', choices=['json', 'csv'], default='json',
                       help='Output format')
    parser.add_argument('--stats', action='store_true', 
                       help='Show statistics about loaded data')
    parser.add_argument('--export-mappings', help='Export all mappings to file')
    
    args = parser.parse_args()
    
    # Initialize mapper
    try:
        mapper = PhenotypeMapper(args.data_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    # Show stats if requested
    if args.stats:
        stats = mapper.get_phenotype_stats()
        print("\nPhenotype Mapping Statistics:")
        print(f"Total phenotype categories: {stats['total_phenotypes']}")
        print(f"ICD10 codes indexed: {stats['icd10_codes']}")
        print(f"SNOMED codes indexed: {stats['snomed_codes']}")
        print(f"ICD9 codes indexed: {stats['icd9_codes']}")
        print(f"\nAvailable phenotypes: {', '.join(stats['phenotype_list'])}")
        return 0
    
    # Export mappings if requested
    if args.export_mappings:
        mapper.export_mappings(args.export_mappings, args.format)
        print(f"Mappings exported to {args.export_mappings}")
        return 0
    
    # Process single code
    if args.code:
        result = mapper.map_code(args.code, args.code_type)
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
        return 0
    
    # Process batch file
    if args.batch_file:
        try:
            with open(args.batch_file, 'r') as f:
                codes = [line.strip() for line in f if line.strip()]
            
            results = mapper.map_codes_batch(codes, args.code_type)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
            else:
                print(json.dumps(results, indent=2))
            
        except FileNotFoundError:
            print(f"Error: Batch file {args.batch_file} not found")
            return 1
        
        return 0
    
    # If no specific action, show help
    parser.print_help()
    return 0

if __name__ == '__main__':
    exit(main())