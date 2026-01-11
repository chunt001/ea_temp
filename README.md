# Legal Affairs EA Assessment - Azure Static Web App (Simplified)

Enterprise Architecture Assessment Dashboard with static JSON data files (no Azure Functions required!)

## 🎯 Overview

This is a **simplified deployment** that uses static JSON files instead of Azure Functions. You convert your Excel files locally using a Python script, then upload the generated JSON files.

### Benefits:
✅ **No Azure Functions** - Simpler, cheaper deployment
✅ **No API complexity** - Just static files
✅ **Full offline capability** - Convert Excel anytime
✅ **Version control friendly** - JSON files in Git
✅ **Free tier covers everything** - Azure Static Web Apps free tier

## 📁 Project Structure

```
azure-static-simple/
├── .github/workflows/
│   └── azure-static-web-apps.yml    # Auto-deployment
├── public/
│   ├── index.html                    # Dashboard (all 9 pages)
│   ├── data/                         # JSON data files
│   │   ├── assessment-data.json      # Combined data
│   │   ├── capabilities.json         # Capability structure
│   │   ├── pain-points.json          # Pain points & gaps
│   │   ├── initiatives.json          # Prioritization data
│   │   └── evolution.json            # Maturity evolution
│   └── staticwebapp.config.json
├── tools/
│   └── excel_to_json.py              # Excel converter
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7+ (for Excel conversion)
- Git
- GitHub account
- Azure account (free tier works!)

### Step 1: Convert Your Excel File

```bash
# Install required Python packages
pip install pandas openpyxl

# Convert your Excel file
cd tools
python excel_to_json.py path/to/your/assessment.xlsx

# JSON files will be created in ../data/
```

### Step 2: Deploy to Azure

#### Option A: Via Azure Portal (5 minutes)

1. **Create GitHub Repository**
   - Create new repo
   - Upload all files from `azure-static-simple` folder

2. **Create Static Web App**
   - Go to [Azure Portal](https://portal.azure.com)
   - Click "+ Create a resource"
   - Search "Static Web App"
   - Click "Create"

3. **Configure**
   - **Name**: `legal-affairs-ea`
   - **Region**: Choose closest to you
   - **SKU**: Free
   - **Source**: GitHub
   - **Organization**: Your GitHub account
   - **Repository**: Your repo
   - **Branch**: main
   - **Build Presets**: Custom
   - **App location**: `/public`
   - **Output location**: (leave empty)

4. **Done!**
   - Wait 2-3 minutes for deployment
   - Your app URL: `https://legal-affairs-ea-xxx.azurestaticapps.net`

#### Option B: Via Azure CLI

```bash
az login

az staticwebapp create \
  --name legal-affairs-ea \
  --resource-group legal-affairs-rg \
  --source https://github.com/YOUR_USERNAME/YOUR_REPO \
  --location eastus \
  --branch main \
  --app-location "/public" \
  --login-with-github
```

## 🔄 Updating Data

### When You Want to Update the Dashboard:

1. **Convert new Excel file**:
   ```bash
   python tools/excel_to_json.py new-assessment.xlsx
   ```

2. **Copy JSON files to public/data**:
   ```bash
   cp data/*.json public/data/
   ```

3. **Commit and push**:
   ```bash
   git add public/data/*.json
   git commit -m "Update assessment data"
   git push
   ```

4. **Done!**
   - GitHub Actions automatically deploys
   - Dashboard updates within 2-3 minutes

## 📊 Excel File Requirements

Your Excel file must contain:

### Required Sheets:

1. **Business Capability Catalog**
   - L1 capabilities in rows 5-12
   - Columns: ID, L1 Capability, Description, Owner

2. **BH Assessment** (Business Health)
   - Header row 3
   - Columns: ID, L1 Capability, L2 Capability, Strategic Importance, Operational Health, etc.
   - **Strategic Importance**: Mission-Critical, Important, Supporting
   - **Operational Health**: Healthy, Moderate Concerns, Unhealthy

3. **BTF Assessment** (Business-Technology Fit)
   - Header row 3
   - Columns: ID, L1 Capability, L2 Capability, Automation Level, Technology Fit, etc.
   - **Automation Level**: Highly Automated, Partially Automated, Mostly Manual, Fully Manual
   - **Technology Fit**: Excellent Fit, Adequate Fit, Poor Fit

4. **Bus-Tech Map**
   - Header row 3
   - Columns: L2 Capability, Technology, Role
   - Maps capabilities to supporting technologies

## 🛠️ Local Development

### Run Locally

```bash
# Serve the public directory
cd public
python -m http.server 8000

# Or use npx
npx serve public
```

Visit `http://localhost:8000`

### Test Excel Conversion

```bash
cd tools
python excel_to_json.py ../test-data/sample.xlsx ../public/data
```

## 📈 Dashboard Features

The dashboard includes **9 comprehensive pages**:

1. **Pain Points & Gaps** - Current state issues
2. **5-Year Roadmap** - Technology transformation timeline
3. **Value vs Complexity** - Initiative prioritization matrix
4. **Maturity Evolution** - Capability progression paths
5. **Capability Heatmap** - Quick visual overview
6. **Detailed Heatmap** - Full table view with filters
7. **Executive Overview** - High-level metrics
8. **Gap Analysis** - Detailed breakdown by dimension
9. **Technology Landscape** - Technology inventory

## 💰 Cost

**Azure Static Web Apps Free Tier:**
- Bandwidth: 100 GB/month FREE
- Storage: 0.5 GB FREE
- Custom domains: FREE
- SSL certificates: FREE

**Expected cost: $0/month** for typical internal use

No storage account or Azure Functions needed!

## 🔒 Security

### Enable Authentication (Optional)

Edit `public/staticwebapp.config.json`:

```json
{
  "auth": {
    "identityProviders": {
      "azureActiveDirectory": {
        "registration": {
          "openIdIssuer": "https://login.microsoftonline.com/YOUR-TENANT-ID/v2.0",
          "clientIdSettingName": "AAD_CLIENT_ID",
          "clientSecretSettingName": "AAD_CLIENT_SECRET"
        }
      }
    }
  },
  "routes": [
    {
      "route": "/*",
      "allowedRoles": ["authenticated"]
    }
  ]
}
```

Then add App Settings in Azure Portal:
- `AAD_CLIENT_ID`
- `AAD_CLIENT_SECRET`

## 🐛 Troubleshooting

### Excel conversion fails

**Check:**
- Python 3.7+ installed
- pandas and openpyxl packages installed: `pip install pandas openpyxl`
- Excel file has required sheets
- File is .xlsx or .xlsm format

**Common errors:**
- "Missing required sheets" → Verify sheet names match exactly
- "KeyError" → Check column headers in row 3 of each sheet

### Dashboard shows "No data found"

**Check:**
- JSON files exist in `public/data/`
- Files are valid JSON (run through validator)
- Files were copied before deployment
- Clear browser cache

### Deployment fails

**Check:**
- GitHub Actions has AZURE_STATIC_WEB_APPS_API_TOKEN secret
- Workflow file is in `.github/workflows/`
- App location is `/public` in workflow

## 📝 Excel Conversion Script Details

The `excel_to_json.py` script:

1. **Validates** Excel file structure
2. **Extracts** L1 and L2 capabilities
3. **Processes** BH and BTF assessments
4. **Maps** technologies to capabilities
5. **Calculates** scoring (1-5 scale)
6. **Generates**:
   - Capability structure
   - Pain points (issues and gaps)
   - Initiatives (RICE-based prioritization)
   - Evolution paths (5-year projections)

### Output Files:

- `capabilities.json` - Full capability hierarchy with scores
- `pain-points.json` - Issues requiring attention
- `initiatives.json` - Prioritized investment opportunities
- `evolution.json` - Maturity progression timelines
- `assessment-data.json` - Combined file with all data

## 🔄 Workflow Example

```bash
# 1. Update Excel file with new assessment data
# 2. Convert to JSON
cd tools
python excel_to_json.py ~/Desktop/Q1-2026-Assessment.xlsx

# 3. Copy to public directory
cp ../data/*.json ../public/data/

# 4. Commit and deploy
cd ..
git add public/data/*.json
git commit -m "Q1 2026 assessment update"
git push

# 5. Wait 2-3 minutes
# 6. Dashboard automatically updates!
```

## 📞 Support

### Common Issues:

**Issue**: "Module not found: pandas"
**Solution**: `pip install pandas openpyxl`

**Issue**: "No data found" in dashboard
**Solution**: Ensure JSON files are in `/public/data/` before deploying

**Issue**: Dashboard doesn't update after push
**Solution**: Check GitHub Actions tab for deployment status

### Resources:

- [Azure Static Web Apps Docs](https://docs.microsoft.com/azure/static-web-apps/)
- [Python pandas Documentation](https://pandas.pydata.org/)

## 🎉 Advantages of This Approach

✅ **Simpler** - No Azure Functions complexity
✅ **Cheaper** - 100% free tier
✅ **Faster** - No API calls, instant loading
✅ **Offline** - Convert Excel files locally anytime
✅ **Version Control** - Track data changes in Git
✅ **No Backend** - Pure static site
✅ **Secure** - No server-side code to exploit
✅ **Reliable** - No moving parts to break

## 📌 Important Notes

- **Data Privacy**: JSON files are public by default. Enable authentication if sensitive.
- **File Size**: Keep JSON files under 10MB for best performance
- **Updates**: Always test locally before pushing to production
- **Backup**: Keep Excel source files as backups

## 🚀 What's Next?

1. **Custom Domain**: Add your domain in Azure Portal
2. **Authentication**: Enable Azure AD login
3. **Automation**: Use GitHub Actions to auto-convert Excel files
4. **Monitoring**: Add Application Insights (optional)

---

**You now have a simple, maintainable, enterprise EA assessment dashboard running on Azure!**
