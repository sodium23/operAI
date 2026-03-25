const tabs = document.querySelectorAll('.tab');
const screens = document.querySelectorAll('.screen');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatThread = document.getElementById('chatThread');

const scenarioPrompt = document.getElementById('scenarioPrompt');
const scenarioOptions = document.getElementById('scenarioOptions');
const scenarioAnswer = document.getElementById('scenarioAnswer');

const scenario = {
  prompt:
    'Your friend wants to meet someone from a dating app in a private apartment on the first meetup and says you are overreacting.',
  options: [
    {
      title: 'Say nothing and let it happen',
      answer: 'Weak move. Consequence: if things go wrong, you gave up your chance to prevent it. Option value: zero.'
    },
    {
      title: 'Push for a public meetup with check-ins',
      answer: 'Smart move. Consequence: maybe your friend gets annoyed, but risk drops hard. This is the strategic play.'
    },
    {
      title: 'Offer to track location and call at set times',
      answer: 'Decent backup plan. Consequence: better than silence, but still riskier than a public first meetup.'
    }
  ]
};

function switchScreen(screenId) {
  tabs.forEach((tab) => {
    tab.classList.toggle('active', tab.dataset.screen === screenId);
  });

  screens.forEach((screen) => {
    screen.classList.toggle('active', screen.id === screenId);
  });
}

function addBubble(text, role) {
  const article = document.createElement('article');
  article.className = `bubble ${role}`;
  const paragraph = document.createElement('p');
  paragraph.textContent = text;
  article.appendChild(paragraph);
  chatThread.appendChild(article);
  chatThread.scrollTop = chatThread.scrollHeight;
}

async function sendChat(message) {
  const response = await fetch('/safercircle/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });

  const data = await response.json();

  if (!data.ok) {
    return data.reply || 'No response. Fix your setup and try again.';
  }

  return data.reply;
}

function renderScenario() {
  scenarioPrompt.textContent = scenario.prompt;

  scenario.options.forEach((option) => {
    const button = document.createElement('button');
    button.className = 'option';
    button.type = 'button';
    button.textContent = option.title;

    button.addEventListener('click', () => {
      scenarioAnswer.classList.remove('hidden');
      scenarioAnswer.textContent = option.answer;
    });

    scenarioOptions.appendChild(button);
  });
}

tabs.forEach((tab) => {
  tab.addEventListener('click', () => switchScreen(tab.dataset.screen));
});

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();

  if (!message) {
    return;
  }

  addBubble(message, 'user');
  chatInput.value = '';

  addBubble('Thinking...', 'ai');
  const loadingBubble = chatThread.lastElementChild;

  try {
    const reply = await sendChat(message);
    loadingBubble.querySelector('p').textContent = reply;
  } catch (error) {
    loadingBubble.querySelector('p').textContent = 'Call failed. Check your connection and API key.';
  }
});

renderScenario();
