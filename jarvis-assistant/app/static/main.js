const canvas = document.getElementById("orb");
const ctx = canvas.getContext("2d");
const statusEl = document.getElementById("status");
const agentStateEl = document.getElementById("agent-state");
const logEl = document.getElementById("log");
const inputEl = document.getElementById("command");
const sendBtn = document.getElementById("send");
const micBtn = document.getElementById("mic");

function resize() {
  canvas.width = canvas.clientWidth;
  canvas.height = canvas.clientHeight;
}
window.addEventListener("resize", resize);
resize();

const particles = [];
const COUNT = 300;
const R = 140;
for (let i = 0; i < COUNT; i++) {
  const theta = Math.acos(2 * Math.random() - 1);
  const phi = 2 * Math.PI * Math.random();
  particles.push({ theta, phi, speed: 0.001 + Math.random() * 0.002 });
}

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;

  for (const p of particles) {
    p.phi += p.speed;
    const x = R * Math.sin(p.theta) * Math.cos(p.phi);
    const y = R * Math.sin(p.theta) * Math.sin(p.phi);
    const z = R * Math.cos(p.theta);
    const depth = (z + R) / (2 * R);
    const scale = 0.6 + depth * 0.6;
    const alpha = 0.35 + depth * 0.55;
    const screenX = cx + x;
    const screenY = cy + y * 0.6;

    const grad = ctx.createRadialGradient(screenX, screenY, 0, screenX, screenY, 6 * scale);
    grad.addColorStop(0, `rgba(39,215,255,${alpha})`);
    grad.addColorStop(1, "rgba(39,215,255,0)");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(screenX, screenY, 6 * scale, 0, Math.PI * 2);
    ctx.fill();
  }
  requestAnimationFrame(render);
}
requestAnimationFrame(render);

let socket = null;
let socketOpen = false;

function initSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const url = `${protocol}//${window.location.host}/ws`;
  socket = new WebSocket(url);

  socket.onopen = () => {
    socketOpen = true;
    setServerStatus(true);
    setAgentState("ready");
  };

  socket.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      if (message.type === "response") {
        const data = message.data || {};
        const reply = data.reply || data.response || "No reply";
        appendLog("jarvis", reply);
        speak(reply);
        setAgentState("idle");
      } else if (message.type === "status") {
        setServerStatus(true);
        setAgentState(message.data.plan_running ? "acting" : "ready");
      } else if (message.type === "screenshot") {
        appendLog("jarvis", "Screen analysis complete.");
      } else if (message.type === "error") {
        appendLog("jarvis", `Error: ${message.message}`);
        setAgentState("error");
      }
    } catch (err) {
      console.error(err);
    }
  };

  socket.onclose = () => {
    socketOpen = false;
    setServerStatus(false);
    setAgentState("offline");
    setTimeout(initSocket, 3000);
  };

  socket.onerror = () => {
    socketOpen = false;
    setServerStatus(false);
    setAgentState("error");
  };
}

function setServerStatus(online) {
  statusEl.textContent = online ? "online" : "offline";
  statusEl.style.color = online ? "#14ffb9" : "#ff7b7b";
}

function setAgentState(state) {
  agentStateEl.textContent = state;
}

initSocket();

async function ping() {
  try {
    const res = await fetch("/status");
    setServerStatus(res.ok);
  } catch {
    setServerStatus(false);
  }
}
ping();

function appendLog(role, text) {
  const div = document.createElement("div");
  div.className = "log-entry";
  div.innerHTML = `<span class="${role === "user" ? "user" : "jarvis"}">${role}:</span> ${text}`;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

async function send(text) {
  if (!text.trim()) return;
  appendLog("user", text);
  inputEl.value = "";
  setAgentState("thinking");

  const payload = { type: "command", data: { text } };
  if (socketOpen && socket) {
    socket.send(JSON.stringify(payload));
    return;
  }

  try {
    const res = await fetch("/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    const reply = data.reply ?? data.response ?? "No reply";
    appendLog("jarvis", reply);
    speak(reply);
    setAgentState("idle");
  } catch (err) {
    appendLog("jarvis", "Error reaching backend.");
    speak("I cannot reach the server.");
    setAgentState("error");
  }
}

sendBtn.onclick = () => send(inputEl.value);
inputEl.onkeydown = (e) => { if (e.key === "Enter") send(inputEl.value); };

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const synth = window.speechSynthesis;
let recognizer = null;
let listening = false;

function speak(text) {
  if (!synth) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 1.02;
  utter.pitch = 1.0;
  synth.cancel();
  synth.speak(utter);
}

if (SpeechRecognition) {
  recognizer = new SpeechRecognition();
  recognizer.lang = "en-US";
  recognizer.interimResults = false;
  recognizer.continuous = false;

  recognizer.onstart = () => {
    listening = true;
    micBtn.textContent = "🎙️";
    micBtn.style.background = "linear-gradient(120deg, #27d7ff, #14ffb9)";
    setAgentState("listening");
  };
  recognizer.onend = () => {
    listening = false;
    micBtn.textContent = "🎤";
    micBtn.style.background = "rgba(255,255,255,0.08)";
    setAgentState("idle");
  };
  recognizer.onerror = () => {
    listening = false;
    micBtn.textContent = "🎤";
    micBtn.style.background = "rgba(255,255,255,0.08)";
    setAgentState("error");
  };
  recognizer.onresult = (event) => {
    const transcript = Array.from(event.results).map(r => r[0].transcript).join(" ");
    send(transcript);
  };

  micBtn.onclick = () => {
    if (listening) {
      recognizer.stop();
    } else {
      recognizer.start();
    }
  };
} else {
  micBtn.disabled = true;
  micBtn.title = "Voice unavailable (Web Speech API not supported)";
}
