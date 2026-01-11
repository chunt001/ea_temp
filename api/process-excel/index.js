const multipart = require('parse-multipart');
const XLSX = require('xlsx');

module.exports = async function (context, req) {
    context.log('Processing Excel file upload');
    
    try {
        // Parse multipart form data
        const bodyBuffer = Buffer.from(req.body);
        const boundary = multipart.getBoundary(req.headers['content-type']);
        const parts = multipart.Parse(bodyBuffer, boundary);
        
        if (!parts || parts.length === 0) {
            context.res = {
                status: 400,
                body: { message: 'No file uploaded' }
            };
            return;
        }
        
        const filePart = parts[0];
        const fileBuffer = filePart.data;
        
        // Parse Excel file
        const workbook = XLSX.read(fileBuffer, { type: 'buffer' });
        
        // Validate required sheets
        const requiredSheets = [
            'Business Capability Catalog',
            'BH Assessment',
            'BTF Assessment',
            'Bus-Tech Map'
        ];
        
        const missingSheets = requiredSheets.filter(sheet => !workbook.SheetNames.includes(sheet));
        if (missingSheets.length > 0) {
            context.res = {
                status: 400,
                body: { message: `Missing required sheets: ${missingSheets.join(', ')}` }
            };
            return;
        }
        
        // Process the data
        const processedData = processExcelData(workbook);
        
        // Store data (in a real app, this would go to Azure Storage/Cosmos DB)
        // For now, we'll use context.bindings for demonstration
        context.bindings.outputData = JSON.stringify(processedData);
        
        context.res = {
            status: 200,
            body: {
                message: 'File processed successfully',
                capabilities: processedData.capabilities.capabilities.length,
                l2Count: processedData.capabilities.capabilities.reduce((sum, l1) => 
                    sum + l1.l2_capabilities.length, 0)
            }
        };
        
    } catch (error) {
        context.log.error('Error processing file:', error);
        context.res = {
            status: 500,
            body: { message: 'Error processing file: ' + error.message }
        };
    }
};

function processExcelData(workbook) {
    // Read capabilities
    const capSheet = workbook.Sheets['Business Capability Catalog'];
    const bhSheet = workbook.Sheets['BH Assessment'];
    const btfSheet = workbook.Sheets['BTF Assessment'];
    const mapSheet = workbook.Sheets['Bus-Tech Map'];
    
    // Convert to JSON
    const capData = XLSX.utils.sheet_to_json(capSheet, { header: 1, defval: null });
    const bhData = XLSX.utils.sheet_to_json(bhSheet, { header: 1, defval: null });
    const btfData = XLSX.utils.sheet_to_json(btfSheet, { header: 1, defval: null });
    const mapData = XLSX.utils.sheet_to_json(mapSheet, { header: 1, defval: null });
    
    // Parse L1 capabilities (rows 4-11 in original format)
    const l1Capabilities = [];
    for (let i = 4; i <= 11; i++) {
        if (i < capData.length && capData[i][0]) {
            l1Capabilities.push({
                id: capData[i][0],
                name: capData[i][1],
                description: capData[i][2] || ''
            });
        }
    }
    
    // Parse BH Assessment (starting from row 3)
    const bhAssessment = [];
    for (let i = 3; i < bhData.length; i++) {
        if (bhData[i][0]) {
            bhAssessment.push({
                id: bhData[i][0],
                l1: bhData[i][1],
                l2: bhData[i][2],
                strategicImportance: bhData[i][5],
                operationalHealth: bhData[i][6]
            });
        }
    }
    
    // Parse BTF Assessment (starting from row 3)
    const btfAssessment = [];
    for (let i = 3; i < btfData.length; i++) {
        if (btfData[i][0]) {
            btfAssessment.push({
                id: btfData[i][0],
                automationLevel: btfData[i][5],
                technologyFit: btfData[i][6]
            });
        }
    }
    
    // Parse Bus-Tech Map (starting from row 3)
    const busMap = [];
    for (let i = 3; i < mapData.length; i++) {
        if (mapData[i][0] && mapData[i][0] !== 'L2 Capability') {
            busMap.push({
                l2: mapData[i][0],
                technology: mapData[i][1]
            });
        }
    }
    
    // Build capability structure with scoring
    const capabilities = buildCapabilityStructure(
        l1Capabilities,
        bhAssessment,
        btfAssessment,
        busMap
    );
    
    // Generate all derived data
    const painPoints = generatePainPoints(capabilities);
    const initiatives = generateInitiatives(capabilities);
    const evolution = generateEvolution(capabilities);
    
    return {
        capabilities,
        painPoints,
        initiatives,
        evolution
    };
}

function buildCapabilityStructure(l1List, bhList, btfList, mapList) {
    const scoreMapping = {
        strategicImportance: {
            'Mission-Critical': 5,
            'Important': 4,
            'Supporting': 3,
            'Nice-to-Have': 2,
            'Minimal': 1
        },
        operationalHealth: {
            'Healthy': 5,
            'Moderate Concerns': 3,
            'Unhealthy': 2
        },
        automationLevel: {
            'Highly Automated': 5,
            'Partially Automated': 3,
            'Mostly Manual': 2,
            'Fully Manual': 1
        },
        technologyFit: {
            'Excellent Fit': 5,
            'Adequate Fit': 3,
            'Poor Fit': 1
        }
    };
    
    const result = {
        capabilities: [],
        scoring_methodology: scoreMapping
    };
    
    l1List.forEach(l1 => {
        const l1Data = {
            l1_id: l1.id,
            l1_name: l1.name,
            l1_description: l1.description,
            l2_capabilities: []
        };
        
        const l2Caps = bhList.filter(bh => bh.l1 === l1.name);
        
        l2Caps.forEach(l2 => {
            const btf = btfList.find(b => b.id === l2.id) || {};
            const techs = mapList.filter(m => m.l2 === l2.l2).map(m => m.technology);
            
            const strategicImportance = scoreMapping.strategicImportance[l2.strategicImportance] || 3;
            const currentMaturity = scoreMapping.operationalHealth[l2.operationalHealth] || 3;
            const automationLevel = scoreMapping.automationLevel[btf.automationLevel] || 2;
            const technologyFit = scoreMapping.technologyFit[btf.technologyFit] || 3;
            
            l1Data.l2_capabilities.push({
                l2_id: l2.id,
                l2_name: l2.l2,
                l2_description: '',
                current_maturity: currentMaturity,
                automation_level: automationLevel,
                technology_fit_score: technologyFit,
                business_tech_fit: (automationLevel + technologyFit) / 2,
                tech_team_tech_fit: technologyFit,
                strategic_importance: strategicImportance,
                current_technologies: techs,
                operational_health_label: l2.operationalHealth,
                automation_level_label: btf.automationLevel || 'Unknown',
                technology_fit_label: btf.technologyFit || 'Unknown',
                strategic_importance_label: l2.strategicImportance
            });
        });
        
        if (l1Data.l2_capabilities.length > 0) {
            result.capabilities.push(l1Data);
        }
    });
    
    return result;
}

function generatePainPoints(capData) {
    const painPoints = [];
    
    capData.capabilities.forEach(l1 => {
        l1.l2_capabilities.forEach(l2 => {
            const issues = [];
            
            if (l2.operational_health_label === 'Unhealthy') {
                issues.push({
                    type: 'Process Health',
                    severity: 'Critical',
                    description: 'Operational health issues identified'
                });
            } else if (l2.operational_health_label === 'Moderate Concerns') {
                issues.push({
                    type: 'Process Health',
                    severity: 'Moderate',
                    description: 'Some operational concerns'
                });
            }
            
            if (l2.technology_fit_label === 'Poor Fit') {
                issues.push({
                    type: 'Technology Fit',
                    severity: 'Critical',
                    description: 'Technology poorly aligned to business needs'
                });
            }
            
            if (l2.automation_level_label === 'Mostly Manual' || l2.automation_level_label === 'Fully Manual') {
                issues.push({
                    type: 'Manual Work',
                    severity: l2.strategic_importance >= 4 ? 'High' : 'Moderate',
                    description: `Heavy manual effort (${l2.automation_level_label})`
                });
            }
            
            if (l2.current_technologies.length === 0) {
                issues.push({
                    type: 'No Technology',
                    severity: 'Critical',
                    description: 'No technology support identified'
                });
            }
            
            if (issues.length > 0) {
                painPoints.push({
                    l1_capability: l1.l1_name,
                    l2_capability: l2.l2_name,
                    l2_id: l2.l2_id,
                    strategic_importance: l2.strategic_importance,
                    operational_health: l2.current_maturity,
                    automation_level: l2.automation_level,
                    technology_fit: l2.technology_fit_score,
                    issues,
                    technologies: l2.current_technologies
                });
            }
        });
    });
    
    return painPoints;
}

function generateInitiatives(capData) {
    const initiatives = [];
    
    capData.capabilities.forEach(l1 => {
        l1.l2_capabilities.forEach(l2 => {
            const maturityGap = 5 - l2.current_maturity;
            const techGap = 5 - l2.business_tech_fit;
            const totalGap = (maturityGap + techGap) / 2;
            
            const value = (l2.strategic_importance * 2 + totalGap * 3) / 5;
            
            let baseComplexity = 6 - l2.current_maturity;
            if (l2.automation_level <= 2) baseComplexity += 1;
            if (l2.technology_fit_score === 1) baseComplexity += 1;
            const complexity = Math.min(5, baseComplexity);
            
            const effortMonths = complexity * 3;
            let timeframe;
            if (effortMonths <= 6) timeframe = 'Quick Win (0-6 months)';
            else if (effortMonths <= 12) timeframe = 'Medium Term (6-12 months)';
            else timeframe = 'Long Term (12+ months)';
            
            initiatives.push({
                l1_capability: l1.l1_name,
                l2_capability: l2.l2_name,
                l2_id: l2.l2_id,
                value: Math.round(value * 100) / 100,
                complexity,
                effort_months: effortMonths,
                timeframe,
                strategic_importance: l2.strategic_importance,
                total_gap: Math.round(totalGap * 100) / 100,
                current_maturity: l2.current_maturity,
                automation_level: l2.automation_level,
                technology_fit: l2.technology_fit_score,
                technologies: l2.current_technologies
            });
        });
    });
    
    return initiatives;
}

function generateEvolution(capData) {
    const evolution = [];
    
    capData.capabilities.forEach(l1 => {
        l1.l2_capabilities.forEach(l2 => {
            const currentState = {
                operational_health: l2.current_maturity,
                automation: l2.automation_level,
                tech_fit: l2.technology_fit_score
            };
            
            const year1_2 = {
                operational_health: Math.min(5, currentState.operational_health + 1),
                automation: currentState.automation,
                tech_fit: Math.min(5, currentState.tech_fit + (currentState.tech_fit < 3 ? 1 : 0))
            };
            
            const year3 = {
                operational_health: year1_2.operational_health,
                automation: Math.min(5, currentState.automation + 1.5),
                tech_fit: Math.min(5, year1_2.tech_fit + 0.5)
            };
            
            const year4_5 = {
                operational_health: Math.min(5, year3.operational_health + 0.5),
                automation: Math.min(5, year3.automation + 1),
                tech_fit: Math.min(5, year3.tech_fit + 0.5)
            };
            
            evolution.push({
                l1_capability: l1.l1_name,
                l2_capability: l2.l2_name,
                l2_id: l2.l2_id,
                strategic_importance: l2.strategic_importance,
                current_state: currentState,
                year1_2: year1_2,
                year3: year3,
                year4_5: year4_5,
                target_state: {
                    operational_health: 5,
                    automation: l2.strategic_importance >= 4 ? 5 : 4,
                    tech_fit: l2.strategic_importance >= 4 ? 5 : 4
                }
            });
        });
    });
    
    return evolution;
}
