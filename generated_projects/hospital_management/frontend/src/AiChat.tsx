import React, { useState, useRef, useEffect } from 'react';

interface AiChatProps {
  onClose: () => void;
  projectName?: string;
}

interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
}

const AiChat: React.FC<AiChatProps> = ({ onClose, projectName = "Hospital Management System" }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      role: 'assistant',
      content: 'Hello! I am your AI Assistant. How can I help you today? You can ask about managing records, customizing views, or finding features.'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const quickPrompts = [
    'How do I add a new record?',
    'What features can I customize?',
    'How do I switch themes or languages?',
    'Show me how to export or backup data'
  ];

  const handleSend = (userText: string) => {
    const text = userText.trim();
    if (!text || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: text
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    setTimeout(() => {
      let reply = 'I can help with that! You can use the sidebar to navigate between sections, add records using the form cards, or click Add Feature to launch new custom modules.';
      const query = text.toLowerCase();
      if (query.includes('add') || query.includes('create') || query.includes('record')) {
        reply = 'To add a new record, navigate to the respective section from the navigation sidebar or dashboard, enter the details in the form fields, and click the Add button. Your records are saved automatically.';
      } else if (query.includes('theme') || query.includes('color') || query.includes('dark') || query.includes('light')) {
        reply = 'You can toggle between Dark Mode and Light Mode using the Customize Website button in the sidebar. You can also pick from curated accent themes like Cyan, Indigo, Emerald, Amber, or Rose!';
      } else if (query.includes('language') || query.includes('translate')) {
        reply = 'Use the Language dropdown in the sidebar to switch between English, Hindi, Kannada, Marathi, or Telugu in real time.';
      } else if (query.includes('feature') || query.includes('module')) {
        reply = 'Click the Add Feature / Module button in the sidebar or the floating launcher at the bottom-right corner to dynamically create Kanban boards, tables, metric cards, or notes!';
      } else if (query.includes('export') || query.includes('backup')) {
        reply = 'All records and customizations are securely stored in your active session. You can also export or download the full project archive directly from the main workspace generator.';
      }
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, role: 'assistant', content: reply }
      ]);
      setIsLoading(false);
    }, 450);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend(input);
  };

  return (
    <div className="ai-chat-backdrop" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="ai-chat-window" role="dialog" aria-modal="true" aria-label="AI Assistant">
        <header className="ai-chat-header">
          <div className="ai-chat-title">
            <span role="img" aria-label="bot">🤖</span>
            <span>{projectName} AI Assistant</span>
            <span className="ai-chat-badge">Online</span>
          </div>
          <button type="button" onClick={onClose} className="btn-del-sm" style={{ fontSize: '1.2rem', padding: '4px 8px' }} title="Close Chat">✕</button>
        </header>

        <div className="ai-chat-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`ai-message ${msg.role === 'user' ? 'user' : 'bot'}`}>
              <div className={`ai-avatar ${msg.role === 'user' ? 'user-av' : 'bot'}`}>
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>
              <div className={`ai-bubble ${msg.role === 'user' ? 'user' : 'bot'}`}>
                {msg.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="ai-message bot">
              <div className="ai-avatar bot">🤖</div>
              <div className="ai-bubble bot">Thinking...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="ai-quick-prompts">
          {quickPrompts.map((promptText, i) => (
            <button key={i} type="button" onClick={() => handleSend(promptText)} className="ai-chip">
              {promptText}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="ai-chat-input-bar">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about this application..."
            disabled={isLoading}
            className="ai-chat-input"
            autoFocus
          />
          <button type="submit" disabled={isLoading || !input.trim()} className="btn-primary" style={{ padding: '10px 18px', borderRadius: '14px' }}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default AiChat;
