# Medical Code-to-Phenotype Mapping Tool - Complete System Specification

## Overview
This document provides a complete specification for recreating a medical code-to-phenotype mapping tool from scratch. The tool converts ICD9, ICD10, and SNOMED codes to broader phenotyping diagnoses.

## Problem Statement
Healthcare datasets use different medical coding systems (ICD9, ICD10, SNOMED CT) to represent diagnoses. Researchers need to map these heterogeneous codes to standardized phenotype categories for epidemiological studies. The tool must handle:

1. Direct mapping from existing phenotype databases
2. ICD9→ICD10→Phenotype bridging via GEM mappings
3. Partial/hierarchical code matching
4. Batch processing capabilities
5. Multiple output formats with confidence scoring

## Data Structure Requirements

### Input Data Sources
1. **Phenotype CSV files** in folder structure:
   ```
   Medical conditions/
   ├── [PHENOTYPE_NAME]_birm_cam/
   │   ├── [PHENOTYPE_NAME]_birm_cam_ICD10.csv
   │   ├── [PHENOTYPE_NAME]_birm_cam_CPRD_AURUM.csv  (SNOMED codes)
   │   ├── [PHENOTYPE_NAME]_birm_cam_CPRD_GOLD.csv   (SNOMED codes)
   │   └── [PHENOTYPE_NAME]_birm_cam_IMRD.csv        (SNOMED codes)
   ```

2. **CSV Format** for phenotype files:
   ```
   MEDICAL_CODE_ID,DESCRIPTION,READ_CODE,SNOMED_CT_CODE,DATABASE
   ```

3. **ICD9-ICD10 Mapping file** (`icd10toicd9gem.csv`):
   ```
   icd10cm,icd9cm,flags,approximate,no_map,combination,scenario,choice_list
   ```

### Core Data Structures

```python
class PhenotypeMapper:
    def __init__(self):
        self.phenotype_index = {
            'icd10': defaultdict(set),    # ICD10_CODE -> {phenotype_names}
            'snomed': defaultdict(set),   # SNOMED_CODE -> {phenotype_names} 
            'icd9': defaultdict(set)      # ICD9_CODE -> {phenotype_names}
        }
        self.code_descriptions = {}       # CODE -> description_text
        self.phenotype_descriptions = {}  # CODE -> phenotype_name
        self.icd9_to_icd10_map = {}      # ICD9 -> {'icd10': code, 'approximate': bool}
        self.icd10_to_icd9_map = defaultdict(set)  # ICD10 -> {icd9_codes}
```

## Core Algorithm Specifications

### 1. Phenotype Index Construction
```python
def _build_phenotype_index(self):
    """
    ALGORITHM: Build comprehensive lookup index
    
    FOR each folder in Medical conditions/:
        IF folder ends with '_birm_cam':
            phenotype_name = folder.replace('_birm_cam.*', '')
            
            # Process ICD10 files
            IF exists([folder]/[folder]_ICD10.csv):
                PARSE CSV with headers: MEDICAL_CODE_ID,DESCRIPTION,READ_CODE,SNOMED_CT_CODE,DATABASE
                FOR each row:
                    code = row['MEDICAL_CODE_ID']
                    self.phenotype_index['icd10'][code].add(phenotype_name)
                    self.code_descriptions[code] = row['DESCRIPTION']
            
            # Process SNOMED files (CPRD_AURUM, CPRD_GOLD, IMRD)
            FOR each snomed_file in [CPRD_AURUM.csv, CPRD_GOLD.csv, IMRD.csv]:
                IF exists(snomed_file):
                    FOR each row:
                        medical_code = row['MEDICAL_CODE_ID']
                        snomed_code = row['SNOMED_CT_CODE']
                        # Index both medical_code and snomed_code if present
                        self.phenotype_index['snomed'][medical_code].add(phenotype_name)
                        IF snomed_code:
                            self.phenotype_index['snomed'][snomed_code].add(phenotype_name)
    """
```

### 2. ICD9-ICD10 Mapping Construction
```python
def _load_icd9_mapping(self):
    """
    ALGORITHM: Load ICD9↔ICD10 mappings
    
    PARSE icd10toicd9gem.csv
    FOR each row:
        icd10_code = row['icd10cm']
        icd9_code = row['icd9cm'] 
        approximate = int(row['approximate'])
        no_map = int(row['no_map'])
        
        IF no_map == 1 OR empty codes:
            SKIP
        
        icd9_formatted = _format_icd9_code(icd9_code)
        icd10_formatted = _format_icd10_code(icd10_code)
        
        # Store bidirectional mapping
        self.icd9_to_icd10_map[icd9_formatted] = {
            'icd10': icd10_formatted,
            'approximate': bool(approximate)
        }
        self.icd10_to_icd9_map[icd10_formatted].add(icd9_formatted)
        
        # If ICD10 has phenotype mapping, propagate to ICD9
        IF icd10_formatted in self.phenotype_index['icd10']:
            phenotypes = self.phenotype_index['icd10'][icd10_formatted]
            self.phenotype_index['icd9'][icd9_formatted].update(phenotypes)
    """
```

### 3. Code Formatting Rules
```python
def _format_icd9_code(self, code):
    """
    RULES:
    - IF starts with 'V' or 'E': return as-is
    - IF length >= 4 and no decimal: insert decimal after position 3
    - ELSE: return as-is
    
    EXAMPLES: "25000" -> "250.00", "V721" -> "V72.1", "250" -> "250"
    """

def _format_icd10_code(self, code):
    """
    RULES:
    - Convert to uppercase
    - IF length >= 4 and no decimal: insert decimal after position 3
    - ELSE: return as-is
    
    EXAMPLES: "e1100" -> "E11.00", "I48" -> "I48"
    """
```

### 4. Code Type Auto-Detection
```python
def _detect_code_type(self, medical_code):
    """
    REGEX PATTERNS:
    - ICD10: ^[A-Z]\d{2}(\.\d+)?$     (e.g., E11, I48.0, F90.1)
    - ICD9:  ^(\d{3}(\.\d+)?|[VE]\d{2}(\.\d+)?)$  (e.g., 250.00, V72.1, E849.9)
    - SNOMED: ^\d{6,18}$              (e.g., 192127007)
    
    RETURN: 'icd10', 'icd9', 'snomed', or 'unknown'
    """
```

### 5. Core Mapping Algorithm
```python
def map_code(self, medical_code, code_type='auto'):
    """
    ALGORITHM: Multi-step mapping with confidence scoring
    
    1. FORMAT INPUT:
       original_code = medical_code.strip()
       IF code_type == 'auto':
           code_type = _detect_code_type(original_code)
       formatted_code = _format_code_by_type(original_code, code_type)
    
    2. INITIALIZE RESULT:
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
    
    3. TRY DIRECT LOOKUP:
       phenotypes = self.phenotype_index[code_type].get(formatted_code)
       IF phenotypes:
           RETURN result with match_type='direct', confidence=1.0
    
    4. TRY MAPPED LOOKUP (ICD9 only):
       IF code_type == 'icd9' AND formatted_code in self.icd9_to_icd10_map:
           mapping_info = self.icd9_to_icd10_map[formatted_code]
           icd10_code = mapping_info['icd10']
           approximate = mapping_info['approximate']
           
           icd10_phenotypes = self.phenotype_index['icd10'].get(icd10_code)
           IF icd10_phenotypes:
               confidence = 0.9 if not approximate else 0.7
               RETURN result with match_type='mapped', confidence=confidence
    
    5. TRY PARTIAL MATCHING:
       partial_phenotypes = _find_partial_matches(formatted_code, code_type)
       IF partial_phenotypes:
           RETURN result with match_type='partial', confidence=0.5
    
    6. RETURN NO MATCH:
       RETURN result with match_type='none', confidence=0.0
    """
```

### 6. Partial Matching Algorithm
```python
def _find_partial_matches(self, medical_code, code_type):
    """
    ALGORITHM: Hierarchical prefix matching
    
    matches = set()
    code_base = medical_code.split('.')[0]  # Remove decimal part
    
    # Try exact base match
    IF code_base in self.phenotype_index[code_type]:
        matches.update(self.phenotype_index[code_type][code_base])
    
    # Try progressive prefix matching (4, 3, 2 characters)
    FOR length in [4, 3, 2]:
        IF len(code_base) > length:
            prefix = code_base[:length]
            FOR indexed_code in self.phenotype_index[code_type]:
                IF indexed_code.startswith(prefix):
                    matches.update(self.phenotype_index[code_type][indexed_code])
    
    RETURN matches
    """
```

## Command Line Interface Specification

### Required Arguments Structure
```python
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
```

### Usage Patterns
```bash
# Single code mapping
python phenotype_mapper.py --code E11
python phenotype_mapper.py --code 250.00 --code-type icd9

# Batch processing
python phenotype_mapper.py --batch-file codes.txt --output results.json

# Data export
python phenotype_mapper.py --export-mappings all_mappings.csv --format csv

# Statistics
python phenotype_mapper.py --stats
```

## Output Format Specifications

### Single Code Result
```json
{
  "input_code": "E11",
  "formatted_code": "E11", 
  "detected_type": "icd10",
  "phenotypes": ["Type2Diabetes_11_3_21"],
  "description": "Type 2 diabetes mellitus",
  "match_type": "direct",
  "confidence": 1.0,
  "mapping_path": "icd10 -> phenotype",
  "approximate_match": false
}
```

### Batch Processing Result
```json
[
  { /* individual result object */ },
  { /* individual result object */ },
  ...
]
```

### CSV Export Format
```csv
Code,Code_Type,Phenotype,Description
E11,icd10,Type2Diabetes_11_3_21,"Type 2 diabetes mellitus"
I48,icd10,AF_Bham_CAM,"Atrial fibrillation and flutter"
```

### Statistics Output
```json
{
  "total_phenotypes": 112,
  "icd10_codes": 1991,
  "snomed_codes": 34520,
  "icd9_codes": 20,
  "phenotype_list": ["ADHD_mm", "Type2Diabetes_11_3_21", ...]
}
```

## Error Handling Requirements

### File Processing Errors
```python
# Handle encoding issues in CSV files
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        # process file
except UnicodeDecodeError:
    print(f"Error processing {file_path}: encoding issue")
    # Continue processing other files
```

### Input Validation
```python
# Validate file paths
if not self.data_dir.exists():
    raise FileNotFoundError(f"Data directory {self.data_dir} not found")

# Validate code formats
if not medical_code.strip():
    return error_result("Empty code provided")
```

## Performance Requirements

### Expected Data Volumes
- ~112 phenotype categories
- ~1,991 ICD10 codes
- ~34,520 SNOMED codes  
- ~13,432 ICD9-ICD10 mappings
- Support for batch processing 1000+ codes

### Memory Optimization
- Use `defaultdict(set)` for sparse indices
- Lazy loading of mapping files
- Generator-based batch processing for large files

## Testing Requirements

### Unit Tests
```python
def test_code_detection():
    mapper = PhenotypeMapper()
    assert mapper._detect_code_type("E11") == "icd10"
    assert mapper._detect_code_type("250.00") == "icd9"
    assert mapper._detect_code_type("192127007") == "snomed"

def test_code_formatting():
    mapper = PhenotypeMapper()
    assert mapper._format_icd9_code("25000") == "250.00"
    assert mapper._format_icd10_code("e1100") == "E11.00"

def test_mapping_logic():
    # Test direct mapping
    # Test ICD9 bridging
    # Test partial matching
    # Test confidence scoring
```

### Integration Tests
```python
def test_batch_processing():
    # Create test file with known codes
    # Process batch
    # Verify all expected mappings found

def test_export_functionality():
    # Test JSON export
    # Test CSV export
    # Verify format compliance
```

## Dependencies

### Required Python Libraries
```python
import csv
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import argparse
```

### External Data Dependencies
- GEM mapping files (CMS ICD9↔ICD10)
- Phenotype category CSV files (user-provided)
- Standard Python 3.6+ installation

## Implementation Notes

### Critical Design Decisions
1. **Bidirectional ICD9↔ICD10 mapping**: Enables both forward and reverse lookups
2. **Set-based phenotype storage**: Handles many-to-many code-phenotype relationships
3. **Hierarchical matching**: Captures broader disease categories when exact matches fail
4. **Confidence scoring**: Provides transparency about mapping quality
5. **Format standardization**: Ensures consistent matching across coding systems

### Performance Optimizations
1. **Index pre-building**: All lookups use pre-computed dictionaries
2. **Lazy evaluation**: Only load mapping files when needed
3. **Memory-efficient structures**: Use generators for large batch operations
4. **Caching**: Store formatted codes to avoid re-computation

### Extensibility Points
1. **Additional coding systems**: Framework supports new code types
2. **Custom confidence functions**: Pluggable scoring algorithms
3. **Alternative matching strategies**: Configurable matching approaches
4. **Export formats**: Modular output system

This specification provides all necessary information to recreate the phenotype mapping tool from scratch, including algorithms, data structures, interface requirements, and implementation guidelines.