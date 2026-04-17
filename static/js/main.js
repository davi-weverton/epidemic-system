const socket = io();
const canvas = document.getElementById('sim');
const ctx = canvas.getContext('2d');
const statusDiv = document.getElementById('status');

socket.on('update', (data) => {
    // 1. Validar se os dados chegaram
    if (!data.agentes || !data.stats) return;

    // 2. Atualizar Estatísticas no Painel Lateral
    document.getElementById('stat-total').innerText = data.stats.total;
    document.getElementById('stat-s').innerText = data.stats.s;
    document.getElementById('stat-i').innerText = data.stats.i;
    document.getElementById('stat-r').innerText = data.stats.r;
    document.getElementById('stat-m').innerText = data.stats.m;
    document.getElementById('stat-l').innerText = data.stats.l;

    // 3. Atualizar Texto de Status e Estilo Visual
    statusDiv.innerText = data.acao_ia;
    if (data.acao_ia === "LOCKDOWN ATIVO") {
        statusDiv.className = "w-full py-3 rounded-xl font-mono font-black text-center transition-all duration-300 bg-red-600 text-white shadow-[0_0_15px_rgba(231,76,60,0.4)] uppercase tracking-tighter";
        canvas.style.borderColor = "#e74c3c";
    } else {
        statusDiv.className = "w-full py-3 rounded-xl font-mono font-black text-center transition-all duration-300 bg-blue-600/20 text-blue-400 border border-blue-600/30 uppercase tracking-tighter";
        canvas.style.borderColor = "#1f2937"; 
    }

    // 4. Desenhar Agentes no Canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Desenha o quadrado de quarentena (opcional, mantido conforme original)
    ctx.strokeStyle = "#333";
    ctx.setLineDash([5, 5]);
    ctx.strokeRect(650, 450, 140, 140);
    ctx.setLineDash([]); 

    data.agentes.forEach(a => {
        ctx.beginPath();
        let x, y;

        if (a.l) {
            // Organiza em grade na quarentena
            let col = (a.id % 12);
            let row = Math.floor((a.id % 144) / 12);
            x = 660 + (col * 10);
            y = 460 + (row * 10);
        } else {
            x = a.x;
            y = a.y;
        }
        
        let radius = 4;
        if (a.s === 1) radius = 6;

        ctx.arc(x, y, radius, 0, Math.PI * 2);
        // Cores baseadas no status
        if (a.s === 0) ctx.fillStyle = "#2ecc71";      // Saudável
        else if (a.s === 1) ctx.fillStyle = "#e74c3c"; // Infectado
        else ctx.fillStyle = "#3498db";                // Imune
        
        ctx.fill();
        ctx.closePath();
    });
});

function startSim() {
    const config = {
        populacao: parseInt(document.getElementById('pop-inicial').value),
        infectados: parseInt(document.getElementById('inf-iniciais').value),
        beta: parseFloat(document.getElementById('beta').value),
        alfa: parseFloat(document.getElementById('alfa').value),
        teta: parseFloat(document.getElementById('teta').value) // Captura o Teta
    };
    
    socket.emit('start', config);
}

function stopSim() {
    socket.emit('stop');
}
let resetIA = true;

function toggleIA(btn) {
    resetIA = !resetIA;

    socket.emit('toggle_ia', { resetar: resetIA });

    btn.innerText = resetIA ? "🧠 Reset IA: ON" : "🧠 Reset IA: OFF";
}
function treinarIA(btn) {
    const n = document.getElementById('input-episodios').value;

    btn.innerText = `⏳ Treinando (${n})...`;
    btn.disabled = true; // Desativa o botão clicado

    socket.emit('treinar', { episodios: n });
}

// Listener global (uma vez só)
socket.on('treino_finalizado', () => {
    const btn = document.getElementById('btn-treinar');
    if (btn) {
        btn.innerText = "⚡ Treinar IA";
        btn.disabled = false;
    }
});
document.querySelectorAll('input[type=range]').forEach(input => {
    input.addEventListener('input', e => {
        document.getElementById('val-' + e.target.id).innerText = e.target.value;
    });
});