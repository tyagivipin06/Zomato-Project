import os

def main():
    root = r"c:\Users\sai\Documents\Phone Data\Next leap\Zomato Project"
    search_file = os.path.join(root, "stitch_ai_restaurant_recommendation_system", "lumiere_gastronomy_search_animated", "code.html")
    rec_file = os.path.join(root, "stitch_ai_restaurant_recommendation_system", "lumiere_gastronomy_recommendations_animated", "code.html")

    with open(search_file, 'r', encoding='utf-8') as f:
        search_html = f.read()
    with open(rec_file, 'r', encoding='utf-8') as f:
        rec_html = f.read()

    # Extract Tailwind config and styles from search_html
    head_start = search_html.find("<head>")
    head_end = search_html.find("</head>")
    head_content = search_html[head_start:head_end + 7]

    # Extract Header and Footer from search_html
    header_start = search_html.find("<header")
    header_end = search_html.find("</header>") + 9
    header_content = search_html[header_start:header_end]

    footer_start = search_html.find("<footer")
    footer_end = search_html.find("</footer>") + 9
    footer_content = search_html[footer_start:footer_end]

    # Extract Search Main
    search_main_start = search_html.find("<main")
    search_main_end = search_html.find("</main>") + 7
    search_main_content = search_html[search_main_start:search_main_end]
    search_main_content = search_main_content.replace("<main", "<main id=\"search-view\"")

    # Extract Rec Main
    rec_main_start = rec_html.find("<main")
    rec_main_end = rec_html.find("</main>") + 7
    rec_main_content = rec_html[rec_main_start:rec_main_end]
    rec_main_content = rec_main_content.replace("<main", "<main id=\"recommendations-view\" class=\"hidden flex-grow pt-24 pb-section-gap px-margin-mobile md:px-margin-desktop max-w-container-max mx-auto w-full flex flex-col gap-stack-lg relative z-10\"")

    # Clean up the Rec Main to serve as templates
    # Replace the hardcoded cards with a container
    grid_start = rec_main_content.find('<div class="grid grid-cols-1')
    # Find the end of the grid div... this is a bit hacky with string find, let's just replace the interior
    
    # We will inject our custom JS logic
    js_logic = """
<script>
    // --- SHADER LOGIC ---
    const canvas = document.getElementById('shader-canvas') || document.getElementById('glcanvas');
    const gl = canvas.getContext('webgl');

    if (gl) {
        const vsSource = `
            attribute vec4 a_position;
            varying vec2 v_texCoord;
            void main() {
                gl_Position = a_position;
                v_texCoord = a_position.xy * 0.5 + 0.5;
            }
        `;
        const fsSource = `
            precision highp float;
            varying vec2 v_texCoord;
            uniform float u_time;
            uniform vec2 u_resolution;

            void main() {
                vec2 uv = v_texCoord;
                float noise = sin(uv.x * 3.0 + u_time * 0.2) * 0.5 + 0.5;
                noise *= sin(uv.y * 2.0 - u_time * 0.1) * 0.5 + 0.5;
                vec3 midnight = vec3(0.043, 0.075, 0.149);
                vec3 violet = vec3(0.545, 0.361, 0.965);
                vec3 deepAzure = vec3(0.0, 0.2, 0.4);
                vec3 color = mix(midnight, deepAzure, uv.y * 0.5);
                color = mix(color, violet * 0.2, noise);
                float dist = distance(uv, vec2(0.5));
                color *= 1.2 - dist;
                gl_FragColor = vec4(color, 1.0);
            }
        `;
        function loadShader(gl, type, source) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            return shader;
        }
        const vertexShader = loadShader(gl, gl.VERTEX_SHADER, vsSource);
        const fragmentShader = loadShader(gl, gl.FRAGMENT_SHADER, fsSource);
        const shaderProgram = gl.createProgram();
        gl.attachShader(shaderProgram, vertexShader);
        gl.attachShader(shaderProgram, fragmentShader);
        gl.linkProgram(shaderProgram);
        
        const positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1.0, 1.0, 1.0, 1.0, -1.0, -1.0, 1.0, -1.0]), gl.STATIC_DRAW);
        
        const posLoc = gl.getAttribLocation(shaderProgram, 'a_position');
        const timeLoc = gl.getUniformLocation(shaderProgram, 'u_time');
        const resLoc = gl.getUniformLocation(shaderProgram, 'u_resolution');
        
        function render(now) {
            now *= 0.001;
            if (canvas.width !== canvas.clientWidth || canvas.height !== canvas.clientHeight) {
                canvas.width = canvas.clientWidth;
                canvas.height = canvas.clientHeight;
                gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
            }
            gl.useProgram(shaderProgram);
            gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
            gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
            gl.enableVertexAttribArray(posLoc);
            gl.uniform1f(timeLoc, now);
            gl.uniform2f(resLoc, canvas.width, canvas.height);
            gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
            requestAnimationFrame(render);
        }
        requestAnimationFrame(render);
    }

    // --- APP LOGIC ---
    document.addEventListener("DOMContentLoaded", () => {
        // Fetch locations and cuisines
        fetch('/api/v1/locations')
            .then(r => r.json())
            .then(data => {
                const dl = document.getElementById('locations');
                if (dl) dl.innerHTML = data.locations.map(l => `<option value="${l}"></option>`).join('');
            });
            
        fetch('/api/v1/cuisines')
            .then(r => r.json())
            .then(data => {
                const dl = document.getElementById('cuisines');
                if (dl) dl.innerHTML = data.cuisines.map(c => `<option value="${c}"></option>`).join('');
            });

        const form = document.querySelector('form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Get values
            const location = document.querySelector('input[list="locations"]').value;
            const cuisine = document.querySelector('input[list="cuisines"]').value;
            const budget = document.querySelector('input[name="budget"]:checked')?.value || "medium";
            const minRating = parseFloat(document.querySelector('input[type="range"]').value);
            const additional = document.querySelector('textarea').value;
            
            if (!location) {
                alert("Destination is required.");
                return;
            }

            // Map frontend budget terms to backend
            const budgetMap = { "accessible": "low", "premium": "medium", "exclusive": "high" };
            
            const payload = {
                location: location,
                budget: budgetMap[budget] || "medium",
                min_rating: minRating,
                cuisine: cuisine || null,
                additional: additional || null
            };

            // UI states
            document.getElementById('search-view').classList.add('hidden');
            document.getElementById('loading-view').classList.remove('hidden');

            try {
                const res = await fetch('/api/v1/recommend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!res.ok) {
                    const err = await res.json();
                    throw new Error(err.detail || "Server error");
                }
                
                const data = await res.json();
                renderRecommendations(data);
                
                document.getElementById('loading-view').classList.add('hidden');
                document.getElementById('recommendations-view').classList.remove('hidden');
                
            } catch (err) {
                alert("Error: " + err.message);
                document.getElementById('loading-view').classList.add('hidden');
                document.getElementById('search-view').classList.remove('hidden');
            }
        });
    });
    
    function renderRecommendations(data) {
        document.getElementById('summary-text').innerText = data.summary;
        
        const banner = document.getElementById('alert-banner');
        if (data.metadata.relaxation_applied) {
            banner.classList.remove('hidden');
            document.getElementById('alert-text').innerText = data.metadata.warnings.join(' ');
        } else {
            banner.classList.add('hidden');
        }
        
        const grid = document.getElementById('results-grid');
        grid.innerHTML = '';
        
        data.recommendations.forEach((rec, idx) => {
            const defaultImages = [
                'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1544148103-0773bf10d330?auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=800&q=80'
            ];
            const img = defaultImages[idx % defaultImages.length];
            
            const card = `
            <article class="glass-panel rounded-xl overflow-hidden flex flex-col relative group hover:-translate-y-1 transition-all duration-300 ai-glow-border shadow-[0_8px_30px_rgb(0,0,0,0.12)]">
                <div class="absolute top-4 left-4 z-20 bg-background/80 backdrop-blur-md text-primary font-bold px-3 py-1 rounded-full border border-primary/30 flex items-center gap-1 shadow-lg">
                    <span class="material-symbols-outlined text-[16px]" style="font-variation-settings: 'FILL' 1;">star</span> #${rec.rank} Match
                </div>
                <div class="relative h-64 w-full overflow-hidden">
                    <div class="bg-cover bg-center w-full h-full group-hover:scale-105 transition-transform duration-700" style="background-image: url('${img}')"></div>
                    <div class="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent opacity-90"></div>
                </div>
                <div class="p-6 flex flex-col flex-grow relative z-10 -mt-16">
                    <h2 class="text-headline-md font-headline-md text-on-surface mb-3">${rec.name}</h2>
                    <div class="flex flex-wrap gap-2 mb-5">
                        <span class="px-2.5 py-1 rounded-md bg-primary-container/20 text-primary-fixed-dim text-label-sm font-label-sm border border-primary/20 backdrop-blur-sm">${rec.cuisine}</span>
                        <span class="px-2.5 py-1 rounded-md bg-surface-container-high text-on-surface-variant text-label-sm font-label-sm border border-white/5 backdrop-blur-sm">₹${rec.estimated_cost}</span>
                    </div>
                    <div class="flex items-center gap-4 mb-5 text-body-md font-body-md text-on-surface-variant">
                        <div class="flex items-center gap-1.5">
                            <span class="material-symbols-outlined text-secondary text-sm" style="font-variation-settings: 'FILL' 1;">star</span>
                            <span>${rec.rating}</span>
                        </div>
                    </div>
                    <div class="mt-auto pt-5 border-t border-white/10">
                        <p class="text-body-md font-body-md text-on-surface-variant/80 italic leading-relaxed">"${rec.explanation}"</p>
                    </div>
                </div>
            </article>
            `;
            grid.innerHTML += card;
        });
    }

    function showSearch() {
        document.getElementById('recommendations-view').classList.add('hidden');
        document.getElementById('search-view').classList.remove('hidden');
    }
</script>
    """

    final_html = f"""<!DOCTYPE html>
<html class="dark" lang="en">
{head_content}
<body class="min-h-screen flex flex-col font-body-md text-body-md relative antialiased selection:bg-primary selection:text-on-primary bg-transparent">
    <canvas id="shader-canvas" class="fixed inset-0 w-full h-full -z-10 pointer-events-none" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -2; pointer-events: none;"></canvas>
    {header_content}
    
    {search_main_content}
    
    <main id="loading-view" class="hidden flex-grow flex items-center justify-center pt-32 pb-20 px-margin-mobile md:px-margin-desktop relative z-10 w-full max-w-container-max mx-auto">
        <div class="flex flex-col items-center gap-4">
            <span class="material-symbols-outlined animate-spin text-primary" style="font-size: 3rem;">autorenew</span>
            <p class="text-on-surface-variant font-headline-md">Curating your experience...</p>
        </div>
    </main>

    <main id="recommendations-view" class="hidden flex-grow pt-24 pb-section-gap px-margin-mobile md:px-margin-desktop max-w-container-max mx-auto w-full flex flex-col gap-stack-lg relative z-10">
        <section class="glass-panel rounded-xl p-8 md:p-12 relative overflow-hidden group">
            <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-primary/20 to-transparent blur-3xl rounded-full translate-x-1/2 -translate-y-1/2"></div>
            <div class="flex items-start gap-5 relative z-10">
                <div class="hidden md:flex mt-2 p-3 rounded-full bg-surface-container-high border border-white/10 text-primary shrink-0 ai-glow-border">
                    <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">auto_awesome</span>
                </div>
                <div>
                    <h1 class="text-headline-lg-mobile md:text-headline-lg font-headline-lg mb-3 text-on-surface tracking-tight">Curated for You</h1>
                    <p id="summary-text" class="text-body-lg font-body-lg text-on-surface-variant max-w-3xl leading-relaxed"></p>
                </div>
            </div>
        </section>

        <div id="alert-banner" class="hidden rounded-xl bg-yellow-900/40 border border-yellow-500/50 p-5 flex gap-4 items-center">
            <span class="material-symbols-outlined text-yellow-400">info</span>
            <p id="alert-text" class="text-body-md font-body-md text-yellow-100/90"></p>
            <button onclick="document.getElementById('alert-banner').classList.add('hidden')" class="ml-auto text-label-sm font-label-sm text-yellow-400 uppercase tracking-wider hover:text-yellow-300 transition-colors">Dismiss</button>
        </div>

        <div id="results-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter mt-stack-md">
            <!-- Rendered via JS -->
        </div>

        <div class="mt-stack-lg flex justify-center">
            <button onclick="showSearch()" class="bg-surface-container/50 glass-panel border border-white/10 text-on-surface px-8 py-4 rounded-full flex items-center gap-3 hover:bg-surface-container hover:border-primary/50 transition-all duration-300 group shadow-lg">
                <span class="material-symbols-outlined group-hover:-rotate-90 transition-transform duration-300 text-primary">tune</span>
                <span class="font-label-sm text-label-sm uppercase tracking-wider">Refine Preferences</span>
            </button>
        </div>
    </main>

    {footer_content}
    {js_logic}
</body>
</html>
"""
    
    with open(os.path.join(root, "index.html"), 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("Successfully built index.html!")

if __name__ == "__main__":
    main()
