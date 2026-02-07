# MISSION: IR + Genome View Integration

**Date**: 6 février 2026  
**Status**: Error correction + Implementation  
**Error**: SVG path attribute malformed (`d: Expected number`)

---

## 🐛 ERROR TO FIX

```
4:81 Error: <path> attribute d: Expected number, "… 2 0 002-2V6a2-2H6a2 2 0 00-2 2v…"
```

**Location**: Likely in SVG icon or inline SVG in template
**Cause**: Missing space between path commands (e.g., `002` should be `0 0 2`)

---

## 🎯 OBJECTIVES

1. **Fix SVG Error**: Correct malformed path data in icons/SVGs
2. **Enhance IR View**: Improve Intent Revue panel display
3. **Enhance Genome View**: Improve Genome panel with proper drilldown
4. **Integration**: Seamless 50/50 layout as per spec

---

## 📋 REQUIREMENTS

### Fix SVG Paths
- Search for malformed SVG paths in templates
- Fix spacing issues in path commands
- Replace inline SVGs with proper icons if needed

### IR View (Left Panel)
- Display endpoints with method badges (GET/POST)
- Show visual hints/wireframes
- Component suggestions by typology
- Expandable sections

### Genome View (Right Panel)
- N0/N1/N2/N3 hierarchy display
- Interactive drilldown
- Component counts per level
- DaisyUI component references

---

## 🔧 IMPLEMENTATION PLAN

```json
{
  "priority": "high",
  "files_to_modify": [
    "Backend/Prod/templates/studio_homeos.html"
  ],
  "tasks": [
    "Fix SVG path syntax errors",
    "Verify IR panel content structure", 
    "Verify Genome panel content structure",
    "Test 50/50 layout responsiveness"
  ]
}
```

---

## ✅ VALIDATION

- [ ] No console errors
- [ ] IR panel displays correctly
- [ ] Genome panel displays correctly  
- [ ] Drilldown works in sidebar
- [ ] Layout is 50/50 as specified

---

## 📝 NOTES

Error suggests path data has `002` instead of `0 0 2`.
Common in SVG paths when numbers concatenate.
Check all icon definitions and inline SVGs.
