// Games JavaScript - CodeDonki
let gamesPlayed = 0;

// Load user profile
async function loadUserProfile() {
    try {
        const token = localStorage.getItem('token');
        if (!token) return;
        const response = await fetch('/api/profile', { headers: { Authorization: `Bearer ${token}` } });
        if (response.ok) {
            const profile = await response.json();
            document.getElementById('userPoints').textContent = profile.xp || 0;
        }
    } catch (error) { console.error('Error loading profile:', error); }
}

function updateGamesPlayed() {
    gamesPlayed++;
    document.getElementById('gamesPlayed').textContent = gamesPlayed;
}

async function awardXP(amount) {
    try {
        const token = localStorage.getItem('token');
        if (!token) return;
        const response = await fetch('/api/profile', { headers: { Authorization: `Bearer ${token}` } });
        if (response.ok) {
            const profile = await response.json();
            const newXP = (profile.xp || 0) + amount;
            document.getElementById('userPoints').textContent = newXP;
        }
    } catch (error) { console.error('Error awarding XP:', error); }
}

// Game configurations
const games = {
    memory: { title: "🧠 Code Memory", description: "Match code snippets with their outputs!", instructions: "Click on cards to reveal code snippets and their outputs. Match them to win!" },
    typing: { title: "⌨️ Code Typing Race", description: "Type code as fast as you can!", instructions: "Type the code shown as quickly and accurately as possible. Beat the timer!" },
    puzzle: { title: "🧩 Code Puzzle", description: "Solve coding puzzles!", instructions: "Write the correct code to solve each puzzle. Think logically!" }
};

// Memory game data
const memoryCards = [
    { id: 1, type: 'code', content: 'print(2 + 2)' }, { id: 1, type: 'output', content: '4' },
    { id: 2, type: 'code', content: 'len("Hello")' }, { id: 2, type: 'output', content: '5' },
    { id: 3, type: 'code', content: '"Hi" * 3' }, { id: 3, type: 'output', content: 'HiHiHi' },
    { id: 4, type: 'code', content: 'type([1, 2])' }, { id: 4, type: 'output', content: '<class \'list\'>' },
    { id: 5, type: 'code', content: '10 // 3' }, { id: 5, type: 'output', content: '3' },
    { id: 6, type: 'code', content: '10 % 3' }, { id: 6, type: 'output', content: '1' },
    { id: 7, type: 'code', content: 'bool([])' }, { id: 7, type: 'output', content: 'False' },
    { id: 8, type: 'code', content: 'max([1,5,3])' }, { id: 8, type: 'output', content: '5' }
];

// Typing game code snippets
const typingSnippets = [
    `for i in range(5):\n    print(i)`,
    `def greet(name):\n    return f"Hello, {name}!"`,
    `numbers = [1, 2, 3, 4, 5]\ntotal = sum(numbers)\nprint(total)`,
    `my_dict = {"name": "Alice", "age": 25}\nprint(my_dict["name"])`,
    `if x > 10:\n    print("Greater")\nelse:\n    print("Smaller")`
];

// Puzzle game questions
const puzzles = [
    { question: "Write a function that returns the sum of two numbers.", hint: "def add(a, b):", solution: (code) => code.includes('return') && code.includes('+') },
    { question: "Write a function that checks if a number is even.", hint: "def is_even(num):", solution: (code) => code.includes('return') && code.includes('%') },
    { question: "Write a function that returns the length of a list.", hint: "def list_length(lst):", solution: (code) => code.includes('return') && code.includes('len') },
    { question: "Write a function that reverses a string.", hint: "def reverse_string(s):", solution: (code) => code.includes('return') && (code.includes('[::-1]') || code.includes('reversed')) },
    { question: "Write a function that finds the maximum of three numbers.", hint: "def max_of_three(a, b, c):", solution: (code) => code.includes('return') && code.includes('max') },
    { question: "Write a function that counts vowels in a string.", hint: "def count_vowels(s):", solution: (code) => code.includes('return') && (code.includes('for') || code.includes('in')) },
    { question: "Write a function that checks if a string is a palindrome.", hint: "def is_palindrome(s):", solution: (code) => code.includes('return') && code.includes('==') },
    { question: "Write a function that returns the factorial of a number.", hint: "def factorial(n):", solution: (code) => code.includes('return') && (code.includes('*') || code.includes('factorial')) }
];

function startGame(gameType) {
    const game = games[gameType];
    if (!game) return;
    document.getElementById('gameTitle').textContent = game.title;
    document.getElementById('gameContent').innerHTML = `
        <div class="game-instructions"><h3>${game.description}</h3><p>${game.instructions}</p></div>
        <div class="game-area" id="gameArea">${getGameHTML(gameType)}</div>
    `;
    document.getElementById('gameModal').style.display = 'block';
    initializeGame(gameType);
}

function getGameHTML(gameType) {
    switch(gameType) {
        case 'memory':
            return `<div class="memory-game"><div class="game-info"><div>Moves: <span id="memoryMoves">0</span></div><div>Matches: <span id="memoryMatches">0</span> / 8</div><button class="btn btn-secondary" onclick="resetMemoryGame()">Reset</button></div><div class="memory-grid" id="memoryGrid"></div><div id="memoryMessage"></div></div>`;
        case 'typing':
            return `<div class="typing-game"><div class="game-info"><div>Time: <span id="typingTime">60</span>s</div><div>WPM: <span id="typingWPM">0</span></div><div>Accuracy: <span id="typingAccuracy">100</span>%</div></div><div class="code-display" id="codeDisplay"></div><div class="typing-input"><textarea id="typingInput" placeholder="Start typing the code above..." disabled></textarea></div><button class="btn btn-primary" id="startTypingBtn" onclick="startTypingGame()">Start Typing!</button><div id="typingMessage"></div></div>`;
        case 'puzzle':
            return `<div class="puzzle-game"><div class="puzzle-info game-info"><div>Puzzle: <span id="puzzleNumber">1</span> / 8</div><div>Score: <span id="puzzleScore">0</span> / 8</div></div><div class="puzzle-question" id="puzzleQuestion"></div><div class="puzzle-editor"><textarea id="puzzleCode" placeholder="Write your solution here..."></textarea><button class="btn btn-primary" onclick="checkPuzzleSolution()">Check Solution</button><button class="btn btn-secondary" onclick="nextPuzzle()" style="margin-left: 10px;" id="nextPuzzleBtn" disabled>Next Puzzle</button></div><div id="puzzleMessage"></div></div>`;
        default: return '<p>Game not found!</p>';
    }
}

function initializeGame(gameType) {
    switch(gameType) {
        case 'memory': initMemoryGame(); break;
        case 'typing': initTypingGame(); break;
        case 'puzzle': initPuzzleGame(); break;
    }
}

function closeGame() { document.getElementById('gameModal').style.display = 'none'; }
window.onclick = function(event) { const modal = document.getElementById('gameModal'); if (event.target === modal) closeGame(); }

// ============ MEMORY GAME ============
let memoryGameState = { cards: [], flipped: [], matched: [], moves: 0 };

function initMemoryGame() {
    memoryGameState.cards = [...memoryCards].sort(() => Math.random() - 0.5);
    memoryGameState.flipped = [];
    memoryGameState.matched = [];
    memoryGameState.moves = 0;
    renderMemoryCards();
}

function renderMemoryCards() {
    const grid = document.getElementById('memoryGrid');
    grid.innerHTML = '';
    memoryGameState.cards.forEach((card, index) => {
        const cardElement = document.createElement('div');
        cardElement.className = 'memory-card';
        cardElement.dataset.index = index;
        cardElement.textContent = '?';
        cardElement.onclick = () => flipCard(index);
        grid.appendChild(cardElement);
    });
    updateMemoryStats();
}

function flipCard(index) {
    if (memoryGameState.flipped.length >= 2 || memoryGameState.flipped.includes(index) || memoryGameState.matched.includes(index)) return;
    const cardElement = document.querySelectorAll('.memory-card')[index];
    const card = memoryGameState.cards[index];
    cardElement.textContent = card.content;
    cardElement.classList.add('flipped');
    memoryGameState.flipped.push(index);
    if (memoryGameState.flipped.length === 2) {
        memoryGameState.moves++;
        updateMemoryStats();
        setTimeout(checkMatch, 1000);
    }
}

function checkMatch() {
    const [index1, index2] = memoryGameState.flipped;
    const card1 = memoryGameState.cards[index1];
    const card2 = memoryGameState.cards[index2];
    const cardElements = document.querySelectorAll('.memory-card');
    if (card1.id === card2.id) {
        cardElements[index1].classList.add('matched');
        cardElements[index2].classList.add('matched');
        memoryGameState.matched.push(index1, index2);
        if (memoryGameState.matched.length === memoryGameState.cards.length) {
            setTimeout(() => showMemoryCompletion(), 500);
        }
    } else {
        cardElements[index1].textContent = '?';
        cardElements[index2].textContent = '?';
        cardElements[index1].classList.remove('flipped');
        cardElements[index2].classList.remove('flipped');
    }
    memoryGameState.flipped = [];
}

function updateMemoryStats() {
    document.getElementById('memoryMoves').textContent = memoryGameState.moves;
    document.getElementById('memoryMatches').textContent = memoryGameState.matched.length / 2;
}

function showMemoryCompletion() {
    const messageDiv = document.getElementById('memoryMessage');
    messageDiv.className = 'game-message success';
    messageDiv.innerHTML = `<h3>🎉 Congratulations!</h3><p>You completed the game in ${memoryGameState.moves} moves!</p><p><strong>+15 XP</strong> earned!</p>`;
    updateGamesPlayed();
    awardXP(15);
}

function resetMemoryGame() {
    initMemoryGame();
    document.getElementById('memoryMessage').innerHTML = '';
}

// ============ TYPING GAME ============
let typingGameState = { snippet: '', startTime: null, timer: null, timeLeft: 60 };

function initTypingGame() {
    const snippet = typingSnippets[Math.floor(Math.random() * typingSnippets.length)];
    typingGameState.snippet = snippet;
    typingGameState.startTime = null;
    typingGameState.timeLeft = 60;
    document.getElementById('codeDisplay').textContent = snippet;
    document.getElementById('typingInput').value = '';
    document.getElementById('typingInput').disabled = true;
    document.getElementById('typingMessage').innerHTML = '';
}

function startTypingGame() {
    document.getElementById('typingInput').disabled = false;
    document.getElementById('typingInput').focus();
    document.getElementById('startTypingBtn').disabled = true;
    typingGameState.startTime = Date.now();
    startTimer();
    const input = document.getElementById('typingInput');
    input.addEventListener('input', updateTypingStats);
}

function startTimer() {
    typingGameState.timer = setInterval(() => {
        typingGameState.timeLeft--;
        document.getElementById('typingTime').textContent = typingGameState.timeLeft;
        if (typingGameState.timeLeft <= 0) endTypingGame();
    }, 1000);
}

function updateTypingStats() {
    const input = document.getElementById('typingInput').value;
    const target = typingGameState.snippet;
    let correct = 0;
    for (let i = 0; i < Math.min(input.length, target.length); i++) {
        if (input[i] === target[i]) correct++;
    }
    const accuracy = input.length > 0 ? Math.round((correct / input.length) * 100) : 100;
    document.getElementById('typingAccuracy').textContent = accuracy;
    const timeElapsed = (Date.now() - typingGameState.startTime) / 1000 / 60;
    const wordsTyped = input.length / 5;
    const wpm = timeElapsed > 0 ? Math.round(wordsTyped / timeElapsed) : 0;
    document.getElementById('typingWPM').textContent = wpm;
    if (input === target) endTypingGame(true);
}

function endTypingGame(completed = false) {
    clearInterval(typingGameState.timer);
    document.getElementById('typingInput').disabled = true;
    document.getElementById('startTypingBtn').disabled = false;
    const messageDiv = document.getElementById('typingMessage');
    const wpm = parseInt(document.getElementById('typingWPM').textContent);
    const accuracy = parseInt(document.getElementById('typingAccuracy').textContent);
    if (completed) {
        messageDiv.className = 'game-message success';
        messageDiv.innerHTML = `<h3>🎉 Great Job!</h3><p>WPM: ${wpm} | Accuracy: ${accuracy}%</p><p><strong>+25 XP</strong> earned!</p>`;
        updateGamesPlayed();
        awardXP(25);
    } else {
        messageDiv.className = 'game-message error';
        messageDiv.innerHTML = `<h3>⏰ Time's Up!</h3><p>Try again to improve your speed!</p>`;
    }
}

// ============ PUZZLE GAME ============
let puzzleGameState = { currentPuzzle: 0, score: 0 };

function initPuzzleGame() {
    puzzleGameState.currentPuzzle = 0;
    puzzleGameState.score = 0;
    loadPuzzle();
}

function loadPuzzle() {
    const puzzle = puzzles[puzzleGameState.currentPuzzle];
    const questionDiv = document.getElementById('puzzleQuestion');
    questionDiv.innerHTML = `<h4>Puzzle ${puzzleGameState.currentPuzzle + 1}</h4><p>${puzzle.question}</p><p><em>Hint: ${puzzle.hint}</em></p>`;
    document.getElementById('puzzleNumber').textContent = puzzleGameState.currentPuzzle + 1;
    document.getElementById('puzzleScore').textContent = puzzleGameState.score;
    document.getElementById('puzzleCode').value = '';
    document.getElementById('puzzleMessage').innerHTML = '';
    document.getElementById('nextPuzzleBtn').disabled = true;
}

function checkPuzzleSolution() {
    const code = document.getElementById('puzzleCode').value;
    const puzzle = puzzles[puzzleGameState.currentPuzzle];
    const messageDiv = document.getElementById('puzzleMessage');
    if (!code.trim()) {
        messageDiv.className = 'game-message error';
        messageDiv.textContent = 'Please write some code first!';
        return;
    }
    if (puzzle.solution(code)) {
        puzzleGameState.score++;
        messageDiv.className = 'game-message success';
        messageDiv.textContent = '✅ Correct! Great job!';
        document.getElementById('puzzleScore').textContent = puzzleGameState.score;
        document.getElementById('nextPuzzleBtn').disabled = false;
        if (puzzleGameState.currentPuzzle === puzzles.length - 1) {
            setTimeout(() => showPuzzleCompletion(), 1000);
        }
    } else {
        messageDiv.className = 'game-message error';
        messageDiv.textContent = '❌ Not quite right. Try again!';
    }
}

function nextPuzzle() {
    puzzleGameState.currentPuzzle++;
    if (puzzleGameState.currentPuzzle < puzzles.length) {
        loadPuzzle();
    } else {
        showPuzzleCompletion();
    }
}

function showPuzzleCompletion() {
    const messageDiv = document.getElementById('puzzleMessage');
    messageDiv.className = 'game-message success';
    messageDiv.innerHTML = `<h3>🎉 All Puzzles Completed!</h3><p>You solved ${puzzleGameState.score} out of ${puzzles.length} puzzles!</p><p><strong>+30 XP</strong> earned!</p>`;
    updateGamesPlayed();
    awardXP(30);
}

// Load user profile on page load
document.addEventListener('DOMContentLoaded', () => loadUserProfile());

