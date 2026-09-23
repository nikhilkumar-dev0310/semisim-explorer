import re

with open("simulator.html", "r") as f:
    html = f.read()

# Replace the whole particle engine and initCanvas
old_engine_pattern = r"// ==========================================\n\s*// Clean Canvas Particle Engine.*?function animate\(\) \{(.*?)\s*requestAnimationFrame\(animate\);\n\s*\}\n\s*animate\(\);\n\s*\}"

def replacer(match):
    return """// ==========================================
    // Clean Canvas Particle Engine
    // ==========================================
    let logicalWidth = 600;
    let logicalHeight = 176;

    class Particle {
      constructor(type) {
        this.type = type;
        this.reset();
      }

      reset() {
        this.y = 20 + Math.random() * (logicalHeight - 40);
        this.radius = this.type === 'electron' ? 3.5 : 4.0;

        if (this.type === 'electron') {
          this.x = 20 + Math.random() * 30;
          this.vx = 0.8 + Math.random() * 1.2;
          this.color = '#8ed5ff';
        } else {
          this.x = logicalWidth - (20 + Math.random() * 30);
          this.vx = -(0.5 + Math.random() * 0.9);
          this.color = '#e1c0ff';
        }
        this.vy = (Math.random() - 0.5) * 0.5;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.y < 15 || this.y > logicalHeight - 15) {
          this.vy *= -1;
        }

        if (this.x > logicalWidth - 25 || this.x < 25) {
          this.reset();
        }
      }

      draw(ctx) {
        ctx.save();
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.shadowColor = this.color;
        ctx.shadowBlur = 6;
        ctx.fill();
        ctx.restore();
      }
    }

    class Burst {
      constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.radius = 2;
        this.maxRadius = 18;
        this.alpha = 1.0;
      }
      update() {
        this.radius += 0.8;
        this.alpha -= 0.04;
      }
      draw(ctx) {
        if (this.alpha <= 0) return;
        ctx.save();
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.strokeStyle = this.color;
        ctx.globalAlpha = Math.max(0, this.alpha);
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.restore();
      }
    }

    let canvas, ctx, particles = [], bursts = [];

    function initCanvas() {
      canvas = document.getElementById('transportCanvas');
      if (!canvas) return;
      ctx = canvas.getContext('2d');

      function resizeCanvas() {
        if (!canvas.parentElement) return;
        const rect = canvas.parentElement.getBoundingClientRect();
        if (rect.width === 0) return; // Hidden
        const dpr = window.devicePixelRatio || 1;
        logicalWidth = rect.width;
        logicalHeight = rect.height;
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        canvas.style.width = rect.width + 'px';
        canvas.style.height = rect.height + 'px';
        ctx.scale(dpr, dpr);
      }

      const ro = new ResizeObserver(() => {
        resizeCanvas();
      });
      ro.observe(canvas.parentElement);
      
      // Delay initial resize to ensure layout is settled
      setTimeout(resizeCanvas, 50);
      requestAnimationFrame(() => requestAnimationFrame(resizeCanvas));

      particles = [];
      for (let i = 0; i < 18; i++) particles.push(new Particle('electron'));
      for (let i = 0; i < 18; i++) particles.push(new Particle('hole'));

      function animate() {
        ctx.clearRect(0, 0, logicalWidth, logicalHeight);

        const midX = logicalWidth / 2;
        ctx.fillStyle = state.mode === 'oled' ? 'rgba(255, 198, 64, 0.08)' : 'rgba(142, 213, 255, 0.08)';
        ctx.fillRect(midX - 40, 10, 80, logicalHeight - 20);
        ctx.strokeStyle = state.mode === 'oled' ? 'rgba(255, 198, 64, 0.3)' : 'rgba(142, 213, 255, 0.3)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.strokeRect(midX - 40, 10, 80, logicalHeight - 20);
        ctx.setLineDash([]);

        ctx.fillStyle = state.mode === 'oled' ? '#ffc640' : '#8ed5ff';
        ctx.font = '10px JetBrains Mono, monospace';
        ctx.textAlign = 'center';
        ctx.fillText(state.mode === 'oled' ? 'Exciton Recomb.' : 'Charge Dissoc.', midX, 26);

        // Update & draw particles
        particles.forEach(p => {
          p.update();
        });

        // Advanced Collision Logic (OLED Recombination)
        if (state.mode === 'oled') {
          const recombZoneStart = midX - 40;
          const recombZoneEnd = midX + 40;
          const electrons = particles.filter(p => p.type === 'electron' && p.x >= recombZoneStart && p.x <= recombZoneEnd);
          const holes = particles.filter(p => p.type === 'hole' && p.x >= recombZoneStart && p.x <= recombZoneEnd);
          const consumedHoles = new Set();
          
          electrons.forEach(e => {
            let nearestHole = null;
            let nearestDist = Infinity;
            holes.forEach(h => {
              if (consumedHoles.has(h)) return;
              const dist = Math.hypot(e.x - h.x, e.y - h.y);
              if (dist < 14 && dist < nearestDist) {
                nearestDist = dist;
                nearestHole = h;
              }
            });

            if (nearestHole && Math.random() < 0.06) {
              consumedHoles.add(nearestHole);
              bursts.push(new Burst((e.x + nearestHole.x) / 2, (e.y + nearestHole.y) / 2, '#ffc640'));
              e.x = 35;
              e.y = Math.random() * (logicalHeight - 20) + 10;
              nearestHole.x = logicalWidth - 35;
              nearestHole.y = Math.random() * (logicalHeight - 20) + 10;
            }
          });
        }

        particles.forEach(p => p.draw(ctx));

        // Draw bursts
        bursts.forEach(b => {
          b.update();
          b.draw(ctx);
        });
        bursts = bursts.filter(b => b.alpha > 0);

        requestAnimationFrame(animate);
      }
      animate();
    }"""

import re
html = re.sub(r"// ==========================================\n\s*// Clean Canvas Particle Engine.*?function animate\(\) \{.*?\s*requestAnimationFrame\(animate\);\n\s*\}\n\s*animate\(\);\n\s*\}", replacer, html, flags=re.DOTALL)

with open("simulator.html", "w") as f:
    f.write(html)
