import React from "react";
import ChatBox from "./components/ChatBox";

function App() {
  return (
    <div style={{ padding: 24, maxWidth: 800, margin: "0 auto", fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 16 }}>Ask a Medical Rep</h1>
      <ChatBox />
      <p style={{ marginTop: 24, fontSize: 12, color: "#666" }}>
        Demo only. Not medical advice.
      </p>
    </div>
  );
}

export default App;
