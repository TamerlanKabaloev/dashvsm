const socket = io();

document.getElementById('createGameBtn').addEventListener('click', () => {
    socket.emit('create_game');
});

document.getElementById('joinGameBtn').addEventListener('click', () => {
    const gameId = document.getElementById('gameIdInput').value.trim();
    if (gameId) {
        window.location.href = `/game/${gameId}`;
    } else {
        alert('Введите ID игры');
    }
});

socket.on('game_created', (data) => {
    const gameLink = document.getElementById('gameLink');
    const url = `${window.location.origin}/game/${data.game_id}`;
    gameLink.innerHTML = `
        <p>Игра создана! Поделитесь ссылкой:</p>
        <a href="${url}" target="_blank">${url}</a>
    `;
    gameLink.classList.remove('hidden');
    
    // Автоматически переходим в игру
    setTimeout(() => {
        window.location.href = url;
    }, 2000);
});

socket.on('error', (data) => {
    alert(data.message);
});

