# Medical Code to Phenotype Conversion Tool

## Overview

This tool converts medical codes (ICD9, ICD10, and SNOMED) to broader phenotyping diagnoses based on the phenotype categories available in your Medical conditions folder. It enables researchers to map specific medical codes to high-level disease categories for epidemiological studies and data analysis.

## Features

- **Multi-format Support**: Handles ICD9, ICD10, and SNOMED CT codes
- **ICD9 to ICD10 Mapping**: Uses GEM (General Equivalence Mappings) for ICD9→ICD10→Phenotype conversion
- **Auto-detection**: Automatically detects code type based on format patterns
- **Batch Processing**: Process multiple codes from a file
- **Multiple Output Formats**: JSON and CSV export options
- **Confidence Scoring**: Rates the quality of matches (1.0 = exact, 0.7-0.9 = mapped, 0.5 = partial)
- **Comprehensive Coverage**: Maps to 112+ phenotype categories

## Installation

No installation required. Just ensure you have Python 3.6+ installed and the required files in your directory:

- `phenotype_mapper.py` - Main tool
- `Medical conditions/` - Directory with phenotype CSV files
- `icd10toicd9gem.csv` - ICD9↔ICD10 mapping file

## Quick Start

### Single Code Mapping
```bash
# Map a single ICD10 code
python phenotype_mapper.py --code E11

# Map an ICD9 code (auto-detected)
python phenotype_mapper.py --code 250.00

# Map a SNOMED code
python phenotype_mapper.py --code 192127007

# Force code type if auto-detection fails
python phenotype_mapper.py --code 250.00 --code-type icd9
```

### Batch Processing
```bash
# Create a file with codes (one per line)
echo -e "E11\\nI48\\nF90.0\\n192127007" > my_codes.txt

# Process all codes
python phenotype_mapper.py --batch-file my_codes.txt --output results.json

# Export results to CSV format
python phenotype_mapper.py --batch-file my_codes.txt --output results.csv --format csv
```

### Data Export
```bash
# Export all available mappings to CSV
python phenotype_mapper.py --export-mappings all_mappings.csv --format csv

# Export to JSON format
python phenotype_mapper.py --export-mappings all_mappings.json --format json

# Get statistics about loaded data
python phenotype_mapper.py --stats
```

## Output Format

The tool returns detailed mapping information:

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

### Match Types
- **direct**: Exact match found in phenotype database
- **mapped**: ICD9 code mapped via ICD10 equivalent
- **partial**: Hierarchical/prefix match (e.g., E11 matches E11.0, E11.1, etc.)
- **none**: No mapping found

### Confidence Scores
- **1.0**: Exact direct match
- **0.9**: Exact mapped match (ICD9→ICD10)
- **0.7**: Approximate mapped match
- **0.5**: Partial/hierarchical match
- **0.0**: No match found

## Available Phenotype Categories

The tool maps codes to 112+ phenotype categories including:

**Mental Health**: ADHD, Anxiety, Depression, Bipolar, Autism, PTSD, etc.
**Cardiovascular**: Heart failure, atrial fibrillation, hypertension, etc.
**Diabetes/Endocrine**: Type 1/2 diabetes, thyroid disorders, etc.
**Cancer**: Breast, lung, prostate cancers, metastatic cancer, etc.
**Neurological**: Alzheimer's, Parkinson's, MS, epilepsy, etc.

Run `python phenotype_mapper.py --stats` for the complete list.

## Code Type Detection

The tool automatically detects code types using these patterns:

- **ICD10**: `[A-Z]\d{2}(\.\d+)?` (e.g., E11, I48.0, F90.1)
- **ICD9**: `\d{3}(\.\d+)?` or `[VE]\d{2}(\.\d+)?` (e.g., 250.00, V72.1, E849.9)
- **SNOMED**: `\d{6,18}` (e.g., 192127007, 464511000000105)

## Limitations

1. **ICD9 Coverage**: Only ~20 ICD9 codes have direct phenotype mappings (those with ICD10 equivalents in your phenotype database)
2. **Encoding Issues**: Some CSV files may have encoding issues (noted in tool output)
3. **Partial Matches**: May return multiple phenotypes for broad codes
4. **Data Dependencies**: Accuracy depends on the completeness of your phenotype CSV files

## File Structure

```
phenotypes/
├── phenotype_mapper.py           # Main conversion tool
├── generate_summary_report.py    # Generate comprehensive report
├── icd10toicd9gem.csv           # ICD9↔ICD10 mapping file
├── Medical conditions/           # Phenotype data directory
│   ├── ADHD_mm_birm_cam/
│   │   ├── ADHD_mm_birm_cam_ICD10.csv
│   │   ├── ADHD_mm_birm_cam_CPRD_AURUM.csv
│   │   └── ...
│   └── Type2Diabetes_11_3_21_birm_cam/
│       ├── Type2Diabetes_11_3_21_birm_cam_ICD10.csv
│       └── ...
└── README_PHENOTYPE_MAPPER.md   # This file
```

## Advanced Usage

### Python Integration
```python
from phenotype_mapper import PhenotypeMapper

# Initialize mapper
mapper = PhenotypeMapper()

# Map single code
result = mapper.map_code("E11")
print(result['phenotypes'])  # ['Type2Diabetes_11_3_21']

# Batch mapping
codes = ["E11", "I48", "F90.0"]
results = mapper.map_codes_batch(codes)

# Get statistics
stats = mapper.get_phenotype_stats()
print(f"Total phenotypes: {stats['total_phenotypes']}")
```

## Future Enhancements

- Add support for ICD-O-3 oncology codes
- Implement direct SNOMED→ICD9 mappings
- Add fuzzy string matching for partial code matches
- Create web interface for easier use
- Add validation against standard medical ontologies

## Support

For issues or questions:
1. Check that all required files are present
2. Verify CSV file encodings (some may need UTF-8 conversion)
3. Review the comprehensive report: `python generate_summary_report.py`
4. Check the tool's statistics: `python phenotype_mapper.py --stats`

---

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>