const socket = io();
const gameId = document.getElementById('gameId').textContent;
let game = new Chess();
let playerColor = null;
let selectedSquare = null;
let boardElement = null;

// Инициализация
socket.emit('join_game', { game_id: gameId });

socket.on('game_joined', (data) => {
    playerColor = data.color;
    updatePlayerStatus();
});

socket.on('game_info', (data) => {
    if (data.fen) {
        game.load(data.fen);
    }
    if (data.color) {
        playerColor = data.color;
    }
    if (data.status) {
        updateGameStatus(data.status);
    }
    renderBoard();
    updatePlayerStatus();
});

socket.on('move_made', (data) => {
    game.load(data.fen);
    renderBoard();
    updateMovesList();
    checkGameStatus();
});

socket.on('player_joined', (data) => {
    updateGameStatus('active');
    updatePlayerStatus();
});

socket.on('player_disconnected', () => {
    updateGameStatus('disconnected');
});

function renderBoard() {
    boardElement = document.getElementById('board');
    boardElement.innerHTML = '';
    
    const isFlipped = playerColor === 'black';
    const ranks = isFlipped ? [1, 2, 3, 4, 5, 6, 7, 8].reverse() : [1, 2, 3, 4, 5, 6, 7, 8];
    const files = isFlipped ? ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a'].reverse() : ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    
    ranks.forEach(rank => {
        files.forEach(file => {
            const square = `${file}${rank}`;
            const squareElement = document.createElement('div');
            squareElement.className = 'square';
            squareElement.dataset.square = square;
            squareElement.dataset.file = file;
            squareElement.dataset.rank = rank;
            
            const isLight = (rank + file.charCodeAt(0) - 96) % 2 === 0;
            squareElement.classList.add(isLight ? 'light' : 'dark');
            
            if (selectedSquare === square) {
                squareElement.classList.add('selected');
            }
            
            const piece = game.get(square);
            if (piece) {
                const pieceElement = document.createElement('div');
                pieceElement.className = `piece piece-${piece.color}-${piece.type}`;
                squareElement.appendChild(pieceElement);
            }
            
            squareElement.addEventListener('click', () => handleSquareClick(square));
            boardElement.appendChild(squareElement);
        });
    });
    
    highlightLastMove();
    highlightCheck();
}

function handleSquareClick(square) {
    if (!playerColor) return;
    if (game.turn() !== playerColor[0]) return;
    if (game.isGameOver()) return;
    
    const piece = game.get(square);
    
    if (selectedSquare) {
        if (selectedSquare === square) {
            selectedSquare = null;
            renderBoard();
            return;
        }
        
        const move = game.move({
            from: selectedSquare,
            to: square,
            promotion: 'q'
        });
        
        if (move) {
            socket.emit('make_move', {
                game_id: gameId,
                move: move.san,
                fen: game.fen()
            });
            selectedSquare = null;
            renderBoard();
            updateMovesList();
            checkGameStatus();
            updateGameStatus('active');
            updatePlayerStatus();
        } else {
            selectedSquare = piece && piece.color === playerColor[0] ? square : null;
            renderBoard();
            if (selectedSquare) {
                highlightPossibleMoves(selectedSquare);
            }
        }
    } else {
        if (piece && piece.color === playerColor[0]) {
            selectedSquare = square;
            renderBoard();
            highlightPossibleMoves(square);
        }
    }
}

function highlightPossibleMoves(square) {
    const moves = game.moves({ square: square, verbose: true });
    moves.forEach(move => {
        const squareElement = document.querySelector(`[data-square="${move.to}"]`);
        if (squareElement) {
            squareElement.classList.add('possible-move');
        }
    });
}

function highlightLastMove() {
    const history = game.history({ verbose: true });
    if (history.length > 0) {
        const lastMove = history[history.length - 1];
        const fromSquare = document.querySelector(`[data-square="${lastMove.from}"]`);
        const toSquare = document.querySelector(`[data-square="${lastMove.to}"]`);
        if (fromSquare) fromSquare.classList.add('last-move');
        if (toSquare) toSquare.classList.add('last-move');
    }
}

function highlightCheck() {
    if (game.inCheck()) {
        const board = game.board();
        for (let rank = 0; rank < 8; rank++) {
            for (let file = 0; file < 8; file++) {
                const square = board[rank][file];
                if (square && square.type === 'k' && square.color === game.turn()) {
                    const fileChar = String.fromCharCode(97 + file);
                    const rankNum = 8 - rank;
                    const squareElement = document.querySelector(`[data-square="${fileChar}${rankNum}"]`);
                    if (squareElement) {
                        squareElement.classList.add('check');
                    }
                }
            }
        }
    }
}

function updateMovesList() {
    const movesList = document.getElementById('movesList');
    movesList.innerHTML = '';
    const history = game.history();
    
    for (let i = 0; i < history.length; i += 2) {
        const moveDiv = document.createElement('div');
        moveDiv.className = 'move-item';
        const moveNumber = Math.floor(i / 2) + 1;
        const whiteMove = history[i];
        const blackMove = history[i + 1] || '';
        moveDiv.textContent = `${moveNumber}. ${whiteMove} ${blackMove}`;
        movesList.appendChild(moveDiv);
    }
    
    movesList.scrollTop = movesList.scrollHeight;
}

function checkGameStatus() {
    if (game.isCheckmate()) {
        updateGameStatus('checkmate');
    } else if (game.isDraw()) {
        updateGameStatus('draw');
    } else if (game.isStalemate()) {
        updateGameStatus('stalemate');
    }
}

function updateGameStatus(status) {
    const statusElement = document.getElementById('gameStatus');
    switch(status) {
        case 'waiting':
            statusElement.textContent = 'Ожидание соперника...';
            break;
        case 'active':
            statusElement.textContent = game.turn() === 'w' ? 'Ход белых' : 'Ход черных';
            break;
        case 'checkmate':
            statusElement.textContent = `Мат! Победили ${game.turn() === 'w' ? 'черные' : 'белые'}`;
            break;
        case 'draw':
            statusElement.textContent = 'Ничья';
            break;
        case 'stalemate':
            statusElement.textContent = 'Пат';
            break;
        case 'disconnected':
            statusElement.textContent = 'Соперник отключился';
            break;
    }
}

function updatePlayerStatus() {
    if (!playerColor) return;
    
    if (playerColor === 'white') {
        document.getElementById('whiteStatus').textContent = 'Вы';
        if (game.turn() === 'b') {
            document.getElementById('blackStatus').textContent = 'Ход';
        } else if (game.turn() === 'w') {
            document.getElementById('blackStatus').textContent = 'Ожидание';
        }
    } else {
        document.getElementById('blackStatus').textContent = 'Вы';
        if (game.turn() === 'w') {
            document.getElementById('whiteStatus').textContent = 'Ход';
        } else if (game.turn() === 'b') {
            document.getElementById('whiteStatus').textContent = 'Ожидание';
        }
    }
}

document.getElementById('copyLinkBtn').addEventListener('click', () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
        alert('Ссылка скопирована!');
    });
});

document.getElementById('resignBtn').addEventListener('click', () => {
    if (confirm('Вы уверены, что хотите сдаться?')) {
        updateGameStatus('resigned');
    }
});

document.getElementById('newGameBtn').addEventListener('click', () => {
    window.location.href = '/';
});

// Обновляем статус хода при изменении игры
const originalMove = game.move;
game.move = function(...args) {
    const result = originalMove.apply(this, args);
    if (result) {
        updateGameStatus('active');
        updatePlayerStatus();
    }
    return result;
};

