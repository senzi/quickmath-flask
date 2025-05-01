/**
 * QuickMath 答题页前端逻辑：计时器、localStorage 缓存与恢复、simple-keyboard 数字键盘
 */

// 计时器
let timer = null;
let startTime = null;
function startTimer() {
    startTime = Date.now();
    timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const min = String(Math.floor(elapsed / 60)).padStart(2, '0');
        const sec = String(elapsed % 60).padStart(2, '0');
        document.getElementById('timer').textContent = `${min}:${sec}`;
        localStorage.setItem('quickmath-timer', elapsed);
    }, 1000);
}
function restoreTimer() {
    const elapsed = parseInt(localStorage.getItem('quickmath-timer') || '0');
    const min = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const sec = String(elapsed % 60).padStart(2, '0');
    document.getElementById('timer').textContent = `${min}:${sec}`;
}

window.addEventListener('DOMContentLoaded', () => {
    // 恢复输入
    document.querySelectorAll('.answer-input').forEach(input => {
        const key = 'quickmath-' + input.name;
        if (localStorage.getItem(key)) {
            input.value = localStorage.getItem(key);
        }
        input.addEventListener('change', () => {
            localStorage.setItem(key, input.value);
        });
        input.addEventListener('blur', () => {
            localStorage.setItem(key, input.value);
        });
    });
    // 恢复计时器
    if (localStorage.getItem('quickmath-timer')) {
        restoreTimer();
    }
    // 启动计时器
    if (!localStorage.getItem('quickmath-timer')) {
        startTimer();
    } else {
        // 继续计时
        const elapsed = parseInt(localStorage.getItem('quickmath-timer') || '0');
        startTime = Date.now() - elapsed * 1000;
        timer = setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const min = String(Math.floor(elapsed / 60)).padStart(2, '0');
            const sec = String(elapsed % 60).padStart(2, '0');
            document.getElementById('timer').textContent = `${min}:${sec}`;
            localStorage.setItem('quickmath-timer', elapsed);
        }, 1000);
    }
    // 提交时清理缓存
    const form = document.getElementById('quiz-form');
    if (form) {
        form.addEventListener('submit', () => {
            document.querySelectorAll('.answer-input').forEach(input => {
                localStorage.removeItem('quickmath-' + input.name);
            });
            localStorage.removeItem('quickmath-timer');
        });
    }

    // ====== 自定义数字键盘实现 ======
    const keyboard = document.getElementById('custom-keyboard');
    let currentInput = null;

    // 生成键盘HTML
    function renderKeyboard() {
        keyboard.innerHTML = `
            <div class="keyboard-row">
                <button type="button" class="keyboard-btn">7</button>
                <button type="button" class="keyboard-btn">8</button>
                <button type="button" class="keyboard-btn">9</button>
            </div>
            <div class="keyboard-row">
                <button type="button" class="keyboard-btn">4</button>
                <button type="button" class="keyboard-btn">5</button>
                <button type="button" class="keyboard-btn">6</button>
            </div>
            <div class="keyboard-row">
                <button type="button" class="keyboard-btn">1</button>
                <button type="button" class="keyboard-btn">2</button>
                <button type="button" class="keyboard-btn">3</button>
            </div>
            <div class="keyboard-row">
                <button type="button" class="keyboard-btn wide">0</button>
                <button type="button" class="keyboard-btn" data-action="minus">-</button>
                <button type="button" class="keyboard-btn" data-action="bksp">⌫</button>
            </div>
            <div class="keyboard-row">
                <button type="button" class="keyboard-btn wide" data-action="clear">清空</button>
            </div>
        `;
    }
    renderKeyboard();

    // 定位键盘到第一个.quiz-card右侧，垂直居中
    function positionKeyboard() {
        const card = document.querySelector('.quiz-card');
        if (card && keyboard.style.display !== 'none') {
            const cardRect = card.getBoundingClientRect();
            const left = cardRect.right + 24 + window.pageXOffset;
            keyboard.style.left = left + 'px';
        }
    }

    // 显示键盘
    function showKeyboard(input) {
        currentInput = input;
        keyboard.style.display = 'block';
        positionKeyboard();
    }
    // 隐藏键盘
    function hideKeyboard() {
        keyboard.style.display = 'none';
        currentInput = null;
    }

    // 输入框聚焦时显示键盘
    document.querySelectorAll('.answer-input').forEach(input => {
        input.addEventListener('focus', () => {
            showKeyboard(input);
            setTimeout(() => {
                input.scrollIntoView({block: 'center', behavior: 'smooth'});
            }, 100);
        });
    });

    // 点击页面其他区域时隐藏键盘
    document.addEventListener('mousedown', (e) => {
        if (
            !e.target.classList.contains('answer-input') &&
            !keyboard.contains(e.target)
        ) {
            hideKeyboard();
        }
    });

    // 键盘按钮点击事件
    keyboard.addEventListener('mousedown', (e) => {
        if (!currentInput) return;
        const btn = e.target.closest('.keyboard-btn');
        if (!btn) return;
        const action = btn.getAttribute('data-action');
        if (action === 'bksp') {
            // 退格
            currentInput.value = currentInput.value.slice(0, -1);
        } else if (action === 'clear') {
            // 清空
            currentInput.value = '';
        } else if (action === 'minus') {
            // 负号
            if (!currentInput.value.includes('-')) {
                currentInput.value = '-' + currentInput.value;
            } else if (currentInput.value.startsWith('-')) {
                currentInput.value = currentInput.value.slice(1);
            }
        } else {
            // 输入数字
            currentInput.value += btn.textContent.trim();
        }
        // 触发input事件和本地存储
        currentInput.dispatchEvent(new Event('input', {bubbles: true}));
        currentInput.dispatchEvent(new Event('change', {bubbles: true}));
        currentInput.focus();
    });

    // 窗口变化时重新定位
    window.addEventListener('resize', positionKeyboard);
    window.addEventListener('scroll', positionKeyboard);

    // 定时刷新，防止错位
    setInterval(positionKeyboard, 500);
});
