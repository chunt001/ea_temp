# EA Visualization App - Azure Deployment

Complete React application for Enterprise Architecture visualization, ready for Azure Static Web Apps.

## Quick Start for Azure Deployment

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: EA Visualization App"
git remote add origin https://github.com/YOUR-USERNAME/ea-viz-app.git
git push -u origin main
```

### 2. Deploy to Azure Static Web Apps

1. Go to https://portal.azure.com
2. Click "+ Create a resource"
3. Search for "Static Web App" and click Create
4. **Configuration:**
   - Subscription: Your Azure subscription
   - Resource Group: Create new (e.g., "ea-viz-rg")
   - Name: `bci-ea-viz`
   - Region: Canada Central
   - **Deployment Source: GitHub**
   - Sign in to GitHub
   - Organization: Your GitHub account
   - Repository: ea-viz-app
   - Branch: main
5. **Build Details:**
   - Build Presets: React
   - App location: `/`
   - Api location: (leave empty)
   - Output location: `dist`
6. Click "Review + Create" then "Create"

Azure will automatically:
- Build your React app
- Deploy to a public URL
- Give you: `https://bci-ea-viz.azurestaticapps.net`

## Features

- ✅ Overview Dashboard with stats and charts
- ✅ Application Portfolio with search/filter
- ✅ Business Capability Model with hierarchy
- ✅ TIME Matrix strategic framework
- ✅ Heat Maps with multiple metrics
- ✅ Full navigation and routing
- ✅ Professional BCI-themed design

## Local Development (if you have permissions)

```bash
npm install
npm run dev
```

Open http://localhost:3000

## File Structure

```
azure-ea-app/
├── src/
│   ├── views/
│   │   ├── OverviewView.jsx
│   │   ├── ApplicationsView.jsx
│   │   ├── CapabilitiesView.jsx
│   │   ├── TIMEMatrixView.jsx
│   │   └── HeatMapView.jsx
│   ├── App.jsx
│   ├── App.css
│   └── index.jsx
├── public/
│   └── staticwebapp.config.json
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## Support

Created for BCI EA Team - Colin Pretorius, Gustavo Leal, Kevin Dowling, Jessie Lan
