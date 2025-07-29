#!/usr/bin/env python3
"""
Generate a comprehensive summary report of the phenotype mapping tool capabilities.
"""

from phenotype_mapper import PhenotypeMapper
import json

def generate_report():
    """Generate comprehensive mapping report."""
    
    print("Generating Phenotype Mapping Summary Report...")
    print("=" * 60)
    
    # Initialize mapper
    mapper = PhenotypeMapper()
    
    # Get statistics
    stats = mapper.get_phenotype_stats()
    
    print(f"\n📊 PHENOTYPE MAPPING STATISTICS")
    print(f"{'─' * 40}")
    print(f"Total phenotype categories: {stats['total_phenotypes']}")
    print(f"ICD10 codes indexed: {stats['icd10_codes']:,}")
    print(f"SNOMED codes indexed: {stats['snomed_codes']:,}")
    print(f"ICD9 codes with mappings: {stats['icd9_codes']:,}")
    print(f"Total ICD9-ICD10 mappings: {len(mapper.icd9_to_icd10_map):,}")
    
    print(f"\n🏥 AVAILABLE PHENOTYPE CATEGORIES")
    print(f"{'─' * 40}")
    
    # Group phenotypes by category for better readability
    phenotypes = sorted(stats['phenotype_list'])
    
    categories = {
        'Mental Health': [],
        'Cardiovascular': [],
        'Diabetes/Endocrine': [],
        'Cancer': [],
        'Neurological': [],
        'Other': []
    }
    
    for phenotype in phenotypes:
        p_lower = phenotype.lower()
        if any(term in p_lower for term in ['anxiety', 'depression', 'bipolar', 'adhd', 'autism', 'ptsd', 'psychosis', 'eating']):
            categories['Mental Health'].append(phenotype)
        elif any(term in p_lower for term in ['cardiac', 'heart', 'hypertension', 'arrhythmia', 'af_', 'ihd', 'mi', 'aneurysm']):
            categories['Cardiovascular'].append(phenotype)
        elif any(term in p_lower for term in ['diabetes', 'thyroid', 'addison']):
            categories['Diabetes/Endocrine'].append(phenotype)
        elif any(term in p_lower for term in ['cancer', 'ca_', 'metastatic', 'breast', 'lung', 'colon', 'prostate', 'skin']):
            categories['Cancer'].append(phenotype)
        elif any(term in p_lower for term in ['alzheimer', 'dementia', 'parkinson', 'ms_', 'epilepsy', 'migraine']):
            categories['Neurological'].append(phenotype)
        else:
            categories['Other'].append(phenotype)
    
    for category, items in categories.items():
        if items:
            print(f"\n  {category} ({len(items)} conditions):")
            for item in items[:10]:  # Show first 10
                print(f"    • {item}")
            if len(items) > 10:
                print(f"    ... and {len(items) - 10} more")
    
    print(f"\n🔧 EXAMPLE MAPPINGS")
    print(f"{'─' * 40}")
    
    # Test some example codes
    test_cases = [
        ("E11", "Type 2 Diabetes (ICD10)"),
        ("I48", "Atrial Fibrillation (ICD10)"), 
        ("F90.0", "ADHD (ICD10)"),
        ("192127007", "ADHD (SNOMED)"),
        ("250", "Diabetes (ICD9 - via ICD10 mapping)")
    ]
    
    for code, description in test_cases:
        result = mapper.map_code(code)
        phenotypes_str = ", ".join(result['phenotypes']) if result['phenotypes'] else "No mapping found"
        confidence = result['confidence']
        match_type = result['match_type']
        
        print(f"\n  {code} → {description}")
        print(f"    Phenotypes: {phenotypes_str}")
        print(f"    Match type: {match_type}, Confidence: {confidence:.1f}")
        if result['mapping_path']:
            print(f"    Mapping path: {result['mapping_path']}")
    
    print(f"\n📋 TOOL CAPABILITIES")
    print(f"{'─' * 40}")
    print("✅ Direct ICD10 → Phenotype mapping")
    print("✅ Direct SNOMED → Phenotype mapping") 
    print("✅ ICD9 → ICD10 → Phenotype mapping (via GEM files)")
    print("✅ Partial/hierarchical code matching")
    print("✅ Batch processing from file")
    print("✅ Multiple output formats (JSON, CSV)")
    print("✅ Confidence scoring")
    print("✅ Auto-detection of code types")
    print("✅ Comprehensive coverage of ~112 phenotype categories")
    
    print(f"\n🚀 USAGE EXAMPLES")
    print(f"{'─' * 40}")
    print("# Map single code:")
    print("python phenotype_mapper.py --code E11")
    print("\n# Batch process codes from file:")
    print("python phenotype_mapper.py --batch-file codes.txt --output results.json")
    print("\n# Export all mappings to CSV:")
    print("python phenotype_mapper.py --export-mappings all_mappings.csv --format csv")
    print("\n# Get statistics:")
    print("python phenotype_mapper.py --stats")
    
    print(f"\n💡 NEXT STEPS FOR ENHANCEMENT")
    print(f"{'─' * 40}")
    print("• Add more sophisticated fuzzy matching algorithms")
    print("• Implement SNOMED → ICD9 direct mappings")
    print("• Add support for ICD-O-3 oncology codes")
    print("• Create web interface for easier use")
    print("• Add validation against known medical ontologies")
    print("• Implement code hierarchy browsing")
    
    print(f"\n{'=' * 60}")
    print("Report generated successfully! 🎉")

if __name__ == '__main__':
    generate_report()