import { useState, useRef, useEffect } from "react";

const SUGGESTIONS = [
  "What is the biggest risk right now?",
  "Which areas are vulnerable?",
  "What should commuters know?",
];

export default function Assistant({ onAsk }) {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Ask me about current risk, zones, or vulnerability. I only answer from AURA's live application data." },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages]);

  const send = async (question) => {
    const q = question ?? input;
    if (!q.trim() || busy) return;
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setBusy(true);
    try {
      const res = await onAsk(q);
      setMessages((m) => [...m, { role: "assistant", text: res.answer }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", text: "I couldn't reach the AURA backend to answer that." }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-lg border border-ink-600 bg-ink-800 p-4 shadow-panel">
      <div className="mb-3 text-[11px] uppercase tracking-wide text-mist-400">AURA Assistant</div>

      <div ref={scrollRef} className="mb-3 flex-1 space-y-2 overflow-y-auto" style={{ maxHeight: 220 }}>
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[90%] rounded-md px-3 py-2 text-[11px] leading-relaxed ${
              m.role === "user"
                ? "ml-auto bg-signal-tealDim/40 text-mist-50"
                : "bg-ink-900 text-mist-300"
            }`}
          >
            {m.text}
          </div>
        ))}
      </div>

      <div className="mb-2 flex flex-wrap gap-1.5">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => send(s)}
            className="rounded-full border border-ink-600 px-2.5 py-1 text-[10px] text-mist-400 hover:border-signal-teal hover:text-signal-teal"
          >
            {s}
          </button>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about current risk…"
          className="flex-1 rounded border border-ink-600 bg-ink-900 px-2 py-2 text-xs text-mist-50 outline-none focus:border-signal-teal"
        />
        <button
          onClick={() => send()}
          disabled={busy}
          className="rounded-md bg-signal-teal px-3 text-xs font-semibold text-ink-950 disabled:opacity-50"
        >
          Ask
        </button>
      </div>
    </div>
  );
}
