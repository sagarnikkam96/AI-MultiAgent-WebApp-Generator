import React, { useState, useEffect } from 'react';

interface LiveWebsitePreviewProps {
  projectName: string;
  projectType: string;
  modules: string[];
  backend: string;
  database: string;
  previewUrl?: string | null;
  onOpenPreview?: () => void;
}

interface MockRecord {
  id: number;
  title: string;
  category: string;
  status: string;
  date: string;
}

interface CustomFeatureItem {
  id: number;
  title: string;
  subtitle?: string;
  status?: string;
  value?: string;
  date: string;
}

interface CustomFeature {
  id: string;
  name: string;
  icon: string;
  description: string;
  type: 'table' | 'kanban' | 'form' | 'metrics' | 'notes';
  items: CustomFeatureItem[];
  formSubmissions?: Array<{ id: number; data: Record<string, string>; date: string }>;
}

export const LiveWebsitePreview: React.FC<LiveWebsitePreviewProps> = ({
  projectName,
  projectType,
  modules,
  backend,
  database,
  previewUrl,
  onOpenPreview,
}) => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [accentColor, setAccentColor] = useState('cyan');
  const [customProjectName, setCustomProjectName] = useState(projectName);
  const [customDomain, setCustomDomain] = useState(projectType);
  const [customFrontend, setCustomFrontend] = useState('React');
  const [customBackend, setCustomBackend] = useState(backend);
  const [customDatabase, setCustomDatabase] = useState(database);
  const [customAuthentication, setCustomAuthentication] = useState('No');
  const [customBrandName, setCustomBrandName] = useState(projectName);
  const [customSubtitle, setCustomSubtitle] = useState(`${projectType} • ${backend} & ${database}`);
  const [bannerMessage, setBannerMessage] = useState<string | null>(null);

  // Main Records
  const [records, setRecords] = useState<MockRecord[]>([
    { id: 1, title: `${projectName} Core Record A`, category: 'Primary', status: 'Active', date: 'Just now' },
    { id: 2, title: `${projectName} Workflow Item B`, category: 'Operation', status: 'Pending Review', date: '10 mins ago' },
    { id: 3, title: `${projectName} Service Task C`, category: 'System', status: 'Completed', date: '1 hour ago' },
    { id: 4, title: `${projectName} Analytics Report D`, category: 'Metrics', status: 'Verified', date: '2 hours ago' },
  ]);

  // Record Modals State
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState('Primary');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editRecord, setEditRecord] = useState<MockRecord | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const [editStatus, setEditStatus] = useState('');

  // Feature Studio State
  const [customFeatures, setCustomFeatures] = useState<CustomFeature[]>([]);
  const [showFeatureStudio, setShowFeatureStudio] = useState(false);
  const [featureTab, setFeatureTab] = useState<'builder' | 'ai'>('builder');
  const [newFeatureName, setNewFeatureName] = useState('');
  const [newFeatureIcon, setNewFeatureIcon] = useState('⚡');
  const [newFeatureType, setNewFeatureType] = useState<'table' | 'kanban' | 'form' | 'metrics' | 'notes'>('table');
  const [newFeatureDesc, setNewFeatureDesc] = useState('');
  const [aiPrompt, setAiPrompt] = useState('');

  // Website Customizer State
  const [showCustomizer, setShowCustomizer] = useState(false);

  // Custom Feature dynamic inputs
  const [customItemInput, setCustomItemInput] = useState<Record<string, string>>({});
  const [customFormValues, setCustomFormValues] = useState<Record<string, Record<string, string>>>({});

  const notify = (msg: string) => {
    setBannerMessage(msg);
    window.setTimeout(() => setBannerMessage(null), 4000);
  };

  // Local storage persistence for simulator
  const storageKey = `sim_custom_${projectName.toLowerCase().replace(/\s+/g, '_')}`;

  useEffect(() => {
    try {
      const saved = localStorage.getItem(storageKey);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.brandName) setCustomBrandName(parsed.brandName);
        if (parsed.subtitle) setCustomSubtitle(parsed.subtitle);
        if (parsed.projectName) setCustomProjectName(parsed.projectName);
        if (parsed.domain) setCustomDomain(parsed.domain);
        if (parsed.frontend) setCustomFrontend(parsed.frontend);
        if (parsed.backend) setCustomBackend(parsed.backend);
        if (parsed.database) setCustomDatabase(parsed.database);
        if (parsed.authentication) setCustomAuthentication(parsed.authentication);
        if (parsed.isDarkMode !== undefined) setIsDarkMode(parsed.isDarkMode);
        if (parsed.accentColor) setAccentColor(parsed.accentColor);
        if (parsed.records && Array.isArray(parsed.records)) setRecords(parsed.records);
        if (parsed.customFeatures && Array.isArray(parsed.customFeatures)) setCustomFeatures(parsed.customFeatures);
      }
    } catch {
      // ignore
    }
  }, [storageKey]);

  const saveToStorage = (updated?: {
    brandName?: string;
    subtitle?: string;
    projectName?: string;
    domain?: string;
    frontend?: string;
    backend?: string;
    database?: string;
    authentication?: string;
    isDarkMode?: boolean;
    accentColor?: string;
    records?: MockRecord[];
    customFeatures?: CustomFeature[];
  }) => {
    try {
      const payload = {
        brandName: updated?.brandName ?? customBrandName,
        subtitle: updated?.subtitle ?? customSubtitle,
        projectName: updated?.projectName ?? customProjectName,
        domain: updated?.domain ?? customDomain,
        frontend: updated?.frontend ?? customFrontend,
        backend: updated?.backend ?? customBackend,
        database: updated?.database ?? customDatabase,
        authentication: updated?.authentication ?? customAuthentication,
        isDarkMode: updated?.isDarkMode ?? isDarkMode,
        accentColor: updated?.accentColor ?? accentColor,
        records: updated?.records ?? records,
        customFeatures: updated?.customFeatures ?? customFeatures,
      };
      localStorage.setItem(storageKey, JSON.stringify(payload));
    } catch {
      // ignore
    }
  };

  const filteredRecords = records.filter(
    (r) =>
      r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.status.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Create Record
  const handleAddRecord = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    const newRec: MockRecord = {
      id: Date.now(),
      title: newTitle.trim(),
      category: newCategory,
      status: 'Active',
      date: 'Just now',
    };
    const nextRecs = [newRec, ...records];
    setRecords(nextRecs);
    saveToStorage({ records: nextRecs });
    setNewTitle('');
    setShowAddModal(false);
    notify(`Created record "${newRec.title}"`);
  };

  // Edit Record
  const openEditRecord = (r: MockRecord) => {
    setEditRecord(r);
    setEditTitle(r.title);
    setEditCategory(r.category);
    setEditStatus(r.status);
  };

  const handleSaveEdit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editRecord || !editTitle.trim()) return;
    const nextRecs = records.map((r) =>
      r.id === editRecord.id
        ? { ...r, title: editTitle.trim(), category: editCategory || r.category, status: editStatus || r.status }
        : r
    );
    setRecords(nextRecs);
    saveToStorage({ records: nextRecs });
    setEditRecord(null);
    notify(`Updated record "${editTitle}"`);
  };

  const handleDeleteRecord = (id: number) => {
    const nextRecs = records.filter((r) => r.id !== id);
    setRecords(nextRecs);
    saveToStorage({ records: nextRecs });
    notify('Record removed.');
  };

  // Feature Studio Handlers
  const handleAddFeature = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const name = newFeatureName.trim();
    if (!name) return;

    let initialItems: CustomFeatureItem[] = [];
    if (newFeatureType === 'kanban') {
      initialItems = [
        { id: Date.now(), title: `${name} Task 1`, status: 'todo', date: 'Just now' },
        { id: Date.now() + 1, title: `${name} Active Item`, status: 'in-progress', date: 'Today' },
        { id: Date.now() + 2, title: `${name} Completed Task`, status: 'done', date: 'Yesterday' },
      ];
    } else if (newFeatureType === 'metrics') {
      initialItems = [
        { id: Date.now(), title: `${name} KPI Rate`, value: '94%', subtitle: 'Target: 90%', date: 'Live' },
        { id: Date.now() + 1, title: `${name} Volume`, value: '1,420', subtitle: '+18% growth', date: 'Monthly' },
      ];
    } else if (newFeatureType === 'notes') {
      initialItems = [
        { id: Date.now(), title: `Key takeaway note for ${name}`, subtitle: 'General', date: 'Today' },
      ];
    } else {
      initialItems = [
        { id: Date.now(), title: `${name} Entry A`, subtitle: 'Primary', status: 'Active', date: 'Just now' },
        { id: Date.now() + 1, title: `${name} Entry B`, subtitle: 'Operation', status: 'Pending', date: '10m ago' },
      ];
    }

    const feature: CustomFeature = {
      id: `feat-${Date.now()}`,
      name,
      icon: newFeatureIcon || '⚡',
      description: newFeatureDesc.trim() || `Custom ${newFeatureType} module for ${name}`,
      type: newFeatureType,
      items: initialItems,
      formSubmissions: [],
    };

    const nextFeatures = [...customFeatures, feature];
    setCustomFeatures(nextFeatures);
    saveToStorage({ customFeatures: nextFeatures });
    setNewFeatureName('');
    setNewFeatureDesc('');
    setShowFeatureStudio(false);
    setActiveTab(feature.id);
    notify(`✨ Feature "${name}" added to website!`);
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
    } else if (lower.includes('metric') || lower.includes('kpi') || lower.includes('analytics') || lower.includes('stats')) {
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
      description: `AI-generated module: "${promptText}"`,
      type: detectedType,
      items: [
        { id: Date.now(), title: `${title} Primary Item`, subtitle: 'High Priority', status: 'Active', value: '100', date: 'Just now' },
        { id: Date.now() + 1, title: `${title} Workflow Card`, subtitle: 'Standard', status: 'in-progress', value: '75', date: 'Today' },
      ],
      formSubmissions: [],
    };

    const nextFeatures = [...customFeatures, feature];
    setCustomFeatures(nextFeatures);
    saveToStorage({ customFeatures: nextFeatures });
    setAiPrompt('');
    setShowFeatureStudio(false);
    setActiveTab(feature.id);
    notify(`🤖 AI created and injected "${title}"!`);
  };

  const handleDeleteFeature = (featId: string) => {
    const nextFeatures = customFeatures.filter((f) => f.id !== featId);
    setCustomFeatures(nextFeatures);
    saveToStorage({ customFeatures: nextFeatures });
    setActiveTab('dashboard');
    notify('Feature module removed.');
  };

  const handleMoveKanban = (featId: string, itemId: number, newStatus: string) => {
    const nextFeatures = customFeatures.map((f) => {
      if (f.id !== featId) return f;
      return {
        ...f,
        items: f.items.map((it) => (it.id === itemId ? { ...it, status: newStatus } : it)),
      };
    });
    setCustomFeatures(nextFeatures);
    saveToStorage({ customFeatures: nextFeatures });
  };

  const handleAddCustomItem = (featId: string) => {
    const title = (customItemInput[featId] || '').trim();
    if (!title) return;
    const nextFeatures = customFeatures.map((f) => {
      if (f.id !== featId) return f;
      const newItem: CustomFeatureItem = {
        id: Date.now(),
        title,
        status: f.type === 'kanban' ? 'todo' : 'Active',
        subtitle: 'Custom Item',
        value: 'New',
        date: 'Just now',
      };
      return { ...f, items: [newItem, ...f.items] };
    });
    setCustomFeatures(nextFeatures);
    saveToStorage({ customFeatures: nextFeatures });
    setCustomItemInput({ ...customItemInput, [featId]: '' });
  };

  const handleDeleteCustomItem = (featId: string, itemId: number) => {
    const nextFeatures = customFeatures.map((f) => {
      if (f.id !== featId) return f;
      return { ...f, items: f.items.filter((it) => it.id !== itemId) };
    });
    setCustomFeatures(nextFeatures);
    saveToStorage({ customFeatures: nextFeatures });
  };

  const handleSubmitCustomForm = (featId: string, e: React.FormEvent) => {
    e.preventDefault();
    const current = customFormValues[featId] || {};
    if (Object.keys(current).length === 0) return;
    const nextFeatures = customFeatures.map((f) => {
      if (f.id !== featId) return f;
      const sub = {
        id: Date.now(),
        data: { ...current },
        date: new Date().toLocaleString(),
      };
      return { ...f, formSubmissions: [sub, ...(f.formSubmissions || [])] };
    });
    setCustomFeatures(nextFeatures);
    saveToStorage({ customFeatures: nextFeatures });
    setCustomFormValues({ ...customFormValues, [featId]: {} });
    notify('Form submission recorded!');
  };

  const handleResetDefaults = () => {
    if (window.confirm('Reset simulator customizations and custom features back to default?')) {
      localStorage.removeItem(storageKey);
      setCustomBrandName(projectName);
      setCustomSubtitle(`${projectType} • ${backend} & ${database}`);
      setCustomProjectName(projectName);
      setCustomDomain(projectType);
      setCustomFrontend('React');
      setCustomBackend(backend);
      setCustomDatabase(database);
      setCustomAuthentication('No');
      setIsDarkMode(true);
      setAccentColor('cyan');
      setCustomFeatures([]);
      setRecords([
        { id: 1, title: `${projectName} Core Record A`, category: 'Primary', status: 'Active', date: 'Just now' },
        { id: 2, title: `${projectName} Workflow Item B`, category: 'Operation', status: 'Pending Review', date: '10 mins ago' },
        { id: 3, title: `${projectName} Service Task C`, category: 'System', status: 'Completed', date: '1 hour ago' },
        { id: 4, title: `${projectName} Analytics Report D`, category: 'Metrics', status: 'Verified', date: '2 hours ago' },
      ]);
      setShowCustomizer(false);
      notify('Website restored to original state.');
    }
  };

  // Find active custom feature if current tab is a custom feature
  const activeCustomFeature = customFeatures.find((f) => f.id === activeTab);

  return (
    <div className={`live-simulator-container ${isDarkMode ? 'dark-sim' : 'light-sim'} theme-${accentColor}`}>
      {/* Simulator Window Header */}
      <div className="sim-window-bar">
        <div className="sim-window-dots">
          <span className="dot dot-red"></span>
          <span className="dot dot-yellow"></span>
          <span className="dot dot-green"></span>
        </div>
        <div className="sim-address-bar">
          <span className="sim-lock">🔒</span>
            <span className="sim-url">https://{customProjectName.toLowerCase().replace(/\s+/g, '-')}.local/app</span>
        </div>
        <div className="sim-actions">
          <button
            type="button"
            onClick={() => setShowFeatureStudio(true)}
            className="sim-tool-btn feature-studio-btn"
            title="Add New Feature / Module"
          >
            ✨ Add Feature
          </button>
          <button
            type="button"
            onClick={() => setShowCustomizer(true)}
            className="sim-tool-btn customizer-tool-btn"
            title="Customize Website Branding & Theme"
          >
            🎨 Customize
          </button>
          <button
            type="button"
            onClick={() => {
              const nextMode = !isDarkMode;
              setIsDarkMode(nextMode);
              saveToStorage({ isDarkMode: nextMode });
            }}
            className="sim-tool-btn"
            title="Toggle Simulator Theme Mode"
          >
            {isDarkMode ? '☀️ Light' : '🌙 Dark'}
          </button>
          {previewUrl && (
            <button
              type="button"
              onClick={onOpenPreview}
              className="sim-tool-btn open-tab-btn"
              title="Open Standalone Application in New Tab"
            >
              ↗ Open App
            </button>
          )}
        </div>
      </div>

      {bannerMessage && (
        <div className="sim-toast-banner">
          {bannerMessage}
        </div>
      )}

      {/* Simulated Application Shell */}
      <div className="sim-app-body">
        {/* Sidebar */}
        <aside className="sim-sidebar">
          <div className="sim-brand">
            <span className="sim-logo-icon">⚡</span>
            <div>
              <div className="sim-brand-text">{customBrandName}</div>
              <small className="sim-brand-sub">{customSubtitle}</small>
            </div>
          </div>

          <nav className="sim-nav">
            <button
              type="button"
              onClick={() => setActiveTab('dashboard')}
              className={`sim-nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            >
              📊 Dashboard
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('records')}
              className={`sim-nav-item ${activeTab === 'records' ? 'active' : ''}`}
            >
              📁 Data Records ({records.length})
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('analytics')}
              className={`sim-nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
            >
              📈 Analytics
            </button>

            {/* Dynamically added custom feature modules in sidebar */}
            {customFeatures.map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setActiveTab(f.id)}
                className={`sim-nav-item custom-nav-item ${activeTab === f.id ? 'active' : ''}`}
              >
                <span>{f.icon}</span> {f.name}
              </button>
            ))}

            <button
              type="button"
              onClick={() => setActiveTab('settings')}
              className={`sim-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            >
              ⚙ System Config
            </button>
          </nav>

          <div className="sim-sidebar-actions">
            <button
              type="button"
              onClick={() => setShowFeatureStudio(true)}
              className="btn-sim-add-feat"
            >
              ➕ Add Feature Module
            </button>
            <button
              type="button"
              onClick={() => setShowCustomizer(true)}
              className="btn-sim-customize"
            >
              🎨 Customize Website
            </button>
          </div>

          <div className="sim-user-box">
            <div className="sim-avatar">A</div>
            <div className="sim-user-info">
              <strong>Admin User</strong>
              <small>admin@system.local</small>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="sim-main-content">
          <header className="sim-topbar">
            <div>
              <h2 className="sim-page-title">{customBrandName}</h2>
              <p className="sim-page-subtitle">{customSubtitle}</p>
            </div>
            <div className="sim-topbar-actions">
              <button
                type="button"
                onClick={() => setShowFeatureStudio(true)}
                className="btn btn-glow-feature btn-sm"
              >
                ✨ Add Feature
              </button>
              <button
                type="button"
                onClick={() => setShowAddModal(true)}
                className="btn btn-primary btn-sm"
              >
                ＋ Add Record
              </button>
              <button
                type="button"
                onClick={() => setShowCustomizer(true)}
                className="btn btn-outline btn-sm"
              >
                🎨 Customize
              </button>
            </div>
          </header>

          {/* Tab 1: Dashboard */}
          {activeTab === 'dashboard' && (
            <div className="sim-tab-view">
              {/* Stat Cards */}
              <div className="sim-stat-grid">
                <div className="sim-stat-card">
                  <span className="sim-stat-title">Total Active Records</span>
                  <span className="sim-stat-num">{records.length}</span>
                  <span className="sim-stat-change positive">↑ 12% this week</span>
                </div>
                <div className="sim-stat-card">
                  <span className="sim-stat-title">Custom Modules</span>
                  <span className="sim-stat-num">{customFeatures.length}</span>
                  <span className="sim-stat-change">{customFeatures.length > 0 ? `${customFeatures.length} Active Modules` : 'Add via Studio'}</span>
                </div>
                <div className="sim-stat-card">
                  <span className="sim-stat-title">Architecture Modules</span>
                  <span className="sim-stat-num">{modules.length}</span>
                  <span className="sim-stat-change">{modules.slice(0, 2).join(', ')}</span>
                </div>
              </div>

              {/* Module Chips */}
              <div className="sim-card-panel">
                <div className="sim-card-head-row">
                  <h3>Active Application Modules &amp; Features</h3>
                  <button type="button" onClick={() => setShowFeatureStudio(true)} className="btn-sm btn-ghost">
                    ➕ Add Custom Module
                  </button>
                </div>
                <div className="sim-chip-wrap">
                  {modules.map((m) => (
                    <span key={m} className="sim-badge-chip">
                      ✓ {m}
                    </span>
                  ))}
                  {customFeatures.map((f) => (
                    <span key={f.id} className="sim-badge-chip custom-chip" onClick={() => setActiveTab(f.id)}>
                      {f.icon} {f.name} ({f.type})
                    </span>
                  ))}
                </div>
              </div>

              {/* Recent Activity Table with Inline Edit & Delete */}
              <div className="sim-card-panel">
                <div className="sim-table-header">
                  <div>
                    <h3>Workspace Records &amp; Actions</h3>
                    <p className="muted">Click "Edit" on any row to modify records directly.</p>
                  </div>
                  <input
                    type="text"
                    placeholder="Search records..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="sim-search-input"
                  />
                </div>

                <div className="sim-table-wrap">
                  <table className="sim-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Record Name</th>
                        <th>Category</th>
                        <th>Status</th>
                        <th>Timestamp</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredRecords.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="text-center muted py-4">
                            No records found. Click "Add New Record" above.
                          </td>
                        </tr>
                      ) : (
                        filteredRecords.map((rec) => (
                          <tr key={rec.id}>
                            <td>#{rec.id.toString().slice(-4)}</td>
                            <td><strong>{rec.title}</strong></td>
                            <td><span className="sim-tag">{rec.category}</span></td>
                            <td><span className="sim-status-pill">{rec.status}</span></td>
                            <td>{rec.date}</td>
                            <td>
                              <div className="sim-row-btns">
                                <button
                                  type="button"
                                  onClick={() => openEditRecord(rec)}
                                  className="sim-edit-btn"
                                  title="Edit this record"
                                >
                                  ✏️ Edit
                                </button>
                                <button
                                  type="button"
                                  onClick={() => handleDeleteRecord(rec.id)}
                                  className="sim-delete-btn"
                                  title="Delete record"
                                >
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
              </div>
            </div>
          )}

          {/* Tab 2: Records */}
          {activeTab === 'records' && (
            <div className="sim-tab-view">
              <div className="sim-card-panel">
                <div className="sim-card-head-row">
                  <h3>All Database Records</h3>
                  <button type="button" onClick={() => setShowAddModal(true)} className="btn-sm btn-primary">
                    ＋ Create Record
                  </button>
                </div>
                <div className="sim-records-grid">
                  {records.map((r) => (
                    <div key={r.id} className="sim-record-item">
                      <div className="sim-rec-head">
                        <strong>{r.title}</strong>
                        <div className="sim-rec-actions">
                          <button onClick={() => openEditRecord(r)} className="sim-edit-icon" title="Edit">✏️</button>
                          <button onClick={() => handleDeleteRecord(r.id)} className="sim-delete-btn" title="Delete">✕</button>
                        </div>
                      </div>
                      <p className="sim-rec-cat">Category: <span className="sim-tag">{r.category}</span></p>
                      <div className="sim-rec-footer">
                        <span className="sim-status-pill">{r.status}</span>
                        <small>{r.date}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab 3: Analytics */}
          {activeTab === 'analytics' && (
            <div className="sim-tab-view">
              <div className="sim-card-panel">
                <h3>System Performance &amp; Traffic</h3>
                <div className="sim-chart-mock">
                  <div className="bar-col"><div className="bar-fill" style={{ height: '65%' }}></div><span>Mon</span></div>
                  <div className="bar-col"><div className="bar-fill" style={{ height: '85%' }}></div><span>Tue</span></div>
                  <div className="bar-col"><div className="bar-fill" style={{ height: '45%' }}></div><span>Wed</span></div>
                  <div className="bar-col"><div className="bar-fill" style={{ height: '95%' }}></div><span>Thu</span></div>
                  <div className="bar-col"><div className="bar-fill" style={{ height: '70%' }}></div><span>Fri</span></div>
                  <div className="bar-col"><div className="bar-fill" style={{ height: '90%' }}></div><span>Sat</span></div>
                  <div className="bar-col"><div className="bar-fill" style={{ height: '80%' }}></div><span>Sun</span></div>
                </div>
              </div>
            </div>
          )}

          {/* Dynamic Custom Feature View */}
          {activeCustomFeature && (
            <div className="sim-tab-view">
              <div className="sim-card-panel">
                <div className="sim-card-head-row">
                  <div className="sim-feat-header">
                    <span className="sim-feat-icon">{activeCustomFeature.icon}</span>
                    <div>
                      <h3>{activeCustomFeature.name}</h3>
                      <p className="muted">{activeCustomFeature.description} • <em>{activeCustomFeature.type.toUpperCase()} Module</em></p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDeleteFeature(activeCustomFeature.id)}
                    className="btn-sm btn-del"
                  >
                    🗑 Remove Module
                  </button>
                </div>

                {/* KANBAN MODULE */}
                {activeCustomFeature.type === 'kanban' && (
                  <div className="sim-kanban-wrap">
                    <div className="sim-add-bar">
                      <input
                        type="text"
                        placeholder={`Add task to ${activeCustomFeature.name}...`}
                        value={customItemInput[activeCustomFeature.id] || ''}
                        onChange={(e) => setCustomItemInput({ ...customItemInput, [activeCustomFeature.id]: e.target.value })}
                        onKeyDown={(e) => { if (e.key === 'Enter') handleAddCustomItem(activeCustomFeature.id); }}
                        className="sim-input-sm"
                      />
                      <button type="button" onClick={() => handleAddCustomItem(activeCustomFeature.id)} className="btn-sm btn-primary">
                        ＋ Add Task
                      </button>
                    </div>

                    <div className="sim-kanban-board">
                      {/* Column 1: To Do */}
                      <div className="sim-kanban-col">
                        <div className="sim-col-head">
                          <span>📋 To Do</span>
                          <span className="sim-badge">{activeCustomFeature.items.filter((i) => i.status === 'todo').length}</span>
                        </div>
                        <div className="sim-col-body">
                          {activeCustomFeature.items.filter((i) => i.status === 'todo').map((it) => (
                            <div key={it.id} className="sim-kanban-card">
                              <strong>{it.title}</strong>
                              <div className="sim-card-foot">
                                <small>{it.date}</small>
                                <button type="button" onClick={() => handleMoveKanban(activeCustomFeature.id, it.id, 'in-progress')} className="sim-mini-btn">
                                  → Progress
                                </button>
                                <button type="button" onClick={() => handleDeleteCustomItem(activeCustomFeature.id, it.id)} className="sim-del-icon">✕</button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Column 2: In Progress */}
                      <div className="sim-kanban-col">
                        <div className="sim-col-head">
                          <span>⚡ In Progress</span>
                          <span className="sim-badge">{activeCustomFeature.items.filter((i) => i.status === 'in-progress').length}</span>
                        </div>
                        <div className="sim-col-body">
                          {activeCustomFeature.items.filter((i) => i.status === 'in-progress').map((it) => (
                            <div key={it.id} className="sim-kanban-card progress">
                              <strong>{it.title}</strong>
                              <div className="sim-card-foot">
                                <small>{it.date}</small>
                                <button type="button" onClick={() => handleMoveKanban(activeCustomFeature.id, it.id, 'done')} className="sim-mini-btn btn-done">
                                  ✓ Done
                                </button>
                                <button type="button" onClick={() => handleDeleteCustomItem(activeCustomFeature.id, it.id)} className="sim-del-icon">✕</button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Column 3: Completed */}
                      <div className="sim-kanban-col">
                        <div className="sim-col-head">
                          <span>✅ Done</span>
                          <span className="sim-badge">{activeCustomFeature.items.filter((i) => i.status === 'done').length}</span>
                        </div>
                        <div className="sim-col-body">
                          {activeCustomFeature.items.filter((i) => i.status === 'done').map((it) => (
                            <div key={it.id} className="sim-kanban-card done">
                              <s>{it.title}</s>
                              <div className="sim-card-foot">
                                <small>{it.date}</small>
                                <button type="button" onClick={() => handleMoveKanban(activeCustomFeature.id, it.id, 'in-progress')} className="sim-mini-btn">
                                  ← Reopen
                                </button>
                                <button type="button" onClick={() => handleDeleteCustomItem(activeCustomFeature.id, it.id)} className="sim-del-icon">✕</button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* TABLE MODULE */}
                {activeCustomFeature.type === 'table' && (
                  <div className="sim-custom-table-wrap">
                    <div className="sim-add-bar">
                      <input
                        type="text"
                        placeholder={`Add new record to ${activeCustomFeature.name}...`}
                        value={customItemInput[activeCustomFeature.id] || ''}
                        onChange={(e) => setCustomItemInput({ ...customItemInput, [activeCustomFeature.id]: e.target.value })}
                        onKeyDown={(e) => { if (e.key === 'Enter') handleAddCustomItem(activeCustomFeature.id); }}
                        className="sim-input-sm"
                      />
                      <button type="button" onClick={() => handleAddCustomItem(activeCustomFeature.id)} className="btn-sm btn-primary">
                        ＋ Add Item
                      </button>
                    </div>

                    <table className="sim-table">
                      <thead>
                        <tr>
                          <th>Item Name</th>
                          <th>Category</th>
                          <th>Status</th>
                          <th>Date</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {activeCustomFeature.items.length === 0 ? (
                          <tr><td colSpan={5} className="text-center muted py-4">No items yet.</td></tr>
                        ) : (
                          activeCustomFeature.items.map((it) => (
                            <tr key={it.id}>
                              <td><strong>{it.title}</strong></td>
                              <td><span className="sim-tag">{it.subtitle || 'Primary'}</span></td>
                              <td><span className="sim-status-pill">{it.status || 'Active'}</span></td>
                              <td>{it.date}</td>
                              <td>
                                <button type="button" onClick={() => handleDeleteCustomItem(activeCustomFeature.id, it.id)} className="sim-delete-btn">
                                  🗑
                                </button>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                )}

                {/* FORM MODULE */}
                {activeCustomFeature.type === 'form' && (
                  <div className="sim-form-module-grid">
                    <form onSubmit={(e) => handleSubmitCustomForm(activeCustomFeature.id, e)} className="sim-form-box">
                      <h4>Submit Entry to {activeCustomFeature.name}</h4>
                      <label>
                        Name / Title
                        <input
                          type="text"
                          required
                          placeholder="e.g. Jane Doe"
                          value={customFormValues[activeCustomFeature.id]?.name || ''}
                          onChange={(e) => setCustomFormValues({
                            ...customFormValues,
                            [activeCustomFeature.id]: { ...(customFormValues[activeCustomFeature.id] || {}), name: e.target.value },
                          })}
                          className="sim-input"
                        />
                      </label>
                      <label>
                        Details / Message
                        <textarea
                          rows={3}
                          required
                          placeholder="Provide request details..."
                          value={customFormValues[activeCustomFeature.id]?.details || ''}
                          onChange={(e) => setCustomFormValues({
                            ...customFormValues,
                            [activeCustomFeature.id]: { ...(customFormValues[activeCustomFeature.id] || {}), details: e.target.value },
                          })}
                          className="sim-input"
                        />
                      </label>
                      <button type="submit" className="btn btn-primary btn-sm">📤 Submit Form</button>
                    </form>

                    <div className="sim-submissions-box">
                      <h4>Submissions ({(activeCustomFeature.formSubmissions || []).length})</h4>
                      {(activeCustomFeature.formSubmissions || []).length === 0 ? (
                        <p className="muted">No submissions recorded yet.</p>
                      ) : (
                        <div className="sim-submissions-list">
                          {(activeCustomFeature.formSubmissions || []).map((s) => (
                            <div key={s.id} className="sim-sub-item">
                              <strong>{s.data.name || 'Submission'}</strong>
                              <p>{s.data.details}</p>
                              <small className="muted">{s.date}</small>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* METRICS MODULE */}
                {activeCustomFeature.type === 'metrics' && (
                  <div className="sim-stat-grid">
                    {activeCustomFeature.items.map((it) => (
                      <div key={it.id} className="sim-stat-card">
                        <span className="sim-stat-title">{it.title}</span>
                        <span className="sim-stat-num">{it.value || '100%'}</span>
                        <span className="sim-stat-change">{it.subtitle}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* NOTES MODULE */}
                {activeCustomFeature.type === 'notes' && (
                  <div className="sim-notes-wrap">
                    <div className="sim-add-bar">
                      <input
                        type="text"
                        placeholder="Write a quick note..."
                        value={customItemInput[activeCustomFeature.id] || ''}
                        onChange={(e) => setCustomItemInput({ ...customItemInput, [activeCustomFeature.id]: e.target.value })}
                        onKeyDown={(e) => { if (e.key === 'Enter') handleAddCustomItem(activeCustomFeature.id); }}
                        className="sim-input-sm"
                      />
                      <button type="button" onClick={() => handleAddCustomItem(activeCustomFeature.id)} className="btn-sm btn-primary">
                        📝 Post Note
                      </button>
                    </div>
                    <div className="sim-records-grid">
                      {activeCustomFeature.items.map((it) => (
                        <div key={it.id} className="sim-record-item">
                          <p style={{ margin: '0 0 10px' }}>{it.title}</p>
                          <div className="sim-rec-footer">
                            <small>{it.date}</small>
                            <button type="button" onClick={() => handleDeleteCustomItem(activeCustomFeature.id, it.id)} className="sim-delete-btn">✕</button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tab 4: Settings */}
          {activeTab === 'settings' && (
            <div className="sim-tab-view">
              <div className="sim-card-panel">
                <h3>Application Configuration</h3>
                <div className="sim-settings-list">
                  <div className="sim-setting-row">
                    <div>
                      <strong>Backend Runtime</strong>
                      <p className="muted">FastAPI Python 3.10 asynchronous server</p>
                    </div>
                    <span className="sim-tag">Port 8000</span>
                  </div>
                  <div className="sim-setting-row">
                    <div>
                      <strong>Database Engine</strong>
                      <p className="muted">SQLAlchemy 2.0 ORM with relational mapping</p>
                    </div>
                    <span className="sim-tag">{customDatabase}</span>
                  </div>
                  <div className="sim-setting-row">
                    <div>
                      <strong>Frontend Client</strong>
                      <p className="muted">{customFrontend} application client</p>
                    </div>
                    <span className="sim-tag">{customFrontend}</span>
                  </div>
                  <div className="sim-setting-row">
                    <div>
                      <strong>Project Domain</strong>
                      <p className="muted">Editable application domain</p>
                    </div>
                    <span className="sim-tag">{customDomain}</span>
                  </div>
                  <div className="sim-setting-row">
                    <div>
                      <strong>Authentication</strong>
                      <p className="muted">User-selected access model</p>
                    </div>
                    <span className="sim-tag">{customAuthentication}</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* MODAL 1: Add Record */}
      {showAddModal && (
        <div className="sim-modal-backdrop" onClick={() => setShowAddModal(false)}>
          <div className="sim-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Add New Record to {customBrandName}</h3>
            <form onSubmit={handleAddRecord}>
              <label>
                Record Title
                <input
                  type="text"
                  autoFocus
                  required
                  placeholder="e.g. Schedule New Examination"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="sim-input"
                />
              </label>
              <label>
                Category / Module
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="sim-input"
                >
                  <option value="Primary">Primary</option>
                  <option value="Operation">Operation</option>
                  <option value="System">System</option>
                  <option value="Metrics">Metrics</option>
                  {modules.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </label>
              <div className="sim-modal-actions">
                <button type="button" onClick={() => setShowAddModal(false)} className="btn btn-ghost">Cancel</button>
                <button type="submit" className="btn btn-primary">Create Record</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: Edit Record */}
      {editRecord && (
        <div className="sim-modal-backdrop" onClick={() => setEditRecord(null)}>
          <div className="sim-modal" onClick={(e) => e.stopPropagation()}>
            <h3>✏️ Edit Record #{editRecord.id.toString().slice(-4)}</h3>
            <form onSubmit={handleSaveEdit}>
              <label>
                Record Title
                <input
                  type="text"
                  autoFocus
                  required
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="sim-input"
                />
              </label>
              <label>
                Category
                <input
                  type="text"
                  value={editCategory}
                  onChange={(e) => setEditCategory(e.target.value)}
                  className="sim-input"
                />
              </label>
              <label>
                Status
                <select
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                  className="sim-input"
                >
                  <option value="Active">Active</option>
                  <option value="Pending Review">Pending Review</option>
                  <option value="Completed">Completed</option>
                  <option value="Verified">Verified</option>
                </select>
              </label>
              <div className="sim-modal-actions">
                <button type="button" onClick={() => setEditRecord(null)} className="btn btn-ghost">Cancel</button>
                <button type="submit" className="btn btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 3: In-Website Feature Studio */}
      {showFeatureStudio && (
        <div className="sim-modal-backdrop" onClick={() => setShowFeatureStudio(false)}>
          <div className="sim-modal sim-modal-lg" onClick={(e) => e.stopPropagation()}>
            <div className="sim-modal-tabs-head">
              <h3>➕ Feature Studio: Add New Interactive Feature</h3>
              <div className="sim-tabs-btn-group">
                <button
                  type="button"
                  onClick={() => setFeatureTab('builder')}
                  className={`sim-tab-toggle ${featureTab === 'builder' ? 'active' : ''}`}
                >
                  🛠 Feature Builder
                </button>
                <button
                  type="button"
                  onClick={() => setFeatureTab('ai')}
                  className={`sim-tab-toggle ${featureTab === 'ai' ? 'active' : ''}`}
                >
                  🤖 AI Feature Copilot
                </button>
              </div>
            </div>

            {featureTab === 'builder' ? (
              <form onSubmit={handleAddFeature}>
                <div className="sim-form-grid-2">
                  <label>
                    Feature Title / Name
                    <input
                      autoFocus
                      type="text"
                      required
                      placeholder="e.g. Invoice Tracker, Shift Roster, Feedback..."
                      value={newFeatureName}
                      onChange={(e) => setNewFeatureName(e.target.value)}
                      className="sim-input"
                    />
                  </label>
                  <label>
                    Feature Type
                    <select
                      value={newFeatureType}
                      onChange={(e) => setNewFeatureType(e.target.value as any)}
                      className="sim-input"
                    >
                      <option value="table">📋 Data Table / Records Manager</option>
                      <option value="kanban">📌 Kanban Workflow Board</option>
                      <option value="form">📝 Form &amp; Feedback Collector</option>
                      <option value="metrics">📈 KPI &amp; Analytics Cards</option>
                      <option value="notes">💡 Scratchpad &amp; Quick Notes</option>
                    </select>
                  </label>
                </div>

                <div className="sim-form-grid-2">
                  <label>
                    Select Icon
                    <div className="sim-icon-picker">
                      {['⚡', '📊', '📝', '💰', '📅', '👥', '🛒', '⚙️', '🎯', '🚀', '💬', '📦', '🏥', '🎓'].map((ic) => (
                        <button
                          key={ic}
                          type="button"
                          onClick={() => setNewFeatureIcon(ic)}
                          className={`sim-icon-chip ${newFeatureIcon === ic ? 'selected' : ''}`}
                        >
                          {ic}
                        </button>
                      ))}
                    </div>
                  </label>
                  <label>
                    Description
                    <input
                      type="text"
                      placeholder="Brief note about this module..."
                      value={newFeatureDesc}
                      onChange={(e) => setNewFeatureDesc(e.target.value)}
                      className="sim-input"
                    />
                  </label>
                </div>

                <div className="sim-modal-actions">
                  <button type="button" onClick={() => setShowFeatureStudio(false)} className="btn btn-ghost">Cancel</button>
                  <button type="submit" className="btn btn-primary">✨ Add Feature Module</button>
                </div>
              </form>
            ) : (
              <div className="sim-ai-copilot-panel">
                <p className="muted">Click any 1-click popular preset or enter a custom prompt:</p>
                <div className="sim-presets-grid">
                  <button
                    type="button"
                    onClick={() => handleApplyPreset('Invoice & Payment Tracker', '💰', 'table', 'Track customer invoices and billing history')}
                    className="sim-preset-card"
                  >
                    💰 Invoice &amp; Payment Tracker
                  </button>
                  <button
                    type="button"
                    onClick={() => handleApplyPreset('Appointment & Shift Roster', '📅', 'kanban', 'Manage scheduled shifts and appointments')}
                    className="sim-preset-card"
                  >
                    📅 Appointment &amp; Shift Roster
                  </button>
                  <button
                    type="button"
                    onClick={() => handleApplyPreset('Customer Feedback Collector', '📝', 'form', 'Collect feedback and user inquiries')}
                    className="sim-preset-card"
                  >
                    📝 Customer Feedback Collector
                  </button>
                  <button
                    type="button"
                    onClick={() => handleApplyPreset('Live KPI Performance', '📈', 'metrics', 'Display real-time KPI metrics')}
                    className="sim-preset-card"
                  >
                    📈 Live KPI Performance
                  </button>
                  <button
                    type="button"
                    onClick={() => handleApplyPreset('Sprint & Task Kanban', '📋', 'kanban', 'Manage sprint cards across To Do, Progress, Done')}
                    className="sim-preset-card"
                  >
                    📋 Sprint &amp; Task Kanban
                  </button>
                </div>

                <div className="sim-ai-input-box">
                  <label>
                    Prompt for AI Feature Generator
                    <textarea
                      rows={3}
                      placeholder="e.g. Add an equipment maintenance board with repair status and inspection dates..."
                      value={aiPrompt}
                      onChange={(e) => setAiPrompt(e.target.value)}
                      className="sim-input"
                    />
                  </label>
                  <div className="sim-modal-actions">
                    <button type="button" onClick={() => setShowFeatureStudio(false)} className="btn btn-ghost">Cancel</button>
                    <button type="button" onClick={handleAiGenerateFeature} className="btn btn-primary">
                      ⚡ Generate &amp; Add Feature
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODAL 4: Website Customizer */}
      {showCustomizer && (
        <div className="sim-modal-backdrop" onClick={() => setShowCustomizer(false)}>
          <div className="sim-modal" onClick={(e) => e.stopPropagation()}>
            <h3>🎨 Website &amp; Theme Customizer</h3>
            <div className="sim-form-grid-2">
              <label>
                Project Name
                <input type="text" value={customProjectName} onChange={(e) => setCustomProjectName(e.target.value)} className="sim-input" />
              </label>
              <label>
                Domain
                <input type="text" value={customDomain} onChange={(e) => setCustomDomain(e.target.value)} className="sim-input" />
              </label>
            </div>
            <div className="sim-form-grid-2">
              <label>
                Frontend
                <input type="text" value={customFrontend} onChange={(e) => setCustomFrontend(e.target.value)} className="sim-input" />
              </label>
              <label>
                Backend
                <input type="text" value={customBackend} onChange={(e) => setCustomBackend(e.target.value)} className="sim-input" />
              </label>
            </div>
            <div className="sim-form-grid-2">
              <label>
                Database
                <input type="text" value={customDatabase} onChange={(e) => setCustomDatabase(e.target.value)} className="sim-input" />
              </label>
              <label>
                Authentication
                <select value={customAuthentication} onChange={(e) => setCustomAuthentication(e.target.value)} className="sim-input">
                  <option value="No">No</option>
                  <option value="Yes">Yes</option>
                </select>
              </label>
            </div>
            <label>
              Website Brand Name
              <input
                type="text"
                value={customBrandName}
                onChange={(e) => setCustomBrandName(e.target.value)}
                className="sim-input"
              />
            </label>
            <label>
              Tagline / Subtitle
              <input
                type="text"
                value={customSubtitle}
                onChange={(e) => setCustomSubtitle(e.target.value)}
                className="sim-input"
              />
            </label>
            <label>
              Accent Color Palette
              <div className="sim-palette-row">
                {[
                  { id: 'cyan', color: '#38bdf8', label: 'Cyan' },
                  { id: 'indigo', color: '#6366f1', label: 'Indigo' },
                  { id: 'emerald', color: '#10b981', label: 'Emerald' },
                  { id: 'amber', color: '#f59e0b', label: 'Amber' },
                  { id: 'rose', color: '#f43f5e', label: 'Rose' },
                  { id: 'purple', color: '#a855f7', label: 'Purple' },
                ].map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setAccentColor(c.id)}
                    className={`sim-color-dot ${accentColor === c.id ? 'active' : ''}`}
                    style={{ backgroundColor: c.color }}
                    title={c.label}
                  >
                    {accentColor === c.id ? '✓' : ''}
                  </button>
                ))}
              </div>
            </label>
            <div className="sim-modal-actions">
              <button type="button" onClick={handleResetDefaults} className="btn btn-ghost" style={{ marginRight: 'auto', color: '#f43f5e' }}>
                🔄 Reset
              </button>
              <button
                type="button"
                onClick={() => {
                  setCustomBrandName(customProjectName);
                  setCustomSubtitle(`${customDomain} • ${customBackend} & ${customDatabase}`);
                  saveToStorage({
                    brandName: customProjectName,
                    subtitle: `${customDomain} • ${customBackend} & ${customDatabase}`,
                    projectName: customProjectName,
                    domain: customDomain,
                    frontend: customFrontend,
                    backend: customBackend,
                    database: customDatabase,
                    authentication: customAuthentication,
                  });
                  setShowCustomizer(false);
                  notify('Customizations applied successfully!');
                }}
                className="btn btn-primary"
              >
                💾 Save &amp; Apply
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

