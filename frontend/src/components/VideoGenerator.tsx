import React, { useState, useRef, useEffect } from 'react';
import { generateVideo, type VideoScene } from '../services/api';

interface VideoGeneratorProps {
  initialPrompt?: string;
}

const THEMES = [
  { id: 'cyberpunk', name: '⚡ Cyberpunk Tech', bg1: '#0f172a', bg2: '#311042', accent: '#a855f7', primary: '#06b6d4' },
  { id: 'modern_saas', name: '💎 Modern SaaS Blue', bg1: '#0a192f', bg2: '#172a45', accent: '#3b82f6', primary: '#60a5fa' },
  { id: 'emerald', name: '🌿 Emerald Clean', bg1: '#022c22', bg2: '#064e3b', accent: '#10b981', primary: '#34d399' },
  { id: 'sunset', name: '🔥 Sunset Fusion', bg1: '#431407', bg2: '#701a75', accent: '#f59e0b', primary: '#ec4899' },
  { id: 'matrix', name: '💻 Terminal Hacker', bg1: '#050505', bg2: '#0a1f0a', accent: '#22c55e', primary: '#4ade80' },
];

const PRESET_VIDEO_PROMPTS = [
  'Hospital Management & Doctor Appointment Platform Demo',
  'Multi-Agent AI Web Application Generator Architecture Flow',
  'Crypto FinTech & DeFi Banking Portal Showcase',
  'Next-Gen E-Commerce Store with Real-time Cart & Checkout',
  'Task & Sprint Management SaaS Board Promo Reel',
];

export const VideoGenerator: React.FC<VideoGeneratorProps> = ({ initialPrompt = '' }) => {
  const [videoPrompt, setVideoPrompt] = useState(initialPrompt || 'AI Multi-Agent Web App Generator Showcase');
  const [selectedTheme, setSelectedTheme] = useState('cyberpunk');
  const [aspectRatio, setAspectRatio] = useState<'16:9' | '9:16' | '1:1'>('16:9');
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [recordedVideoUrl, setRecordedVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const videoPlayerRef = useRef<HTMLVideoElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    if (initialPrompt && !videoPrompt) {
      setVideoPrompt(initialPrompt);
    }
  }, [initialPrompt]);

  const getCanvasDimensions = () => {
    if (aspectRatio === '9:16') return { width: 720, height: 1280 };
    if (aspectRatio === '1:1') return { width: 720, height: 720 };
    return { width: 1280, height: 720 }; // 16:9
  };

  const handleGenerateMotionVideo = async () => {
    if (!videoPrompt.trim()) {
      setError('Please enter a description for the video.');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setProgress(0);
    if (recordedVideoUrl) {
      URL.revokeObjectURL(recordedVideoUrl);
      setRecordedVideoUrl(null);
    }

    try {
      const dim = getCanvasDimensions();
      const apiResult = await generateVideo(videoPrompt, dim.width, dim.height, selectedTheme);
      const scenes: VideoScene[] = apiResult.scenes || [
        {
          id: 1,
          title: `🚀 ${videoPrompt.slice(0, 30)}`,
          subtitle: 'AI Multi-Agent Web Architecture',
          type: 'intro',
          duration: 3.5,
          color: '#6366f1',
          accent: '#a855f7',
          voiceover: 'Welcome to the AI Multi-Agent Generated Web Application.',
        },
        {
          id: 2,
          title: '⚡ Autonomous Agent Swarm',
          subtitle: 'Requirement Agent • Planner Agent • Code Generators',
          type: 'architecture',
          duration: 3.5,
          color: '#06b6d4',
          accent: '#3b82f6',
          voiceover: 'Multi-agent orchestration coordinates the full system pipeline.',
        },
        {
          id: 3,
          title: '🛠 Production Tech Stack',
          subtitle: 'React 18 + TypeScript + FastAPI + PostgreSQL',
          type: 'tech_stack',
          duration: 3.5,
          color: '#10b981',
          accent: '#059669',
          voiceover: 'Fully functional, responsive, and ready for instant deployment.',
        },
        {
          id: 4,
          title: '✨ Ready in VS Code',
          subtitle: 'Download ZIP • Live In-Browser Preview',
          type: 'demo',
          duration: 3.5,
          color: '#f59e0b',
          accent: '#ea580c',
          voiceover: 'Inspect, build, and run complete source code in VS Code.',
        },
      ];

      // Procedural Canvas Video Recording
      await renderAndRecordCanvasVideo(scenes, dim.width, dim.height);
    } catch (err: any) {
      setError(err?.message || 'Failed to render AI video.');
      setIsGenerating(false);
    }
  };

  const renderAndRecordCanvasVideo = (scenes: VideoScene[], width: number, height: number): Promise<void> => {
    return new Promise((resolve, reject) => {
      const canvas = canvasRef.current;
      if (!canvas) {
        reject(new Error('Canvas element not available'));
        return;
      }

      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Canvas 2D context not available'));
        return;
      }

      const stream = canvas.captureStream(30);
      let mediaRecorder: MediaRecorder;
      const recordedChunks: Blob[] = [];

      try {
        const mimeTypes = ['video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm', 'video/mp4'];
        const supportedMime = mimeTypes.find((m) => MediaRecorder.isTypeSupported(m)) || 'video/webm';
        mediaRecorder = new MediaRecorder(stream, { mimeType: supportedMime });
      } catch (err) {
        mediaRecorder = new MediaRecorder(stream);
      }

      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          recordedChunks.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: mediaRecorder.mimeType || 'video/webm' });
        const videoUrl = URL.createObjectURL(blob);
        setRecordedVideoUrl(videoUrl);
        setIsGenerating(false);
        setProgress(100);
        resolve();
      };

      mediaRecorder.start();

      const themeConfig = THEMES.find((t) => t.id === selectedTheme) || THEMES[0];
      const totalDuration = scenes.reduce((sum, s) => sum + s.duration, 0);
      const startTime = performance.now();

      // Particle system for dynamic background
      const particles: Array<{ x: number; y: number; vx: number; vy: number; radius: number; color: string }> = [];
      for (let i = 0; i < 45; i++) {
        particles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 1.5,
          vy: (Math.random() - 0.5) * 1.5,
          radius: Math.random() * 3 + 1,
          color: i % 2 === 0 ? themeConfig.primary : themeConfig.accent,
        });
      }

      const drawFrame = (currentTime: number) => {
        const elapsed = (currentTime - startTime) / 1000;
        const currentProgress = Math.min(Math.round((elapsed / totalDuration) * 100), 99);
        setProgress(currentProgress);

        if (elapsed >= totalDuration) {
          if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
          }
          mediaRecorder.stop();
          return;
        }

        // Determine active scene
        let sceneStart = 0;
        let activeScene = scenes[0];
        let sceneElapsed = 0;

        for (const s of scenes) {
          if (elapsed >= sceneStart && elapsed < sceneStart + s.duration) {
            activeScene = s;
            sceneElapsed = elapsed - sceneStart;
            break;
          }
          sceneStart += s.duration;
        }

        // 1. Draw Background Gradient
        const bgGrad = ctx.createLinearGradient(0, 0, width, height);
        bgGrad.addColorStop(0, themeConfig.bg1);
        bgGrad.addColorStop(1, themeConfig.bg2);
        ctx.fillStyle = bgGrad;
        ctx.fillRect(0, 0, width, height);

        // 2. Cyberpunk Tech Grid Lines
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        ctx.lineWidth = 1;
        const gridSize = 40;
        const gridOffset = (elapsed * 20) % gridSize;
        for (let x = 0; x < width; x += gridSize) {
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, height);
          ctx.stroke();
        }
        for (let y = gridOffset; y < height; y += gridSize) {
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(width, y);
          ctx.stroke();
        }

        // 3. Animated Particles
        for (const p of particles) {
          p.x += p.vx;
          p.y += p.vy;
          if (p.x < 0) p.x = width;
          if (p.x > width) p.x = 0;
          if (p.y < 0) p.y = height;
          if (p.y > height) p.y = 0;

          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
          ctx.fillStyle = p.color;
          ctx.shadowColor = p.color;
          ctx.shadowBlur = 8;
          ctx.fill();
        }
        ctx.shadowBlur = 0;

        // 4. Central Glowing Card UI Mockup
        const cardWidth = Math.min(width * 0.85, 900);
        const cardHeight = Math.min(height * 0.65, 450);
        const cardX = (width - cardWidth) / 2;
        const cardY = (height - cardHeight) / 2;

        ctx.save();
        ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
        ctx.strokeStyle = activeScene.color || themeConfig.primary;
        ctx.lineWidth = 2;
        ctx.shadowColor = activeScene.accent || themeConfig.accent;
        ctx.shadowBlur = 20;

        ctx.beginPath();
        ctx.roundRect(cardX, cardY, cardWidth, cardHeight, 16);
        ctx.fill();
        ctx.stroke();
        ctx.restore();

        // 5. Card Header Window Bar
        ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
        ctx.beginPath();
        ctx.roundRect(cardX, cardY, cardWidth, 40, [16, 16, 0, 0]);
        ctx.fill();

        // Window Dot Buttons
        ['#ef4444', '#eab308', '#22c55e'].forEach((col, idx) => {
          ctx.beginPath();
          ctx.arc(cardX + 24 + idx * 16, cardY + 20, 5, 0, Math.PI * 2);
          ctx.fillStyle = col;
          ctx.fill();
        });

        // Window Title
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.font = '13px system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`AI Video Studio • Scene ${activeScene.id}/${scenes.length}`, cardX + cardWidth / 2, cardY + 25);

        // 6. Main Animated Scene Text
        ctx.textAlign = 'center';

        // Scene Title with Glow
        ctx.save();
        ctx.fillStyle = '#ffffff';
        ctx.shadowColor = activeScene.color;
        ctx.shadowBlur = 12;
        ctx.font = 'bold 32px system-ui, sans-serif';
        ctx.fillText(activeScene.title, width / 2, cardY + 120);
        ctx.restore();

        // Subtitle
        ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
        ctx.font = '18px system-ui, sans-serif';
        ctx.fillText(activeScene.subtitle, width / 2, cardY + 165);

        // 7. Visual Component Diagrams / Mockup in Center
        const boxY = cardY + 205;
        const boxW = (cardWidth - 80) / 3;
        const boxH = 110;

        ['Agent Orchestration', 'Full-Stack Engine', 'Instant Preview'].forEach((label, i) => {
          const bx = cardX + 30 + i * (boxW + 10);
          ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
          ctx.strokeStyle = i === (activeScene.id % 3) ? activeScene.accent : 'rgba(255, 255, 255, 0.1)';
          ctx.lineWidth = i === (activeScene.id % 3) ? 2 : 1;
          ctx.beginPath();
          ctx.roundRect(bx, boxY, boxW, boxH, 8);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = '#ffffff';
          ctx.font = '14px system-ui, sans-serif';
          ctx.fillText(label, bx + boxW / 2, boxY + 45);

          // Simulated mini status bar
          ctx.fillStyle = themeConfig.primary;
          ctx.fillRect(bx + 20, boxY + 70, (boxW - 40) * Math.min(1, sceneElapsed / activeScene.duration), 6);
        });

        // 8. Bottom Subtitle / Voiceover HUD
        const voiceoverText = activeScene.voiceover;
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.beginPath();
        ctx.roundRect(width * 0.1, height - 75, width * 0.8, 48, 8);
        ctx.fill();

        ctx.fillStyle = '#f8fafc';
        ctx.font = '15px system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`🎙 "${voiceoverText}"`, width / 2, height - 45);

        // 9. Timeline Progress Bar at bottom of screen
        ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.fillRect(0, height - 6, width, 6);
        ctx.fillStyle = themeConfig.accent;
        ctx.fillRect(0, height - 6, (elapsed / totalDuration) * width, 6);

        animationFrameRef.current = requestAnimationFrame(drawFrame);
      };

      animationFrameRef.current = requestAnimationFrame(drawFrame);
    });
  };

  const handleDownloadVideo = () => {
    if (!recordedVideoUrl) return;
    const a = document.createElement('a');
    a.href = recordedVideoUrl;
    a.download = `AI_Project_Video_${Date.now()}.webm`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="video-generator-studio">
      <div className="video-prompt-bar">
        <input
          type="text"
          value={videoPrompt}
          onChange={(e) => setVideoPrompt(e.target.value)}
          placeholder="Describe your video prompt..."
          className="video-prompt-input"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !isGenerating) {
              handleGenerateMotionVideo();
            }
          }}
        />
        <button
          onClick={handleGenerateMotionVideo}
          disabled={isGenerating}
          className="btn btn-primary btn-glow"
        >
          {isGenerating ? `Rendering (${progress}%)` : '🎬 Render AI Motion Video'}
        </button>
      </div>

      <div className="video-options-row">
        <div className="option-group">
          <span className="option-label">Theme:</span>
          <select
            value={selectedTheme}
            onChange={(e) => setSelectedTheme(e.target.value)}
            className="video-select"
          >
            {THEMES.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
        </div>

        <div className="option-group">
          <span className="option-label">Format:</span>
          <div className="pill-group">
            {(['16:9', '9:16', '1:1'] as const).map((ratio) => (
              <button
                key={ratio}
                type="button"
                onClick={() => setAspectRatio(ratio)}
                className={`pill-btn ${aspectRatio === ratio ? 'active' : ''}`}
              >
                {ratio === '16:9' ? '🖥 16:9 HD' : ratio === '9:16' ? '📱 9:16 Reel' : '⏹ 1:1'}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="preset-chips video-presets">
        <span className="preset-label">Sample Prompts:</span>
        {PRESET_VIDEO_PROMPTS.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setVideoPrompt(p)}
            className="preset-chip"
          >
            {p}
          </button>
        ))}
      </div>

      {error && <p className="alert alert-error">{error}</p>}

      {/* Hidden/Offscreen Canvas for Video Rendering */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Video Player Display */}
      {recordedVideoUrl && (
        <div className="video-player-card">
          <div className="video-player-header">
            <span className="video-badge">✅ AI Generated Motion Video (Ready)</span>
            <div className="video-player-actions">
              <button onClick={handleDownloadVideo} className="btn btn-sm btn-purple">
                ⬇ Download Video (.webm)
              </button>
              <button
                onClick={() => {
                  if (videoPlayerRef.current) {
                    if (videoPlayerRef.current.requestFullscreen) {
                      videoPlayerRef.current.requestFullscreen();
                    }
                  }
                }}
                className="btn btn-sm btn-ghost"
              >
                ⛶ Fullscreen
              </button>
            </div>
          </div>

          <div className="video-container">
            <video
              ref={videoPlayerRef}
              src={recordedVideoUrl}
              controls
              autoPlay
              loop
              className="rendered-video-element"
            />
          </div>
        </div>
      )}
    </div>
  );
};
