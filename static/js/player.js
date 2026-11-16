/* ==========================================================================
   SomTeca — Player de MP3 (JavaScript puro, sem bibliotecas)

   Como funciona:
   1. Cada página que tem músicas gera um <script type="application/json">
      com a lista de faixas (tag {% fila_json %} no template).
   2. Os botões de play têm a classe "js-tocar" e dois atributos:
        data-fila="id-do-json"  -> qual lista de músicas tocar
        data-indice="3"         -> a partir de qual posição
   3. Ao clicar, o player carrega essa lista como "fila" e toca usando a
      tag <audio> do HTML5.
   4. Cada vez que uma faixa começa, avisamos o servidor com fetch() (POST
      com token CSRF) para registrar a reprodução no banco de dados.
   ========================================================================== */

(function () {
    'use strict';

    // ---- Elementos da página -------------------------------------------------
    const audio = document.getElementById('player-audio');
    if (!audio) return; // página sem player (não deveria acontecer)

    const el = {
        capa: document.getElementById('player-capa'),
        capaVazia: document.getElementById('player-capa-vazia'),
        titulo: document.getElementById('player-titulo'),
        artista: document.getElementById('player-artista'),
        tocar: document.getElementById('player-tocar'),
        iconeTocar: document.getElementById('player-icone-tocar'),
        anterior: document.getElementById('player-anterior'),
        proxima: document.getElementById('player-proxima'),
        progresso: document.getElementById('player-progresso'),
        tempoAtual: document.getElementById('player-tempo-atual'),
        tempoTotal: document.getElementById('player-tempo-total'),
        volume: document.getElementById('player-volume'),
        mudo: document.getElementById('player-mudo'),
        iconeVolume: document.getElementById('player-icone-volume'),
    };

    // URL para registrar reproduções. Vem do atributo data-url-reproducao do <body>
    // no formato "/player/reproducao/0/"; trocamos o 0 pelo id da música.
    const urlReproducao = document.body.dataset.urlReproducao;

    // ---- Estado do player ----------------------------------------------------
    let fila = [];      // lista de faixas {id, titulo, artistas, capa, src, url}
    let indice = -1;    // posição da faixa atual na fila
    let arrastando = false; // true enquanto o usuário arrasta a barra de progresso

    // ---- Funções auxiliares --------------------------------------------------

    /** Lê um cookie pelo nome (usado para pegar o csrftoken do Django). */
    function lerCookie(nome) {
        const partes = document.cookie ? document.cookie.split(';') : [];
        for (const parte of partes) {
            const [chave, ...valor] = parte.trim().split('=');
            if (chave === nome) return decodeURIComponent(valor.join('='));
        }
        return null;
    }

    /** Converte segundos em "m:ss". */
    function formatarTempo(segundos) {
        if (!isFinite(segundos) || segundos < 0) return '0:00';
        const m = Math.floor(segundos / 60);
        const s = Math.floor(segundos % 60);
        return `${m}:${String(s).padStart(2, '0')}`;
    }

    /** Pinta a parte "já preenchida" de uma barra (efeito verde/branco). */
    function pintarBarra(barra) {
        const max = Number(barra.max) || 1;
        barra.style.setProperty('--preenchido', `${(Number(barra.value) / max) * 100}%`);
    }

    /** Avisa o servidor que a música começou a tocar. */
    function registrarReproducao(idMusica) {
        if (!urlReproducao) return;
        const url = urlReproducao.replace('/0/', `/${idMusica}/`);
        fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': lerCookie('csrftoken') || '' },
            credentials: 'same-origin',
        })
            .then((resposta) => resposta.json())
            .then((dados) => {
                // Atualiza o contador da página, se ele estiver visível
                document
                    .querySelectorAll(`[data-contador-musica="${idMusica}"]`)
                    .forEach((elemento) => { elemento.textContent = dados.total; });
            })
            .catch(() => { /* se falhar, a música continua tocando normalmente */ });
    }

    /** Marca na página a faixa que está tocando. */
    function destacarFaixaAtual() {
        const atual = fila[indice];
        document.querySelectorAll('.faixa').forEach((linha) => {
            linha.classList.toggle('tocando', !!atual && linha.dataset.musica === String(atual.id));
        });
    }

    /** Atualiza os botões (play/pause, anterior, próxima). */
    function atualizarBotoes() {
        const tocando = !audio.paused && !audio.ended;
        el.iconeTocar.className = tocando ? 'bi bi-pause-fill' : 'bi bi-play-fill';
        el.tocar.setAttribute('aria-label', tocando ? 'Pausar' : 'Tocar');
        el.tocar.disabled = fila.length === 0;
        el.anterior.disabled = indice <= 0 && audio.currentTime < 3;
        el.proxima.disabled = indice >= fila.length - 1;
    }

    /** Mostra capa, título e artista da faixa atual. */
    function mostrarInformacoes(faixa) {
        el.titulo.textContent = faixa.titulo;
        el.titulo.href = faixa.url;
        el.artista.textContent = faixa.artistas;
        if (faixa.capa) {
            el.capa.src = faixa.capa;
            el.capa.hidden = false;
            el.capaVazia.hidden = true;
        } else {
            el.capa.hidden = true;
            el.capaVazia.hidden = false;
        }
        document.title = `${faixa.titulo} · ${faixa.artistas} — SomTeca`;
    }

    // ---- Ações principais ------------------------------------------------------

    /** Carrega e toca a faixa na posição `novoIndice` da fila. */
    function tocarIndice(novoIndice) {
        if (novoIndice < 0 || novoIndice >= fila.length) return;
        indice = novoIndice;
        const faixa = fila[indice];

        if (!faixa.src) {
            // Música sem arquivo de áudio: pula para a próxima
            if (indice < fila.length - 1) tocarIndice(indice + 1);
            return;
        }

        audio.src = faixa.src;
        mostrarInformacoes(faixa);
        destacarFaixaAtual();
        audio.play()
            .then(() => registrarReproducao(faixa.id))
            .catch(() => atualizarBotoes());
    }

    /** Substitui a fila atual por uma nova lista e começa a tocar. */
    function tocarFila(novaFila, inicio) {
        fila = novaFila;
        tocarIndice(inicio || 0);
    }

    function alternarPlayPause() {
        if (fila.length === 0) return;
        if (audio.paused) audio.play(); else audio.pause();
    }

    function anterior() {
        // Igual aos apps de música: se já passou de 3s, volta ao início da faixa
        if (audio.currentTime > 3 || indice <= 0) {
            audio.currentTime = 0;
        } else {
            tocarIndice(indice - 1);
        }
    }

    function proxima() {
        if (indice < fila.length - 1) tocarIndice(indice + 1);
    }

    // ---- Eventos ---------------------------------------------------------------

    // Cliques em qualquer botão .js-tocar da página (delegação de eventos:
    // um único "ouvinte" no documento serve para todos os botões)
    document.addEventListener('click', (evento) => {
        const botao = evento.target.closest('.js-tocar');
        if (!botao) return;
        evento.preventDefault();

        const elementoJson = document.getElementById(botao.dataset.fila);
        if (!elementoJson) return;
        const novaFila = JSON.parse(elementoJson.textContent);
        const inicio = Number(botao.dataset.indice || 0);

        // Clicou na música que já está tocando? Então só pausa/continua
        const atual = fila[indice];
        if (atual && novaFila[inicio] && atual.id === novaFila[inicio].id && audio.src) {
            fila = novaFila;
            indice = inicio;
            alternarPlayPause();
            return;
        }
        tocarFila(novaFila, inicio);
    });

    el.tocar.addEventListener('click', alternarPlayPause);
    el.anterior.addEventListener('click', anterior);
    el.proxima.addEventListener('click', proxima);

    // Eventos da própria tag <audio>
    audio.addEventListener('play', atualizarBotoes);
    audio.addEventListener('pause', atualizarBotoes);
    audio.addEventListener('ended', () => {
        if (indice < fila.length - 1) proxima(); else atualizarBotoes();
    });
    audio.addEventListener('loadedmetadata', () => {
        el.progresso.max = Math.floor(audio.duration) || 0;
        el.tempoTotal.textContent = formatarTempo(audio.duration);
    });
    audio.addEventListener('timeupdate', () => {
        if (arrastando) return;
        el.progresso.value = Math.floor(audio.currentTime);
        el.tempoAtual.textContent = formatarTempo(audio.currentTime);
        pintarBarra(el.progresso);
        atualizarBotoes();
    });

    // Barra de progresso: arrastar muda a posição da música
    el.progresso.addEventListener('input', () => {
        arrastando = true;
        el.tempoAtual.textContent = formatarTempo(Number(el.progresso.value));
        pintarBarra(el.progresso);
    });
    el.progresso.addEventListener('change', () => {
        audio.currentTime = Number(el.progresso.value);
        arrastando = false;
    });

    // Volume (o valor escolhido fica salvo no navegador)
    function aplicarVolume(valor) {
        audio.volume = valor / 100;
        audio.muted = valor === 0;
        el.volume.value = valor;
        pintarBarra(el.volume);
        el.iconeVolume.className = valor === 0 ? 'bi bi-volume-mute'
            : valor < 50 ? 'bi bi-volume-down' : 'bi bi-volume-up';
        try { localStorage.setItem('somteca-volume', String(valor)); } catch (e) { /* sem armazenamento */ }
    }

    let volumeAntesDoMudo = 80;
    el.volume.addEventListener('input', () => aplicarVolume(Number(el.volume.value)));
    el.mudo.addEventListener('click', () => {
        if (Number(el.volume.value) > 0) {
            volumeAntesDoMudo = Number(el.volume.value);
            aplicarVolume(0);
        } else {
            aplicarVolume(volumeAntesDoMudo || 80);
        }
    });

    // Atalho: barra de espaço = play/pause (quando não está digitando num campo)
    document.addEventListener('keydown', (evento) => {
        const digitando = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName);
        if (evento.code === 'Space' && !digitando && fila.length) {
            evento.preventDefault();
            alternarPlayPause();
        }
    });

    // ---- Inicialização -----------------------------------------------------------
    let volumeSalvo = 80;
    try {
        const valor = localStorage.getItem('somteca-volume');
        if (valor !== null) volumeSalvo = Number(valor);
    } catch (e) { /* sem armazenamento */ }
    aplicarVolume(volumeSalvo);
    pintarBarra(el.progresso);
    atualizarBotoes();
})();
