// Animações de Bolinhas de Vôlei - Fundo Dinâmico
document.addEventListener('DOMContentLoaded', function() {
    // Criar container de animação se estiver na home
    if (window.location.pathname === '/' || window.location.pathname === '') {
        createVolleyballAnimation();
    }
});

function createVolleyballAnimation() {
    const container = document.createElement('div');
    container.id = 'volleyball-bg-animation';
    container.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
        background: transparent;
    `;
    
    document.body.insertBefore(container, document.body.firstChild);
    
    // Criar 8 bolinhas de vôlei animadas
    const ballCount = 8;
    for (let i = 0; i < ballCount; i++) {
        createVolleyball(container, i);
    }
    
    // Aumentar z-index do main-content para ficar acima das animações
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.style.position = 'relative';
        mainContent.style.zIndex = '10';
    }
}

function createVolleyball(container, index) {
    const ball = document.createElement('div');
    const size = 40 + Math.random() * 60; // 40px a 100px
    const startX = Math.random() * 100;
    const startY = Math.random() * 100;
    const duration = 15 + Math.random() * 15; // 15s a 30s
    const delay = index * 0.5;
    
    ball.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: radial-gradient(circle at 30% 30%, rgba(0, 255, 163, 0.4), rgba(0, 255, 163, 0.1));
        border: 2px solid rgba(0, 255, 163, 0.3);
        border-radius: 50%;
        left: ${startX}%;
        top: ${startY}%;
        opacity: 0.3;
        box-shadow: 0 0 ${size/2}px rgba(0, 255, 163, 0.2), inset -2px -2px 8px rgba(0, 0, 0, 0.3);
        animation: floatVolleyball ${duration}s ease-in-out ${delay}s infinite;
    `;
    
    container.appendChild(ball);
}

// Adicionar animação CSS dinamicamente
const style = document.createElement('style');
style.textContent = `
    @keyframes floatVolleyball {
        0% {
            transform: translateY(0px) translateX(0px) scale(1);
            opacity: 0.2;
        }
        25% {
            transform: translateY(-100px) translateX(50px) scale(1.1);
            opacity: 0.4;
        }
        50% {
            transform: translateY(-200px) translateX(-30px) scale(0.9);
            opacity: 0.3;
        }
        75% {
            transform: translateY(-100px) translateX(80px) scale(1.05);
            opacity: 0.35;
        }
        100% {
            transform: translateY(0px) translateX(0px) scale(1);
            opacity: 0.2;
        }
    }
    
    @keyframes floatVolleyballSlow {
        0% {
            transform: translateY(0px) translateX(0px) rotateZ(0deg);
            opacity: 0.15;
        }
        50% {
            transform: translateY(-300px) translateX(150px) rotateZ(180deg);
            opacity: 0.3;
        }
        100% {
            transform: translateY(0px) translateX(0px) rotateZ(360deg);
            opacity: 0.15;
        }
    }
    
    #volleyball-bg-animation {
        background: 
            radial-gradient(circle at 20% 50%, rgba(0, 255, 163, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(112, 0, 255, 0.05) 0%, transparent 50%);
    }
`;
document.head.appendChild(style);
