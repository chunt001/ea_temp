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
        
        # Read L2 descriptions from capability catalog (starting row 21)
        print("Extracting L2 descriptions from catalog...")
        l2_descriptions = {}
        for i in range(21, len(cap_raw)):
            if pd.notna(cap_raw.iloc[i, 0]) and str(cap_raw.iloc[i, 0]).startswith('L2'):
                l2_id = cap_raw.iloc[i, 0]
                l2_name = cap_raw.iloc[i, 2]  # Column C has L2 name
                l2_desc = cap_raw.iloc[i, 3] if pd.notna(cap_raw.iloc[i, 3]) else ""  # Column D has L2 description
                if l2_name:
                    l2_descriptions[str(l2_id)] = str(l2_desc)
        
        print(f"Found {len(l2_descriptions)} L2 descriptions")
        
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
                    'l2_description': l2_descriptions.get(str(l2_id), ''),
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
        
        # Extract and save assessment guides
        print("Extracting assessment guides...")
        guides_data = extract_assessment_guides(excel_path)
        
        with open(f"{output_dir}/guides.json", 'w') as f:
            json.dump(guides_data, f, indent=2)
            files_created.append('guides.json')
        
        # Generate capability map data
        print("Generating capability map data...")
        map_data = generate_capability_map_data(capability_data)
        
        with open(f"{output_dir}/capability-map-data.json", 'w') as f:
            json.dump(map_data, f, indent=2)
            files_created.append('capability-map-data.json')
        
        # Generate technology roadmap
        print("Generating technology roadmap...")
        roadmap_data = generate_technology_roadmap(capability_data)
        
        with open(f"{output_dir}/technology-roadmap.json", 'w') as f:
            json.dump(roadmap_data, f, indent=2)
            files_created.append('technology-roadmap.json')
        
        # Generate TIME matrix
        print("Generating TIME matrix...")
        time_matrix_data = generate_time_matrix(capability_data)
        
        with open(f"{output_dir}/time-matrix.json", 'w') as f:
            json.dump(time_matrix_data, f, indent=2)
            files_created.append('time-matrix.json')
        
        # Generate TIME matrix for technologies
        print("Generating technology TIME matrix...")
        time_tech_data = generate_time_technologies(excel_path)
        
        with open(f"{output_dir}/time-technologies.json", 'w') as f:
            json.dump(time_tech_data, f, indent=2)
            files_created.append('time-technologies.json')
        
        # Generate executive dashboard data
        print("Generating executive dashboard...")
        exec_data = generate_executive_dashboard(capability_data)
        
        with open(f"{output_dir}/executive-dashboard.json", 'w') as f:
            json.dump(exec_data, f, indent=2)
            files_created.append('executive-dashboard.json')
        
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

def extract_assessment_guides(excel_path):
    """Extract assessment guide sheets from Excel"""
    
    bh_guide = pd.read_excel(excel_path, sheet_name='BH Assessment Guide', header=None)
    btf_guide = pd.read_excel(excel_path, sheet_name='BTF Assessment Guide', header=None)
    th_guide = pd.read_excel(excel_path, sheet_name='TH Assessment Guide', header=None)
    
    def parse_guide_sheet(df):
        guide_content = {
            'title': '',
            'overview': '',
            'dimensions': []
        }
        
        current_dimension = None
        
        for i in range(len(df)):
            row = df.iloc[i].tolist()
            first_col = row[0] if pd.notna(row[0]) else None
            
            if not first_col:
                continue
            
            first_col_str = str(first_col).strip()
            
            # Title
            if i == 0:
                guide_content['title'] = first_col_str
            elif i == 1:
                guide_content['overview'] = first_col_str
            
            # Dimension headers (ALL CAPS)
            elif first_col_str.isupper() and len(first_col_str) > 3 and 'GUIDE' not in first_col_str:
                if current_dimension:
                    guide_content['dimensions'].append(current_dimension)
                
                current_dimension = {
                    'name': first_col_str,
                    'question': '',
                    'scale': []
                }
            
            # Question row
            elif first_col_str.startswith('Question:'):
                if current_dimension:
                    current_dimension['question'] = first_col_str.replace('Question: ', '')
            
            # Header row for scale
            elif first_col_str in ['Label', 'Score', 'Weight']:
                if current_dimension:
                    current_dimension['headers'] = [str(x) for x in row if pd.notna(x)]
            
            # Scale data rows
            elif current_dimension and 'headers' in current_dimension:
                row_data = {}
                for j, val in enumerate(row):
                    if pd.notna(val) and j < len(current_dimension.get('headers', [])):
                        header = current_dimension['headers'][j]
                        row_data[header] = str(val)
                
                if row_data and len(row_data) > 1:  # At least 2 fields
                    current_dimension['scale'].append(row_data)
        
        # Add last dimension
        if current_dimension:
            guide_content['dimensions'].append(current_dimension)
        
        return guide_content
    
    return {
        'business_health': parse_guide_sheet(bh_guide),
        'business_tech_fit': parse_guide_sheet(btf_guide),
        'tech_health': parse_guide_sheet(th_guide)
    }

def generate_capability_map_data(cap_data):
    """Generate data structure for visual capability map"""
    
    def get_domain_for_l1(l1_name):
        """Map L1 capabilities to logical domains"""
        # All capabilities belong to Legal Affairs org unit
        # But organized into functional domains
        mapping = {
            'Contract Legal Services': 'Contract Management',
            'Investment Legal Services': 'Investment Management',
            'Corporate Governance': 'Governance & Compliance',
            'Legal Regulatory & Compliance': 'Governance & Compliance',
            'Government Relations': 'Governance & Compliance',
            'Legal Advisory & Research': 'Advisory & Research',
            'Legal Operations & Administration': 'Operations & Support',
            'Matter & Case Management': 'Litigation & Matters'
        }
        return mapping.get(l1_name, 'Other')
    
    domains = {}
    
    # Define organization unit (from Excel ASSESSMENT SCOPE)
    org_unit = "Legal Affairs"  # This comes from row 1 of the Excel file
    
    for l1 in cap_data['capabilities']:
        domain = get_domain_for_l1(l1['l1_name'])
        
        if domain not in domains:
            domains[domain] = {
                'name': domain,
                'org_unit': org_unit,
                'l1_capabilities': []
            }
        
        l1_map_data = {
            'id': l1['l1_id'],
            'name': l1['l1_name'],
            'description': l1['l1_description'],
            'l2_capabilities': []
        }
        
        for l2 in l1['l2_capabilities']:
            avg_score = (l2['current_maturity'] + l2['automation_level'] + l2['technology_fit_score']) / 3
            
            # Use L2 description from capability catalog, fall back to BH notes
            description = l2.get('l2_description', '') or l2.get('bh_notes', '') or f"{l2['l2_name']} capability"
            
            l1_map_data['l2_capabilities'].append({
                'id': l2['l2_id'],
                'name': l2['l2_name'],
                'description': description,
                'maturity': l2['current_maturity'],
                'automation': l2['automation_level'],
                'tech_fit': l2['technology_fit_score'],
                'business_tech_fit': l2['business_tech_fit'],
                'importance': l2['strategic_importance'],
                'avg_score': round(avg_score, 1)
            })
        
        domains[domain]['l1_capabilities'].append(l1_map_data)
    
    return list(domains.values())

def generate_technology_roadmap(cap_data):
    """Generate technology roadmap showing current and proposed tech by L1 and year"""
    
    roadmap = []
    
    for l1 in cap_data['capabilities']:
        # Collect current technologies
        current_techs = set()
        for l2 in l1['l2_capabilities']:
            current_techs.update(l2['current_technologies'])
        
        roadmap_entry = {
            'l1_id': l1['l1_id'],
            'l1_name': l1['l1_name'],
            'l1_description': l1['l1_description'],
            'org_unit': 'Legal Affairs',
            'current_technologies': sorted(list(current_techs)),
            'roadmap': {
                '2026': {
                    'current': sorted(list(current_techs)),
                    'proposed': ['Platform Assessment & Selection', 'Integration Planning'],
                    'deliverables': ['Technology assessment', 'Vendor evaluation', 'Platform selection']
                },
                '2027': {
                    'current': [],
                    'proposed': ['New Platform Implementation', 'Enhanced Tools'],
                    'deliverables': ['Platform deployment', 'User training', 'Process automation']
                },
                '2028': {
                    'current': [],
                    'proposed': ['AI/ML Capabilities', 'Advanced Analytics'],
                    'deliverables': ['AI integration', 'Analytics implementation', 'Process optimization']
                },
                '2029': {
                    'current': [],
                    'proposed': ['Advanced Features', 'Predictive Capabilities'],
                    'deliverables': ['Advanced capabilities', 'Predictive tools', 'Optimization']
                },
                '2030': {
                    'current': [],
                    'proposed': ['Next-Gen Platform', 'Autonomous AI'],
                    'deliverables': ['Next-generation capabilities', 'Full automation', 'AI-driven operations']
                }
            }
        }
        
        roadmap.append(roadmap_entry)
    
    return roadmap

def generate_time_matrix(cap_data):
    """Generate TIME matrix analysis data"""
    
    time_matrix = []
    
    for l1 in cap_data['capabilities']:
        for l2 in l1['l2_capabilities']:
            # Calculate TIME dimensions
            # T = Technology complexity (inverse of tech fit)
            tech_complexity = 6 - l2['technology_fit_score']
            
            # I = Impact/Importance
            impact = l2['strategic_importance']
            
            # M = Maturity gap
            maturity_gap = 5 - l2['current_maturity']
            
            # E = Effort (inverse of automation)
            effort = 6 - l2['automation_level']
            
            # Overall TIME score (higher = more urgent)
            time_score = (tech_complexity + maturity_gap + effort) / 3
            
            time_matrix.append({
                'l1_capability': l1['l1_name'],
                'l2_capability': l2['l2_name'],
                'l2_id': l2['l2_id'],
                'technology_complexity': tech_complexity,
                'impact': impact,
                'maturity_gap': maturity_gap,
                'effort': effort,
                'time_score': round(time_score, 2),
                'current_maturity': l2['current_maturity'],
                'automation_level': l2['automation_level'],
                'tech_fit': l2['technology_fit_score'],
                'strategic_importance': l2['strategic_importance'],
                'business_tech_fit': l2['business_tech_fit']
            })
    
    return time_matrix

def generate_time_technologies(excel_path):
    """Generate TIME matrix for technology portfolio"""
    
    # Read TH Assessment
    th = pd.read_excel(excel_path, sheet_name='TH Assessment', header=2)
    th.columns = ['ID', 'Application', 'Tech Owner', 'Assessment Date', 
                  'Operational Health', 'Tech Standards', 'Cloud Strategy', 'Zero Trust', 'AI-Enablement',
                  'Ops Health Score', 'Tech Std Score', 'Cloud Score', 'ZT Score', 'AI Score',
                  'Alignment Pct', 'Alignment Score', 'Tech Health Score', 'Tech Health Status',
                  'Recommended Action', 'Notes']
    th = th.dropna(subset=['ID'])
    
    # Read Technology Catalog for priority
    tech_cat = pd.read_excel(excel_path, sheet_name='Technology Catalog NEW', header=2)
    tech_priorities = {}
    for _, row in tech_cat.iterrows():
        if pd.notna(row.iloc[0]) and pd.notna(row.iloc[-1]):
            tech_priorities[str(row.iloc[0])] = str(row.iloc[-1])
    
    time_technologies = []
    
    for _, row in th.iterrows():
        app_name = row['Application']
        
        tech_health = row['Tech Health Score'] if pd.notna(row['Tech Health Score']) else 2.0
        alignment_score = row['Alignment Score'] if pd.notna(row['Alignment Score']) else 2.0
        ops_health = row['Ops Health Score'] if pd.notna(row['Ops Health Score']) else 2.0
        
        priority = tech_priorities.get(app_name, 'MEDIUM')
        
        # Determine TIME quadrant
        # X-axis: Tech Health (low left, high right)
        # Y-axis: Strategic Alignment (low bottom, high top)
        if tech_health >= 2.5 and alignment_score >= 2.5:
            time_category = 'INVEST'  # Top-Right: High health, high alignment
        elif tech_health < 2 and alignment_score >= 2:
            time_category = 'TOLERATE'  # Top-Left: Low health, high alignment
        elif tech_health >= 2.5 and alignment_score < 2:
            time_category = 'MIGRATE'  # Bottom-Right: High health, low alignment
        else:
            time_category = 'ELIMINATE'  # Bottom-Left: Low health, low alignment
        
        # Strategic value based on priority
        if priority == 'CRITICAL':
            strategic_value = 5
        elif priority == 'HIGH':
            strategic_value = 4
        else:
            strategic_value = 3
        
        time_technologies.append({
            'id': row['ID'],
            'name': app_name,
            'tech_health': round(tech_health, 1),
            'alignment': round(alignment_score, 1),
            'ops_health': round(ops_health, 1),
            'tech_health_status': row['Tech Health Status'],
            'alignment_pct': round(row['Alignment Pct'] * 100, 1) if pd.notna(row['Alignment Pct']) else 50.0,
            'recommended_action': str(row['Recommended Action']) if pd.notna(row['Recommended Action']) else '',
            'priority': priority,
            'strategic_value': strategic_value,
            'time_category': time_category,
            'notes': str(row['Notes']) if pd.notna(row['Notes']) else ''
        })
    
    return time_technologies

def generate_executive_dashboard(cap_data):
    """Generate executive-level transformation metrics"""
    
    # 1. Maturity radar
    maturity_radar = {
        'current_state': {},
        'target_state': {},
        'year_2027': {},
        'year_2029': {}
    }
    
    for l1 in cap_data['capabilities']:
        l2_maturities = [l2['current_maturity'] for l2 in l1['l2_capabilities']]
        current_avg = round(sum(l2_maturities) / len(l2_maturities), 1)
        
        maturity_radar['current_state'][l1['l1_name']] = current_avg
        maturity_radar['target_state'][l1['l1_name']] = 4.5
        maturity_radar['year_2027'][l1['l1_name']] = min(4.5, round(current_avg + 0.8, 1))
        maturity_radar['year_2029'][l1['l1_name']] = min(4.5, round(current_avg + 1.6, 1))
    
    # 2. Technical debt burn-down
    total_gaps = sum(1 for l1 in cap_data['capabilities'] for l2 in l1['l2_capabilities'] if l2['current_maturity'] < 3)
    
    debt_burndown = {
        '2026': {'critical_issues': total_gaps, 'high_priority': 15, 'medium_priority': 10},
        '2027': {'critical_issues': int(total_gaps * 0.7), 'high_priority': 10, 'medium_priority': 8},
        '2028': {'critical_issues': int(total_gaps * 0.4), 'high_priority': 6, 'medium_priority': 5},
        '2029': {'critical_issues': int(total_gaps * 0.2), 'high_priority': 3, 'medium_priority': 3},
        '2030': {'critical_issues': 0, 'high_priority': 0, 'medium_priority': 2}
    }
    
    # 3. Value realization (example numbers)
    value_realization = {
        '2026': {'investment': -2.5, 'annual_value': 0.3, 'cumulative_value': 0.3},
        '2027': {'investment': -3.0, 'annual_value': 1.2, 'cumulative_value': 1.5},
        '2028': {'investment': -2.0, 'annual_value': 2.5, 'cumulative_value': 4.0},
        '2029': {'investment': -1.5, 'annual_value': 3.2, 'cumulative_value': 7.2},
        '2030': {'investment': -1.0, 'annual_value': 4.0, 'cumulative_value': 11.2}
    }
    
    # 4. Automation coverage
    automation_coverage = {}
    for l1 in cap_data['capabilities']:
        automations = [l2['automation_level'] for l2 in l1['l2_capabilities']]
        current_pct = (sum(automations) / (len(automations) * 5)) * 100
        target_pct = 90
        
        automation_coverage[l1['l1_name']] = {
            'current': round(current_pct, 1),
            'target': target_pct,
            'gap': round(target_pct - current_pct, 1)
        }
    
    return {
        'maturity_radar': maturity_radar,
        'debt_burndown': debt_burndown,
        'value_realization': value_realization,
        'automation_coverage': automation_coverage
    }

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
