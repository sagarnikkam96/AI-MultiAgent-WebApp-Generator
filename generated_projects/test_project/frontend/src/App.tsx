import React, { useState, useEffect } from 'react';
import AiChat from './AiChat';
import brandMark from './assets/brand-mark.svg';
import Login from './Login';
import Dashboard from './Dashboard';
import LanguageSwitcher from './LanguageSwitcher';
import { LanguageProvider, useLanguage } from './LanguageContext';
import Tasks from './Tasks';
import Projects from './Projects';
import Team from './Team';

export interface AppRecord {
  id: number;
  name: string;
  field2: string;
  field3: string;
  createdAt: string;
}

export interface CustomFeatureItem {
  id: number;
  title: string;
  subtitle?: string;
  status?: string;
  value?: string;
  date: string;
  createdAt?: string;
}

export interface CustomFeature {
  id: string;
  name: string;
  icon: string;
  description: string;
  type: 'table' | 'kanban' | 'form' | 'metrics' | 'notes';
  kind?: string;
  items: CustomFeatureItem[];
  formSubmissions?: Array<{ id: number; data: Record<string, string>; date: string }>;
}

const modules = [{"component": "Tasks", "label": "Tasks", "href": "#section-1"}, {"component": "Projects", "label": "Projects", "href": "#section-2"}, {"component": "Team", "label": "Team", "href": "#section-3"}];
const initialCounts: Record<string, number> = {"tasks": 0, "projects": 0, "teams": 0};
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/+$/, '') || 'http://127.0.0.1:8001';
const STORAGE_KEY = 'website_custom_test_project';
const defaultSiteName = "Test Project";
const defaultTagline = "Keep projects, teams, priorities, and work moving forward.";

const palettes = [
  { name: 'Cyan', id: 'cyan', value: '#38bdf8', dark: ['#0d1b24', '#132833', '#1a3542'], light: ['#d7ebff', '#c3e0ff', '#a7cefa'] },
  { name: 'Indigo', id: 'indigo', value: '#7868e8', dark: ['#161528', '#201e38', '#2a2750'], light: ['#e2e0ff', '#ccc8ff', '#b3adfa'] },
  { name: 'Emerald', id: 'emerald', value: '#10b981', dark: ['#0f201c', '#172e28', '#204037'], light: ['#d8f3e5', '#c0ead5', '#a2ddc0'] },
  { name: 'Amber', id: 'amber', value: '#f59e0b', dark: ['#211b12', '#302518', '#41321e'], light: ['#f9e8c7', '#f4d9a7', '#eac781'] },
  { name: 'Rose', id: 'rose', value: '#d47b83', dark: ['#24171d', '#35212b', '#492b39'], light: ['#f8dfe4', '#f1cbd3', '#e6aeb9'] },
  { name: 'Purple', id: 'purple', value: '#a855f7', dark: ['#1d1727', '#2a2038', '#3a2a50'], light: ['#eee0ff', '#ddc5ff', '#c8a6f4'] },
];

const InnerApp: React.FC = () => {
  const { t } = useLanguage();
  const [appName, setAppName] = useState(t('appLabel') || defaultSiteName);
  const [appSubtitle, setAppSubtitle] = useState('Autonomous Web Application');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const themeMode = theme;
  const setThemeMode = setTheme;
  const [accentColor, setAccentColor] = useState('#7776d8');
  const [user, setUser] = useState<string | null>(() => {
    try {
      const active = localStorage.getItem('website_active_user');
      if (!active) return null;
      const parsed = JSON.parse(active);
      return parsed?.name || parsed?.email || active;
    } catch {
      return localStorage.getItem('website_active_user');
    }
  });
  const [active, setActive] = useState('dashboard');
  const [msg, setMsg] = useState<string | null>(null);
  const message = msg;
  const setMessage = setMsg;

  // Records & Entity state
  const [recs, setRecs] = useState<AppRecord[]>([]);
  const records = recs;
  const setRecords = setRecs;
  const [entityCounts, setEntityCounts] = useState<Record<string, number>>(initialCounts);
  const [databaseCounts, setDatabaseCounts] = useState<Record<string, number> | null>(null);
  const [databaseCountError, setDatabaseCountError] = useState<string | null>(null);

  // Storage and UI state
  const [storageReady, setStorageReady] = useState(false);
  const [storageError, setStorageError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [cN, setCN] = useState('');
  const [c2, setC2] = useState('');
  const [c3, setC3] = useState('');
  const recordName = cN;
  const setRecordName = setCN;
  const [editRecord, setEditRecord] = useState<AppRecord | null>(null);
  const [eN, setEN] = useState('');
  const [e2, setE2] = useState('');
  const [e3, setE3] = useState('');

  // Custom Features added in website
  const [customFeatures, setCustomFeatures] = useState<CustomFeature[]>([]);
  const [showFeatureStudio, setShowFeatureStudio] = useState(false);
  const [showAiChat, setShowAiChat] = useState(false);
  const [featureTab, setFeatureTab] = useState<'builder' | 'ai'>('builder');
  const [newFeatureName, setNewFeatureName] = useState('');
  const featureName = newFeatureName;
  const setFeatureName = setNewFeatureName;
  const [newFeatureIcon, setNewFeatureIcon] = useState('⚡');
  const [newFeatureType, setNewFeatureType] = useState<'table' | 'kanban' | 'form' | 'metrics' | 'notes'>('table');
  const featureKind = newFeatureType;
  const setFeatureKind = (k: any) => setNewFeatureType(k);
  const [newFeatureDesc, setNewFeatureDesc] = useState('');
  const featureDescription = newFeatureDesc;
  const setFeatureDescription = setNewFeatureDesc;
  const [aiPrompt, setAiPrompt] = useState('');

  // Modals for editing custom features & items
  const [editCustomItem, setEditCustomItem] = useState<{ featId: string; item: CustomFeatureItem } | null>(null);
  const [editItemTitle, setEditItemTitle] = useState('');
  const [editItemSub, setEditItemSub] = useState('');
  const [editItemStatus, setEditItemStatus] = useState('');
  const [editItemVal, setEditItemVal] = useState('');

  const [editFeat, setEditFeat] = useState<CustomFeature | null>(null);
  const [editFeatName, setEditFeatName] = useState('');
  const [editFeatDesc, setEditFeatDesc] = useState('');
  const [editFeatIcon, setEditFeatIcon] = useState('⚡');

  // Customizer and Media
  const [showCustomizer, setShowCustomizer] = useState(false);
  const [customItemInput, setCustomItemInput] = useState<Record<string, string>>({});
  const featureItemDrafts = customItemInput;
  const setFeatureItemDrafts = setCustomItemInput;
  const [customFormValues, setCustomFormValues] = useState<Record<string, Record<string, string>>>({});
  const [reportSearch, setReportSearch] = useState('');
  const [media, setMedia] = useState<Array<{ id: number; name: string; url: string; type: string }>>([]);

  const selectedPalette = palettes.find((palette) => palette.value === accentColor) ?? palettes[0];
  const reportRecords = recs.filter((record) =>
    `${record.name} ${record.field2} ${record.field3}`.toLocaleLowerCase().includes(reportSearch.toLocaleLowerCase())
  );

  const ntf = (text: string) => {
    setMsg(text);
    window.setTimeout(() => setMsg(null), 4500);
  };

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE_URL}/counts`)
      .then((response) => {
        if (!response.ok) throw new Error(`Database count request failed (${response.status}).`);
        return response.json() as Promise<Record<string, unknown>>;
      })
      .then((payload) => {
        const counts: Record<string, number> = {};
        for (const [key, value] of Object.entries(payload)) {
          if (typeof value === 'number' && Number.isInteger(value) && value >= 0) {
            counts[key] = value;
          }
        }
        if (!cancelled && Object.keys(counts).length > 0) {
          setDatabaseCounts(counts);
          setDatabaseCountError(null);
        }
      })
      .catch((error: unknown) => {
        if (!cancelled) {
          setDatabaseCountError(error instanceof Error ? error.message : 'Database counts are unavailable.');
        }
      });
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    const isLight = theme === 'light';
    const [pageColor, cardColor, innerColor] = selectedPalette[theme === 'light' ? 'light' : 'dark'];
    const variables: Record<string, string> = {
      '--accent-primary': selectedPalette.value,
      '--accent-glow': `color-mix(in srgb, ${selectedPalette.value} 24%, transparent)`,
      '--bg-page': pageColor,
      '--bg-card': cardColor,
      '--bg-inner': innerColor,
      '--border-color': `color-mix(in srgb, ${selectedPalette.value} 22%, transparent)`,
      '--text-main': isLight ? '#1d2933' : '#f5f2e9',
      '--text-muted': isLight ? '#586775' : '#b6c0c4',
    };
    for (const target of [document.documentElement, document.body, document.querySelector<HTMLElement>('.app-shell')]) {
      if (!target) continue;
      for (const [property, value] of Object.entries(variables)) target.style.setProperty(property, value);
    }
  }, [accentColor, selectedPalette, theme]);

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.appName) setAppName(parsed.appName);
        if (parsed.siteName) setAppName(parsed.siteName);
        if (parsed.appSubtitle) setAppSubtitle(parsed.appSubtitle);
        if (parsed.tagline) setAppSubtitle(parsed.tagline);
        if (parsed.themeMode) setThemeMode(parsed.themeMode);
        if (parsed.theme) setThemeMode(parsed.theme);
        if (parsed.accentColor) setAccentColor(parsed.accentColor);
        if (Array.isArray(parsed.recs)) setRecs(parsed.recs);
        if (Array.isArray(parsed.records)) setRecs(parsed.records);
        if (Array.isArray(parsed.customFeatures)) setCustomFeatures(parsed.customFeatures);
      }
      setStorageReady(true);
    } catch (error) {
      setStorageError(error instanceof Error ? error.message : 'Saved website settings could not be loaded.');
    }
  }, []);

  useEffect(() => {
    if (!storageReady) return;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        appName,
        appSubtitle,
        siteName: appName,
        tagline: appSubtitle,
        themeMode,
        theme: themeMode,
        accentColor,
        recs,
        records: recs,
        customFeatures,
      }));
      setStorageError(null);
    } catch (error) {
      setStorageError(error instanceof Error ? error.message : 'Website changes could not be saved in this browser.');
    }
  }, [storageReady, appName, appSubtitle, themeMode, accentColor, recs, customFeatures]);

  const login = (name: string, email?: string) => {
    const display = name || email || 'User';
    setUser(display);
    try {
      localStorage.setItem('website_active_user', JSON.stringify({ name: display, email: email || '' }));
    } catch {}
    ntf(t('welcomeBack').replace('{email}', display));
  };

  const logout = () => {
    setUser(null);
    try {
      localStorage.removeItem('website_active_user');
    } catch {}
    ntf(t('signedOut'));
  };

  const openC = () => {
    if (!user) {
      ntf(t('signInFirst'));
      return;
    }
    setCN('');
    setC2('');
    setC3('');
    setShowCreate(true);
  };

  const create = (e: React.FormEvent) => {
    e.preventDefault();
    const n = cN.trim();
    if (!n) return;
    const newRec: AppRecord = {
      id: Date.now(),
      name: n,
      field2: c2.trim() || 'General',
      field3: c3.trim() || 'Active',
      createdAt: new Date().toLocaleDateString(),
    };
    const next = [newRec, ...recs];
    setRecs(next);
    setShowCreate(false);
    ntf(t('createdSuccess').replace('{name}', n));
  };

  const openEdit = (r: AppRecord) => {
    setEditRecord(r);
    setEN(r.name);
    setE2(r.field2);
    setE3(r.field3);
  };

  const handleSaveEdit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editRecord || !eN.trim()) return;
    const next = recs.map((r) =>
      r.id === editRecord.id ? { ...r, name: eN.trim(), field2: e2.trim() || r.field2, field3: e3.trim() || r.field3 } : r
    );
    setRecs(next);
    setEditRecord(null);
    ntf('Record updated successfully!');
  };

  const handleDeleteRecord = (id: number) => {
    const next = recs.filter((r) => r.id !== id);
    setRecs(next);
    ntf('Record removed from workspace.');
  };

  const handleAddFeature = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const name = newFeatureName.trim();
    if (!name) return;

    const feature: CustomFeature = {
      id: `feat-${Date.now()}`,
      name,
      icon: newFeatureIcon || '⚡',
      description: newFeatureDesc.trim() || `Custom ${newFeatureType} module for ${name}`,
      type: newFeatureType,
      kind: newFeatureType,
      items: [],
      formSubmissions: [],
    };

    setCustomFeatures((current) => [...current, feature]);
    setNewFeatureName('');
    setNewFeatureDesc('');
    setShowFeatureStudio(false);
    ntf('✨ Feature "' + name + '" added successfully to your website!');
  };

  const handleApplyPreset = (presetName: string, icon: string, type: 'table' | 'kanban' | 'form' | 'metrics' | 'notes', desc: string) => {
    setNewFeatureName(presetName);
    setNewFeatureIcon(icon);
    setNewFeatureType(type);
    setNewFeatureDesc(desc);
    setFeatureTab('builder');
  };

  const handleAiGenerateFeature = () => {
    const promptText = aiPrompt.trim();
    if (!promptText) return;

    let detectedType: 'table' | 'kanban' | 'form' | 'metrics' | 'notes' = 'table';
    let icon = '⚡';
    const lower = promptText.toLowerCase();

    if (lower.includes('kanban') || lower.includes('task') || lower.includes('sprint') || lower.includes('todo')) {
      detectedType = 'kanban';
      icon = '📋';
    } else if (lower.includes('form') || lower.includes('feedback') || lower.includes('survey') || lower.includes('inquiry')) {
      detectedType = 'form';
      icon = '📝';
    } else if (lower.includes('metric') || lower.includes('kpi') || lower.includes('analytics') || lower.includes('revenue') || lower.includes('stats')) {
      detectedType = 'metrics';
      icon = '📈';
    } else if (lower.includes('note') || lower.includes('memo') || lower.includes('scratchpad') || lower.includes('idea')) {
      detectedType = 'notes';
      icon = '💡';
    } else if (lower.includes('invoice') || lower.includes('payment') || lower.includes('bill')) {
      icon = '💰';
    } else if (lower.includes('schedule') || lower.includes('calendar') || lower.includes('booking') || lower.includes('appointment')) {
      icon = '📅';
    }

    const title = promptText.charAt(0).toUpperCase() + promptText.slice(1, 40);

    const feature: CustomFeature = {
      id: `feat-${Date.now()}`,
      name: title,
      icon,
      description: `AI-generated feature based on prompt: "${promptText}"`,
      type: detectedType,
      kind: detectedType,
      items: [],
      formSubmissions: [],
    };

    const next = [...customFeatures, feature];
    setCustomFeatures(next);
    setAiPrompt('');
    setShowFeatureStudio(false);
    ntf('🤖 AI successfully created and injected "' + title + '" into your website!');
  };

  const handleDeleteFeature = (featId: string) => {
    setCustomFeatures((current) => current.filter((f) => f.id !== featId));
    ntf('Feature section removed.');
  };

  const handleMoveKanban = (featId: string, itemId: number, newStatus: string) => {
    const next = customFeatures.map((f) => {
      if (f.id !== featId) return f;
      return {
        ...f,
        items: f.items.map((it) => (it.id === itemId ? { ...it, status: newStatus } : it)),
      };
    });
    setCustomFeatures(next);
  };

  const handleAddCustomItem = (featId: string) => {
    const title = (customItemInput[featId] || '').trim();
    if (!title) return;
    const next = customFeatures.map((f) => {
      if (f.id !== featId) return f;
      const newItem: CustomFeatureItem = {
        id: Date.now(),
        title,
        status: f.type === 'kanban' ? 'todo' : 'Active',
        subtitle: 'Custom Item',
        value: 'New',
        date: 'Just now',
        createdAt: new Date().toLocaleDateString(),
      };
      return { ...f, items: [newItem, ...f.items] };
    });
    setCustomFeatures(next);
    setCustomItemInput({ ...customItemInput, [featId]: '' });
  };

  const handleDeleteCustomItem = (featId: string, itemId: number) => {
    const next = customFeatures.map((f) => {
      if (f.id !== featId) return f;
      return { ...f, items: f.items.filter((it) => it.id !== itemId) };
    });
    setCustomFeatures(next);
  };

  const handleSubmitCustomForm = (featId: string, e: React.FormEvent) => {
    e.preventDefault();
    const current = customFormValues[featId] || {};
    if (Object.keys(current).length === 0) return;
    const next = customFeatures.map((f) => {
      if (f.id !== featId) return f;
      const sub = {
        id: Date.now(),
        data: { ...current },
        date: new Date().toLocaleString(),
      };
      return { ...f, formSubmissions: [sub, ...(f.formSubmissions || [])] };
    });
    setCustomFeatures(next);
    setCustomFormValues({ ...customFormValues, [featId]: {} });
    ntf('Form submission recorded successfully!');
  };

  const handleResetDefaults = () => {
    if (window.confirm('Reset all website edits and custom features back to default generated state?')) {
      localStorage.removeItem(STORAGE_KEY);
      setAppName(t('appLabel') || defaultSiteName);
      setAppSubtitle('Autonomous Web Application');
      setThemeMode('dark');
      setAccentColor('#7776d8');
      setCustomFeatures([]);
      setRecs([]);
      setShowCustomizer(false);
      ntf('Website restored to original state.');
    }
  };

  const handleMediaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setMedia((current) => [
      ...current,
      ...files.map((file, i) => ({ id: Date.now() + i, name: file.name, url: URL.createObjectURL(file), type: file.type })),
    ]);
    e.target.value = '';
    ntf(`Added ${files.length} media file(s).`);
  };

  const insights = () => {
    setActive('reports');
    document.getElementById('reports')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className={`app-shell theme-${selectedPalette.id || 'cyan'} ${theme === 'light' ? 'light-mode' : 'dark-mode'}`}>
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <a className="brand" href="#dashboard">
          <img className="brand-icon" src={brandMark} alt="" />
          <div>
            <div className="brand-name">{appName}</div>
            <small className="brand-sub">{appSubtitle}</small>
          </div>
        </a>

        <nav className="nav-list" aria-label="Application navigation">
          <a href="#dashboard" className={active === 'dashboard' ? 'active' : ''} onClick={() => setActive('dashboard')}>
            {t('dashboard')}
          </a>
          <a href="#section-1" className={active === "section-1" ? "active" : ""} onClick={() => setActive("section-1")}>{"Tasks"}</a>
          <a href="#section-2" className={active === "section-2" ? "active" : ""} onClick={() => setActive("section-2")}>{"Projects"}</a>
          <a href="#section-3" className={active === "section-3" ? "active" : ""} onClick={() => setActive("section-3")}>{"Team"}</a>
          <a href="#reports" className={active === 'reports' ? 'active' : ''} onClick={() => setActive('reports')}>
            {t('insights')} ({recs.length})
          </a>
          {customFeatures.map((feature) => (
            <a key={feature.id} href={`#${feature.id}`} className={`custom-nav-link ${active === feature.id ? 'active' : ''}`} onClick={() => setActive(feature.id)}>
              <span>{feature.icon}</span> {feature.name}
            </a>
          ))}
          <a href="#media-gallery" className={active === 'media-gallery' ? 'active' : ''} onClick={() => setActive('media-gallery')}>
            {t('mediaGallery')}
          </a>
          <a href="#quick-access" className={active === 'quick-access' ? 'active' : ''} onClick={() => setActive('quick-access')}>
            {t('quickAccess')}
          </a>
        </nav>

        <div className="sidebar-action-box">
          <button type="button" onClick={() => setShowFeatureStudio(true)} className="btn-feature-add btn-feature">
            ➕ Add Feature / Module
          </button>
          <button type="button" onClick={() => setShowCustomizer(true)} className="btn-customizer btn-outline">
            🎨 Customize Website
          </button>
          <button type="button" onClick={() => setShowAiChat(true)} className="btn-ai-chat btn-outline">
            🤖 AI Chat
          </button>
        </div>

        <LanguageSwitcher />

        {user ? (
          <div className="sidebar-user">
            <span className="avatar">{user[0]?.toUpperCase()}</span>
            <div>
              <strong>{user}</strong>
              <button type="button" className="btn-ghost" onClick={logout}>{t('signOut')}</button>
            </div>
          </div>
        ) : (
          <p className="muted">{t('notSignedIn')}</p>
        )}
      </aside>
        {showAiChat && <AiChat onClose={() => setShowAiChat(false)} />}

      {/* Main Page Area */}
      <main className="page-content">
        <header className="topbar">
          <div>
            <h1>{appName}</h1>
            <p className="topbar-subtitle">{appSubtitle}</p>
          </div>

          <div className="top-actions" aria-label="Quick actions">
            {user ? (
              <div className="topbar-user-badge">
                <span>👤 <strong>{user}</strong></span>
                <button type="button" onClick={logout} className="btn-xs btn-del" title="Sign Out">Sign Out</button>
              </div>
            ) : (
              <a href="#quick-access" className="btn-xs btn-primary btn-outline">Sign in / Register</a>
            )}
            <button type="button" onClick={() => setShowAiChat(true)} className="btn-ai-chat" title="Open AI Chat Assistant" style={{ padding: '8px 14px', borderRadius: '12px' }}>
              🤖 AI Chat
            </button>
            <button type="button" onClick={() => setShowFeatureStudio(true)} className="btn-glow-feature btn-feature">
              ➕ Add New Feature
            </button>
            <button type="button" onClick={openC} className="btn-primary">
              ＋ Create New
            </button>
            <button type="button" onClick={() => setShowCustomizer(true)} className="btn-outline">
              🎨 Customize Site
            </button>
            <button type="button" onClick={() => document.getElementById('media-upload')?.click()} className="btn-ghost btn-outline">
              📎 Add Media
            </button>
            <input id="media-upload" type="file" multiple accept="image/*,video/*,.pdf,.doc,.docx,.txt,.md" onChange={handleMediaChange} hidden />
            <a href="#reports" onClick={insights} className="btn-ghost btn-outline">
              Reports &amp; Insights
            </a>
          </div>
        </header>

        {msg && <div className="banner toast-banner">{msg}</div>}
        {storageError && <p className="form-error" role="alert">Browser storage: {storageError}</p>}

        {/* Domain Hero Welcome Banner: dynamically themed to the input domain */}
        <div className="domain-hero-banner">
          <div className="domain-hero-left">
            <div className="domain-hero-badge">Project & Task Operations</div>
            <h2 className="domain-hero-title">{appName} Workspace</h2>
            <p className="domain-hero-desc">Keep projects, teams, priorities, and work moving forward.</p>
            <div className="domain-hero-actions">
              <button type="button" className="btn-primary" onClick={openC}>＋ Add Task</button>
              <a className="btn-outline" href={modules[0]?.href || '#dashboard'}>Explore modules</a>
            </div>
          </div>
          <div className="domain-hero-visual">
            <img className="domain-hero-image" src="https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?auto=format&fit=crop&w=1000&q=85" alt="Agile project planning checklist and workspace" loading="lazy" />
            <img className="domain-hero-image" src="https://images.unsplash.com/photo-1507925921958-8a62f3d1a50d?auto=format&fit=crop&w=700&q=85" alt="Project task notes and sprint kanban board" loading="lazy" />
          </div>
          <div className="domain-hero-stats">
            <div className="domain-stat-card">
              <strong className="domain-stat-val">
                {databaseCounts ? (databaseCounts.total ?? Object.values(databaseCounts).reduce((sum, count) => sum + count, 0)) : Object.values(entityCounts).reduce((sum, count) => sum + count, 0) + recs.length}
              </strong>
              <span className="domain-stat-lbl">{databaseCounts ? 'Database records' : 'Total Records'}</span>
              <small className="muted text-xs">Records saved in this browser</small>
            </div>
            <div className="domain-stat-card">
              <strong className="domain-stat-val">{Object.keys(entityCounts).length + customFeatures.length}</strong>
              <span className="domain-stat-lbl">Modules</span>
              <small className="muted text-xs">Application modules</small>
            </div>
            <div className="domain-stat-card">
              <strong className="domain-stat-val">{user ? 'Active' : 'Guest'}</strong>
              <span className="domain-stat-lbl">Auth Status</span>
              <small className="muted text-xs">Session</small>
            </div>
          </div>
        </div>

        {databaseCountError && <p className="muted" role="status">Database counts are unavailable: {databaseCountError}</p>}

        {/* Dashboard Section */}
        <section id="dashboard" className="content-block">
          <Dashboard records={recs} entityCounts={databaseCounts ?? entityCounts} databaseCountError={databaseCountError} countsSource={databaseCounts ? 'database' : 'browser'} />
        </section>

        {/* Resource Module Sections */}
        <section id="section-1" className="content-block"><Tasks onCountChange={(count) => setEntityCounts((current) => ({ ...current, 'tasks': count }))} /></section>
        <section id="section-2" className="content-block"><Projects onCountChange={(count) => setEntityCounts((current) => ({ ...current, 'projects': count }))} /></section>
        <section id="section-3" className="content-block"><Team onCountChange={(count) => setEntityCounts((current) => ({ ...current, 'teams': count }))} /></section>

        {/* Reports & Insights Section */}
        <section id="reports" className="content-block report-block insights-section">
          <div className="section-head-row">
            <div>
              <p className="eyebrow">Workspace activity</p>
              <h2>Reports &amp; Insights</h2>
              <p className="muted">{t('insightsSubtitle')}</p>
            </div>
            <div className="action-btn-group">
              <label className="search-field">Search records
                <input
                  type="search"
                  value={reportSearch}
                  onChange={(e) => setReportSearch(e.target.value)}
                  placeholder="Search name, category, or status"
                  className="input-sm"
                />
              </label>
              <button type="button" onClick={openC} className="btn-sm btn-primary">
                ＋ {t('createNew')}
              </button>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Tasks</th>
                  <th>Category</th>
                  <th>Detail / Metric</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reportRecords.length === 0 ? (
                  <tr><td colSpan={6} className="muted text-center py-4">{recs.length === 0 ? t('noRecords') : 'No matching records found.'}</td></tr>
                ) : (
                  reportRecords.map((r, i) => (
                    <tr key={r.id}>
                      <td>{i + 1}</td>
                      <td><strong>{r.name}</strong></td>
                      <td><span className="badge-pill">{r.field2}</span></td>
                      <td>{r.field3}</td>
                      <td><span className="status-pill status-active">Active</span></td>
                      <td>
                        <div className="action-btn-group">
                          <button type="button" onClick={() => openEdit(r)} className="btn-sm btn-edit" title="Edit this record">
                            ✏️ Edit
                          </button>
                          <button type="button" onClick={() => handleDeleteRecord(r.id)} className="btn-sm btn-del" title="Delete record">
                            🗑
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Dynamic User Custom Feature Sections */}
        {customFeatures.map((feature) => {
          const feat = feature;
          return (
          <section key={feat.id} id={feat.id} className="content-block custom-feature-section">
            <div className="section-head-row">
              <div className="feat-title-group">
                <span className="feat-large-icon">{feat.icon}</span>
                <div>
                  <p className="eyebrow">Custom module · {feat.type}</p>
                  <h2>{feat.name}</h2>
                  <p className="muted">{feat.description}</p>
                </div>
              </div>
              <div className="action-btn-group">
                <button type="button" onClick={() => { setEditFeat(feat); setEditFeatName(feat.name); setEditFeatDesc(feat.description); setEditFeatIcon(feat.icon); }} className="btn-sm btn-edit" title="Edit module">
                  ✏️ Edit Module
                </button>
                <button type="button" onClick={() => handleDeleteFeature(feat.id)} className="btn-sm btn-del" title="Remove entire module">
                  🗑 Remove Module
                </button>
              </div>
            </div>

            {feat.type === 'kanban' && (
              <div className="kanban-container">
                <div className="kanban-add-bar">
                  <input
                    type="text"
                    placeholder={`Add task to ${feat.name}...`}
                    value={customItemInput[feat.id] || ''}
                    onChange={(e) => setCustomItemInput({ ...customItemInput, [feat.id]: e.target.value })}
                    onKeyDown={(e) => { if (e.key === 'Enter') handleAddCustomItem(feat.id); }}
                    className="input-sm"
                  />
                  <button type="button" onClick={() => handleAddCustomItem(feat.id)} className="btn-sm btn-primary">＋ Add Card</button>
                </div>
                <div className="kanban-board">
                  <div className="kanban-col">
                    <div className="kanban-col-head"><span>📋 To Do</span><span className="col-count">{feat.items.filter((i) => i.status === 'todo').length}</span></div>
                    <div className="kanban-col-body">
                      {feat.items.filter((i) => i.status === 'todo').map((it) => (
                        <div key={it.id} className="kanban-card">
                          <div className="kanban-card-title">{it.title}</div>
                          <div className="kanban-card-meta"><small>{it.date}</small><div className="kanban-card-btns"><button type="button" onClick={() => handleMoveKanban(feat.id, it.id, 'in-progress')}>→ In Progress</button><button type="button" onClick={() => handleDeleteCustomItem(feat.id, it.id)} className="text-danger">✕</button></div></div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="kanban-col">
                    <div className="kanban-col-head"><span>⚡ In Progress</span><span className="col-count">{feat.items.filter((i) => i.status === 'in-progress').length}</span></div>
                    <div className="kanban-col-body">
                      {feat.items.filter((i) => i.status === 'in-progress').map((it) => (
                        <div key={it.id} className="kanban-card in-progress">
                          <div className="kanban-card-title">{it.title}</div>
                          <div className="kanban-card-meta"><small>{it.date}</small><div className="kanban-card-btns"><button type="button" onClick={() => handleMoveKanban(feat.id, it.id, 'todo')}>← Back</button><button type="button" onClick={() => handleMoveKanban(feat.id, it.id, 'done')} className="btn-done">✓ Done</button><button type="button" onClick={() => handleDeleteCustomItem(feat.id, it.id)} className="text-danger">✕</button></div></div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="kanban-col">
                    <div className="kanban-col-head"><span>✅ Completed</span><span className="col-count">{feat.items.filter((i) => i.status === 'done').length}</span></div>
                    <div className="kanban-col-body">
                      {feat.items.filter((i) => i.status === 'done').map((it) => (
                        <div key={it.id} className="kanban-card done">
                          <div className="kanban-card-title"><s>{it.title}</s></div>
                          <div className="kanban-card-meta"><small>{it.date}</small><div className="kanban-card-btns"><button type="button" onClick={() => handleMoveKanban(feat.id, it.id, 'in-progress')}>← Reopen</button><button type="button" onClick={() => handleDeleteCustomItem(feat.id, it.id)} className="text-danger">✕</button></div></div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {feat.type === 'table' && (
              <div className="custom-table-container">
                <div className="custom-table-add-bar">
                  <input
                    type="text"
                    placeholder={`New item name for ${feat.name}...`}
                    value={customItemInput[feat.id] || ''}
                    onChange={(e) => setCustomItemInput({ ...customItemInput, [feat.id]: e.target.value })}
                    onKeyDown={(e) => { if (e.key === 'Enter') handleAddCustomItem(feat.id); }}
                    className="input-sm"
                  />
                  <button type="button" onClick={() => handleAddCustomItem(feat.id)} className="btn-sm btn-primary">＋ Add Item</button>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Item Name</th><th>Category</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
                    <tbody>
                      {feat.items.length === 0 ? (
                        <tr><td colSpan={5} className="muted text-center py-3">No items yet. Type above and click Add Item.</td></tr>
                      ) : (
                        feat.items.map((it) => (
                          <tr key={it.id}>
                            <td><strong>{it.title}</strong></td>
                            <td><span className="badge-pill">{it.subtitle || 'General'}</span></td>
                            <td><span className="status-pill status-active">{it.status || 'Active'}</span></td>
                            <td>{it.date}</td>
                            <td><button type="button" onClick={() => handleDeleteCustomItem(feat.id, it.id)} className="btn-sm btn-del">🗑</button></td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {feat.type === 'form' && (
              <div className="custom-form-container">
                <form onSubmit={(e) => handleSubmitCustomForm(feat.id, e)} className="custom-form-panel">
                  <h3>Submit Entry to {feat.name}</h3>
                  <div className="form-row-2">
                    <label>Name / Title<input type="text" required placeholder="e.g. John Doe" value={customFormValues[feat.id]?.name || ''} onChange={(e) => setCustomFormValues({ ...customFormValues, [feat.id]: { ...(customFormValues[feat.id] || {}), name: e.target.value } })} /></label>
                    <label>Category<input type="text" placeholder="e.g. Support" value={customFormValues[feat.id]?.category || ''} onChange={(e) => setCustomFormValues({ ...customFormValues, [feat.id]: { ...(customFormValues[feat.id] || {}), category: e.target.value } })} /></label>
                  </div>
                  <label>Details / Message<textarea rows={3} required placeholder="Enter message or request..." value={customFormValues[feat.id]?.details || ''} onChange={(e) => setCustomFormValues({ ...customFormValues, [feat.id]: { ...(customFormValues[feat.id] || {}), details: e.target.value } })} /></label>
                  <button type="submit" className="btn-primary">📤 Submit Entry</button>
                </form>
                <div className="custom-submissions-panel">
                  <h3>Submissions ({(feat.formSubmissions || []).length})</h3>
                  {(feat.formSubmissions || []).length === 0 ? (
                    <p className="muted">No submissions yet. Use the form above to record entries.</p>
                  ) : (
                    <ul className="submissions-list">
                      {(feat.formSubmissions || []).map((sub) => (
                        <li key={sub.id} className="submission-card">
                          <div><strong>{sub.data.name || 'Entry'}</strong> — <span className="badge-pill">{sub.data.category || 'General'}</span><p className="submission-text">{sub.data.details}</p></div>
                          <small className="muted">{sub.date}</small>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}

            {feat.type === 'metrics' && (
              <div className="dashboard-grid">
                {feat.items.map((it) => (
                  <div key={it.id} className="dashboard-card feat-metric-card">
                    <span className="stat-label">{it.title}</span>
                    <strong>{it.value || '100%'}</strong>
                    <small className="stat-sub">{it.subtitle}</small>
                    <button type="button" onClick={() => handleDeleteCustomItem(feat.id, it.id)} className="btn-del-corner">✕</button>
                  </div>
                ))}
              </div>
            )}

            {feat.type === 'notes' && (
              <div className="custom-notes-container">
                <div className="notes-add-row">
                  <input type="text" placeholder="Write a quick note..." value={customItemInput[feat.id] || ''} onChange={(e) => setCustomItemInput({ ...customItemInput, [feat.id]: e.target.value })} onKeyDown={(e) => { if (e.key === 'Enter') handleAddCustomItem(feat.id); }} />
                  <button type="button" onClick={() => handleAddCustomItem(feat.id)} className="btn-primary">📝 Post Note</button>
                </div>
                <div className="notes-grid">
                  {feat.items.map((it) => (
                    <div key={it.id} className="note-card">
                      <p className="note-body">{it.title}</p>
                      <div className="note-footer"><small>{it.date}</small><button type="button" onClick={() => handleDeleteCustomItem(feat.id, it.id)} className="btn-del-sm">✕</button></div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        ); })}

        {/* Media Gallery Section */}
        <section id="media-gallery" className="content-block">
          <div className="section-head-row">
            <div>
              <p className="eyebrow">Workspace files</p>
              <h2>Media gallery</h2>
              <p className="muted">Files you add are shown for this browser session.</p>
            </div>
            <label className="btn-outline upload-label" htmlFor="media-upload">＋ Add Media</label>
          </div>
          {media.length === 0 ? (
            <p className="muted empty-state">No media files added yet. Choose a file to build this gallery.</p>
          ) : (
            <div className="media-grid">
              {media.map((item) => (
                <article key={item.id} className="media-card media-item">
                  {item.type.startsWith('image/') ? (
                    <img src={item.url} alt={item.name} className="media-image" />
                  ) : item.type.startsWith('video/') ? (
                    <video src={item.url} controls className="media-video" />
                  ) : (
                    <div className="media-file"><span className="media-icon">📄</span><span>{item.name}</span></div>
                  )}
                  <div>
                    <strong>{item.name}</strong>
                    <button type="button" onClick={() => setMedia(media.filter((m) => m.id !== item.id))} className="btn-sm btn-del">Remove</button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        {/* Quick Access Section */}
        <section id="quick-access" className="content-block auth-block">
          <div className="panel">
            <h2>{t('quickAccess')}</h2>
            {user ? (
              <p className="muted signed-in-msg">{t('signedInMsg').replace('{user}', user)}</p>
            ) : (
              <Login onLogin={login} onSignIn={login} />
            )}
          </div>
        </section>
      </main>

      {/* MODAL 1: Create Record */}
      {showCreate && (
        <div className="modal-overlay modal-backdrop" onClick={() => setShowCreate(false)}>
          <form className="modal modal-card" onSubmit={create} onClick={(e) => e.stopPropagation()}>
            <h2>{t('createRecord')}</h2>
            <label htmlFor="record-name">Tasks Name *
              <input id="record-name" autoFocus type="text" value={cN} onChange={(e) => setCN(e.target.value)} placeholder="Enter title/name" required />
            </label>
            <label>Category
              <input type="text" value={c2} onChange={(e) => setC2(e.target.value)} placeholder="Enter category" />
            </label>
            <label>Detail / Metric
              <input type="text" value={c3} onChange={(e) => setC3(e.target.value)} placeholder="Enter detail or metric" />
            </label>
            <div className="modal-actions form-actions">
              <button type="button" className="btn-ghost btn-outline" onClick={() => setShowCreate(false)}>{t('cancel')}</button>
              <button type="submit" className="btn-primary">{t('create')}</button>
            </div>
          </form>
        </div>
      )}

      {/* MODAL 2: Edit Record */}
      {editRecord && (
        <div className="modal-overlay modal-backdrop" onClick={() => setEditRecord(null)}>
          <form className="modal modal-card" onSubmit={handleSaveEdit} onClick={(e) => e.stopPropagation()}>
            <h2>✏️ Edit Record #{editRecord.id.toString().slice(-4)}</h2>
            <label>Name / Title
              <input autoFocus type="text" value={eN} onChange={(e) => setEN(e.target.value)} required />
            </label>
            <label>Category
              <input type="text" value={e2} onChange={(e) => setE2(e.target.value)} />
            </label>
            <label>Detail / Metric
              <input type="text" value={e3} onChange={(e) => setE3(e.target.value)} />
            </label>
            <div className="modal-actions form-actions">
              <button type="button" className="btn-ghost btn-outline" onClick={() => setEditRecord(null)}>{t('cancel')}</button>
              <button type="submit" className="btn-primary">Save Changes</button>
            </div>
          </form>
        </div>
      )}

      {/* MODAL 3: In-Website Feature Studio */}
      {showFeatureStudio && (
        <div className="modal-overlay modal-backdrop" onClick={() => setShowFeatureStudio(false)}>
          <div className="modal modal-lg modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-tabs">
              <p className="eyebrow">Extend your workspace</p>
              <h2>➕ Feature Studio: Add a feature module</h2>
              <div className="modal-tabs">
                <button type="button" onClick={() => setFeatureTab('builder')} className={`modal-tab-btn ${featureTab === 'builder' ? 'active' : ''}`}>🛠 Feature Builder</button>
                <button type="button" onClick={() => setFeatureTab('ai')} className={`modal-tab-btn ${featureTab === 'ai' ? 'active' : ''}`}>🤖 AI Feature Copilot</button>
              </div>
            </div>

            {featureTab === 'builder' ? (
              <form onSubmit={handleAddFeature}>
                <div className="form-row-2">
                  <label htmlFor="feature-name">Module name
                    <input id="feature-name" autoFocus type="text" required placeholder="e.g. Invoices, Roster, Maintenance..." value={newFeatureName} onChange={(e) => setNewFeatureName(e.target.value)} />
                  </label>
                  <label htmlFor="feature-kind">Module format
                    <select id="feature-kind" value={newFeatureType} onChange={(e) => setNewFeatureType(e.target.value as any)} className="input-select">
                      <option value="table">📋 Data Table / Records Manager</option>
                      <option value="kanban">📌 Kanban Workflow Board</option>
                      <option value="form">📝 Form &amp; Feedback Collector</option>
                      <option value="metrics">📈 KPI &amp; Analytics Cards</option>
                      <option value="notes">💡 Scratchpad &amp; Quick Notes</option>
                    </select>
                  </label>
                </div>
                <div className="form-row-2">
                  <label>Choose Icon
                    <div className="icon-picker">
                      {['⚡', '📊', '📝', '💰', '📅', '👥', '🛒', '⚙️', '🎯', '🚀', '💬', '📦', '🏥', '🎓', '🛠️'].map((ic) => (
                        <button key={ic} type="button" onClick={() => setNewFeatureIcon(ic)} className={`icon-btn ${newFeatureIcon === ic ? 'selected' : ''}`}>{ic}</button>
                      ))}
                    </div>
                  </label>
                  <label htmlFor="feature-description">Description
                    <input id="feature-description" type="text" placeholder="What will this module help manage?" value={newFeatureDesc} onChange={(e) => setNewFeatureDesc(e.target.value)} />
                  </label>
                </div>
                <div className="modal-actions form-actions">
                  <button type="button" className="btn-ghost btn-outline" onClick={() => setShowFeatureStudio(false)}>{t('cancel')}</button>
                  <button type="submit" className="btn-primary">Add module</button>
                </div>
              </form>
            ) : (
              <div className="ai-feature-copilot">
                <p className="muted">Choose a 1-click popular preset, or type what feature you need:</p>
                <div className="preset-grid">
                  <button type="button" onClick={() => handleApplyPreset('Invoice & Payment Tracker', '💰', 'table', 'Track billing, transactions, and client payment invoices')} className="preset-chip">💰 Invoice &amp; Payment Tracker</button>
                  <button type="button" onClick={() => handleApplyPreset('Appointment / Roster Board', '📅', 'kanban', 'Manage scheduled shifts, patient visits, or bookings')} className="preset-chip">📅 Appointment / Roster Board</button>
                  <button type="button" onClick={() => handleApplyPreset('Customer Feedback Collector', '📝', 'form', 'Collect reviews, inquiries, and customer feedback')} className="preset-chip">📝 Customer Feedback Collector</button>
                  <button type="button" onClick={() => handleApplyPreset('Live KPI & Performance Metrics', '📈', 'metrics', 'Display key operational metrics and revenue gauges')} className="preset-chip">📈 Live KPI &amp; Performance Metrics</button>
                  <button type="button" onClick={() => handleApplyPreset('Task & Sprint Kanban', '📋', 'kanban', 'To Do, In Progress, and Completed sprint task cards')} className="preset-chip">📋 Task &amp; Sprint Kanban</button>
                </div>
                <div className="ai-prompt-box">
                  <label>Custom Prompt for AI Feature Generator
                    <textarea rows={3} placeholder="e.g. Add a staff schedule planner with shifts and timestamps..." value={aiPrompt} onChange={(e) => setAiPrompt(e.target.value)} />
                  </label>
                  <div className="modal-actions form-actions">
                    <button type="button" className="btn-ghost btn-outline" onClick={() => setShowFeatureStudio(false)}>{t('cancel')}</button>
                    <button type="button" onClick={handleAiGenerateFeature} className="btn-primary btn-glow">⚡ Generate &amp; Add Feature</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODAL 4: Website Customizer & Theme Studio */}
      {showCustomizer && (
        <div className="modal-overlay modal-backdrop" onClick={() => setShowCustomizer(false)}>
          <div className="modal modal-card" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="customizer-title">
            <p className="eyebrow">Personalize this workspace</p>
            <h2 id="customizer-title">Website &amp; Theme Customizer</h2>
            <label htmlFor="site-name">Brand name
              <input id="site-name" type="text" value={appName} onChange={(e) => setAppName(e.target.value)} placeholder="e.g. Apex Health Portal" />
            </label>
            <label htmlFor="site-tagline">Tagline
              <input id="site-tagline" type="text" value={appSubtitle} onChange={(e) => setAppSubtitle(e.target.value)} placeholder="e.g. Next-Gen Enterprise Solution" />
            </label>
            <fieldset className="palette-picker">
              <legend>Accent palette</legend>
              <div className="palette-grid">
                {palettes.map((palette) => (
                  <button
                    key={palette.value}
                    type="button"
                    onClick={() => setAccentColor(palette.value)}
                    className={`palette-swatch color-swatch ${accentColor === palette.value ? 'selected' : ''}`}
                    style={{ backgroundColor: palette.value }}
                    title={palette.name}
                    aria-label={palette.name}
                    aria-pressed={accentColor === palette.value}
                  >
                    {accentColor === palette.value ? '✓' : ''}
                  </button>
                ))}
              </div>
            </fieldset>
            <fieldset className="theme-picker" style={{ marginTop: '14px' }}>
              <legend>Appearance</legend>
              <div className="form-actions btn-group">
                <button type="button" onClick={() => setTheme('dark')} className={`btn-toggle ${theme === 'dark' ? 'btn-primary active' : 'btn-outline'}`} aria-pressed={theme === 'dark'}>🌙 Dark</button>
                <button type="button" onClick={() => setTheme('light')} className={`btn-toggle ${theme === 'light' ? 'btn-primary active' : 'btn-outline'}`} aria-pressed={theme === 'light'}>☀️ Light</button>
              </div>
            </fieldset>
            <div className="modal-actions form-actions" style={{ marginTop: '20px' }}>
              <button type="button" onClick={handleResetDefaults} className="btn-danger-ghost btn-danger">Reset defaults</button>
              <button type="button" onClick={() => { setShowCustomizer(false); ntf('Website customizations saved successfully!'); }} className="btn-primary">Save &amp; apply</button>
            </div>
          </div>
        </div>
      )}

      {/* Floating AI Chat Assistant Launcher */}
      <button
        type="button"
        onClick={() => setShowAiChat(true)}
        className="floating-ai-btn"
        title="Open AI Chat Assistant"
        aria-label="Open AI Chat Assistant"
      >
        🤖 <span>AI Chat</span>
      </button>

      {/* Floating Action Studio Launcher */}
      <button
        type="button"
        onClick={() => setShowFeatureStudio(true)}
        className="floating-studio-btn floating-feature"
        title="Open Feature Studio to add new features"
        aria-label="Add a feature module"
      >
        ✨ <span>Add Feature</span>
      </button>
    </div>
  );
};

export default App;
