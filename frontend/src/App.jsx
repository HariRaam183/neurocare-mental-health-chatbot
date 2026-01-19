import React, { useState } from "react";

const API_URL = "http://127.0.0.1:8001/api/chat";

function App() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hi, I’m NeuroCare. I’m here to listen. How are you feeling today?",
      emotion: null,
      intent: null,
      mode: "template",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("gemini"); // "gemini" | "openai"

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    // Add user message to chat
    const newMessages = [
      ...messages,
      { sender: "user", text: trimmed, emotion: null, intent: null, mode: null },
    ];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const body = {
        message: trimmed,
        history: newMessages.map((m) => ({
          sender: m.sender,
          text: m.text,
        })),
        mode, // 👈 send current mode to backend
      };

      const res = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error("Server error");
      }

      const data = await res.json();

      const botMessage = {
        sender: "bot",
        text: data.reply,
        emotion: data.emotion_label,
        intent: data.intent,
        mode: data.llm_mode, // 👈 gemini / openai / template from backend
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text:
            "Sorry, I had trouble connecting to the server. Please try again.",
          emotion: null,
          intent: null,
          mode: "error",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  const chipStyle = {
    padding: "2px 8px",
    borderRadius: "999px",
    border: "1px solid #6b7280",
  };

  // Show the mode of the last bot reply in the header
  const lastBot = [...messages].reverse().find((m) => m.sender === "bot");
  const currentBackendMode = lastBot?.mode || "template";

  const toggleMode = () => {
    setMode((prev) => (prev === "gemini" ? "openai" : "gemini"));
  };

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#0f172a",
        color: "white",
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "900px",
          height: "80vh",
          background: "#020617",
          borderRadius: "16px",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          boxShadow: "0 20px 40px rgba(0,0,0,0.6)",
          border: "1px solid #1f2937",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "16px 20px",
            borderBottom: "1px solid #1f2937",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            background:
              "linear-gradient(to right, rgba(56,189,248,0.1), rgba(129,140,248,0.1))",
          }}
        >
          <div>
            <div style={{ fontSize: "18px", fontWeight: 600 }}>NeuroCare</div>
            <div style={{ fontSize: "12px", color: "#9ca3af" }}>
              AI Mental Health Companion
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            {/* Online badge */}
            <div
              style={{
                fontSize: "12px",
                padding: "4px 10px",
                borderRadius: "999px",
                border: "1px solid #22c55e",
                color: "#22c55e",
              }}
            >
              ● Online
            </div>

            {/* Current backend mode (from response) */}
            <div
              style={{
                fontSize: "12px",
                padding: "4px 10px",
                borderRadius: "999px",
                border: "1px solid #4b5563",
                color: "#e5e7eb",
              }}
            >
              Mode: {currentBackendMode}
            </div>

            {/* Toggle button for request mode */}
            <button
              onClick={toggleMode}
              style={{
                fontSize: "12px",
                padding: "6px 12px",
                borderRadius: "999px",
                border: "none",
                cursor: "pointer",
                background:
                  mode === "gemini"
                    ? "linear-gradient(to right, #22c55e, #22d3ee)"
                    : "linear-gradient(to right, #6366f1, #a855f7)",
                color: "#020617",
                fontWeight: 500,
              }}
            >
              Use: {mode}
            </button>
          </div>
        </div>

        {/* Messages */}
        <div
          style={{
            flex: 1,
            padding: "16px",
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: "10px",
          }}
        >
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                display: "flex",
                justifyContent:
                  msg.sender === "user" ? "flex-end" : "flex-start",
              }}
            >
              <div
                style={{
                  maxWidth: "70%",
                  background:
                    msg.sender === "user" ? "#4f46e5" : "#111827",
                  padding: "10px 14px",
                  borderRadius:
                    msg.sender === "user"
                      ? "16px 16px 2px 16px"
                      : "16px 16px 16px 2px",
                  fontSize: "14px",
                  position: "relative",
                }}
              >
                <div>{msg.text}</div>
                {msg.sender === "bot" && msg.text.length > 40 && (msg.emotion || msg.intent || msg.mode) && (
                  <div
                    style={{
                      marginTop: "6px",
                      fontSize: "11px",
                      color: "#9ca3af",
                      display: "flex",
                      gap: "8px",
                      flexWrap: "wrap",
                    }}
                  >
                    {msg.emotion && (
                      <span style={chipStyle}>
                        Emotion: {msg.emotion}
                      </span>
                    )}
                    {msg.intent && (
                      <span style={chipStyle}>
                        Topic: {msg.intent}
                      </span>
                    )}
                    {msg.mode && (
                      <span style={chipStyle}>
                        Mode: {msg.mode}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ fontSize: "12px", color: "#9ca3af", marginTop: 8 }}>
              NeuroCare is thinking...
            </div>
          )}
        </div>

        {/* Input */}
        <div
          style={{
            padding: "12px 16px",
            borderTop: "1px solid #1f2937",
            display: "flex",
            gap: "8px",
            background: "#020617",
          }}
        >
          <input
            type="text"
            placeholder="Type how you're feeling..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{
              flex: 1,
              padding: "10px 12px",
              borderRadius: "999px",
              border: "1px solid #374151",
              background: "#020617",
              color: "white",
              fontSize: "14px",
              outline: "none",
            }}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            style={{
              padding: "10px 18px",
              borderRadius: "999px",
              border: "none",
              fontSize: "14px",
              fontWeight: 500,
              cursor: "pointer",
              background: loading
                ? "#4b5563"
                : "linear-gradient(to right, #22c55e, #22d3ee)",
              color: "#020617",
            }}
          >
            {loading ? "Sending..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
