
import os

css_path = "/Users/francois-jeandazin/AETHERFLOW/Frontend/3. STENCILER/static/css/stenciler.css"
kimi_path = "/Users/francois-jeandazin/AETHERFLOW/Frontend/3. STENCILER/static/css/kimi_mess.css"

with open(kimi_path, "r") as f:
    kimi_css = f.read()

overrides = """
/* === GEMINI-PAI: STRUCTURAL ENFORCEMENT === */

.stenciler-app {
  display: flex !important;
  flex-direction: column !important;
  height: 100vh !important;
  overflow: hidden !important;
}

.stenciler-workspace {
  display: flex !important;
  flex: 1 !important;
  overflow: hidden !important;
}

#slot-sidebar-left {
  width: 220px !important;
  min-width: 220px !important;
  max-width: 220px !important;
  flex-shrink: 0 !important;
  border-right: 1px solid var(--border-subtle) !important;
  background: var(--bg-secondary) !important;
  display: flex !important;
  flex-direction: column !important;
  overflow-y: auto !important;
}

#slot-sidebar-right {
  width: 220px !important;
  min-width: 220px !important;
  max-width: 220px !important;
  flex-shrink: 0 !important;
  border-left: 1px solid var(--border-subtle) !important;
  background: var(--bg-secondary) !important;
  display: flex !important;
  flex-direction: column !important;
  overflow-y: auto !important;
  padding: 16px !important;
}

.right-zone {
  flex: 1 !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
  min-width: 0 !important;
}

#slot-main {
  flex: 1 !important;
  position: relative !important;
  display: flex !important;
  flex-direction: column !important;
  background: var(--bg-primary) !important;
}

#slot-canvas-zone {
  flex: 1 !important;
}

/* Fix for the black preview issue */
#slot-canvas-zone canvas {
    background: transparent !important;
}
"""

with open(css_path, "w") as f:
    f.write(kimi_css)
    f.write("\n")
    f.write(overrides)

print("CSS Merged Successfully with Overrides.")
