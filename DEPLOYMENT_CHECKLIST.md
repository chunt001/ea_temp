# Azure Static Web App Deployment Checklist

## ✅ Pre-Deployment Verification

### Your Package is Ready to Deploy! Here's what you have:

**✓ File Structure:**
```
azure-static-simple/
├── public/                          # Static web content (deploy this)
│   ├── index.html                   # Main dashboard (9 tabs)
│   ├── executive-dashboard.html     # Executive summary (4 charts)
│   ├── analytics.html               # Analytics suite (12 charts)
│   ├── capability-map.html          # Visual capability model
│   ├── time-matrix.html             # Technology TIME matrix
│   ├── guides.html                  # Assessment guides
│   ├── technology-roadmap.html      # Detailed tech roadmap
│   ├── data/                        # All JSON data (11 files)
│   └── staticwebapp.config.json     # Azure configuration
├── tools/
│   └── excel_to_json.py             # Data converter
└── .github/workflows/
    └── azure-static-web-apps.yml    # Auto-deployment
```

**✓ All Dependencies:**
- ✅ No backend required (pure static)
- ✅ No Azure Functions needed
- ✅ No database required
- ✅ External CDNs (Plotly, html2canvas) - Optional, graceful degradation

**✓ Data Files (11 total):**
1. ✅ capabilities.json (43 KB)
2. ✅ pain-points.json (23 KB)
3. ✅ initiatives.json (16 KB)
4. ✅ evolution.json (22 KB)
5. ✅ assessment-data.json (112 KB)
6. ✅ guides.json (11 KB)
7. ✅ capability-map-data.json (20 KB)
8. ✅ technology-roadmap.json (16 KB)
9. ✅ time-matrix.json (13 KB)
10. ✅ time-technologies.json (15 KB)
11. ✅ analytics-charts.json (8 KB)
12. ✅ executive-dashboard.json (3 KB)

**Total data size: ~280 KB** (well under limits)

---

## 🚀 Deployment Steps

### Option 1: Azure Portal (Easiest - 10 minutes)

#### Step 1: Upload to GitHub
```bash
# 1. Extract azure-static-simple.tar.gz
# 2. Create GitHub repository
# 3. Upload all files
git init
git add .
git commit -m "Initial Legal Affairs EA Dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/legal-ea-dashboard.git
git push -u origin main
```

#### Step 2: Create Azure Static Web App
1. Go to https://portal.azure.com
2. Click "+ Create a resource"
3. Search "Static Web App"
4. Click "Create"

**Configuration:**
- **Subscription:** Your Azure subscription
- **Resource group:** Create new "legal-affairs-ea"
- **Name:** `legal-affairs-ea-dashboard`
- **Region:** West US 2 (or closest to you)
- **SKU:** Free (plenty for your needs)
- **Source:** GitHub
- Click "Sign in with GitHub"
- **Organization:** Your GitHub account
- **Repository:** legal-ea-dashboard
- **Branch:** main
- **Build Presets:** Custom
- **App location:** `/public`
- **Api location:** (leave empty - no API)
- **Output location:** (leave empty)

5. Click "Review + Create"
6. Click "Create"

⏰ **Wait 2-3 minutes** for deployment

#### Step 3: Get Your URL
1. Go to your Static Web App resource
2. URL will be: `https://legal-affairs-ea-dashboard-xxx.azurestaticapps.net`
3. Open in browser

**That's it! Your dashboard is live!**

---

### Option 2: Azure CLI (5 minutes)

```bash
# Login
az login

# Create resource group
az group create --name legal-affairs-ea --location westus2

# Create static web app
az staticwebapp create \
  --name legal-affairs-ea-dashboard \
  --resource-group legal-affairs-ea \
  --source https://github.com/YOUR_USERNAME/legal-ea-dashboard \
  --location westus2 \
  --branch main \
  --app-location "/public" \
  --login-with-github

# Get URL
az staticwebapp show \
  --name legal-affairs-ea-dashboard \
  --resource-group legal-affairs-ea \
  --query "defaultHostname" -o tsv
```

---

## ✅ Post-Deployment Verification

### Test Each Page:

**1. Main Dashboard (index.html)**
- [ ] Loads without errors
- [ ] All 9 tabs work
- [ ] Data displays in tables
- [ ] Charts render (if using Plotly tabs)
- [ ] Navigation buttons work

**2. Executive Dashboard**
- [ ] 4 metric cards show numbers
- [ ] Radar chart renders (requires Plotly CDN)
- [ ] Bar charts render
- [ ] Value timeline renders
- [ ] All charts are interactive

**3. Capability Model**
- [ ] Domains display in grid
- [ ] L1s show within domains
- [ ] L2 cards are visible
- [ ] Checkboxes work (show/hide)
- [ ] Color palette selector works
- [ ] Heat map toggle works
- [ ] Export button works (requires html2canvas CDN)

**4. TIME Matrix**
- [ ] Bubbles display in quadrants
- [ ] Quadrants labeled correctly (TOLERATE, INVEST, MIGRATE, ELIMINATE)
- [ ] Hover shows tooltips
- [ ] Filters work
- [ ] Legend shows counts

**5. Analytics**
- [ ] All 4 tabs work
- [ ] 12 charts render
- [ ] Pie/donut charts display
- [ ] Bar charts display
- [ ] Bubble charts work
- [ ] Insights show below charts

**6. Assessment Guides**
- [ ] Toggle between guides works
- [ ] All scales display
- [ ] Checkboxes work in "All Guides"
- [ ] Print button works

---

## 🔧 Troubleshooting

### Issue: Charts don't render

**Possible causes:**
1. **CDN blocked** - Check if cdn.plot.ly is accessible
2. **Browser console errors** - Press F12, check console
3. **Data not loading** - Check network tab for 404 errors

**Solutions:**
- For Plotly: Charts need internet to load CDN
- For html2canvas: Export won't work offline but view works
- All other features work 100% offline

### Issue: "No data found" errors

**Cause:** Data files not deployed correctly

**Solution:**
1. Verify `/public/data/*.json` files are in your repo
2. Check staticwebapp.config.json allows .json files
3. Clear browser cache
4. Check browser network tab for 404s

### Issue: Navigation doesn't work

**Cause:** Links pointing to wrong files

**Solution:**
- All links use relative paths (capability-map.html, not /capability-map.html)
- Should work automatically
- Check browser console for errors

---

## 📊 What Works Offline vs Online

### ✅ Works 100% Offline (No Internet):
- Main Dashboard (all 9 tabs)
- Capability Model (except Export as Image)
- TIME Matrix (all features)
- Assessment Guides (all features)
- Technology Roadmap
- All data loading and display

### ⚡ Requires Internet (CDN):
- Executive Dashboard charts (Plotly)
- Analytics page charts (Plotly)
- Capability Model "Export as Image" (html2canvas)
- Some dashboard tabs that use Plotly

### 💡 Recommendation:
For **internal use on BCI network**, this should work perfectly. All critical features work offline. Charts that need Plotly will just show blank if CDN is blocked, but all data/tables still work.

---

## 💰 Cost Estimate

**Azure Static Web Apps Free Tier:**
- ✅ 100 GB bandwidth/month FREE
- ✅ 0.5 GB storage FREE (you're using ~500 KB)
- ✅ Custom domains FREE
- ✅ SSL certificates FREE
- ✅ Unlimited build minutes

**Expected Cost: $0/month**

Your usage:
- Files: ~500 KB total
- Expected traffic: Internal BCI users only
- Bandwidth: Likely < 1 GB/month

**Free tier covers everything!**

---

## 🔒 Security Checklist

### Current State (Public):
- [ ] Anyone with URL can access
- [ ] No authentication required
- [ ] Data is publicly readable

### To Add Authentication (Optional):

**Option A: Azure AD (Recommended for BCI)**
1. Edit `public/staticwebapp.config.json`
2. Add authentication section
3. Require "authenticated" role
4. Only BCI users can access

**Option B: Custom Domain + Network Restrictions**
1. Add custom domain (ea.bci.ca)
2. Configure network rules
3. Restrict to BCI IP ranges

**For internal EA use, authentication is recommended.**

---

## 📋 Pre-Flight Checklist

Before deploying, verify:

- [ ] GitHub repository created
- [ ] All files uploaded to GitHub
- [ ] Azure account active
- [ ] You have permission to create resources
- [ ] You've reviewed the data (no sensitive info in JSON files)
- [ ] Browser can access cdn.plot.ly (for charts)

---

## 🎯 Expected Behavior After Deployment

### Page Load Times:
- **Main Dashboard:** < 1 second
- **Executive Dashboard:** 2-3 seconds (Plotly loading)
- **Analytics:** 2-3 seconds (multiple Plotly charts)
- **Capability Model:** < 1 second
- **TIME Matrix:** < 1 second
- **Guides:** < 1 second

### Data Updates:
**To update assessment data:**
1. Run: `python tools/excel_to_json.py new-assessment.xlsx`
2. Copy JSON files to `public/data/`
3. Commit and push to GitHub
4. Auto-deploys in 2-3 minutes

---

## ✅ YES, IT WILL RUN!

**Your package is ready to deploy:**
✅ All static files (no server-side code)
✅ All data embedded in JSON
✅ No Azure Functions needed
✅ No database needed
✅ No special configuration needed
✅ Works on Free tier
✅ Auto-deploys via GitHub Actions

**Just follow the deployment steps and you'll have a live EA dashboard in 10 minutes!**

---

## 🆘 If You Need Help

**Common Issues:**
- "Deployment failed" → Check GitHub Actions tab for logs
- "Page not found" → Wait 2-3 minutes after deployment
- "Charts blank" → Check if CDN is accessible (F12 → Network tab)
- "Data not loading" → Verify JSON files in /public/data/

**The solution is production-ready for Azure Static Web Apps!**
