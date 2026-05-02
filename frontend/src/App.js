import React, { useEffect, useRef, useState } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

function App() {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const recognitionRef = useRef(null);
  const recognitionActiveRef = useRef(false);
  const lastSpokenRef = useRef('');
  const scanTimerRef = useRef(null);
  // reserved for future use
  const [detections, setDetections] = useState([]);
  const [assistantText, setAssistantText] = useState('Starting vision assistant...');
  const [recognizedName, setRecognizedName] = useState('');
  const [pendingSave, setPendingSave] = useState(false);
  const [heardName, setHeardName] = useState('');
  const [locationText, setLocationText] = useState('Location permission not requested.');
  const [locationMeta, setLocationMeta] = useState({
    accuracy: null,
    updatedAt: '',
    quality: 'Unknown',
  });
  const [knownFaces, setKnownFaces] = useState([]);
  // flags reserved (auto modes disabled)
  const [aiInput, setAiInput] = useState('');
  const [aiReply, setAiReply] = useState('');
  const [listening, setListening] = useState(false);
  const [scanLine, setScanLine] = useState(0);

  const formatLabel = (label) =>
    label
      .split(' ')
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(' ');

  const getLocationQuality = (accuracy) => {
    if (accuracy == null) {
      return 'Unknown';
    }
    if (accuracy <= 20) {
      return 'High';
    }
    if (accuracy <= 75) {
      return 'Medium';
    }
    return 'Low';
  };

  const speak = (text, force = false) => {
    if (!text) {
      return;
    }

    if (!force && text === lastSpokenRef.current) {
      return;
    }

    window.speechSynthesis.cancel();
    const message = new SpeechSynthesisUtterance(text);
    message.lang = 'en-IN';
    message.rate = 1;
    lastSpokenRef.current = text;
    window.speechSynthesis.speak(message);
  };

  const drawHud = (items) => {
    const canvas = canvasRef.current;
    const video = webcamRef.current?.video;
    if (!canvas || !video) {
      return;
    }

    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;
    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, width, height);

    items.forEach((det) => {
      const [x1, y1, x2, y2] = det.box;
      const boxWidth = x2 - x1;
      const boxHeight = y2 - y1;
      const accent =
        det.label === 'person' || det.label.includes('face') ? '#79f2a0' : '#ffce6b';

      ctx.strokeStyle = accent;
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, boxWidth, boxHeight);

      ctx.fillStyle = 'rgba(6, 16, 26, 0.72)';
      ctx.fillRect(x1, Math.max(8, y1 - 44), Math.max(170, boxWidth), 36);

      ctx.fillStyle = accent;
      ctx.font = 'bold 14px monospace';
      ctx.fillText(
        `${formatLabel(det.label).toUpperCase()}  ${det.distance_m ?? '?'} m`,
        x1 + 8,
        Math.max(30, y1 - 22)
      );

      ctx.font = '12px monospace';
      ctx.fillText(
        `${Math.round(det.conf * 100)}%  ${det.position.horizontal}`,
        x1 + 8,
        Math.max(44, y1 - 8)
      );
    });
  };

  const captureFrameBlob = async () => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (!imageSrc) {
      return null;
    }
    return fetch(imageSrc).then((response) => response.blob());
  };

  const saveFaceWithName = async (name) => {
    const blob = await captureFrameBlob();
    if (!blob) {
      setAssistantText('Camera frame not available for saving.');
      speak('Camera frame not available for saving.', true);
      return;
    }

    const formData = new FormData();
    formData.append('file', blob, 'frame.jpg');

    try {
        const response = await axios.post(
          `${API_BASE}/save_face?name=${encodeURIComponent(name)}`,
          formData
        );
        const message = response.data.message || `Face saved for ${name}.`;
        setPendingSave(false);
        setHeardName(name);
        setAssistantText(message);
        speak(message, true);
        fetchFaces();
      } catch (error) {
        const message =
          error.response?.data?.detail || 'I could not save the face profile.';
        setAssistantText(message);
        speak(message, true);
    }
  };

  const askAssistant = async (text) => {
    const prompt = text || aiInput.trim();
    if (!prompt) return;
    try {
      const res = await axios.post(`${API_BASE}/chat`, { message: prompt });
      const reply = res.data.reply || 'No reply.';
      setAiReply(reply);
      speak(reply, true);
    } catch (e) {
      const msg = 'Assistant unavailable.';
      setAiReply(msg);
      speak(msg, true);
    }
  };

  const fetchFaces = async () => {
    try {
      const res = await axios.get(`${API_BASE}/faces`);
      setKnownFaces(res.data.names || []);
    } catch (e) {
      // ignore
    }
  };

  const requestLocationVoice = () => {
    if (!navigator.geolocation) {
      const message = 'Geolocation is not supported in this browser.';
      setLocationText(message);
      speak(message, true);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const payload = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy_m: position.coords.accuracy,
        };

        const readable = `Lat ${payload.latitude.toFixed(5)}, Lng ${payload.longitude.toFixed(5)}, accuracy ${Math.round(payload.accuracy_m)} m`;
        setLocationText(readable);
        setLocationMeta({
          accuracy: Math.round(payload.accuracy_m),
          updatedAt: new Date().toLocaleTimeString(),
          quality: getLocationQuality(payload.accuracy_m),
        });

        try {
          const response = await axios.post(`${API_BASE}/location_voice`, payload);
          speak(response.data.voice, true);
        } catch (error) {
          speak(`Your current location is ${readable}.`, true);
        }
      },
      () => {
        const message = 'Location permission was denied.';
        setLocationText(message);
        setLocationMeta({
          accuracy: null,
          updatedAt: '',
          quality: 'Denied',
        });
        speak(message, true);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const startNameListening = () => {
    if (!SpeechRecognition) {
      const fallbackName = window.prompt('Speech recognition unavailable. Enter your name:');
      if (fallbackName) {
        saveFaceWithName(fallbackName.trim());
      }
      return;
    }

    if (!recognitionRef.current) {
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-IN';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        recognitionActiveRef.current = true;
        setListening(true);
      };
      recognition.onend = () => {
        recognitionActiveRef.current = false;
        setListening(false);
      };
      recognition.onerror = () => {
        recognitionActiveRef.current = false;
        setListening(false);
        setPendingSave(false);
        setAssistantText('Voice capture failed. Please try again.');
      };
      recognition.onresult = (event) => {
        const transcript = event.results?.[0]?.[0]?.transcript?.trim();
        if (!transcript) {
          return;
        }
        setHeardName(transcript);
        setAssistantText(`I heard ${transcript}. Saving face profile.`);
        speak(`I heard ${transcript}. Saving your face profile now.`, true);
        saveFaceWithName(transcript);
      };

      recognitionRef.current = recognition;
    }

    setPendingSave(true);
    setAssistantText('Please say your name clearly after the beep.');
    speak('Please say your name clearly after the beep.', true);
    if (recognitionActiveRef.current) {
      setAssistantText('Voice recognition is already listening.');
      speak('Voice recognition is already listening.', true);
      return;
    }

    try {
      recognitionRef.current.start();
    } catch (error) {
      setPendingSave(false);
      setAssistantText('Voice recognition could not start. Please try again.');
      speak('Voice recognition could not start. Please try again.', true);
    }
  };

  const handleVoiceCommand = () => {
    if (!SpeechRecognition) {
      speak('Voice control is unavailable in this browser.', true);
      return;
    }

    const commandRec = new SpeechRecognition();
    commandRec.lang = 'en-IN';
    commandRec.interimResults = false;
    commandRec.maxAlternatives = 1;

    setAssistantText('Voice control: say save face, speak location, or ask assistant ...');
    speak('Voice control ready. Say save face, speak location, or ask assistant followed by your question.', true);

    commandRec.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript?.trim().toLowerCase();
      if (!transcript) {
        speak('I did not catch that.', true);
        return;
      }
      if (transcript.includes('save face')) {
        startNameListening();
      } else if (transcript.includes('location')) {
        requestLocationVoice();
      } else if (transcript.startsWith('ask assistant')) {
        const q = transcript.replace('ask assistant', '').trim();
        if (q.length > 0) {
          askAssistant(q);
        } else {
          speak('Please say ask assistant followed by your question.', true);
        }
      } else {
        speak('Command not recognized. Say save face, speak location, or ask assistant.', true);
      }
    };

    commandRec.onerror = () => {
      speak('Voice control error. Please try again.', true);
    };

    try {
      commandRec.start();
    } catch {
      speak('Voice control could not start. Please try again.', true);
    }
  };


  useEffect(() => {
    scanTimerRef.current = window.setInterval(() => {
      setScanLine((prev) => (prev >= 92 ? 0 : prev + 4));
    }, 120);

    return () => {
      window.clearInterval(scanTimerRef.current);
    };
  }, []);

  useEffect(() => {
    const interval = window.setInterval(async () => {
      if (webcamRef.current?.video?.readyState !== 4) {
        return;
      }

      const blob = await captureFrameBlob();
      if (!blob) {
        return;
      }

      const formData = new FormData();
      formData.append('file', blob, 'frame.jpg');

      try {
        const response = await axios.post(`${API_BASE}/analyze`, formData);
        const data = response.data;
        setDetections(data.detections || []);
        drawHud(data.detections || []);

        if (data.recognized_name) {
          setRecognizedName(data.recognized_name);
        } else {
          setRecognizedName('');
        }

        const summary = data.voice || 'No spoken update available.';
        setAssistantText(summary);
        speak(summary);

        // No auto-enroll or auto-save; user must trigger save with their name.
      } catch (error) {
        setAssistantText('Backend offline. Start FastAPI in VS Code terminal.');
      }
    }, 2200);

    fetchFaces();

    return () => window.clearInterval(interval);
  }, []);

  const primaryDetection = detections[0];
  const topDetections = detections.slice(0, 3);

  return (
    <div className="app-shell">
      <div className="ambient-grid" />
      <section className="hero-panel">
        <div className="title-block">
          <p className="eyebrow">YOLO Vision Assistant</p>
          <h1>Face recognition, object awareness, voice guidance, and live camera automation.</h1>
          <p className="subcopy">
            Detects people, objects, and animals with YOLO. If your face is new, say your
            name once and it will remember you for later sessions.
          </p>
        </div>

        <div className="controls">
          <button className="primary-btn" onClick={startNameListening}>
            {pendingSave || listening ? 'Listening For Name...' : 'Scan Face And Save Name'}
          </button>
          <button className="secondary-btn" onClick={requestLocationVoice}>
            Speak My Location
          </button>
          <button className="secondary-btn" onClick={handleVoiceCommand}>
            Voice Command
          </button>
        </div>

        <div className="status-grid">
          <div className="status-card">
            <span className="label">Assistant</span>
            <strong>{assistantText}</strong>
          </div>
          <div className="status-card">
            <span className="label">Recognized Face</span>
            <strong>{recognizedName || 'No known face recognized yet'}</strong>
          </div>
          <div className="status-card">
            <span className="label">Last Heard Name</span>
            <strong>{heardName || 'Waiting for voice input'}</strong>
          </div>
          <div className="status-card">
            <span className="label">Location</span>
            <strong>{locationText}</strong>
            <small>
              Quality: {locationMeta.quality}
              {locationMeta.accuracy ? ` | +/-${locationMeta.accuracy} m` : ''}
              {locationMeta.updatedAt ? ` | Updated ${locationMeta.updatedAt}` : ''}
            </small>
          </div>
          <div className="status-card">
            <span className="label">Saved Faces</span>
            <strong>{knownFaces.length ? knownFaces.join(', ') : 'None saved yet'}</strong>
          </div>
          <div className="status-card">
            <span className="label">Assistant Reply</span>
            <strong>{aiReply || 'No reply yet'}</strong>
          </div>
        </div>
      </section>

      <section className="viewer-panel">
        <div className="viewer-frame">
          <Webcam
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            mirrored
            audio={false}
            videoConstraints={{ width: 960, height: 540, facingMode: 'user' }}
            className="camera-feed"
          />
          <canvas ref={canvasRef} className="hud-layer" />
          <div className="scan-line" style={{ top: `${scanLine}%` }} />
        </div>

        <div className="detection-panel">
          <div className="detection-header">
            <span>Live Detections</span>
            <span>{detections.length} visible</span>
          </div>

          {primaryDetection ? (
            <div className="focus-card">
              <p>Nearest target</p>
              <h2>{formatLabel(primaryDetection.label)}</h2>
              <strong>{primaryDetection.distance_m ?? '?'} meters away</strong>
              <span>
                Position: {primaryDetection.position.horizontal}, {primaryDetection.position.vertical}
              </span>
            </div>
          ) : (
            <div className="focus-card empty">
              <p>Nearest target</p>
              <h2>No target</h2>
              <span>Show an object, animal, or face to begin analysis.</span>
            </div>
          )}

          <div className="list-panel">
            {detections.map((det, index) => (
              <div className="list-row" key={`${det.label}-${index}-${det.conf}`}>
                <span>{formatLabel(det.label)}</span>
                <span>{det.distance_m ?? '?'} m</span>
                <span>{Math.round(det.conf * 100)}%</span>
              </div>
            ))}
          </div>

          <div className="insight-card">
            <span className="label">Quick Summary</span>
            {topDetections.length > 0 ? (
              <strong>
                {topDetections
                  .map(
                    (det) =>
                      `${formatLabel(det.label)} ${det.distance_m ?? '?'} m ${det.position.horizontal}`
                  )
                  .join(' | ')}
              </strong>
            ) : (
              <strong>Waiting for camera detections.</strong>
            )}
          </div>

          <div className="insight-card">
            <span className="label">Ask Assistant</span>
            <textarea
              value={aiInput}
              onChange={(e) => setAiInput(e.target.value)}
              placeholder="Ask a question..."
              style={{ width: '100%', minHeight: '60px', marginBottom: '8px' }}
            />
            <button className="secondary-btn" onClick={() => askAssistant()}>
              Ask
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}

export default App;
