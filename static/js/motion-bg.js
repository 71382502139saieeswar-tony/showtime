/* SHOWTIME APP - LIVELY MOTION CANVAS ENGINE */

class MotionBackground {
    constructor() {
        this.canvas = document.createElement("canvas");
        this.ctx = this.canvas.getContext("2d");
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 150 };
        this.spotlightAngle = 0;

        this.init();
    }

    init() {
        this.canvas.id = "motionCanvas";
        this.canvas.style.position = "fixed";
        this.canvas.style.top = "0";
        this.canvas.style.left = "0";
        this.canvas.style.width = "100vw";
        this.canvas.style.height = "100vh";
        this.canvas.style.pointerEvents = "none";
        this.canvas.style.zIndex = "0";

        document.body.prepend(this.canvas);
        this.resize();

        window.addEventListener("resize", () => this.resize());
        window.addEventListener("mousemove", (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        this.createParticles();
        this.animate();
    }

    resize() {
        this.width = this.canvas.width = window.innerWidth;
        this.height = this.canvas.height = window.innerHeight;
    }

    createParticles() {
        this.particles = [];
        const count = Math.floor((this.width * this.height) / 12000);
        const colors = ["#ff2a5f", "#ffb800", "#00f0ff", "#ffffff"];

        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * this.width,
                y: Math.random() * this.height,
                radius: Math.random() * 2 + 0.8,
                color: colors[Math.floor(Math.random() * colors.length)],
                vx: (Math.random() - 0.5) * 0.6,
                vy: (Math.random() - 0.5) * 0.6,
                alpha: Math.random() * 0.7 + 0.3
            });
        }
    }

    drawProjectorBeam() {
        this.spotlightAngle += 0.005;
        const originX = this.width * 0.5;
        const originY = -50;

        const targetX = originX + Math.sin(this.spotlightAngle) * (this.width * 0.4);
        const targetY = this.height + 100;

        const gradient = this.ctx.createRadialGradient(
            originX, originY, 10,
            targetX, targetY, this.width * 0.6
        );

        gradient.addColorStop(0, "rgba(255, 42, 95, 0.12)");
        gradient.addColorStop(0.5, "rgba(0, 240, 255, 0.05)");
        gradient.addColorStop(1, "rgba(10, 12, 20, 0)");

        this.ctx.save();
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.moveTo(originX, originY);
        this.ctx.lineTo(targetX - 250, targetY);
        this.ctx.lineTo(targetX + 250, targetY);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.restore();
    }

    animate() {
        this.ctx.clearRect(0, 0, this.width, this.height);

        // Projector Sweep
        this.drawProjectorBeam();

        // Mouse glow
        if (this.mouse.x !== null) {
            const mGlow = this.ctx.createRadialGradient(
                this.mouse.x, this.mouse.y, 0,
                this.mouse.x, this.mouse.y, 180
            );
            mGlow.addColorStop(0, "rgba(255, 42, 95, 0.15)");
            mGlow.addColorStop(1, "rgba(0,0,0,0)");
            this.ctx.fillStyle = mGlow;
            this.ctx.beginPath();
            this.ctx.arc(this.mouse.x, this.mouse.y, 180, 0, Math.PI * 2);
            this.ctx.fill();
        }

        // Draw Particles
        this.particles.forEach((p) => {
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0) p.x = this.width;
            if (p.x > this.width) p.x = 0;
            if (p.y < 0) p.y = this.height;
            if (p.y > this.height) p.y = 0;

            this.ctx.save();
            this.ctx.globalAlpha = p.alpha;
            this.ctx.fillStyle = p.color;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();
        });

        requestAnimationFrame(() => this.animate());
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new MotionBackground();
});
