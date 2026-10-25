import { useEffect, useRef, useState, type ChangeEvent } from 'react';
import { useLanguage } from './LanguageContext';
import { LANG_NAMES, SPEECH_LOCALES, type LangCode } from './i18n';
import {
  analyzeProject,
  analyzeMultimodal,
  planSDLC as requestSDLCPlan,
  generateApprovedSDLC as generateFromApprovedDesign,
  getBackendStatus,
  buildProject,
  getProjectStatus,
  downloadProjectZipUrl,
  projectPreviewUrl,
  generateImage,
  explainProject,
  testProject,
  debugProject,
  getProjectSecurity,
  getProjectDeployment,
  projectFileUrl,
  createPremiumDesignPreview,
  premiumDesignPreviewUrl,
  acceptPremiumDesign,
  rejectPremiumDesign,
  type AnalyzeProjectResponse,
  type SDLCPlanResponse,
  type BuildProjectResponse,
  type ProjectStatusResponse,
  type GeneratedWebsite,
  type MultimodalAttachment,
  registerUser,
  loginUser,
  getAuthMe,
  getGeneratedWebsites,
  logoutUser,
  type AuthUser,
  type PremiumDesignPersonality,
  type PremiumDesignPreviewResponse,
  type PremiumDesignAcceptanceResponse,
} from './services/api';
import { AudioNarrator } from './components/AudioNarrator';
import { RequirementModal } from './components/RequirementModal';
import { VideoGenerator } from './components/VideoGenerator';
import { LiveWebsitePreview } from './components/LiveWebsitePreview';

type BackendStatus = {
  message: string;
  status: string;
  version: string;
};

type Attachment = {
  file: File;
  preview?: string;
};

type EditableProjectDetails = {
  projectName: string;
  domain: string;
  frontend: string;
  backend: string;
  database: string;
  authentication: boolean;
};

const LANG_OPTIONS = Object.entries(LANG_NAMES).map(([value, label]) => ({
  value: value as LangCode,
  label,
}));

const PREMIUM_DESIGN_STYLES: Array<{ value: PremiumDesignPersonality; label: string }> = [
  { value: 'auto', label: 'AI art direction' },
  { value: 'futuristic', label: 'Futuristic' },
  { value: 'luxury', label: 'Luxury' },
  { value: 'cinematic', label: 'Cinematic' },
  { value: 'creative', label: 'Creative' },
  { value: 'editorial', label: 'Editorial' },
  { value: 'organic', label: 'Organic' },
  { value: 'minimalist', label: 'Minimalist' },
  { value: 'glassmorphism', label: 'Glassmorphism' },
  { value: 'bold', label: 'Bold' },
];

function App() {
  const [status, setStatus] = useState<BackendStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [analysis, setAnalysis] = useState<AnalyzeProjectResponse | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [planningSDLC, setPlanningSDLC] = useState(false);
  const [sdlcPlan, setSdlcPlan] = useState<SDLCPlanResponse | null>(null);
  const [sdlcPrompt, setSdlcPrompt] = useState('');
  const [qualityRunInProgress, setQualityRunInProgress] = useState(false);
  const [maintenanceRequest, setMaintenanceRequest] = useState('');
  const [premiumDesignStyle, setPremiumDesignStyle] = useState<PremiumDesignPersonality>('auto');
  const [premiumDesignPreview, setPremiumDesignPreview] = useState<PremiumDesignPreviewResponse | null>(null);
  const [premiumDesignAccepted, setPremiumDesignAccepted] = useState<PremiumDesignAcceptanceResponse | null>(null);
  const [premiumDesignBusy, setPremiumDesignBusy] = useState(false);
  const [premiumDesignError, setPremiumDesignError] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [projectStatus, setProjectStatus] = useState<ProjectStatusResponse | null>(null);
  const [buildResult, setBuildResult] = useState<BuildProjectResponse | null>(null);
  const [building, setBuilding] = useState(false);
  const [buildMessage, setBuildMessage] = useState<string | null>(null);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [listening, setListening] = useState(false);

  // Active tab for result view
  const [activeResultTab, setActiveResultTab] = useState<'simulator' | 'code' | 'testing' | 'security' | 'deployment'>('simulator');

  // Agent flow progress (0-6)
  const [progressStep, setProgressStep] = useState(0);

  // Custom Requirement Modal state

  // Real Authentication System State
  const [authenticated, setAuthenticated] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [authUsername, setAuthUsername] = useState('');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authConfirmPassword, setAuthConfirmPassword] = useState('');
  const [authFullName, setAuthFullName] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authSuccessMsg, setAuthSuccessMsg] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [generatedWebsites, setGeneratedWebsites] = useState<GeneratedWebsite[]>([]);
  const [websitesLoading, setWebsitesLoading] = useState(false);
  const [websiteHistoryError, setWebsiteHistoryError] = useState<string | null>(null);
  const [previewingWebsiteSlug, setPreviewingWebsiteSlug] = useState<string | null>(null);
  const [websitePreviewError, setWebsitePreviewError] = useState<string | null>(null);

  const refreshGeneratedWebsites = async () => {
    try {
      const response = await getGeneratedWebsites();
      setGeneratedWebsites(response.projects);
      setWebsiteHistoryError(null);
    } catch (err) {
      setWebsiteHistoryError(err instanceof Error ? err.message : 'Unable to load your generated websites.');
    }
  };

  // Check persistent session on mount
  useEffect(() => {
    const token = localStorage.getItem('generator_auth_token');
    if (token) {
      getAuthMe(token)
        .then((res) => {
          if (res.user) {
            setCurrentUser(res.user);
            setAuthenticated(true);
          }
        })
        .catch(() => {
          localStorage.removeItem('generator_auth_token');
        });
    }
  }, []);

  useEffect(() => {
    if (!authenticated || !currentUser) {
      setGeneratedWebsites([]);
      setWebsitesLoading(false);
      return;
    }

    let cancelled = false;
    setWebsitesLoading(true);
    getGeneratedWebsites()
      .then((response) => {
        if (!cancelled) {
          setGeneratedWebsites(response.projects);
          setWebsiteHistoryError(null);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setWebsiteHistoryError(err instanceof Error ? err.message : 'Unable to load your generated websites.');
        }
      })
      .finally(() => {
        if (!cancelled) setWebsitesLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [authenticated, currentUser?.id]);

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    setAuthSuccessMsg(null);

    if (authMode === 'register') {
      if (!authUsername.trim()) {
        setAuthError('Please choose a username (at least 3 characters).');
        return;
      }
      if (!authEmail.trim() || !authEmail.includes('@')) {
        setAuthError('Please enter a valid email address.');
        return;
      }
      if (authPassword.length < 6) {
        setAuthError('Password must be at least 6 characters.');
        return;
      }
      if (authPassword !== authConfirmPassword) {
        setAuthError('Passwords do not match.');
        return;
      }

      setAuthLoading(true);
      try {
        const res = await registerUser(authUsername, authEmail, authPassword, authFullName);
        if (res.token) {
          localStorage.setItem('generator_auth_token', res.token);
          setCurrentUser(res.user);
          setAuthenticated(true);
        } else {
          setAuthSuccessMsg('Registration successful! Please sign in with your credentials.');
          setAuthMode('login');
        }
      } catch (err) {
        setAuthError(err instanceof Error ? err.message : 'Registration failed.');
      } finally {
        setAuthLoading(false);
      }
    } else {
      const loginIdent = authEmail.trim() || authUsername.trim();
      if (!loginIdent) {
        setAuthError('Please enter your email or username.');
        return;
      }
      if (!authPassword) {
        setAuthError('Please enter your password.');
        return;
      }

      setAuthLoading(true);
      try {
        const res = await loginUser(loginIdent, authPassword);
        if (res.token) {
          localStorage.setItem('generator_auth_token', res.token);
          setCurrentUser(res.user);
          setAuthenticated(true);
        }
      } catch (err) {
        setAuthError(err instanceof Error ? err.message : 'Invalid credentials. If you are new, please register first.');
      } finally {
        setAuthLoading(false);
      }
    }
  };

  const handleSignOut = async () => {
    await logoutUser();
    localStorage.removeItem('generator_auth_token');
    setCurrentUser(null);
    setAuthenticated(false);
    setGeneratedWebsites([]);
    setAuthSuccessMsg('Signed out successfully.');
  };

  const [editableProjectDetails, setEditableProjectDetails] = useState<EditableProjectDetails | null>(null);
  const [showProjectDetailsEditor, setShowProjectDetailsEditor] = useState(false);
  const [selectedGeneratedFile, setSelectedGeneratedFile] = useState<string | null>(null);
  const [generatedFileContent, setGeneratedFileContent] = useState('');
  const [copiedGeneratedFile, setCopiedGeneratedFile] = useState<string | null>(null);

  const [showRequirementModal, setShowRequirementModal] = useState(false);
  const [showAudioNarrator, setShowAudioNarrator] = useState(false);
  const [narrationText, setNarrationText] = useState('');
  const [narrationTitle, setNarrationTitle] = useState('');

  // Image Generation Panel
  const [imagePrompt, setImagePrompt] = useState('');
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [generatingImage, setGeneratingImage] = useState(false);
  const [imageError, setImageError] = useState<string | null>(null);
  const [showImagePanel, setShowImagePanel] = useState(false);

  // Video Generation Studio
  const [showVideoPanel, setShowVideoPanel] = useState(false);

  const recognitionRef = useRef<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { lang, setLang, t } = useLanguage();

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (analyzing) {
      setProgressStep(0);
      interval = setInterval(() => {
        setProgressStep((prev) => (prev < 6 ? prev + 1 : prev));
      }, 3000); // Flow to next agent every 3 seconds
    } else {
      if (analysis) {
        setProgressStep(7); // All complete
      } else {
        setProgressStep(0); // Reset on error
      }
    }
    return () => clearInterval(interval);
  }, [analyzing, analysis]);

  useEffect(() => {
    if (analysis) {
      setEditableProjectDetails({
        projectName: analysis.requirements.project_name,
        domain: analysis.requirements.domain || analysis.requirements.project_type,
        frontend: analysis.requirements.frontend,
        backend: analysis.requirements.backend,
        database: analysis.requirements.database,
        authentication: analysis.requirements.authentication,
      });
    }
  }, [analysis]);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await getBackendStatus();
        setStatus(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load backend status');
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
        recognitionRef.current = null;
      }
    };
  }, []);

  const applyAnalysisResult = async (result: AnalyzeProjectResponse) => {
    setAnalysis(result);
    setPremiumDesignPreview(null);
    setPremiumDesignAccepted(null);
    setPremiumDesignError(null);
    setBuildResult(null);
    setBuildMessage(null);
    setProjectStatus(null);
    setActiveResultTab('simulator');

    const pName = result.requirements.project_name || 'Web App';
    setNarrationTitle(pName);
    setNarrationText(
      result.narration_script ||
      `This is ${pName}, a ${result.requirements.project_type} created by the AI multi-agent generator. It includes ${result.requirements.modules.join(', ')}.`
    );

    const slug = result.generated_project?.project_slug;
    if (slug) {
      try {
        setProjectStatus(await getProjectStatus(slug));
      } catch {
        setProjectStatus(null);
      }
      await refreshGeneratedWebsites();
    }
  };

  const handlePlanSDLC = async (overridePrompt?: string) => {
    const targetPrompt = (overridePrompt || prompt).trim();
    if (!targetPrompt) {
      setAnalysisError(t('enterPrompt'));
      return;
    }

    setPlanningSDLC(true);
    setAnalysisError(null);
    setAnalysis(null);
    try {
      const plan = await requestSDLCPlan(targetPrompt, lang);
      setSdlcPrompt(targetPrompt);
      setSdlcPlan(plan);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : 'Unable to create the SRS and system design.');
    } finally {
      setPlanningSDLC(false);
    }
  };

  const handleApproveAndGenerate = async () => {
    if (!sdlcPlan) return;
    setAnalyzing(true);
    setAnalysisError(null);
    try {
      const result = await generateFromApprovedDesign(sdlcPrompt, lang, sdlcPlan);
      setSdlcPlan(null);
      await applyAnalysisResult(result);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : 'Unable to generate from the approved design.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleRetestAndHeal = async () => {
    const slug = analysis?.generated_project?.project_slug;
    if (!slug) return;
    setQualityRunInProgress(true);
    setAnalysisError(null);
    try {
      const result = await debugProject(slug);
      setAnalysis((current) => current
        ? { ...current, testing_report: result.testing_report, debug_report: result.debug_report }
        : current);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : 'Unable to run tests and self-healing.');
    } finally {
      setQualityRunInProgress(false);
    }
  };

  const handleAnalyze = async (overridePrompt?: string) => {
    const targetPrompt = (overridePrompt || prompt).trim();
    if (!targetPrompt) {
      setAnalysisError(t('enterPrompt'));
      return;
    }

    setAnalyzing(true);
    setAnalysisError(null);
    setAnalysis(null);
    setSdlcPlan(null);

    try {
      const result = await analyzeProject(targetPrompt, lang);
      await applyAnalysisResult(result);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : t('errorPrefix'));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleMaintenanceRequest = async () => {
    const change = maintenanceRequest.trim();
    if (!change) return;
    const updatedPrompt = `${prompt.trim()}\n\nMaintenance change request: ${change}`;
    setPrompt(updatedPrompt);
    setMaintenanceRequest('');
    await handlePlanSDLC(updatedPrompt);
  };

  const startVoice = () => {
    const SpeechRecognitionRef =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognitionRef) {
      setAnalysisError(
        'Voice input is not supported in this browser. Use Chrome or Edge on localhost, then allow microphone access.'
      );
      return;
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch {
        // ignore
      }
      recognitionRef.current = null;
      setListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognitionRef();
      recognition.lang = SPEECH_LOCALES[lang] || 'en-IN';
      recognition.interimResults = true;
      recognition.continuous = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setListening(true);
        setAnalysisError(null);
      };

      recognition.onresult = (event: any) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript + ' ';
          }
        }
        if (finalTranscript) {
          setPrompt((prev) => (prev.trim() ? `${prev.trim()} ${finalTranscript.trim()}` : finalTranscript.trim()));
        }
      };

      recognition.onerror = (event: any) => {
        const err = event.error || 'unknown';
        const messages: Record<string, string> = {
          'not-allowed': 'Microphone access was denied. Click the lock icon in the browser address bar and allow Microphone.',
          'service-not-allowed': 'The browser speech service is unavailable. Use Chrome or Edge while connected to the internet.',
          'audio-capture': 'No microphone was found. Connect a microphone and try again.',
          network: 'Speech recognition needs an internet connection. Check your connection and try again.',
          'no-speech': 'No speech was detected. Click Speak and say your requirement clearly.',
        };
        if (err !== 'aborted') {
          setAnalysisError(messages[err] || `Voice input could not start (${err}). Please try again.`);
        }
        setListening(false);
        recognitionRef.current = null;
      };

      recognition.onend = () => {
        setListening(false);
        recognitionRef.current = null;
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err: any) {
      setListening(false);
      recognitionRef.current = null;
      setAnalysisError(err?.message || 'Could not start voice microphone.');
    }
  };

  const handleExplainProjectVoice = async () => {
    const pPrompt = prompt.trim() || 'AI Multi-Agent Web Application Generator';
    const slug = analysis?.generated_project?.project_slug || undefined;

    try {
      const explainRes = await explainProject(pPrompt, slug, lang);
      setNarrationTitle(explainRes.project_name);
      setNarrationText(explainRes.narration_script);
      setShowAudioNarrator(true);
    } catch {
      setNarrationTitle(analysis?.requirements?.project_name || 'Project Overview');
      setNarrationText(
        analysis?.ollama_response ||
        'The AI Multi-Agent Web Application Generator autonomously analyzes requirements, plans full-stack architectures, and produces ready-to-run React and FastAPI code.'
      );
      setShowAudioNarrator(true);
    }
  };

  const handleFilesSelected = (event: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? []);
    if (files.length === 0) return;

    const added: Attachment[] = files.map((file) => {
      const previewable = file.type.startsWith('image/') || file.type.startsWith('video/');
      return {
        file,
        preview: previewable ? URL.createObjectURL(file) : undefined,
      };
    });

    setAttachments((prev) => [...prev, ...added]);
    event.target.value = '';
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => {
      const next = [...prev];
      const target = next[index];
      if (target?.preview) {
        URL.revokeObjectURL(target.preview);
      }
      next.splice(index, 1);
      return next;
    });
  };

  const handleMultimodalAnalyze = async () => {
    if (!prompt.trim() && attachments.length === 0) {
      setAnalysisError(t('addPromptFirst'));
      return;
    }

    setAnalyzing(true);
    setAnalysisError(null);
    setAnalysis(null);

    try {
      const result = await analyzeMultimodal(prompt.trim(), attachments.map((att) => att.file), lang);
      setAnalysis(result);
      setBuildResult(null);
      setBuildMessage(null);
      setProjectStatus(null);
      setActiveResultTab('simulator');

      const pName = result.requirements.project_name || 'Web App';
      setNarrationTitle(pName);
      if (result.narration_script) {
        setNarrationText(result.narration_script);
      }

      const slug = result.generated_project?.project_slug;
      if (slug) {
        try {
          setProjectStatus(await getProjectStatus(slug));
        } catch {
          setProjectStatus(null);
        }
        await refreshGeneratedWebsites();
      }
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : t('multimodalError'));
    } finally {
      setAnalyzing(false);
    }
  };

  const generatedProject = analysis?.generated_project;
  const projectSlug = generatedProject?.project_slug ?? null;
  const previewLink = projectSlug ? projectPreviewUrl(projectSlug) : null;

  const handlePremiumDesignPreview = async () => {
    if (!projectSlug) return;
    if (!projectStatus?.built) {
      setPremiumDesignError('Build the generated website before creating a visual comparison.');
      return;
    }
    setPremiumDesignBusy(true);
    setPremiumDesignError(null);
    setPremiumDesignAccepted(null);
    try {
      if (premiumDesignPreview) {
        await rejectPremiumDesign(premiumDesignPreview.project_slug, premiumDesignPreview.preview_id);
        setPremiumDesignPreview(null);
      }
      const artPrompt = prompt.trim() || [
        analysis?.requirements.project_name,
        analysis?.requirements.domain,
        ...(analysis?.requirements.modules || []),
      ].filter(Boolean).join(' ');
      const result = await createPremiumDesignPreview(projectSlug, artPrompt, premiumDesignStyle);
      setPremiumDesignPreview(result);
    } catch (err) {
      setPremiumDesignError(err instanceof Error ? err.message : 'Unable to create the premium design preview.');
    } finally {
      setPremiumDesignBusy(false);
    }
  };

  const handleAcceptPremiumDesign = async () => {
    if (!premiumDesignPreview) return;
    setPremiumDesignBusy(true);
    setPremiumDesignError(null);
    try {
      const result = await acceptPremiumDesign(premiumDesignPreview.project_slug, premiumDesignPreview.preview_id);
      setPremiumDesignAccepted(result);
      setPremiumDesignPreview(null);
      setProjectStatus(await getProjectStatus(result.project_slug));
    } catch (err) {
      setPremiumDesignError(err instanceof Error ? err.message : 'Unable to apply the premium design.');
    } finally {
      setPremiumDesignBusy(false);
    }
  };

  const handleRejectPremiumDesign = async () => {
    if (!premiumDesignPreview) return;
    setPremiumDesignBusy(true);
    setPremiumDesignError(null);
    try {
      await rejectPremiumDesign(premiumDesignPreview.project_slug, premiumDesignPreview.preview_id);
      setPremiumDesignPreview(null);
    } catch (err) {
      setPremiumDesignError(err instanceof Error ? err.message : 'Unable to discard the premium design preview.');
    } finally {
      setPremiumDesignBusy(false);
    }
  };

  const handleBuild = async () => {
    if (!projectSlug) return;
    setBuilding(true);
    setBuildMessage('Installing dependencies and building the frontend...');
    setBuildResult(null);
    try {
      const result = await buildProject(projectSlug, setBuildMessage);
      setBuildResult(result);
      setBuildMessage(
        result.built
          ? t('buildSuccess')
          : t('buildFailed')
      );
      try {
        setProjectStatus(await getProjectStatus(projectSlug));
      } catch {
        setProjectStatus(null);
      }
    } catch (err) {
      setBuildMessage(err instanceof Error ? err.message : t('buildError'));
    } finally {
      setBuilding(false);
    }
  };

  const handleDownload = () => {
    if (!projectSlug) return;
    window.open(downloadProjectZipUrl(projectSlug), '_blank');
  };

  const generatedFilePath = (file: string) => {
    const prefix = projectSlug ? `generated_projects/${projectSlug}/` : '';
    return file.startsWith(prefix) ? file.slice(prefix.length) : file;
  };

  const viewGeneratedFile = async (file: string) => {
    if (!projectSlug) return;
    const path = generatedFilePath(file);
    try {
      const response = await fetch(projectFileUrl(projectSlug, path));
      if (!response.ok) throw new Error('Unable to read generated file');
      setSelectedGeneratedFile(file);
      setGeneratedFileContent(await response.text());
    } catch (err) {
      setBuildMessage(err instanceof Error ? err.message : 'Unable to read generated file');
    }
  };

  const copyGeneratedFile = async (file: string) => {
    if (!projectSlug) return;
    const path = generatedFilePath(file);
    try {
      const response = await fetch(projectFileUrl(projectSlug, path));
      if (!response.ok) throw new Error('Unable to copy generated file');
      await navigator.clipboard.writeText(await response.text());
      setCopiedGeneratedFile(file);
      window.setTimeout(() => setCopiedGeneratedFile(null), 1800);
    } catch (err) {
      setBuildMessage(err instanceof Error ? err.message : 'Unable to copy generated file');
    }
  };

  const saveGeneratedFile = (file: string) => {
    if (!projectSlug) return;
    const link = document.createElement('a');
    link.href = projectFileUrl(projectSlug, generatedFilePath(file));
    link.download = generatedFilePath(file).split('/').pop() || 'generated-file';
    link.click();
  };

  const handlePreview = () => {
    if (previewLink) {
      window.open(previewLink, '_blank');
    }
  };

  const handleOpenGeneratedWebsite = async (website: GeneratedWebsite) => {
    const previewWindow = window.open('', '_blank');
    if (!previewWindow) {
      setWebsitePreviewError('Allow pop-ups for this site to open the generated website preview.');
      return;
    }

    previewWindow.document.title = `Preparing ${website.project_name}`;
    previewWindow.document.body.innerText = 'Installing dependencies and preparing your website preview…';
    setPreviewingWebsiteSlug(website.project_slug);
    setWebsitePreviewError(null);

    try {
      const project = await getProjectStatus(website.project_slug);
      if (!project.built) {
        const build = await buildProject(website.project_slug, (phase) => {
          if (!previewWindow.closed) previewWindow.document.body.innerText = phase;
        });
        if (!build.built || !build.build_success) {
          const details = build.build_log || build.install_log;
          throw new Error(details ? `Build failed: ${details}` : 'Build failed. Check the project build logs and try again.');
        }
      }

      setGeneratedWebsites((current) =>
        current.map((item) => item.project_slug === website.project_slug ? { ...item, built: true } : item)
      );
      previewWindow.location.replace(projectPreviewUrl(website.project_slug));
    } catch (err) {
      previewWindow.close();
      setWebsitePreviewError(
        `${website.project_name}: ${err instanceof Error ? err.message : 'Unable to build or open the website preview.'}`
      );
    } finally {
      setPreviewingWebsiteSlug(null);
    }
  };

  const handleGenerateImage = async () => {
    if (!imagePrompt.trim()) {
      setImageError('Please enter an image description.');
      return;
    }

    setGeneratingImage(true);
    setImageError(null);
    setGeneratedImage(null);

    try {
      const result = await generateImage(imagePrompt.trim());
      const url = new URL(result.image_url);
      url.searchParams.set('t', Date.now().toString());
      setGeneratedImage(url.toString());
    } catch (err) {
      setImageError(err instanceof Error ? err.message : 'Failed to generate image');
    } finally {
      setGeneratingImage(false);
    }
  };

  return (<>
    {!authenticated && (
      <div className="login-screen">
        <div className="login-ambient ambient-one" />
        <div className="login-ambient ambient-two" />
        <div className="login-layout">
          <section className="login-showcase" aria-label="AI agent collaboration">
            <div className="brand-lockup">
              <div className="brand-mark"><span>✦</span></div>
              <span>Autonomous Multi-Agent AI<br /><span className="brand-mark-accent">Web App Generator</span></span>
            </div>
            <div className="showcase-copy">
              <p className="eyebrow"><span className="eyebrow-dot" /> Autonomous build intelligence</p>
              <h1>Ideas in.<br /><span>Production out.</span></h1>
              <p className="showcase-description">A coordinated team of AI agents turns your product vision into a tested, deployable web experience.</p>
            </div>

            <div className="agent-network">
              <div className="network-halo halo-outer" />
              <div className="network-halo halo-inner" />
              <div className="network-grid" />
              <span className="connection connection-a" />
              <span className="connection connection-b" />
              <span className="connection connection-c" />
              <span className="connection connection-d" />
              <span className="connection connection-e" />
              <div className="agent-node node-architect"><span>⌘</span><small>Architect</small></div>
              <div className="agent-node node-builder"><span>⌁</span><small>Builder</small></div>
              <div className="agent-node node-qa"><span>✓</span><small>QA Agent</small></div>
              <div className="agent-node node-security"><span>◈</span><small>Security</small></div>
              <div className="core-node"><div className="core-pulse" /><span>✦</span><small>ORCHESTRATOR</small></div>
            </div>

            <div className="showcase-footer">
              <div><strong>09</strong><span>specialist agents</span></div>
              <div><strong>24/7</strong><span>always building</span></div>
              <div className="live-signal"><span /> Systems operational</div>
            </div>
          </section>

          <section className="login-panel">
            <div className="login-panel-inner">
              <div className="login-heading">
                <div className="mobile-brand-mark brand-mark"><span>✦</span></div>
                <p className="login-kicker">{authMode === 'login' ? 'Welcome back' : 'New User Onboarding'}</p>
                <h2>{authMode === 'login' ? 'Enter the command center' : 'Create your account'}</h2>
                <p className="login-subtitle">
                  {authMode === 'login'
                    ? 'Sign in to access and orchestrate multi-agent web applications.'
                    : 'Register your account to generate and run autonomous projects.'}
                </p>
              </div>

              {/* Toggle tabs: Sign In vs Register */}
              <div className="auth-toggle-bar">
                <button
                  type="button"
                  className={`auth-tab-btn ${authMode === 'login' ? 'active' : ''}`}
                  onClick={() => { setAuthMode('login'); setAuthError(null); setAuthSuccessMsg(null); }}
                >
                  Sign In
                </button>
                <button
                  type="button"
                  className={`auth-tab-btn ${authMode === 'register' ? 'active' : ''}`}
                  onClick={() => { setAuthMode('register'); setAuthError(null); setAuthSuccessMsg(null); }}
                >
                  Register (New User)
                </button>
              </div>

              {authError && (
                <div className="auth-alert-box auth-alert-error">
                  <span>⚠</span> {authError}
                </div>
              )}

              {authSuccessMsg && (
                <div className="auth-alert-box auth-alert-success">
                  <span>✓</span> {authSuccessMsg}
                </div>
              )}

              <form className="login-form" onSubmit={handleAuthSubmit}>
                {authMode === 'register' ? (
                  <>
                    <label className="login-field">
                      <span>Full Name</span>
                      <input
                        type="text"
                        placeholder="e.g. John Doe"
                        className="login-input"
                        value={authFullName}
                        onChange={(e) => setAuthFullName(e.target.value)}
                      />
                    </label>
                    <label className="login-field">
                      <span>Username *</span>
                      <input
                        type="text"
                        required
                        placeholder="Choose unique username"
                        className="login-input"
                        value={authUsername}
                        onChange={(e) => setAuthUsername(e.target.value)}
                      />
                    </label>
                    <label className="login-field">
                      <span>Email address *</span>
                      <input
                        type="email"
                        required
                        placeholder="you@company.com"
                        className="login-input"
                        value={authEmail}
                        onChange={(e) => setAuthEmail(e.target.value)}
                      />
                    </label>
                    <label className="login-field">
                      <span>Password (min. 6 characters) *</span>
                      <input
                        type="password"
                        required
                        placeholder="Create strong password"
                        className="login-input"
                        value={authPassword}
                        onChange={(e) => setAuthPassword(e.target.value)}
                      />
                    </label>
                    <label className="login-field">
                      <span>Confirm Password *</span>
                      <input
                        type="password"
                        required
                        placeholder="Repeat your password"
                        className="login-input"
                        value={authConfirmPassword}
                        onChange={(e) => setAuthConfirmPassword(e.target.value)}
                      />
                    </label>
                    <button type="submit" className="btn btn-primary btn-login" disabled={authLoading}>
                      <span>{authLoading ? 'Creating Account…' : 'Register & Enter Workspace'}</span>
                      <span className="button-arrow">↗</span>
                    </button>
                    <p className="auth-switch-prompt">
                      Already have an account?
                      <button
                        type="button"
                        className="auth-switch-link"
                        onClick={() => { setAuthMode('login'); setAuthError(null); }}
                      >
                        Sign In here
                      </button>
                    </p>
                  </>
                ) : (
                  <>
                    <label className="login-field">
                      <span>Email or Username</span>
                      <input
                        type="text"
                        required
                        placeholder="you@company.com or username"
                        className="login-input"
                        value={authEmail}
                        onChange={(e) => setAuthEmail(e.target.value)}
                      />
                    </label>
                    <label className="login-field">
                      <span>Password</span>
                      <input
                        type="password"
                        required
                        placeholder="Enter your password"
                        className="login-input"
                        value={authPassword}
                        onChange={(e) => setAuthPassword(e.target.value)}
                      />
                    </label>
                    <button type="submit" className="btn btn-primary btn-login" disabled={authLoading}>
                      <span>{authLoading ? 'Signing in…' : 'Launch workspace'}</span>
                      <span className="button-arrow">↗</span>
                    </button>
                    <p className="auth-switch-prompt">
                      New user?
                      <button
                        type="button"
                        className="auth-switch-link"
                        onClick={() => { setAuthMode('register'); setAuthError(null); }}
                      >
                        Register first to create account
                      </button>
                    </p>
                  </>
                )}
              </form>
              <div className="login-divider"><span>secure access</span></div>
              <p className="login-trust"><span className="lock-icon">⌑</span> Your workspace is protected with SQLite-backed hashed authentication.</p>
              <p className="login-legal">By continuing, you agree to our <a href="#terms">Terms of Service</a> and <a href="#privacy">Privacy Policy</a>.</p>
            </div>
          </section>
        </div>
      </div>
    )}
    {authenticated && (
    <main className="app-shell">
      {/* Hero Header */}
      <header className="hero">
        <span className="hero-badge">{t('badge')}</span>
        <h1 className="hero-title">{t('title')}</h1>
        <p className="hero-subtitle">{t('heroSubtitle')}</p>

        <div className="status-pill-wrap">
          {loading && <span className="status-pill loading">Checking backend…</span>}
          {error && <span className="status-pill error">⚠ {error}</span>}
          {status && (
            <span className="status-pill ok">
              ● {status.status === 'success' ? t('backendOnline') : status.status} · v{status.version}
            </span>
          )}
          {currentUser && (
            <div className="auth-user-bar">
              <div className="auth-user-avatar">
                {(currentUser.full_name || currentUser.username || 'U')[0].toUpperCase()}
              </div>
              <div className="auth-user-info">
                <span className="auth-user-name">{currentUser.full_name || currentUser.username}</span>
                <span className="auth-user-email">{currentUser.email}</span>
              </div>
              <button type="button" onClick={handleSignOut} className="btn-signout" title="Sign out of workspace">
                Sign Out
              </button>
            </div>
          )}
        </div>
      </header>

        <div className="lang-row">
          <label className="lang-label" htmlFor="lang-select">{t('outputLanguage')}</label>
          <select
            id="lang-select"
            value={lang}
            onChange={(e) => setLang(e.target.value as LangCode)}
            className="lang-select"
          >
            {LANG_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        <textarea
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder={t("promptPlaceholder")}
          rows={5}
          className="prompt-input"
        />

        {/* Toolbar with Voice, Attachment, and Custom Requirement */}
        <div className="multimodal-toolbar">
          <button
            type="button"
            onClick={(event) => {
              event.preventDefault();
              event.stopPropagation();
              startVoice();
            }}
            className={`btn btn-voice ${listening ? 'listening-pulse' : ''}`}
            title="Click to speak and transcribe requirements into text"
          >
            {listening ? t('listening') : '🎙 ' + t('speak')}
          </button>

          <button
            type="button"
            onClick={() => setShowRequirementModal(true)}
            className="btn btn-secondary"
            title="Open Custom Requirement dialog to add or iterate features"
          >
            ➕ {t('customRequirement')}
          </button>

          <button
            type="button"
            className="btn btn-attach"
            onClick={() => fileInputRef.current?.click()}
          >
            {t('attachFiles')}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,video/*,audio/*,.pdf,.docx,.txt,.md,.json,.csv,.py,.js,.ts,.tsx,.html,.css"
            onChange={handleFilesSelected}
            hidden
          />
        </div>

        {attachments.length > 0 && (
          <div className="attachment-row">
            {attachments.map((att, index) => (
              <div className="attachment-chip" key={`${att.file.name}-${index}`}>
                {att.preview ? (
                  <img className="attachment-thumb" src={att.preview} alt={att.file.name} />
                ) : (
                  <span className="attachment-icon">📄</span>
                )}
                <span className="attachment-name" title={att.file.name}>
                  {att.file.name}
                </span>
                <button
                  type="button"
                  className="attachment-remove"
                  onClick={() => removeAttachment(index)}
                  aria-label={`Remove ${att.file.name}`}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="row">
          <button onClick={() => handleAnalyze()} disabled={analyzing} className="btn btn-primary btn-lg btn-glow">
            {analyzing ? t('generating') : t('generateText')}
          </button>
          <button
            type="button"
            onClick={() => handlePlanSDLC()}
            disabled={analyzing || planningSDLC}
            className="btn btn-secondary btn-lg"
          >
            {planningSDLC ? t('preparingSDLC') : `🧭 ${t('planSDLC')}`}
          </button>
          <button
            onClick={handleMultimodalAnalyze}
            disabled={analyzing}
            className="btn btn-secondary btn-lg"
            title="Generate using your text/voice plus any attached files"
          >
            {analyzing ? t('generating') : t('generateMultimodal')}
          </button>
          <span className="hint">{t('hint')}</span>
        </div>

        {analysisError && <p className="alert alert-error">{analysisError}</p>}

        {sdlcPlan && (
          <section className="card inner" aria-labelledby="sdlc-review-heading">
            <div className="card-title-row">
              <div>
                <h2 className="card-title" id="sdlc-review-heading">🧭 AI SDLC — Review before generation</h2>
                <p className="project-details-hint">Review this SRS and technical design. Application generation remains paused until you approve it.</p>
              </div>
            </div>
            <div className="result-grid">
              <div className="stat"><span className="stat-label">Project</span><span className="stat-value">{sdlcPlan.srs.project_name}</span></div>
              <div className="stat"><span className="stat-label">Purpose</span><span className="stat-value">{sdlcPlan.srs.purpose}</span></div>
            </div>
            <div className="sdlc-review-grid">
              {([
                ['Scope', sdlcPlan.srs.scope],
                ['Stakeholders / roles', sdlcPlan.srs.stakeholders],
                ['Functional requirements', sdlcPlan.srs.functional_requirements],
                ['Non-functional requirements', sdlcPlan.srs.non_functional_requirements],
                ['Data requirements', sdlcPlan.srs.data_requirements],
                ['Acceptance criteria', sdlcPlan.srs.acceptance_criteria],
              ] as const).map(([heading, items]) => (
                <section className="card inner" key={heading}>
                  <h3 className="card-title">{heading}</h3>
                  {items.length ? (
                    <ul>{items.map((item, index) => <li key={`${heading}-${index}`}>{item}</li>)}</ul>
                  ) : <p className="project-details-hint">No items identified.</p>}
                </section>
              ))}
            </div>

            <section className="card inner">
              <h3 className="card-title">🏗 System architecture</h3>
              <p>{sdlcPlan.project_plan.system_architecture}</p>
              <div className="sdlc-review-grid">
                {([
                  ['Frontend', sdlcPlan.project_plan.frontend_architecture],
                  ['Backend', sdlcPlan.project_plan.backend_architecture],
                  ['Database design', sdlcPlan.project_plan.database_architecture],
                ] as const).map(([heading, items]) => (
                  <div key={heading}>
                    <h4>{heading}</h4>
                    <ul>{(items || []).map((item, index) => <li key={`${heading}-${index}`}>{item}</li>)}</ul>
                  </div>
                ))}
              </div>
            </section>

            <section className="card inner">
              <h3 className="card-title">🗄 Database schema</h3>
              <p>{sdlcPlan.database_blueprint.database_type}</p>
              {sdlcPlan.database_blueprint.table_details?.map((table) => (
                <div className="deploy-artifact-card" key={table.name}>
                  <strong>{table.name}</strong> <span className="project-details-hint">({table.model_name})</span>
                  <ul>{table.columns.map((column) => (
                    <li key={column.name}>
                      {column.name}: {column.data_type}
                      {column.primary_key ? ' · primary key' : ''}
                      {column.unique ? ' · unique' : ''}
                      {!column.nullable ? ' · required' : ''}
                    </li>
                  ))}</ul>
                  {table.foreign_keys.length > 0 && <p>Relations: {table.foreign_keys.join(', ')}</p>}
                </div>
              ))}
              <p>Relationships: {(sdlcPlan.database_blueprint.relationships || []).join(' · ')}</p>
              <p>Indexes: {(sdlcPlan.database_blueprint.indexes || []).join(' · ')}</p>
            </section>

            <section className="card inner">
              <h3 className="card-title">🔌 API plan</h3>
              {sdlcPlan.backend_blueprint.endpoints?.map((endpoint, index) => (
                <div className="deploy-artifact-card" key={`${endpoint.method}-${endpoint.path}-${index}`}>
                  <strong>{endpoint.method} {endpoint.path}</strong>
                  <p>{endpoint.description}</p>
                  <span className="project-details-hint">
                    Request: {endpoint.request_schema || 'none'} · Response: {endpoint.response_schema}
                  </span>
                </div>
              ))}
            </section>

            <div className="btn-row">
              <button type="button" className="btn btn-primary btn-lg" onClick={handleApproveAndGenerate} disabled={analyzing}>
                {analyzing ? 'Generating approved design…' : '✓ Approve design & generate application'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setSdlcPlan(null)} disabled={analyzing}>
                Discard plan
              </button>
            </div>
          </section>
        )}

        <h3 className="card-title" style={{ marginTop: '32px', marginBottom: '16px' }}>🤖 Autonomous Agent Workflow</h3>
        <div className={`agent-pipeline-grid`}>
          <div className={`agent-card ${analyzing && progressStep === 0 ? 'processing' : ''}`}>
            <div className="agent-card-header">
              <span className="agent-card-num">Step 2</span>
              {progressStep > 0 && <span className="agent-status-tag completed">✓ Complete</span>}
            </div>
            <h4 className="agent-card-title">📋 Requirement Agent</h4>
            <p className="agent-card-desc">Analyze and extract requirements from natural language input.</p>
          </div>

          <div className={`agent-card ${analyzing && progressStep === 1 ? 'processing' : ''}`}>
            <div className="agent-card-header">
              <span className="agent-card-num">Step 3</span>
              {progressStep > 1 && <span className="agent-status-tag completed">✓ Complete</span>}
            </div>
            <h4 className="agent-card-title">📐 Design Agent</h4>
            <p className="agent-card-desc">Create system design and UI/UX architecture flows.</p>
          </div>

          <div className={`agent-card ${analyzing && progressStep === 2 ? 'processing' : ''}`}>
            <div className="agent-card-header">
              <span className="agent-card-num">Step 4</span>
              {progressStep > 2 && <span className="agent-status-tag completed">✓ Complete</span>}
            </div>
            <h4 className="agent-card-title">💻 Code Agent</h4>
            <p className="agent-card-desc">Generate application code and full-stack structure.</p>
          </div>

          <div className={`agent-card ${analyzing && progressStep === 3 ? 'processing' : ''}`}>
            <div className="agent-card-header">
              <span className="agent-card-num">Step 5</span>
              {progressStep > 3 && <span className="agent-status-tag completed">✓ Complete</span>}
            </div>
            <h4 className="agent-card-title">🧪 Testing Agent</h4>
            <p className="agent-card-desc">Run automated tests and validate system functionality.</p>
          </div>

          <div className={`agent-card ${analyzing && progressStep === 4 ? 'processing' : ''}`}>
            <div className="agent-card-header">
              <span className="agent-card-num">Step 6</span>
              {progressStep > 4 && <span className="agent-status-tag completed">✓ Complete</span>}
            </div>
            <h4 className="agent-card-title">🩺 Debug Agent</h4>
            <p className="agent-card-desc">Identify underlying issues, diagnose errors, and fix bugs.</p>
          </div>

          <div className={`agent-card ${analyzing && progressStep === 5 ? 'processing' : ''}`}>
            <div className="agent-card-header">
              <span className="agent-card-num">Step 7</span>
              {progressStep > 5 && <span className="agent-status-tag completed">✓ Complete</span>}
            </div>
            <h4 className="agent-card-title">🛡 Security Agent</h4>
            <p className="agent-card-desc">Check for vulnerabilities and ensure comprehensive security.</p>
          </div>

          <div className={`agent-card ${analyzing && progressStep === 6 ? 'processing' : ''}`}>
            <div className="agent-card-header">
              <span className="agent-card-num">Step 8</span>
              {progressStep > 6 && <span className="agent-status-tag completed">✓ Complete</span>}
            </div>
            <h4 className="agent-card-title">🚀 Deployment Agent</h4>
            <p className="agent-card-desc">Prepare artifacts and deploy the generated application.</p>
          </div>
        </div>

        {/* Results Area */}
        {analysis && (
          <div className="results">
            {/* Primary Stats Grid */}
            <div className="project-details-heading">
              <div>
                <p className="project-details-eyebrow">Project configuration</p>
                <p className="project-details-hint">Customize these details before exploring your generated workspace.</p>
              </div>
              <button type="button" className="btn btn-sm btn-secondary" onClick={() => setShowProjectDetailsEditor(true)}>
                ✏️ Edit details
              </button>
            </div>
            <div className="result-grid">
              <div className="stat"><span className="stat-label">Project Name</span><span className="stat-value">{editableProjectDetails?.projectName || analysis.requirements.project_name}</span></div>
              <div className="stat"><span className="stat-label">Domain</span><span className="stat-value">{editableProjectDetails?.domain || analysis.requirements.domain || analysis.requirements.project_type}</span></div>
              <div className="stat"><span className="stat-label">Frontend</span><span className="stat-value">{editableProjectDetails?.frontend || analysis.requirements.frontend}</span></div>
              <div className="stat"><span className="stat-label">Backend</span><span className="stat-value">{editableProjectDetails?.backend || analysis.requirements.backend}</span></div>
              <div className="stat"><span className="stat-label">Database</span><span className="stat-value">{editableProjectDetails?.database || analysis.requirements.database}</span></div>
              <div className="stat"><span className="stat-label">Authentication</span><span className="stat-value">{(editableProjectDetails?.authentication ?? analysis.requirements.authentication) ? t('yes') : t('no')}</span></div>
            </div>

            <div className="chip-row">
              <span className="chip-label">Modules:</span>
              {analysis.requirements.modules.length > 0 ? (
                analysis.requirements.modules.map((m) => <span key={m} className="chip">{m}</span>)
              ) : (
                <span className="stat-value">None</span>
              )}
            </div>

            {analysis.requirements.validation_errors.length > 0 && (
              <p className="alert alert-error">
                <strong>Validation errors:</strong> {analysis.requirements.validation_errors.join(', ')}
              </p>
            )}

            {/* AI Architectural Summary */}
            <section className="card inner" style={{ marginBottom: '20px' }}>
              <div className="card-title-row">
                <h3 className="card-title">✨ AI Architectural Summary</h3>
                <button
                  type="button"
                  onClick={() => {
                    setNarrationTitle(analysis.requirements.project_name || 'Project Overview');
                    const fallback = `This is ${analysis.requirements.project_name || 'a project'}, a ${analysis.requirements.project_type || 'web application'}.`;
                    setNarrationText(analysis.narration_script || analysis.ollama_response || fallback);
                    setShowAudioNarrator(true);
                  }}
                  className="btn btn-voice-play btn-sm"
                >
                  🔊 Narrate
                </button>
              </div>
              <div className="ai-summary">
                {analysis.ollama_response ? analysis.ollama_response : t('noAiResponse')}
              </div>
              {showAudioNarrator && (
                <AudioNarrator
                  textToSpeak={narrationText}
                  projectName={narrationTitle}
                  onClose={() => setShowAudioNarrator(false)}
                />
              )}
            </section>

            {/* Navigation Tabs for Generated Views */}
            <div className="tab-row" style={{ display: 'flex', gap: '8px', margin: '20px 0 12px', flexWrap: 'wrap' }}>
              <button
                type="button"
                onClick={() => setActiveResultTab('simulator')}
                className={`btn btn-sm ${activeResultTab === 'simulator' ? 'btn-primary' : 'btn-secondary'}`}
              >
                🌐 Live Simulator
              </button>
              <button
                type="button"
                onClick={() => setActiveResultTab('code')}
                className={`btn btn-sm ${activeResultTab === 'code' ? 'btn-primary' : 'btn-secondary'}`}
              >
                🛠 Full-Stack Code &amp; Build
              </button>
              <button
                type="button"
                onClick={() => setActiveResultTab('testing')}
                className={`btn btn-sm ${activeResultTab === 'testing' ? 'btn-primary' : 'btn-secondary'}`}
              >
                🧪 Automated Testing ({analysis.testing_report?.passed_count ?? 0} Passed)
              </button>
              <button
                type="button"
                onClick={() => setActiveResultTab('security')}
                className={`btn btn-sm ${activeResultTab === 'security' ? 'btn-primary' : 'btn-secondary'}`}
              >
                🛡 Security Audit ({analysis.security_report?.score ?? 100}/100)
              </button>
              <button
                type="button"
                onClick={() => setActiveResultTab('deployment')}
                className={`btn btn-sm ${activeResultTab === 'deployment' ? 'btn-primary' : 'btn-secondary'}`}
              >
                🚀 Deployment Package
              </button>
            </div>

            {/* TAB 2: Live Simulator */}
            {activeResultTab === 'simulator' && (
              <section className="card inner">
                <div className="card-title-row">
                  <h3 className="card-title">🌐 Live Interactive Website Simulator</h3>
                  <button
                    type="button"
                    onClick={() => setShowRequirementModal(true)}
                    className="btn btn-sm btn-secondary"
                  >
                    ➕ Modify Requirements
                  </button>
                </div>

                <LiveWebsitePreview
                  projectName={analysis.requirements.project_name || 'Web App'}
                  projectType={analysis.requirements.project_type || 'Full-Stack Application'}
                  modules={analysis.requirements.modules || []}
                  backend={analysis.requirements.backend || 'FastAPI'}
                  database={analysis.requirements.database || 'PostgreSQL'}
                  previewUrl={previewLink}
                  onOpenPreview={handlePreview}
                />
              </section>
            )}

            {/* TAB 3: Code & Build */}
            {activeResultTab === 'code' && (
              <section className="card inner">
                <h3 className="card-title">🛠 Generated Full-Stack Codebase</h3>

                {generatedProject?.error ? (
                  <p className="alert alert-error"><strong>Project generation failed:</strong> {generatedProject.error}</p>
                ) : (
                  <>
                    <div className="result-grid">
                      <div className="stat"><span className="stat-label">Project folder</span><span className="stat-value">{generatedProject?.project_path ? `backend/${generatedProject.project_path}` : 'backend/generated_projects'}</span></div>
                      <div className="stat"><span className="stat-label">Files created</span><span className="stat-value">{generatedProject?.files_count ?? 0}</span></div>
                      <div className="stat"><span className="stat-label">Status</span>
                        <span className="stat-value">
                          {projectStatus?.built
                            ? t('builtReady')
                            : projectStatus?.frontend
                            ? t('notBuilt')
                            : t('generated')}
                        </span>
                      </div>
                    </div>

                    <div className="btn-row">
                      <button
                        onClick={handleBuild}
                        disabled={building || !projectSlug}
                        className="btn btn-green"
                      >
                        {building ? t('building') : t('buildPreview')}
                      </button>

                      {projectStatus?.built && (
                        <button onClick={handlePreview} className="btn btn-blue">▶ Open Built Preview</button>
                      )}

                      <button onClick={handleDownload} disabled={!projectSlug} className="btn btn-purple">
                        ⬇ Download ZIP (VS Code Folder)
                      </button>
                    </div>

                    {buildMessage && (
                      <div className="alert alert-info"><strong>{buildMessage}</strong></div>
                    )}

                    {buildResult?.build_success && (
                      <p className="alert alert-success">
                        ✅ Your website is live. Click{' '}
                        <a href={previewLink ?? '#'} target="_blank" rel="noreferrer">Open Built Preview</a>{' '}
                        to view it in a new browser tab.
                      </p>
                    )}

                    {buildResult && (
                      <details className="log-block">
                        <summary>Build logs</summary>
                        <pre className="log-pre">
                          {buildResult.install_log || 'No install log'}
                          {'\n\n--- BUILD ---\n\n'}
                          {buildResult.build_log || 'No build log'}
                        </pre>
                      </details>
                    )}

                    <section className="premium-design-panel" aria-labelledby="premium-design-heading">
                      <div className="premium-design-heading">
                        <div>
                          <p className="project-details-eyebrow">CSS-only visual upgrade</p>
                          <h3 id="premium-design-heading">✨ Upgrade to Premium Design</h3>
                          <p className="project-details-hint">
                            Preview an art-directed visual layer before applying it. App source, data, forms, authentication, and API behavior are left untouched.
                          </p>
                        </div>
                        <div className="premium-design-controls">
                          <label htmlFor="premium-design-style">Visual personality</label>
                          <select
                            id="premium-design-style"
                            value={premiumDesignStyle}
                            onChange={(event) => setPremiumDesignStyle(event.target.value as PremiumDesignPersonality)}
                            disabled={premiumDesignBusy}
                          >
                            {PREMIUM_DESIGN_STYLES.map((style) => (
                              <option value={style.value} key={style.value}>{style.label}</option>
                            ))}
                          </select>
                          <button
                            type="button"
                            className="btn btn-primary"
                            onClick={handlePremiumDesignPreview}
                            disabled={premiumDesignBusy || building || !projectStatus?.built || !projectSlug}
                          >
                            {premiumDesignBusy ? 'Preparing…' : 'Create visual comparison'}
                          </button>
                        </div>
                      </div>

                      {!projectStatus?.built && (
                        <p className="project-details-hint">
                          Build the website above first. The premium preview reuses the built app and existing media assets.
                        </p>
                      )}
                      {premiumDesignError && <p className="alert alert-error">{premiumDesignError}</p>}
                      {premiumDesignAccepted && (
                        <div className="alert alert-success">
                          <strong>{premiumDesignAccepted.message}</strong>
                          <span>
                            {' '}Functional checks passed: {premiumDesignAccepted.functional_validation.passed_count};
                            failed: {premiumDesignAccepted.functional_validation.failed_count}.
                          </span>
                        </div>
                      )}
                      {premiumDesignPreview && (
                        <>
                          <div className="premium-art-direction">
                            <div>
                              <span className="premium-style-tag">{premiumDesignPreview.direction.personality}</span>
                              <p>{premiumDesignPreview.direction.rationale}</p>
                              <p><strong>Layout:</strong> {premiumDesignPreview.direction.layout_direction}</p>
                              <p><strong>Imagery:</strong> {premiumDesignPreview.direction.imagery_direction}</p>
                              <p><strong>Typography:</strong> {premiumDesignPreview.direction.typography}</p>
                              {premiumDesignPreview.direction.fallback_reason && (
                                <p className="project-details-hint">
                                  {premiumDesignPreview.direction.fallback_reason} A prompt-aware built-in art direction was used.
                                </p>
                              )}
                            </div>
                            <div className="premium-palette" aria-label="Proposed color palette">
                              {['page', 'card', 'inner', 'accent', 'action', 'secondary'].map((token) => (
                                <span
                                  key={token}
                                  className="premium-color-swatch"
                                  title={`${token}: ${premiumDesignPreview.direction.palette[token]}`}
                                  style={{ background: premiumDesignPreview.direction.palette[token] }}
                                />
                              ))}
                            </div>
                          </div>

                          <div className="premium-design-comparison">
                            <section>
                              <h4>Before · Current site</h4>
                              <iframe
                                title="Current generated website design"
                                src={previewLink || undefined}
                                loading="lazy"
                              />
                            </section>
                            <section>
                              <h4>After · {premiumDesignPreview.direction.personality}</h4>
                              <iframe
                                title={`Premium ${premiumDesignPreview.direction.personality} design preview`}
                                src={premiumDesignPreviewUrl(premiumDesignPreview.project_slug, premiumDesignPreview.preview_id)}
                                loading="lazy"
                              />
                            </section>
                          </div>
                          <ul className="premium-validation-list">
                            {premiumDesignPreview.validation.checks.map((check) => <li key={check}>✓ {check}</li>)}
                          </ul>
                          <div className="btn-row">
                            <button
                              type="button"
                              className="btn btn-green"
                              onClick={handleAcceptPremiumDesign}
                              disabled={premiumDesignBusy}
                            >
                              {premiumDesignBusy ? 'Building & validating…' : 'Accept & apply design'}
                            </button>
                            <button
                              type="button"
                              className="btn btn-secondary"
                              onClick={handleRejectPremiumDesign}
                              disabled={premiumDesignBusy}
                            >
                              Reject preview
                            </button>
                          </div>
                        </>
                      )}
                    </section>

                    {generatedProject?.files_created && generatedProject.files_created.length > 0 && (
                      <section className="generated-files-panel">
                        <div className="generated-files-header">
                          <div>
                            <h4>Generated files ({generatedProject.files_created.length})</h4>
                            <p>Every generated source file is available to view, copy, or save.</p>
                          </div>
                          <button onClick={handleDownload} disabled={!projectSlug} className="btn btn-sm btn-purple">⬇ Save all files</button>
                        </div>
                        <div className="generated-files-layout">
                          <ul className="generated-files-list">
                            {generatedProject.files_created.map((file) => (
                              <li key={file} className={selectedGeneratedFile === file ? 'selected' : ''}>
                                <span className="generated-file-name" title={file}>{generatedFilePath(file)}</span>
                                <span className="generated-file-actions">
                                  <button type="button" onClick={() => viewGeneratedFile(file)}>View</button>
                                  <button type="button" onClick={() => copyGeneratedFile(file)}>{copiedGeneratedFile === file ? 'Copied' : 'Copy'}</button>
                                  <button type="button" onClick={() => saveGeneratedFile(file)}>Save</button>
                                </span>
                              </li>
                            ))}
                          </ul>
                          <div className="generated-file-viewer">
                            {selectedGeneratedFile ? (
                              <>
                                <div className="generated-file-viewer-title">{generatedFilePath(selectedGeneratedFile)}</div>
                                <pre>{generatedFileContent}</pre>
                              </>
                            ) : (
                              <p>Select any file to view its generated source.</p>
                            )}
                          </div>
                        </div>
                      </section>
                    )}
                  </>
                )}
              </section>
            )}

            {/* TAB 4: Automated Testing & Verification */}
            {activeResultTab === 'testing' && (
              <section className="card inner">
                <div className="card-title-row">
                  <h3 className="card-title">🧪 Automated Testing &amp; Self-Healing Report</h3>
                  <div className="btn-row">
                    <span className={`status-pill ${analysis.testing_report?.is_valid ? 'ok' : 'error'}`}>
                      {analysis.testing_report?.is_valid ? '✅ All Tests Passed' : '⚠ Test issues remain'}
                    </span>
                    <button
                      type="button"
                      className="btn btn-sm btn-secondary"
                      onClick={handleRetestAndHeal}
                      disabled={qualityRunInProgress || !projectSlug}
                    >
                      {qualityRunInProgress ? 'Testing and repairing…' : '↻ Run tests & self-heal'}
                    </button>
                  </div>
                </div>

                <div className="result-grid" style={{ marginBottom: '16px' }}>
                  <div className="stat"><span className="stat-label">Passed Checks</span><span className="stat-value" style={{ color: '#34d399' }}>{analysis.testing_report?.passed_count ?? 0}</span></div>
                  <div className="stat"><span className="stat-label">Failed Checks</span><span className="stat-value">{analysis.testing_report?.failed_count ?? 0}</span></div>
                  <div className="stat"><span className="stat-label">Debug Iterations</span><span className="stat-value">{analysis.debug_report?.attempts ?? 0}</span></div>
                </div>

                {analysis.debug_report?.fixes && analysis.debug_report.fixes.length > 0 && (
                  <div className="alert alert-info" style={{ marginBottom: '14px' }}>
                    <strong>🩺 Debug Agent Applied Fixes:</strong>
                    <ul style={{ margin: '6px 0 0 16px', padding: 0 }}>
                      {analysis.debug_report.fixes.map((f, i) => (
                        <li key={i}>{f.file_path}: {f.fix_description}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="checks-list">
                  {analysis.testing_report?.checks?.map((check, i) => (
                    <div key={i} className={`check-item ${check.passed ? 'pass' : 'fail'}`}>
                      <span className="check-icon">{check.passed ? '✅' : '❌'}</span>
                      <div className="check-body">
                        <div className="check-title">{check.name} ({check.category})</div>
                        <div className="check-details">{check.details}</div>
                      </div>
                    </div>
                  ))}
                </div>

                {analysis.testing_report?.logs && (
                  <details className="log-block" style={{ marginTop: '14px' }}>
                    <summary>Detailed Test Execution Log</summary>
                    <pre className="log-pre">{analysis.testing_report.logs}</pre>
                  </details>
                )}
              </section>
            )}

            {/* TAB 5: Security Audit */}
            {activeResultTab === 'security' && (
              <section className="card inner">
                <div className="card-title-row">
                  <h3 className="card-title">🛡 Automated Security Audit Report</h3>
                  <div className="security-score-badge">
                    🔒 Score: {analysis.security_report?.score ?? 100} / 100
                  </div>
                </div>

                <p style={{ color: '#cbd5e1', fontSize: '0.9rem', marginBottom: '16px' }}>
                  {analysis.security_report?.summary || 'Static security analysis completed.'}
                </p>

                <h4 style={{ color: '#a78bfa', fontSize: '0.9rem', marginBottom: '8px' }}>✓ Verified Security Controls:</h4>
                <ul style={{ color: '#e2e8f0', fontSize: '0.86rem', lineHeight: '1.7', margin: '0 0 16px 20px' }}>
                  {analysis.security_report?.passed_checks?.map((p, i) => (
                    <li key={i}>{p}</li>
                  ))}
                </ul>

                {analysis.security_report?.vulnerabilities && analysis.security_report.vulnerabilities.length > 0 && (
                  <div>
                    <h4 style={{ color: '#fbbf24', fontSize: '0.9rem', marginBottom: '8px' }}>Remediated Security Findings:</h4>
                    {analysis.security_report.vulnerabilities.map((v, i) => (
                      <div key={i} className="check-item" style={{ borderLeft: '3px solid #fbbf24' }}>
                        <span className="check-icon">🛡</span>
                        <div className="check-body">
                          <div className="check-title">{v.check_name} ({v.severity.toUpperCase()})</div>
                          <div className="check-details">{v.description}</div>
                          <div className="check-details" style={{ color: '#34d399' }}>✓ Mitigation: {v.remediation}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            )}

            {/* TAB 6: Deployment Package */}
            {activeResultTab === 'deployment' && (
              <section className="card inner">
                <div className="card-title-row">
                  <h3 className="card-title">🚀 Production Deployment Package</h3>
                  <span className="status-pill ok">● Ready</span>
                </div>

                <p style={{ color: '#cbd5e1', fontSize: '0.88rem', marginBottom: '14px' }}>
                  {analysis.deployment_report?.status_message || 'Deployment artifacts prepared.'}
                </p>

                <h4 style={{ color: '#67e8f9', fontSize: '0.9rem', marginBottom: '10px' }}>Generated Container &amp; Config Artifacts:</h4>
                {analysis.deployment_report?.artifacts?.map((art, i) => (
                  <div key={i} className="deploy-artifact-card">
                    <div className="deploy-artifact-header">
                      <span>📄 {art.filename}</span>
                      <span style={{ color: '#94a3b8', fontSize: '0.75rem' }}>{art.path}</span>
                    </div>
                    <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: '#cbd5e1' }}>{art.description}</p>
                  </div>
                ))}

                <h4 style={{ color: '#a78bfa', fontSize: '0.9rem', margin: '16px 0 8px' }}>Quick Start Command:</h4>
                <pre className="log-pre" style={{ background: '#090d16', color: '#38bdf8' }}>
                  docker compose up --build
                </pre>
                <section className="card inner" style={{ marginTop: '20px' }}>
                  <h3 className="card-title">🛠 AI maintenance / change request</h3>
                  <p className="project-details-hint">
                    Describe a future change to create an updated SRS and design for review. Approve the new design to regenerate, test, self-heal, and repackage the project.
                  </p>
                  <textarea
                    value={maintenanceRequest}
                    onChange={(event) => setMaintenanceRequest(event.target.value)}
                    placeholder="Describe a feature, bug fix, or operational change…"
                    rows={3}
                    className="prompt-input"
                  />
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleMaintenanceRequest}
                    disabled={analyzing || planningSDLC || !maintenanceRequest.trim()}
                  >
                    {planningSDLC ? 'Planning change…' : 'Plan maintenance change'}
                  </button>
                </section>
              </section>
            )}
          </div>
        )}
      

      {/* AI Video Generation Studio */}
      <section className="card">
        <div className="card-title-row">
          <h2 className="card-title"><span className="emoji">🎬</span> AI Video Generation Studio</h2>
          <button
            type="button"
            onClick={() => setShowVideoPanel((prev) => !prev)}
            className="btn btn-sm"
          >
            {showVideoPanel ? 'Hide' : 'Show'}
          </button>
        </div>

        {showVideoPanel && (
          <VideoGenerator initialPrompt={prompt || 'AI Multi-Agent Web App Generator Architecture'} />
        )}
      </section>

      {/* AI Image Generation Panel */}
      <section className="card">
        <div className="card-title-row">
          <h2 className="card-title"><span className="emoji">🎨</span> AI Image Generation</h2>
          <button
            type="button"
            onClick={() => setShowImagePanel((prev) => !prev)}
            className="btn btn-sm"
          >
            {showImagePanel ? 'Hide' : 'Show'}
          </button>
        </div>

        {showImagePanel && (
          <div className="image-panel">
            <div className="image-prompt-row">
              <input
                type="text"
                value={imagePrompt}
                onChange={(e) => setImagePrompt(e.target.value)}
                placeholder="Describe the image you want to generate..."
                className="image-prompt-input"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleGenerateImage();
                  }
                }}
              />
              <button
                onClick={handleGenerateImage}
                disabled={generatingImage}
                className="btn btn-primary"
              >
                {generatingImage ? 'Generating...' : 'Generate Image'}
              </button>
            </div>

            {imageError && <p className="alert alert-error">{imageError}</p>}

            {generatedImage && (
              <div className="image-result">
                <img src={generatedImage} alt={imagePrompt} className="generated-image" />
                <div className="image-actions">
                  <a href={generatedImage} target="_blank" rel="noreferrer" className="btn btn-sm">
                    Open Full Size
                  </a>
                  <button
                    type="button"
                    onClick={() => {
                      const a = document.createElement('a');
                      a.href = generatedImage;
                      a.download = `generated-${Date.now()}.png`;
                      document.body.appendChild(a);
                      a.click();
                      document.body.removeChild(a);
                    }}
                    className="btn btn-sm"
                  >
                    Download
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      <section className="card generated-websites-section">
        <div className="card-title-row">
          <div>
            <h2 className="card-title">🗂 Your Generated Websites</h2>
            <p className="generated-websites-subtitle">
              {generatedWebsites.length} website{generatedWebsites.length === 1 ? '' : 's'} generated for {currentUser?.full_name || currentUser?.username || 'your account'}.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-sm"
            onClick={() => {
              setWebsitesLoading(true);
              void refreshGeneratedWebsites().finally(() => setWebsitesLoading(false));
            }}
            disabled={websitesLoading}
          >
            {websitesLoading ? 'Refreshing…' : '↻ Refresh'}
          </button>
        </div>

        {websiteHistoryError && <p className="alert alert-error">{websiteHistoryError}</p>}
        {websitePreviewError && <p className="alert alert-error">{websitePreviewError}</p>}
        {websitesLoading && generatedWebsites.length === 0 ? (
          <p className="generated-websites-empty">Loading your website history…</p>
        ) : generatedWebsites.length === 0 ? (
          <p className="generated-websites-empty">No websites yet. Generate your first website and it will appear here.</p>
        ) : (
          <div className="generated-websites-list">
            {generatedWebsites.map((website) => (
              <article className="generated-website-item" key={website.project_slug}>
                <div className="generated-website-details">
                  <strong>{website.project_name}</strong>
                  <span>{new Date(website.created_at * 1000).toLocaleString()}</span>
                  <code>{website.project_slug}</code>
                </div>
                <div className="generated-website-actions">
                  <span className={`generated-website-status ${website.built ? 'is-built' : ''}`}>
                    {website.built ? 'Ready to preview' : 'Needs build'}
                  </span>
                  <button
                    type="button"
                    className="btn btn-blue"
                    onClick={() => void handleOpenGeneratedWebsite(website)}
                    disabled={previewingWebsiteSlug !== null}
                  >
                    {previewingWebsiteSlug === website.project_slug
                      ? 'Installing & building…'
                      : website.built
                        ? '▶ Open Preview'
                        : '⚙ Build & Open Preview'}
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      {/* Custom Requirement Modal */}
      <RequirementModal
        isOpen={showRequirementModal}
        onClose={() => setShowRequirementModal(false)}
        currentPrompt={prompt}
        onApplyRequirements={(newPrompt) => {
          setPrompt(newPrompt);
          handleAnalyze(newPrompt);
        }}
      />
      {showProjectDetailsEditor && editableProjectDetails && (
        <div className="modal-overlay" onClick={() => setShowProjectDetailsEditor(false)}>
          <form
            className="modal project-details-modal"
            onClick={(event) => event.stopPropagation()}
            onSubmit={(event) => {
              event.preventDefault();
              setShowProjectDetailsEditor(false);
            }}
          >
            <div className="modal-header">
              <div className="modal-title-wrap">
                <span className="modal-badge">✏️ Editable configuration</span>
                <h2>Change project details</h2>
              </div>
              <button type="button" className="close-btn" onClick={() => setShowProjectDetailsEditor(false)}>✕</button>
            </div>
            <p className="modal-subtitle">Update the project information to match your application. Changes are applied immediately to this workspace view.</p>
            <div className="project-details-form-grid">
              <label>Project Name<input value={editableProjectDetails.projectName} onChange={(event) => setEditableProjectDetails({ ...editableProjectDetails, projectName: event.target.value })} required /></label>
              <label>Domain<input value={editableProjectDetails.domain} onChange={(event) => setEditableProjectDetails({ ...editableProjectDetails, domain: event.target.value })} required /></label>
              <label>Frontend<input value={editableProjectDetails.frontend} onChange={(event) => setEditableProjectDetails({ ...editableProjectDetails, frontend: event.target.value })} required /></label>
              <label>Backend<input value={editableProjectDetails.backend} onChange={(event) => setEditableProjectDetails({ ...editableProjectDetails, backend: event.target.value })} required /></label>
              <label>Database<input value={editableProjectDetails.database} onChange={(event) => setEditableProjectDetails({ ...editableProjectDetails, database: event.target.value })} required /></label>
              <label>Authentication<select value={editableProjectDetails.authentication ? 'yes' : 'no'} onChange={(event) => setEditableProjectDetails({ ...editableProjectDetails, authentication: event.target.value === 'yes' })}><option value="no">No</option><option value="yes">Yes</option></select></label>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-ghost" onClick={() => setShowProjectDetailsEditor(false)}>Cancel</button>
              <button type="submit" className="btn btn-primary">Save changes</button>
            </div>
          </form>
        </div>
      )}
            </main>
          )}
        </>
      );
}

export default App;
