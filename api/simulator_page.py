"""
A tiny phone-style web UI that exercises /ussd exactly the way a USSD
gateway (e.g. Africa's Talking) would, without needing that gateway.
Useful for testing/demoing the flow from an actual phone browser.
"""

SIMULATOR_HTML = """<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>USSD Simulator</title>
<style>
  body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #1c1c1e;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }
  .phone {
    width: 300px;
    padding: 20px;
    border-radius: 24px;
    background: #2c2c2e;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  }
  .screen {
    background: #000;
    color: #4ade80;
    font-family: "SF Mono", Menlo, monospace;
    font-size: 15px;
    line-height: 1.5;
    padding: 16px;
    border-radius: 10px;
    min-height: 140px;
    white-space: pre-wrap;
  }
  input {
    width: 100%;
    box-sizing: border-box;
    margin-top: 12px;
    padding: 10px;
    border-radius: 8px;
    border: none;
    font-size: 16px;
  }
  button {
    width: 100%;
    margin-top: 10px;
    padding: 12px;
    border-radius: 8px;
    border: none;
    font-size: 16px;
    font-weight: 600;
    background: #f97316;
    color: #fff;
  }
  button:disabled { background: #6b7280; }
  #resetBtn { background: #3f3f46; }
</style>
</head>
<body>
  <div class="phone">
    <div class="screen" id="screen">Dial a USSD code below (e.g. *384*44773#) and press Call.</div>
    <input id="input" type="text" placeholder="*384*44773#" />
    <button id="actionBtn">Call</button>
    <button id="resetBtn" style="display:none">Restart</button>
  </div>
<script>
let sessionId = null;
let text = "";
let sessionActive = false;

const screen = document.getElementById('screen');
const input = document.getElementById('input');
const actionBtn = document.getElementById('actionBtn');
const resetBtn = document.getElementById('resetBtn');

function resetSession() {
  sessionId = 'sim-' + Date.now();
  text = "";
  sessionActive = false;
  input.value = "";
  input.disabled = false;
  input.placeholder = "*384*44773#";
  actionBtn.disabled = false;
  actionBtn.textContent = "Call";
  screen.textContent = "Dial a USSD code below (e.g. *384*44773#) and press Call.";
  resetBtn.style.display = "none";
}

async function sendUssd() {
  const formData = new URLSearchParams();
  formData.set('sessionId', sessionId);
  formData.set('phoneNumber', '+233200000000');
  formData.set('serviceCode', '*384*44773#');
  formData.set('text', text);

  const res = await fetch('/ussd', { method: 'POST', body: formData });
  const body = await res.text();
  const isEnd = body.startsWith('END');
  const message = body.replace(/^(CON|END)\\s?/, '');

  screen.textContent = message;

  if (isEnd) {
    sessionActive = false;
    input.disabled = true;
    actionBtn.disabled = true;
    resetBtn.style.display = "block";
  } else {
    sessionActive = true;
    input.value = "";
    input.placeholder = "Enter your answer";
    actionBtn.textContent = "Send";
  }
}

actionBtn.addEventListener('click', () => {
  if (!sessionActive) {
    sessionId = 'sim-' + Date.now();
    text = "";
    sendUssd();
  } else {
    const val = input.value.trim();
    if (!val) return;
    text = text ? text + '*' + val : val;
    sendUssd();
  }
});

resetBtn.addEventListener('click', resetSession);
</script>
</body>
</html>
"""
