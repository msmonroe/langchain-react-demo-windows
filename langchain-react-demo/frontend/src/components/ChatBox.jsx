import React, { useState } from "react";

function ChatBox() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const apiBase = import.meta.env.VITE_API_BASE || "";
  const endpoint = `${apiBase}/ask`;

  const ask = async () => {
    setLoading(true);
    setError("");
    setAnswer("");

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setAnswer(data.answer);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        style={{ border: "1px solid #ccc", padding: 8, width: "100%" }}
        placeholder="Ask a medical question..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button
        onClick={ask}
        style={{ marginTop: 8, padding: "8px 12px", background: "#2563eb", color: "#fff", borderRadius: 8, border: 0 }}
        disabled={!question || loading}
      >
        {loading ? "Thinking..." : "Ask"}
      </button>

      {error && <pre style={{ marginTop: 12, padding: 12, background: "#fef2f2", border: "1px solid #fecaca", color: "#991b1b" }}>{error}</pre>}
      {answer && <p style={{ marginTop: 12, padding: 12, background: "#f5f5f5", borderRadius: 8 }}>{answer}</p>}
    </div>
  );
}

export default ChatBox;
