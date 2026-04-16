const socket = io();
const canvas = document.getElementById('sim');
const ctx = canvas.getContext('2d');
const statusText = document.getElementById('status');

socket.on('update', (data) => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    statusText.innerText = data.acao_ia;

    // Área de quarentena
    ctx.strokeStyle = "#333";
    ctx.strokeRect(650, 450, 140, 140);

    data.agentes.forEach(a => {
        ctx.beginPath();
        // Se em lockdown, desenha na caixa
        let x = a.l ? (a.id % 130) + 655 : a.x;
        let y = a.l ? (a.id % 130) + 455 : a.y;
        
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        if (a.s === 0) ctx.fillStyle = "#2ecc71";
        else if (a.s === 1) ctx.fillStyle = "#e74c3c";
        else ctx.fillStyle = "#3498db";
        
        ctx.fill();
    });
});