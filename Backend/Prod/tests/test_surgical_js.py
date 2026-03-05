import sys
import os
from pathlib import Path

# Setup path
cwd = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(cwd, "../..")
sys.path.append(backend_dir)

from Prod.core.apply_engine import ApplyEngine

def test_surgical_js():
    print("Testing Surgical JS...")
    
    # 1. Create a dummy JS file
    prod_dir = os.path.join(backend_dir, "Prod")
    dummy_js = Path(prod_dir) / "tests" / "dummy_canvas.js"
    dummy_js.write_text("""
import { Renderer } from './renderer.js';

class CanvasEngine {
    constructor() {
        this.ctx = null;
    }

    render() {
        console.log("old render");
    }
}

function initCanvas() {
    console.log("init");
}
""", encoding='utf-8')

    # 2. Give fake LLM Output containing Surgical JSON targeting the JS file
    llm_output = '''
I will fix the rendering issue.
```json
{
  "operations": [
    {
      "type": "add_import",
      "import": "import { MathUtils } from './math.js';"
    },
    {
      "type": "add_method",
      "target": "CanvasEngine",
      "code": "    resize(newW, newH) {\\n        console.log(\\"resized\\", newW, newH);\\n    }"
    },
    {
      "type": "modify_method",
      "target": "CanvasEngine.render",
      "code": "    render() {\\n        this.ctx.clear();\\n        console.log(\\"new render\\");\\n    }"
    },
    {
      "type": "modify_function",
      "target": "initCanvas",
      "code": "function initCanvas() {\\n    console.log(\\"init V2\\");\\n    return new CanvasEngine();\\n}"
    }
  ]
}
```
'''

    # 3. Apply changes via Engine
    engine = ApplyEngine(project_root=Path(prod_dir).parent.parent)
    results = engine.apply(
        step_id="test_js",
        output=llm_output,
        target_files=[str(dummy_js)],
        step_type="refactoring",
        surgical_mode=True,
        context={"auto_apply": True}
    )

    print("\nResults:", results)
    print("\nModified File Content:")
    print(dummy_js.read_text(encoding='utf-8'))
    
if __name__ == "__main__":
    test_surgical_js()
