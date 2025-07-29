# Medical Code-to-Phenotype Mapping Tool 🏥

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive tool for mapping medical codes (ICD-9, ICD-10, SNOMED CT) to standardized phenotype categories for epidemiological research and clinical data analysis.

## 🚀 Quick Start

```bash
# Map a single medical code
python phenotype_mapper.py --code E11

# Process multiple codes from a file
python phenotype_mapper.py --batch-file my_codes.txt --output results.json

# Get comprehensive statistics
python phenotype_mapper.py --stats

# Generate detailed report
python generate_summary_report.py
```

## ✨ Features

- **🔄 Multi-format Support**: Handles ICD-9, ICD-10, and SNOMED CT codes
- **🌉 ICD-9 Bridging**: Maps ICD-9 codes via ICD-10 equivalents using official GEM mappings
- **🤖 Auto-detection**: Automatically identifies code type based on format patterns
- **📊 Batch Processing**: Process thousands of codes efficiently
- **📈 Confidence Scoring**: Provides reliability scores for all mappings (0.0-1.0)
- **📋 Multiple Outputs**: JSON and CSV export formats
- **🎯 Comprehensive Coverage**: Maps to 112+ phenotype categories
- **⚡ High Performance**: Optimized for large-scale healthcare datasets

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Phenotype Categories](#phenotype-categories)
- [Output Format](#output-format)
- [API Reference](#api-reference)
- [Academic Usage](#academic-usage)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Installation

### Prerequisites
- Python 3.6 or higher
- No additional dependencies required (uses only standard library)

### Setup
```bash
git clone <repository-url>
cd phenotypes
# No installation required - ready to use!
```

### Data Requirements
- **Phenotype CSV files** in `Medical conditions/` directory
- **ICD-9↔ICD-10 mapping file** (`icd10toicd9gem.csv`) - included

## 📖 Usage

### Single Code Mapping
```bash
# ICD-10 code (auto-detected)
python phenotype_mapper.py --code E11
# Output: Type2Diabetes_11_3_21

# ICD-9 code with type specification
python phenotype_mapper.py --code 250.00 --code-type icd9

# SNOMED CT code
python phenotype_mapper.py --code 192127007
# Output: ADHD_mm
```

### Batch Processing
```bash
# Create input file
echo -e "E11\nI48\nF90.0\n192127007" > codes.txt

# Process batch
python phenotype_mapper.py --batch-file codes.txt --output results.json

# Export to CSV format
python phenotype_mapper.py --batch-file codes.txt --output results.csv --format csv
```

### Data Export and Analysis
```bash
# Export all available mappings
python phenotype_mapper.py --export-mappings all_mappings.csv --format csv

# View comprehensive statistics
python phenotype_mapper.py --stats

# Generate detailed analysis report
python generate_summary_report.py
```

## 🏥 Phenotype Categories

The tool maps medical codes to **112+ phenotype categories** across major clinical domains:

| Domain | Categories | Examples |
|--------|------------|----------|
| **Mental Health** | 8 | ADHD, Depression, Anxiety, Bipolar, Autism, PTSD |
| **Cardiovascular** | 10+ | Heart Failure, Atrial Fibrillation, Hypertension, MI |
| **Endocrine** | 5 | Type 1/2 Diabetes, Thyroid Disorders, Addison's Disease |
| **Oncology** | 7+ | Breast Cancer, Lung Cancer, Metastatic Cancer |
| **Neurological** | 6+ | Alzheimer's, Parkinson's, MS, Epilepsy |
| **Other** | 70+ | Respiratory, GI, Rheumatological, and more |

<details>
<summary>View complete phenotype list</summary>

Run `python phenotype_mapper.py --stats` to see all 112 available phenotype categories.

</details>

## 📊 Output Format

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

### Match Types & Confidence Scores

| Match Type | Confidence | Description |
|------------|------------|-------------|
| `direct` | 1.0 | Exact match in phenotype database |
| `mapped` | 0.9 | ICD-9 mapped via exact ICD-10 equivalent |
| `mapped` | 0.7 | ICD-9 mapped via approximate ICD-10 equivalent |
| `partial` | 0.5 | Hierarchical/prefix match |
| `none` | 0.0 | No mapping found |

## 🔧 API Reference

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

### Command Line Options
```bash
python phenotype_mapper.py [OPTIONS]

Options:
  --code TEXT              Single medical code to map
  --code-type [icd9|icd10|snomed|auto]  Force code type (default: auto)
  --batch-file TEXT        File with codes (one per line)
  --output TEXT            Output file path
  --format [json|csv]      Output format (default: json)
  --stats                  Show mapping statistics
  --export-mappings TEXT   Export all mappings to file
  --data-dir TEXT          Phenotype data directory (default: Medical conditions)
```

## 📚 Academic Usage

### Citation
If you use this tool in academic research, please cite:

```bibtex
@software{phenotype_mapper_2025,
  title={Medical Code-to-Phenotype Mapping Tool},
  author={Author Name},
  year={2025},
  url={https://github.com/username/phenotypes},
  note={Generated with Claude Code}
}
```

### Methods Description
A detailed LaTeX methods section is available in [`methods_preprint.tex`](methods_preprint.tex) for inclusion in academic papers.

### Coverage Statistics
- **36,531 total medical codes** indexed
- **1,991 ICD-10 codes** with direct phenotype mappings
- **34,520 SNOMED CT codes** with direct phenotype mappings  
- **13,432 ICD-9↔ICD-10 mappings** via official GEM files
- **112 phenotype categories** across all major clinical domains

## 🏗️ Architecture

### Core Components
```
phenotype_mapper.py          # Main mapping engine
├── PhenotypeMapper         # Core mapping class
├── Code detection          # Auto-identification of code types
├── Direct mapping          # ICD-10/SNOMED → phenotype
├── Bridged mapping         # ICD-9 → ICD-10 → phenotype
└── Batch processing        # High-throughput operations

generate_summary_report.py  # Analysis and reporting
README_PHENOTYPE_MAPPER.md  # Detailed user documentation
SYSTEM_SPECIFICATION.md     # Complete technical specification
methods_preprint.tex         # Academic methods description
```

### Data Flow
```
Input Code → Format Detection → Code Standardization → Index Lookup → Confidence Scoring → Output
     ↓
ICD-9: Code → GEM Mapping → ICD-10 → Phenotype Lookup → Result
ICD-10/SNOMED: Code → Direct Lookup → Result
```

## 🧪 Testing

### Run Tests
```bash
# Test with sample codes
python phenotype_mapper.py --batch-file test_codes.txt

# Validate mappings
python generate_summary_report.py

# Check system integrity
python phenotype_mapper.py --stats
```

### Sample Test Cases
```python
# Test cases included in test_codes.txt
E11        # Type 2 Diabetes (ICD-10)
I48        # Atrial Fibrillation (ICD-10)
F90.0      # ADHD (ICD-10)
250.00     # Diabetes (ICD-9)
192127007  # ADHD (SNOMED)
```

## 🚨 Limitations

- **ICD-9 Coverage**: Limited to codes with ICD-10 equivalents (~20 direct mappings)
- **Data Dependencies**: Accuracy depends on completeness of phenotype CSV files
- **Encoding Issues**: Some legacy CSV files may have character encoding problems
- **Context Independence**: Mappings don't consider clinical context or patient history

## 🔮 Future Enhancements

- [ ] Support for ICD-O-3 oncology codes
- [ ] Direct SNOMED → ICD-9 mappings
- [ ] Fuzzy string matching for partial codes
- [ ] Web-based interface
- [ ] Integration with FHIR terminology services
- [ ] Support for ICD-11 codes
- [ ] Machine learning-based confidence estimation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
```bash
git clone <repository-url>
cd phenotypes
# Make your changes
python phenotype_mapper.py --stats  # Test basic functionality
```

### Reporting Issues
Please include:
- Input code(s) that caused the issue
- Expected vs. actual output
- Your system information (Python version, OS)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Clinical Research Teams**: Birmingham and Cambridge collaborators for phenotype definitions
- **CMS**: For providing official GEM mapping files
- **SNOMED International**: For SNOMED CT terminology
- **WHO**: For ICD coding standards
- **Claude Code**: For AI-assisted development

## 📞 Support

- 📖 **Documentation**: See [`README_PHENOTYPE_MAPPER.md`](README_PHENOTYPE_MAPPER.md) for detailed usage
- 🔧 **Technical Specification**: See [`SYSTEM_SPECIFICATION.md`](SYSTEM_SPECIFICATION.md) for implementation details
- 📊 **Analysis**: Run `python generate_summary_report.py` for comprehensive tool analysis
- 🐛 **Issues**: Use GitHub Issues for bug reports and feature requests

---

<div align="center">

**🤖 Generated with [Claude Code](https://claude.ai/code)**

**Co-Authored-By: Claude <noreply@anthropic.com>**

*Making healthcare data interoperable, one code at a time* 🩺

</div>