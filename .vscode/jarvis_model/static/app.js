const stateText = document.getElementById("stateText");
const messageText = document.getElementById("messageText");
const micBtn = document.getElementById("micBtn");
const speakBtn = document.getElementById("speakBtn");
const sendBtn = document.getElementById("sendBtn");
const commandInput = document.getElementById("commandInput");
const ocrCheck = document.getElementById("ocrCheck");

let browserVoiceEnabled = true;
let visualState = "idle";

function speakInBrowser(text) {
  if (!browserVoiceEnabled || !("speechSynthesis" in window)) return;
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 1.0;
  utter.pitch = 1.0;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
}

function setState(state, msg = "") {
  visualState = state;
  stateText.textContent = `State: ${state}`;
  if (msg) messageText.textContent = msg;
}

async function sendCommand(text) {
  if (!text) return;
  setState("thinking", text);
  try {
    const res = await fetch("/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        include_screen_context: ocrCheck.checked
      })
    });
    const data = await res.json();
    setState("speaking", data.response);
    speakInBrowser(data.response);
    setTimeout(() => setState("idle", "Ready."), 900);
  } catch (err) {
    setState("idle", `Error: ${err}`);
  }
}

sendBtn.addEventListener("click", () => {
  const text = commandInput.value.trim();
  commandInput.value = "";
  sendCommand(text);
});

commandInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendBtn.click();
});

speakBtn.addEventListener("click", () => {
  browserVoiceEnabled = !browserVoiceEnabled;
  speakBtn.textContent = browserVoiceEnabled ? "🔊 Toggle Browser Voice" : "🔇 Browser Voice Off";
});

micBtn.addEventListener("click", () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    setState("idle", "Browser speech recognition is not supported here. Use latest Chrome.");
    return;
  }
  const recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  setState("listening", "Listening...");
  recognition.start();
  recognition.onresult = (event) => {
    const text = event.results[0][0].transcript;
    sendCommand(text);
  };
  recognition.onerror = (event) => {
    const code = event.error || "unknown";
    if (code === "not-allowed") {
      setState("idle", "Mic blocked by browser permission. Allow microphone access and retry.");
      return;
    }
    if (code === "no-speech") {
      setState("idle", "No speech detected. Try again and speak immediately.");
      return;
    }
    if (code === "audio-capture") {
      setState("idle", "No usable microphone found by browser. Check Windows input device and retry.");
      return;
    }
    setState("idle", `Browser mic error (${code}). Retry after refreshing page.`);
  };
});

const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
const ws = new WebSocket(`${wsProtocol}://${window.location.host}/ws`);
ws.onmessage = (event) => {
  try {
    const data = JSON.parse(event.data);
    setState(data.state || "idle", data.message || "");
    if (data.state === "speaking" && data.message) speakInBrowser(data.message);
  } catch {
    // ignore malformed payload
  }
};

const canvas = document.getElementById("orbCanvas");
const ctx = canvas.getContext("2d");
let w = 0;
let h = 0;
const particles = [];
const particleCount = 260;

function resize() {
  w = canvas.width = window.innerWidth;
  h = canvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();

for (let i = 0; i < particleCount; i += 1) {
  particles.push({
    angle: Math.random() * Math.PI * 2,
    radius: 80 + Math.random() * 230,
    speed: 0.001 + Math.random() * 0.004,
    size: 0.5 + Math.random() * 2.0
  });
}

function stateGlow(state) {
  if (state === "listening") return "#00e5ff";
  if (state === "thinking") return "#8a7dff";
  if (state === "acting") return "#ffbd59";
  if (state === "speaking") return "#43ff87";
  return "#41b7ff";
}

function animate() {
  const cx = w / 2;
  const cy = h / 2 - 50;
  const color = stateGlow(visualState);

  ctx.fillStyle = "rgba(2,7,18,0.25)";
  ctx.fillRect(0, 0, w, h);

  ctx.beginPath();
  ctx.arc(cx, cy, 70, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(65,183,255,0.16)";
  ctx.fill();

  ctx.beginPath();
  ctx.arc(cx, cy, 64, 0, Math.PI * 2);
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.shadowBlur = 24;
  ctx.shadowColor = color;
  ctx.stroke();
  ctx.shadowBlur = 0;

  for (const p of particles) {
    p.angle += p.speed;
    const pulse = visualState === "speaking" ? 1.2 : visualState === "listening" ? 1.1 : 1.0;
    const r = p.radius * pulse;
    const x = cx + Math.cos(p.angle) * r;
    const y = cy + Math.sin(p.angle) * (r * 0.45);
    ctx.beginPath();
    ctx.arc(x, y, p.size, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }

  requestAnimationFrame(animate);
}

animate();
