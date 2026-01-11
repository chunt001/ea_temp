#!/usr/bin/env python3
"""
Excel to JSON Converter for Legal Affairs EA Assessment
Converts Business-Technology Assessment Excel file to JSON data files
"""

import pandas as pd
import json
import sys
import os
from pathlib import Path

def convert_strategic_importance(val):
    mapping = {
        'Mission-Critical': 5,
        'Important': 4,
        'Supporting': 3,
        'Nice-to-Have': 2,
        'Minimal': 1
    }
    return mapping.get(val, 3)

def convert_operational_health(val):
    mapping = {
        'Healthy': 5,
        'Moderate Concerns': 3,
        'Unhealthy': 2
    }
    return mapping.get(val, 3)

def convert_automation_level(val):
    mapping = {
        'Highly Automated': 5,
        'Partially Automated': 3,
        'Mostly Manual': 2,
        'Fully Manual': 1
    }
    return mapping.get(val, 2)

def convert_technology_fit(val):
    mapping = {
        'Excellent Fit': 5,
        'Adequate Fit': 3,
        'Poor Fit': 1
    }
    return mapping.get(val, 3)

def process_excel_file(excel_path, output_dir):
    """Process Excel file and generate JSON data files"""
    
    print(f"Reading Excel file: {excel_path}")
    
    try:
        # Read Excel file
        xl_file = pd.ExcelFile(excel_path)
        
        # Validate required sheets
        required_sheets = [
            'Business Capability Catalog',
            'BH Assessment',
            'BTF Assessment',
            'Bus-Tech Map'
        ]
        
        missing_sheets = [s for s in required_sheets if s not in xl_file.sheet_names]
        if missing_sheets:
            print(f"ERROR: Missing required sheets: {', '.join(missing_sheets)}")
            print(f"Available sheets: {', '.join(xl_file.sheet_names)}")
            return False
        
        # Read capabilities (raw to preserve structure)
        print("Processing Business Capability Catalog...")
        cap_raw = pd.read_excel(excel_path, sheet_name='Business Capability Catalog', header=None)
        
        # Read assessments
        print("Processing BH Assessment...")
        bh_assessment = pd.read_excel(excel_path, sheet_name='BH Assessment', header=2)
        bh_assessment.columns = ['ID', 'L1 Capability', 'L2 Capability', 'Capability Owner', 'Assessment Date', 
                                  'Strategic Importance', 'Operational Health', 'Priority Score', 'Priority Level', 
                                  'Recommended Business Action', 'Notes / Rationale']
        bh_assessment = bh_assessment.dropna(subset=['ID'])
        
        print("Processing BTF Assessment...")
        btf_assessment = pd.read_excel(excel_path, sheet_name='BTF Assessment', header=2)
        btf_assessment.columns = ['ID', 'L1 Capability', 'L2 Capability', 'Process Owner', 'Assessment Date',
                                  'Automation Level', 'Technology Fit', 'Recommended Action', 'Description', 'Notes / Rationale']
        btf_assessment = btf_assessment.dropna(subset=['ID'])
        
        print("Processing Bus-Tech Map...")
        bus_tech_map = pd.read_excel(excel_path, sheet_name='Bus-Tech Map', header=2)
        bus_tech_map.columns = ['L2 Capability', 'Technology', 'Role']
        bus_tech_map = bus_tech_map.dropna(subset=['L2 Capability'])
        bus_tech_map = bus_tech_map[bus_tech_map['Technology'] != 'Application Name']
        
        # Extract L1 capabilities (rows 4-11 typically)
        print("Extracting L1 capabilities...")
        l1_capabilities = []
        for i in range(4, 12):
            if i < len(cap_raw) and pd.notna(cap_raw.iloc[i, 0]):
                l1_id = cap_raw.iloc[i, 0]
                l1_name = cap_raw.iloc[i, 1]
                l1_desc = cap_raw.iloc[i, 2] if pd.notna(cap_raw.iloc[i, 2]) else ""
                l1_capabilities.append({
                    'id': l1_id,
                    'name': l1_name,
                    'description': l1_desc
                })
        
        print(f"Found {len(l1_capabilities)} L1 capabilities")
        
        # Build capability structure
        print("Building capability structure...")
        capability_data = {
            'capabilities': [],
            'maturity_levels': {
                '1': {'label': 'Critical Gap', 'description': 'Unhealthy / Poor Fit', 'color': '#d32f2f'},
                '2': {'label': 'Needs Improvement', 'description': 'Unhealthy / Mostly Manual', 'color': '#f57c00'},
                '3': {'label': 'Adequate', 'description': 'Moderate Concerns / Adequate Fit', 'color': '#fbc02d'},
                '4': {'label': 'Good', 'description': 'Between Adequate and Excellent', 'color': '#7cb342'},
                '5': {'label': 'Excellent', 'description': 'Healthy / Excellent Fit', 'color': '#388e3c'}
            },
            'scoring_methodology': {
                'strategic_importance': {
                    'Mission-Critical': 5,
                    'Important': 4,
                    'Supporting': 3
                },
                'operational_health': {
                    'Healthy': 5,
                    'Moderate Concerns': 3,
                    'Unhealthy': 2
                },
                'automation_level': {
                    'Highly Automated': 5,
                    'Partially Automated': 3,
                    'Mostly Manual': 2,
                    'Fully Manual': 1
                },
                'technology_fit': {
                    'Excellent Fit': 5,
                    'Adequate Fit': 3,
                    'Poor Fit': 1
                }
            }
        }
        
        for l1 in l1_capabilities:
            l1_data = {
                'l1_id': l1['id'],
                'l1_name': l1['name'],
                'l1_description': l1['description'],
                'l2_capabilities': []
            }
            
            # Get L2 capabilities for this L1
            l2_caps = bh_assessment[bh_assessment['L1 Capability'] == l1['name']]
            
            for _, l2_row in l2_caps.iterrows():
                l2_id = l2_row['ID']
                l2_name = l2_row['L2 Capability']
                
                # Get BTF assessment
                btf_row = btf_assessment[btf_assessment['ID'] == l2_id]
                
                # Get technologies
                techs = bus_tech_map[bus_tech_map['L2 Capability'] == l2_name]['Technology'].tolist()
                
                # Calculate scores
                strategic_importance = convert_strategic_importance(l2_row['Strategic Importance'])
                operational_health = convert_operational_health(l2_row['Operational Health'])
                
                automation_level = 3
                technology_fit = 3
                if len(btf_row) > 0:
                    automation_level = convert_automation_level(btf_row.iloc[0]['Automation Level'])
                    technology_fit = convert_technology_fit(btf_row.iloc[0]['Technology Fit'])
                
                business_tech_fit = round((automation_level + technology_fit) / 2, 1)
                
                l2_data = {
                    'l2_id': l2_id,
                    'l2_name': l2_name,
                    'l2_description': '',
                    'current_maturity': operational_health,
                    'business_tech_fit': business_tech_fit,
                    'automation_level': automation_level,
                    'technology_fit_score': technology_fit,
                    'tech_team_tech_fit': technology_fit,
                    'strategic_importance': strategic_importance,
                    'current_technologies': techs,
                    'operational_health_label': l2_row['Operational Health'],
                    'automation_level_label': btf_row.iloc[0]['Automation Level'] if len(btf_row) > 0 else 'Unknown',
                    'technology_fit_label': btf_row.iloc[0]['Technology Fit'] if len(btf_row) > 0 else 'Unknown',
                    'strategic_importance_label': l2_row['Strategic Importance'],
                    'priority_level': l2_row.get('Priority Level', ''),
                    'bh_notes': str(l2_row.get('Notes / Rationale', '')) if pd.notna(l2_row.get('Notes / Rationale')) else '',
                    'btf_notes': str(btf_row.iloc[0]['Notes / Rationale']) if len(btf_row) > 0 and pd.notna(btf_row.iloc[0]['Notes / Rationale']) else '',
                    'recommended_action': str(btf_row.iloc[0]['Recommended Action']) if len(btf_row) > 0 and pd.notna(btf_row.iloc[0]['Recommended Action']) else ''
                }
                
                l1_data['l2_capabilities'].append(l2_data)
            
            if l1_data['l2_capabilities']:
                capability_data['capabilities'].append(l1_data)
        
        print(f"Processed {len(capability_data['capabilities'])} L1 capabilities with L2 capabilities")
        
        # Generate pain points
        print("Generating pain points...")
        pain_points = generate_pain_points(capability_data)
        print(f"Generated {len(pain_points)} pain points")
        
        # Generate initiatives
        print("Generating initiatives...")
        initiatives = generate_initiatives(capability_data)
        print(f"Generated {len(initiatives)} initiatives")
        
        # Generate evolution data
        print("Generating maturity evolution...")
        evolution = generate_evolution(capability_data)
        print(f"Generated {len(evolution)} evolution paths")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save all JSON files
        print(f"\nSaving JSON files to {output_dir}...")
        
        files_created = []
        
        with open(f"{output_dir}/capabilities.json", 'w') as f:
            json.dump(capability_data, f, indent=2)
            files_created.append('capabilities.json')
        
        with open(f"{output_dir}/pain-points.json", 'w') as f:
            json.dump(pain_points, f, indent=2)
            files_created.append('pain-points.json')
        
        with open(f"{output_dir}/initiatives.json", 'w') as f:
            json.dump(initiatives, f, indent=2)
            files_created.append('initiatives.json')
        
        with open(f"{output_dir}/evolution.json", 'w') as f:
            json.dump(evolution, f, indent=2)
            files_created.append('evolution.json')
        
        # Create a combined file for easy loading
        combined_data = {
            'capabilities': capability_data,
            'painPoints': pain_points,
            'initiatives': initiatives,
            'evolution': evolution
        }
        
        with open(f"{output_dir}/assessment-data.json", 'w') as f:
            json.dump(combined_data, f, indent=2)
            files_created.append('assessment-data.json')
        
        print("\n✅ SUCCESS! Generated files:")
        for file in files_created:
            file_path = f"{output_dir}/{file}"
            size = os.path.getsize(file_path)
            print(f"  - {file} ({size:,} bytes)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def generate_pain_points(cap_data):
    pain_points = []
    
    for l1 in cap_data['capabilities']:
        for l2 in l1['l2_capabilities']:
            issues = []
            
            if l2['operational_health_label'] == 'Unhealthy':
                issues.append({
                    'type': 'Process Health',
                    'severity': 'Critical',
                    'description': 'Operational health issues identified'
                })
            elif l2['operational_health_label'] == 'Moderate Concerns':
                issues.append({
                    'type': 'Process Health',
                    'severity': 'Moderate',
                    'description': 'Some operational concerns'
                })
            
            if l2['technology_fit_label'] == 'Poor Fit':
                issues.append({
                    'type': 'Technology Fit',
                    'severity': 'Critical',
                    'description': 'Technology poorly aligned to business needs'
                })
            elif l2['technology_fit_label'] == 'Adequate Fit':
                issues.append({
                    'type': 'Technology Fit',
                    'severity': 'Moderate',
                    'description': 'Technology meets basic needs with gaps'
                })
            
            if l2['automation_level_label'] in ['Mostly Manual', 'Fully Manual']:
                issues.append({
                    'type': 'Manual Work',
                    'severity': 'High' if l2['strategic_importance'] >= 4 else 'Moderate',
                    'description': f"Heavy manual effort ({l2['automation_level_label']})"
                })
            
            if len(l2['current_technologies']) == 0:
                issues.append({
                    'type': 'No Technology',
                    'severity': 'Critical',
                    'description': 'No technology support identified'
                })
            
            if issues:
                pain_points.append({
                    'l1_capability': l1['l1_name'],
                    'l2_capability': l2['l2_name'],
                    'l2_id': l2['l2_id'],
                    'strategic_importance': l2['strategic_importance'],
                    'operational_health': l2['current_maturity'],
                    'automation_level': l2['automation_level'],
                    'technology_fit': l2['technology_fit_score'],
                    'issues': issues,
                    'bh_notes': l2.get('bh_notes', ''),
                    'btf_notes': l2.get('btf_notes', ''),
                    'recommended_action': l2.get('recommended_action', ''),
                    'technologies': l2['current_technologies']
                })
    
    return pain_points

def generate_initiatives(cap_data):
    initiatives = []
    
    for l1 in cap_data['capabilities']:
        for l2 in l1['l2_capabilities']:
            maturity_gap = 5 - l2['current_maturity']
            tech_gap = 5 - l2['business_tech_fit']
            total_gap = (maturity_gap + tech_gap) / 2
            
            value = (l2['strategic_importance'] * 2 + total_gap * 3) / 5
            
            base_complexity = 6 - l2['current_maturity']
            if l2['automation_level'] <= 2:
                base_complexity += 1
            if l2['technology_fit_score'] == 1:
                base_complexity += 1
            complexity = min(5, base_complexity)
            
            effort_months = complexity * 3
            
            if effort_months <= 6:
                timeframe = 'Quick Win (0-6 months)'
            elif effort_months <= 12:
                timeframe = 'Medium Term (6-12 months)'
            else:
                timeframe = 'Long Term (12+ months)'
            
            initiatives.append({
                'l1_capability': l1['l1_name'],
                'l2_capability': l2['l2_name'],
                'l2_id': l2['l2_id'],
                'value': round(value, 2),
                'complexity': complexity,
                'effort_months': effort_months,
                'timeframe': timeframe,
                'strategic_importance': l2['strategic_importance'],
                'total_gap': round(total_gap, 2),
                'current_maturity': l2['current_maturity'],
                'automation_level': l2['automation_level'],
                'technology_fit': l2['technology_fit_score'],
                'recommended_action': l2.get('recommended_action', ''),
                'technologies': l2['current_technologies']
            })
    
    return initiatives

def generate_evolution(cap_data):
    evolution = []
    
    for l1 in cap_data['capabilities']:
        for l2 in l1['l2_capabilities']:
            current_state = {
                'operational_health': l2['current_maturity'],
                'automation': l2['automation_level'],
                'tech_fit': l2['technology_fit_score']
            }
            
            year1_2 = {
                'operational_health': min(5, current_state['operational_health'] + 1),
                'automation': current_state['automation'],
                'tech_fit': min(5, current_state['tech_fit'] + (1 if current_state['tech_fit'] < 3 else 0))
            }
            
            year3 = {
                'operational_health': year1_2['operational_health'],
                'automation': min(5, current_state['automation'] + 1.5),
                'tech_fit': min(5, year1_2['tech_fit'] + 0.5)
            }
            
            year4_5 = {
                'operational_health': min(5, year3['operational_health'] + 0.5),
                'automation': min(5, year3['automation'] + 1),
                'tech_fit': min(5, year3['tech_fit'] + 0.5)
            }
            
            evolution.append({
                'l1_capability': l1['l1_name'],
                'l2_capability': l2['l2_name'],
                'l2_id': l2['l2_id'],
                'strategic_importance': l2['strategic_importance'],
                'current_state': current_state,
                'year1_2': year1_2,
                'year3': year3,
                'year4_5': year4_5,
                'target_state': {
                    'operational_health': 5,
                    'automation': 5 if l2['strategic_importance'] >= 4 else 4,
                    'tech_fit': 5 if l2['strategic_importance'] >= 4 else 4
                }
            })
    
    return evolution

def main():
    print("=" * 60)
    print("Legal Affairs EA Assessment - Excel to JSON Converter")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python excel_to_json.py <excel_file> [output_directory]")
        print()
        print("Example:")
        print("  python excel_to_json.py assessment.xlsx")
        print("  python excel_to_json.py assessment.xlsx ../public/data")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '../data'
    
    if not os.path.exists(excel_file):
        print(f"ERROR: File not found: {excel_file}")
        sys.exit(1)
    
    success = process_excel_file(excel_file, output_dir)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Conversion completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Copy the generated JSON files to your Azure Static Web App")
        print("2. Upload them to the /data folder")
        print("3. Your dashboard will automatically load the new data")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Conversion failed!")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
