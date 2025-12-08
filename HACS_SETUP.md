# HACS Setup Guide for GDD Calculator

## 📁 Repository Structure

For HACS compatibility, your GitHub repository should be organized like this:

```
HA-GDD-calculator/
├── custom_components/
│   └── gdd/
│       ├── __init__.py
│       ├── config_flow.py
│       ├── const.py
│       ├── coordinator.py
│       ├── manifest.json
│       ├── sensor.py
│       ├── services.yaml
│       ├── strings.json
│       └── translations/
│           └── en.json
├── hacs.json
├── README.md
├── LICENSE
└── .gitignore
```

## 🚀 Publishing to GitHub

### 1. Create Repository Structure
```bash
mkdir HA-GDD-calculator
cd HA-GDD-calculator
mkdir -p custom_components/gdd
mkdir -p custom_components/gdd/translations
```

### 2. Copy Files
Place all the integration files in the correct locations:
- All Python files → `custom_components/gdd/`
- `en.json` → `custom_components/gdd/translations/`
- `hacs.json` → root directory
- `README.md` → root directory
- `LICENSE` → root directory

### 3. Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial release of GDD Calculator integration"
git remote add origin https://github.com/Nathanc87/HA-GDD-calculator.git
git branch -M main
git push -u origin main
```

### 4. Create Release
1. Go to GitHub → Releases → "Create a new release"
2. Tag: `v2.0.0`
3. Title: `GDD Calculator v2.0.0`
4. Description: List the features and improvements
5. Attach a ZIP file of the integration

## 🔧 HACS Integration

### Option 1: Submit to HACS Default Repository
1. Fork the [HACS repository](https://github.com/hacs/default)
2. Add your repository to `integration.json`
3. Submit a Pull Request

### Option 2: Add as Custom Repository
Users can add your integration manually:
1. HACS → Integrations
2. Three dots menu → "Custom repositories"
3. Add: `https://github.com/Nathanc87/HA-GDD-calculator`
4. Category: Integration

## ✅ HACS Validation Checklist

- ✅ `hacs.json` file present
- ✅ `manifest.json` with correct domain
- ✅ README.md with installation instructions
- ✅ LICENSE file
- ✅ Proper directory structure
- ✅ GitHub releases for versioning
- ✅ No hardcoded paths
- ✅ Follows Home Assistant coding standards

## 📋 Release Checklist

Before each release:

1. **Update Version Numbers**:
   - `manifest.json` → version
   - `const.py` → any version constants
   - Create git tag

2. **Test Integration**:
   - Install manually first
   - Verify all sensors work
   - Test config flow
   - Check services

3. **Update Documentation**:
   - README.md changes
   - Release notes
   - Screenshots if UI changed

4. **Create GitHub Release**:
   - Semantic versioning (v2.0.0, v2.1.0, etc.)
   - Include ZIP file
   - Document changes

## 🎯 HACS Benefits

Once published, users get:
- ✅ **Easy installation** via HACS GUI
- ✅ **Automatic updates** when you release new versions
- ✅ **Version management** and rollback capabilities
- ✅ **Integration discovery** through HACS store
- ✅ **Dependency tracking** for Home Assistant versions

## 📞 Support

For HACS-specific issues:
- HACS Documentation: https://hacs.xyz/
- HACS Discord: https://discord.gg/apgchf8
- Home Assistant Community: https://community.home-assistant.io/

Your integration is now ready for HACS! 🎉
