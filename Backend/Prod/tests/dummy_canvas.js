
import { Renderer } from './renderer.js';
import { MathUtils } from './math.js';


class CanvasEngine {
    constructor() {
        this.ctx = null;
    }

        render() {
        this.ctx.clear();
        console.log("new render");
    }


    resize(newW, newH) {
        console.log("resized", newW, newH);
    }
}

function initCanvas() {
    console.log("init V2");
    return new CanvasEngine();
}
