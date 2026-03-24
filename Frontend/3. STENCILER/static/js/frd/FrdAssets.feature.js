// static/js/frd/FrdAssets.feature.js

export class FrdAssets {
    constructor(main) {
        this.main = main;
    }

    async load() {
        try {
            const res = await fetch('/api/frd/assets');
            if (res.ok) {
                const data = await res.json();
                this.main.state.uploadedAssets = data.assets.map(a => a.url);
                document.getElementById('asset-thumbnails').innerHTML = '';
                data.assets.forEach(a => this.addThumbnail(a.name, a.url));
            }
        } catch (e) { console.error("Load assets failed", e); }
    }

    addThumbnail(name, url) {
        const container = document.getElementById('asset-thumbnails');
        const wrap = document.createElement('div');
        wrap.className = 'relative group';
        wrap.innerHTML = `
            <img src="${url}" title="${name} (Click to copy URL)"
                 class="w-8 h-8 object-cover border border-[#333] cursor-pointer hover:border-figma-tabActive transition-all"
                 onclick="window.frdApp.assets.copyUrl('${url}', this)">
            <span class="absolute -top-1 -right-1 hidden group-hover:flex w-3 h-3
                         bg-red-500 text-white text-[8px] items-center justify-center
                         cursor-pointer rounded-full"
                  onclick="event.stopPropagation(); window.frdApp.assets.remove('${url}', this.parentElement)">×</span>
        `;
        container.appendChild(wrap);
    }

    async copyUrl(url, el) {
        await navigator.clipboard.writeText(url);
        el.style.borderColor = '#8cc63f';
        el.style.boxShadow = '0 0 5px #8cc63f';
        setTimeout(() => {
            el.style.borderColor = '#333';
            el.style.boxShadow = 'none';
        }, 500);
    }

    remove(url, el) {
        this.main.state.uploadedAssets = this.main.state.uploadedAssets.filter(u => u !== url);
        el.remove();
    }

    async handleUpload(files) {
        for (const file of files) {
            const fd = new FormData();
            fd.append('file', file);
            try {
                const res = await fetch('/api/frd/upload', { method: 'POST', body: fd });
                if (res.ok) {
                    const data = await res.json();
                    if (!this.main.state.uploadedAssets.includes(data.url)) {
                        this.main.state.uploadedAssets.push(data.url);
                        this.addThumbnail(file.name, data.url);
                    }
                }
            } catch (e) { console.error("Upload failed", e); }
        }
    }
}
