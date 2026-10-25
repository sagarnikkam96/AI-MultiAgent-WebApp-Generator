import React, { useEffect, useState, useRef } from 'react';
import { useLanguage } from '../LanguageContext';
import { SPEECH_LOCALES } from '../i18n';

interface AudioNarratorProps {
  textToSpeak: string;
  projectName?: string;
  onClose?: () => void;
}

export const AudioNarrator: React.FC<AudioNarratorProps> = ({
  textToSpeak,
  projectName = 'Project Overview',
  onClose,
}) => {
  const { lang } = useLanguage();
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [speechRate, setSpeechRate] = useState(1.0);
  const [currentSentence, setCurrentSentence] = useState('');
  const [isSupported, setIsSupported] = useState(true);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      setIsSupported(false);
      return;
    }

    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
    };

    loadVoices();
    window.speechSynthesis.addEventListener('voiceschanged', loadVoices);
    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', loadVoices);
    };
  }, []);

  const cleanText = (() => {
    const cleaned = textToSpeak
      .replace(/[#*_`]/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .trim();
    return cleaned || textToSpeak.trim() || 'Project overview is ready to be narrated.';
  })();

  const getMatchedVoice = (utterance: SpeechSynthesisUtterance) => {
    if (voices.length === 0) {
      const fallbackVoices = window.speechSynthesis.getVoices();
      if (fallbackVoices.length > 0) {
        const targetLangPrefix = utterance.lang.split('-')[0];
        return fallbackVoices.find((v) => v.lang.startsWith(targetLangPrefix)) || null;
      }
      return null;
    }
    const targetLangPrefix = utterance.lang.split('-')[0];
    return voices.find((v) => v.lang.startsWith(targetLangPrefix)) || null;
  };

  const handlePlay = () => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      setIsSupported(false);
      return;
    }

    if (!cleanText) {
      setSpeechError('There is no narration text to play.');
      return;
    }

    setSpeechError(null);
    if (isPaused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
      setIsPlaying(true);
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = speechRate;
    utterance.lang = SPEECH_LOCALES[lang] || 'en-IN';

    const matchedVoice = getMatchedVoice(utterance);
    if (matchedVoice) {
      utterance.voice = matchedVoice;
    }

    utterance.onboundary = (event) => {
      if (event.name === 'sentence' || event.name === 'word') {
        const charIndex = event.charIndex;
        const textSlice = cleanText.substring(charIndex, charIndex + 120);
        setCurrentSentence(textSlice);
      }
    };

    utterance.onstart = () => {
      setIsPlaying(true);
      setIsPaused(false);
    };

    utterance.onend = () => {
      setIsPlaying(false);
      setIsPaused(false);
      setCurrentSentence('');
    };

    utterance.onerror = (event) => {
      setIsPlaying(false);
      setIsPaused(false);
      setCurrentSentence('');
      setSpeechError(`Voice narration could not play (${event.error}). Check that your browser has a voice available and audio is enabled.`);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const handlePause = () => {
    if (isPlaying && !isPaused) {
      window.speechSynthesis.pause();
      setIsPaused(true);
      setIsPlaying(false);
    }
  };

  const handleStop = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsPlaying(false);
    setIsPaused(false);
    setCurrentSentence('');
  };

  const handleRateChange = (rate: number) => {
    setSpeechRate(rate);
    if (isPlaying) {
      handleStop();
      setTimeout(handlePlay, 100);
    }
  };

  useEffect(() => {
    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  return (
    <div className="audio-narrator-card">
      <div className="narrator-header">
        <div className="narrator-title-wrap">
          <span className="narrator-badge">🔊 AI Voice Narrator</span>
          <h4 className="narrator-title">{projectName}</h4>
        </div>
        {onClose && (
          <button type="button" onClick={onClose} className="narrator-close-btn" title="Close narrator">
            ✕
          </button>
        )}
      </div>

      <div className="narrator-controls-row">
        <div className="narrator-playback-btns">
          {!isSupported ? (
            <p className="alert alert-error">Voice narration is not supported by this browser.</p>
          ) : !isPlaying ? (
            <button
              type="button"
              onClick={handlePlay}
              className="btn btn-voice-play"
              title="Play Voice Narration"
            >
              ▶ {isPaused ? 'Resume Narration' : 'Narrate Project'}
            </button>
          ) : (
            <button
              type="button"
              onClick={handlePause}
              className="btn btn-voice-pause"
              title="Pause Voice Narration"
            >
              ⏸ Pause
            </button>
          )}

          <button
            type="button"
            onClick={handleStop}
            disabled={!isPlaying && !isPaused}
            className="btn btn-ghost btn-sm"
            title="Stop Voice Narration"
          >
            ⏹ Stop
          </button>
        </div>

        {speechError && <p className="alert alert-error">{speechError}</p>}

        <div className="narrator-speed-selector">
          <span className="speed-label">Speed:</span>
          {[0.75, 1.0, 1.25, 1.5].map((rate) => (
            <button
              key={rate}
              type="button"
              onClick={() => handleRateChange(rate)}
              className={`speed-pill ${speechRate === rate ? 'active' : ''}`}
            >
              {rate}x
            </button>
          ))}
        </div>
      </div>

      {isPlaying && (
        <div className="equalizer-container">
          <div className="equalizer-bar bar-1"></div>
          <div className="equalizer-bar bar-2"></div>
          <div className="equalizer-bar bar-3"></div>
          <div className="equalizer-bar bar-4"></div>
          <div className="equalizer-bar bar-5"></div>
          <div className="equalizer-bar bar-6"></div>
          <span className="equalizer-text">Speaking aloud project architecture &amp; generated features...</span>
        </div>
      )}

      {currentSentence && (
        <div className="narrator-captions">
          <span className="caption-tag">Live Spoken Caption:</span>
          <p className="caption-text">"{currentSentence}..."</p>
        </div>
      )}
    </div>
  );
};
