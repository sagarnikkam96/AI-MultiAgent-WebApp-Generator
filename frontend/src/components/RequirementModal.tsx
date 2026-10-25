import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../LanguageContext';
import { SPEECH_LOCALES } from '../i18n';

interface RequirementModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApplyRequirements: (newRequirementText: string) => void;
  currentPrompt: string;
}

const PRESET_REQUIREMENTS = [
  '🌙 Add Dark/Light Mode Theme Switcher',
  '🔍 Add Real-time Search Bar & Filter Controls',
  '💳 Add Mock Payment Gateway & Checkout Flow',
  '🔐 Add Multi-Role Access Control (Admin, Manager, User)',
  '📊 Add Analytics Dashboard with Interactive Stat Cards',
  '📥 Add Export Data to CSV and PDF functionality',
  '🔔 Add Live Toast Notifications & Activity Logs',
  '📱 Enhance Mobile Responsive Touch Navigation',
];

export const RequirementModal: React.FC<RequirementModalProps> = ({
  isOpen,
  onClose,
  onApplyRequirements,
  currentPrompt,
}) => {
  const { lang, t } = useLanguage();
  const [requirementText, setRequirementText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  if (!isOpen) return null;

  const handleStartVoice = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setVoiceError('Voice input is not supported in this browser. You can type your requirements directly.');
      return;
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {
        // ignore
      }
      recognitionRef.current = null;
      setIsListening(false);
      return;
    }

    setVoiceError(null);
    const recognition = new SpeechRecognition();
    recognition.lang = SPEECH_LOCALES[lang] || 'en-IN';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript + ' ';
        }
      }
      if (finalTranscript) {
        setRequirementText((prev) => (prev.trim() ? `${prev.trim()} ${finalTranscript.trim()}` : finalTranscript.trim()));
      }
    };

    recognition.onerror = (event: any) => {
      const err = event.error || 'unknown';
      if (err === 'not-allowed') {
        setVoiceError('Microphone permission denied. Please allow microphone access in browser settings.');
      } else if (err !== 'no-speech') {
        setVoiceError(`Voice recognition error: ${err}`);
      }
      setIsListening(false);
      recognitionRef.current = null;
    };

    recognition.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };

    try {
      recognition.start();
      recognitionRef.current = recognition;
      setIsListening(true);
    } catch (err: any) {
      setVoiceError(err?.message || 'Could not start microphone.');
      setIsListening(false);
    }
  };

  const handleAddPreset = (preset: string) => {
    const cleanPreset = preset.replace(/^[^\w\s]+/, '').trim();
    setRequirementText((prev) =>
      prev.trim() ? `${prev.trim()}; ${cleanPreset}` : cleanPreset
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!requirementText.trim()) return;

    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {
        // ignore
      }
    }

    const mergedPrompt = currentPrompt.trim()
      ? `${currentPrompt.trim()}\n\n[Custom Requirements]: ${requirementText.trim()}`
      : requirementText.trim();

    onApplyRequirements(mergedPrompt);
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal requirement-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-wrap">
            <span className="modal-badge">✨ Custom Requirements &amp; Iteration</span>
            <h2>Modify &amp; Add Requirements</h2>
          </div>
          <button type="button" className="close-btn" onClick={onClose}>✕</button>
        </div>

        <p className="modal-subtitle">
          Type or speak custom features, UI changes, or modules to update the generated website:
        </p>

        <form onSubmit={handleSubmit}>
          <div className="textarea-wrap">
            <textarea
              autoFocus
              rows={4}
              value={requirementText}
              onChange={(e) => setRequirementText(e.target.value)}
              placeholder="e.g. Add an appointment cancellation feature, change the primary color to emerald, and include a patient feedback form."
              className="requirement-textarea"
            />
          </div>

          <div className="modal-voice-bar">
            <button
              type="button"
              onClick={handleStartVoice}
              className={`btn btn-voice-modal ${isListening ? 'listening-pulse' : ''}`}
            >
              {isListening ? '🎙 Stop Listening' : '🎙 Speak Requirements'}
            </button>
            {isListening && (
              <span className="listening-indicator">
                <span className="pulse-dot"></span> Listening... Speak now
              </span>
            )}
          </div>

          {voiceError && <p className="alert alert-error">{voiceError}</p>}

          <div className="preset-section">
            <label className="preset-label">Quick Feature Presets:</label>
            <div className="preset-chips">
              {PRESET_REQUIREMENTS.map((preset) => (
                <button
                  key={preset}
                  type="button"
                  onClick={() => handleAddPreset(preset)}
                  className="preset-chip"
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-ghost" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              disabled={!requirementText.trim()}
              className="btn btn-primary btn-glow"
            >
              ⚡ Apply &amp; Regenerate Website
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
