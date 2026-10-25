import React, { useState, useEffect } from 'react';
import Dashboard from './Dashboard';
import SectionOne from './SectionOne';
import SectionTwo from './SectionTwo';

export interface AppRecord {
  id: number;
  name: string;
  role: string;
  createdAt: string;
}

export interface CustomFeatureItem {
  id: number;
  title: string;
  subtitle?: string;
  status?: string;
  value?: string;
  date: string;
}

export interface CustomFeature {
  id: string;
  name: string;
  icon: string;
  description: string;
  type: 'table' | 'kanban' | 'form' | 'metrics' | 'notes';
  items: CustomFeatureItem[];
  formSubmissions?: Array<{ id: number; data: Record<string, string>; date: string }>;
}

const App: React.FC = () => {
  const [appName, setAppName] = useState('College Management System');
  const [appSubtitle, setAppSubtitle] = useState('Autonomous Web Application');
  const [themeMode, setThemeMode] = useState<'dark' | 'light'>('dark');
  const [accentColor, setAccentColor] = useState('cyan');
  const [user] = useState<string | null>('workspace-user');
  const [message, setMessage] = useState<string | null>(null);

  // Main Domain Records
  const [records, setRecords] = useState<AppRecord[]>([
    { id: 1, name: 'Sample Record 1', role: 'Primary Lead', createdAt: new Date().toLocaleDateString() },
    { id: 2, name: 'Sample Record 2', role: 'Active Member', createdAt: new Date().toLocaleDateString() },
  ]);

  // Record Modals
  const [showCreate, setShowCreate] = useState(false);
  const [createName, setCreateName] = useState('');
  const [createRole, setCreateRole] = useState('');
  const [editRecord, setEditRecord] = useState<AppRecord | null>(null);
  const [editName, setEditName] = useState('');
  const [editRole, setEditRole] = useState('');

  // Custom In-Website Features
  const [customFeatures, setCustomFeatures] = useState<CustomFeature[]>([]);
  const [showFeatureStudio, setShowFeatureStudio] = useState(false);
  const [featureTab, setFeatureTab] = useState<'builder' | 'ai'>('builder');
  const [newFeatureName, setNewFeatureName] = useState('');
  const [newFeatureIcon, setNewFeatureIcon] = useState('⚡');
  const [newFeatureType, setNewFeatureType] = useState<'table' | 'kanban' | 'form' | 'metrics' | 'notes'>('table');
  const [newFeatureDesc, setNewFeatureDesc] = useState('');
  const [aiPrompt, setAiPrompt] = useState('');

  // Website Customizer
  const [showCustomizer, setShowCustomizer] = useState(false);

  // Dynamic inputs for custom features
  const [customItemInput, setCustomItemInput] = useState<Record<string, string>>({});
  const [customFormValues, setCustomFormValues] = useState<Record<string, Record<string, string>>>({});

  // Media
  const [media, setMedia] = useState<Array<{ id: number; name: string; url: string; type: string }>>([]);

  const notify = (text: string) => {
    setMessage(text);
    window.setTimeout(() => setMessage(null), 4500);
  };

  // Load customizations from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('app_site_customization');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.appName) setAppName(parsed.appName);
        if (parsed.appSubtitle) setAppSubtitle(parsed.appSubtitle);
        if (parsed.themeMode) setThemeMode(parsed.themeMode);
        if (parsed.accentColor) setAccentColor(parsed.accentColor);
        if (parsed.records && Array.isArray(parsed.records)) setRecords(parsed.records);
        if (parsed.customFeatures && Array.isArray(parsed.customFeatures)) setCustomFeatures(parsed.customFeatures);
      }
    } catch {
      // ignore
    }
  }, []);

  // Save customizations to localStorage
  const saveToStorage = (updated?: {
    name?: string;
    sub?: string;
    theme?: 'dark' | 'light';
    color?: string;
    recs?: AppRecord[];
    features?: CustomFeature[];
  }) => {
    try {
      const payload = {
        appName: updated?.name ?? appName,
        appSubtitle: updated?.sub ?? appSubtitle,
        themeMode: updated?.theme ?? themeMode,
        accentColor: updated?.color ?? accentColor,
        records: updated?.recs ?? records,
        customFeatures: updated?.features ?? customFeatures,
      };
      localStorage.setItem('app_site_customization', JSON.stringify(payload));
    } catch {
      // ignore
    }
  };

  // Create Record
  const openCreate = () => {
    setCreateName('');
    setCreateRole('');
    setShowCreate(true);
  };

  const handleCreate = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const name = createName.trim();
    if (!name) return;
    const newRec: AppRecord = {
      id: Date.now(),
      name,
      role: createRole.trim() || 'Member',
      createdAt: new Date().toLocaleString(),
    };
    const nextRecs = [newRec, ...records];
    setRecords(nextRecs);
    saveToStorage({ recs: nextRecs });
    setShowCreate(false);
    notify(`Created record "${name}" successfully.`);
  };

  // Edit Record
  const openEdit = (record: AppRecord) => {
    setEditRecord(record);
    setEditName(record.name);
    setEditRole(record.role);
  };

  const handleSaveEdit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editRecord || !editName.trim()) return;
    const nextRecs = records.map((r) =>
      r.id === editRecord.id ? { ...r, name: editName.trim(), role: editRole.trim() || r.role } : r
    );
    setRecords(nextRecs);
    saveToStorage({ recs: nextRecs });
    setEditRecord(null);
    notify(`Updated record "${editName}" successfully.`);
  };

  const handleDeleteRecord = (id: number) => {
    const nextRecs = records.filter((r) => r.id !== id);
    setRecords(nextRecs);
    saveToStorage({ recs: nextRecs });
    notify('Record removed from workspace.');
  };

  // Add Custom Feature
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
        { id: Date.now(), title: `Key takeaway for ${name}`, subtitle: 'Important note on operations', date: 'Today' },
      ];
    } else {
      initialItems = [
        { id: Date.now(), title: `${name} Entry A`, subtitle: 'General', status: 'Active', date: 'Just now' },
        { id: Date.now() + 1, title: `${name} Entry B`, subtitle: 'Operations', status: 'Pending', date: '10m ago' },
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
    saveToStorage({ features: nextFeatures });
    setNewFeatureName('');
    setNewFeatureDesc('');
    setShowFeatureStudio(false);
    notify(`✨ Feature "${name}" added successfully to your website!`);
  };

  // AI Feature Copilot preset trigger
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
      items: [
        { id: Date.now(), title: `${title} Primary Item`, subtitle: 'High Priority', status: 'Active', value: '100', date: 'Just now' },
        { id: Date.now() + 1, title: `${title} Workflow Item`, subtitle: 'Standard', status: 'in-progress', value: '75', date: 'Today' },
      ],
      formSubmissions: [],
    };

    const nextFeatures = [...customFeatures, feature];
    setCustomFeatures(nextFeatures);
    saveToStorage({ features: nextFeatures });
    setAiPrompt('');
    setShowFeatureStudio(false);
    notify(`🤖 AI successfully created and injected "${title}" into your website!`);
  };

  const handleDeleteFeature = (featId: string) => {
    const nextFeatures = customFeatures.filter((f) => f.id !== featId);
    setCustomFeatures(nextFeatures);
    saveToStorage({ features: nextFeatures });
    notify('Feature section removed.');
  };

  // Move Kanban Card
  const handleMoveKanban = (featId: string, itemId: number, newStatus: string) => {
    const nextFeatures = customFeatures.map((f) => {
      if (f.id !== featId) return f;
      return {
        ...f,
        items: f.items.map((it) => (it.id === itemId ? { ...it, status: newStatus } : it)),
      };
    });
    setCustomFeatures(nextFeatures);
    saveToStorage({ features: nextFeatures });
  };

  // Add Item to Custom Feature
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
    saveToStorage({ features: nextFeatures });
    setCustomItemInput({ ...customItemInput, [featId]: '' });
  };

  const handleDeleteCustomItem = (featId: string, itemId: number) => {
    const nextFeatures = customFeatures.map((f) => {
      if (f.id !== featId) return f;
      return { ...f, items: f.items.filter((it) => it.id !== itemId) };
    });
    setCustomFeatures(nextFeatures);
    saveToStorage({ features: nextFeatures });
  };

  // Submit Custom Form
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
    saveToStorage({ features: nextFeatures });
    setCustomFormValues({ ...customFormValues, [featId]: {} });
    notify('Form submission recorded successfully!');
  };

  // Reset to default
  const handleResetDefaults = () => {
    if (window.confirm('Reset all website edits and custom features back to default generated state?')) {
      localStorage.removeItem('app_site_customization');
      setAppName('Hospital Management System');
      setAppSubtitle('Autonomous Web Application');
      setThemeMode('dark');
      setAccentColor('cyan');
      setCustomFeatures([]);
      setRecords([
        { id: 1, name: 'Sample Record 1', role: 'Primary Lead', createdAt: new Date().toLocaleDateString() },
        { id: 2, name: 'Sample Record 2', role: 'Active Member', createdAt: new Date().toLocaleDateString() },
      ]);
      setShowCustomizer(false);
      notify('Website restored to original state.');
    }
  };

  const handleMediaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setMedia((p) => [
      ...p,
      ...files.map((f, i) => ({ id: Date.now() + i, name: f.name, url: URL.createObjectURL(f), type: f.type })),
    ]);
    e.target.value = '';
    notify(`Added ${files.length} media file(s).`);
  };

  return (
    <div className={`app-shell theme-${accentColor} ${themeMode === 'light' ? 'light-mode' : 'dark-mode'}`}>
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">⚡</span>
          <div>
            <div className="brand-name">{appName}</div>
            <small className="brand-sub">{appSubtitle}</small>
          </div>
        </div>

        <nav className="nav-list">
          <a href="#dashboard" className="active">📊 Dashboard</a>
          <a href="#section-1">Patients</a>
          <a href="#section-2">Doctors</a>
          <a href="#reports-section">📈 Reports &amp; Records ({records.length})</a>
          
          {/* Dynamically added custom feature nav links */}
          {customFeatures.map((f) => (
            <a key={f.id} href={`#${f.id}`} className="custom-nav-link">
              <span>{f.icon}</span> {f.name}
            </a>
          ))}

          <a href="#media-gallery">📁 Media Gallery</a>
          <a href="#quick-access">🔒 Quick Access</a>
        </nav>

        {/* Sidebar Actions */}
        <div className="sidebar-action-box">
          <button type="button" onClick={() => setShowFeatureStudio(true)} className="btn-feature-add">
            ➕ Add Feature / Module
          </button>
          <button type="button" onClick={() => setShowCustomizer(true)} className="btn-customizer">
            🎨 Customize Website
          </button>
        </div>

        {user ? (
          <div className="sidebar-user">
            <span className="avatar">{user[0]?.toUpperCase()}</span>
            <div>
              <strong>{user}</strong>
              <span className="access-badge">Full edit access</span>
            </div>
          </div>
        ) : (
          <p className="muted">Not signed in</p>
        )}
      </aside>

      {/* Main Page Content */}
      <main className="page-content">
        <header className="topbar">
          <div>
            <h1>{appName}</h1>
            <p className="topbar-subtitle">{appSubtitle}</p>
          </div>

          <div className="top-actions">
            <button type="button" onClick={() => setShowFeatureStudio(true)} className="btn-glow-feature">
              ➕ Add New Feature
            </button>
            <button type="button" onClick={openCreate} className="btn-primary">
              ＋ Create Record
            </button>
            <button type="button" onClick={() => setShowCustomizer(true)} className="btn-outline">
              🎨 Customize Site
            </button>
            <button type="button" onClick={() => document.getElementById('media-upload-input')?.click()} className="btn-ghost">
              📎 Add Media
            </button>
            <input id="media-upload-input" type="file" multiple accept="image/*,video/*,.pdf,.doc,.docx,.txt" onChange={handleMediaChange} hidden />
          </div>
        </header>

        {message && <div className="banner toast-banner">{message}</div>}

        {/* Section 0: Dashboard */}
        <section id="dashboard" className="content-block">
          <Dashboard records={records} />
        </section>

        {/* Section 1 & 2 */}
        <section id="section-1" className="content-block grid-block">
          <div>
            <SectionOne />
          </div>
          <div>
            <SectionTwo />
          </div>
        </section>

        {/* Main Records & Reports Section */}
        <section id="reports-section" className="content-block">
          <div className="section-head-row">
            <div>
              <h2>Reports &amp; Data Records</h2>
              <p className="muted">Manage and edit records directly in this workspace.</p>
            </div>
            <button type="button" onClick={openCreate} className="btn-sm btn-primary">
              ＋ Add Record
            </button>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Role / Category</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="muted text-center py-4">
                      No records yet. Click "Create Record" above to add one.
                    </td>
                  </tr>
                ) : (
                  records.map((r, index) => (
                    <tr key={r.id}>
                      <td>{index + 1}</td>
                      <td><strong>{r.name}</strong></td>
                      <td><span className="badge-pill">{r.role}</span></td>
                      <td>{r.createdAt}</td>
                      <td>
                        <div className="action-btn-group">
                          <button type="button" onClick={() => openEdit(r)} className="btn-sm btn-edit" title="Edit this record">
                            ✏️ Edit
                          </button>
                          <button type="button" onClick={() => handleDeleteRecord(r.id)} className="btn-sm btn-del" title="Delete this record">
                            🗑 Delete
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

        {/* Dynamically Rendered In-Website Custom Features */}
        {customFeatures.map((feat) => (
          <section key={feat.id} id={feat.id} className="content-block custom-feature-section">
            <div className="section-head-row">
              <div className="feat-title-group">
                <span className="feat-large-icon">{feat.icon}</span>
                <div>
                  <h2>{feat.name}</h2>
                  <p className="muted">{feat.description} • <em>{feat.type.toUpperCase()} Module</em></p>
                </div>
              </div>

              <div className="feat-header-actions">
                <button type="button" onClick={() => handleDeleteFeature(feat.id)} className="btn-sm btn-del" title="Remove this feature module">
                  🗑 Remove Module
                </button>
              </div>
            </div>

            {/* Feature Type: KANBAN WORKFLOW */}
            {feat.type === 'kanban' && (
              <div className="kanban-container">
                <div className="kanban-add-bar">
                  <input
                    type="text"
                    placeholder={`Add new task to ${feat.name}...`}
                    value={customItemInput[feat.id] || ''}
                    onChange={(e) => setCustomItemInput({ ...customItemInput, [feat.id]: e.target.value })}
                    onKeyDown={(e) => { if (e.key === 'Enter') handleAddCustomItem(feat.id); }}
                    className="input-sm"
                  />
                  <button type="button" onClick={() => handleAddCustomItem(feat.id)} className="btn-sm btn-primary">
                    ＋ Add Card
                  </button>
                </div>

                <div className="kanban-board">
                  {/* Column 1: To Do */}
                  <div className="kanban-col">
                    <div className="kanban-col-head col-todo">
                      <span>📋 To Do</span>
                      <span className="col-count">{feat.items.filter((i) => i.status === 'todo').length}</span>
                    </div>
                    <div className="kanban-col-body">
                      {feat.items.filter((i) => i.status === 'todo').map((item) => (
                        <div key={item.id} className="kanban-card">
                          <div className="kanban-card-title">{item.title}</div>
                          <div className="kanban-card-meta">
                            <small>{item.date}</small>
                            <div className="kanban-card-btns">
                              <button type="button" onClick={() => handleMoveKanban(feat.id, item.id, 'in-progress')} title="Move to In Progress">
                                → In Progress
                              </button>
                              <button type="button" onClick={() => handleDeleteCustomItem(feat.id, item.id)} className="text-danger">
                                ✕
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Column 2: In Progress */}
                  <div className="kanban-col">
                    <div className="kanban-col-head col-progress">
                      <span>⚡ In Progress</span>
                      <span className="col-count">{feat.items.filter((i) => i.status === 'in-progress').length}</span>
                    </div>
                    <div className="kanban-col-body">
                      {feat.items.filter((i) => i.status === 'in-progress').map((item) => (
                        <div key={item.id} className="kanban-card in-progress">
                          <div className="kanban-card-title">{item.title}</div>
                          <div className="kanban-card-meta">
                            <small>{item.date}</small>
                            <div className="kanban-card-btns">
                              <button type="button" onClick={() => handleMoveKanban(feat.id, item.id, 'todo')}>
                                ← Back
                              </button>
                              <button type="button" onClick={() => handleMoveKanban(feat.id, item.id, 'done')} className="btn-done">
                                ✓ Done
                              </button>
                              <button type="button" onClick={() => handleDeleteCustomItem(feat.id, item.id)} className="text-danger">
                                ✕
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Column 3: Done */}
                  <div className="kanban-col">
                    <div className="kanban-col-head col-done">
                      <span>✅ Completed</span>
                      <span className="col-count">{feat.items.filter((i) => i.status === 'done').length}</span>
                    </div>
                    <div className="kanban-col-body">
                      {feat.items.filter((i) => i.status === 'done').map((item) => (
                        <div key={item.id} className="kanban-card done">
                          <div className="kanban-card-title"><s>{item.title}</s></div>
                          <div className="kanban-card-meta">
                            <small>{item.date}</small>
                            <div className="kanban-card-btns">
                              <button type="button" onClick={() => handleMoveKanban(feat.id, item.id, 'in-progress')}>
                                ← Reopen
                              </button>
                              <button type="button" onClick={() => handleDeleteCustomItem(feat.id, item.id)} className="text-danger">
                                ✕
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Feature Type: DATA TABLE */}
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
                  <button type="button" onClick={() => handleAddCustomItem(feat.id)} className="btn-sm btn-primary">
                    ＋ Add Item
                  </button>
                </div>

                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Item Name</th>
                        <th>Category</th>
                        <th>Status</th>
                        <th>Timestamp</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {feat.items.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="muted text-center py-3">No items yet. Type above and click Add Item.</td>
                        </tr>
                      ) : (
                        feat.items.map((item) => (
                          <tr key={item.id}>
                            <td><strong>{item.title}</strong></td>
                            <td><span className="badge-pill">{item.subtitle || 'Primary'}</span></td>
                            <td><span className="status-pill status-active">{item.status || 'Active'}</span></td>
                            <td>{item.date}</td>
                            <td>
                              <button type="button" onClick={() => handleDeleteCustomItem(feat.id, item.id)} className="btn-sm btn-del">
                                🗑 Delete
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Feature Type: INTERACTIVE FORM & FEEDBACK */}
            {feat.type === 'form' && (
              <div className="custom-form-container">
                <form onSubmit={(e) => handleSubmitCustomForm(feat.id, e)} className="custom-form-panel">
                  <h3>Submit New Entry to {feat.name}</h3>
                  <div className="form-row-2">
                    <label>
                      Name / Title
                      <input
                        type="text"
                        required
                        placeholder="e.g. John Doe"
                        value={customFormValues[feat.id]?.name || ''}
                        onChange={(e) => setCustomFormValues({
                          ...customFormValues,
                          [feat.id]: { ...(customFormValues[feat.id] || {}), name: e.target.value },
                        })}
                      />
                    </label>
                    <label>
                      Category / Topic
                      <input
                        type="text"
                        placeholder="e.g. Customer Support"
                        value={customFormValues[feat.id]?.category || ''}
                        onChange={(e) => setCustomFormValues({
                          ...customFormValues,
                          [feat.id]: { ...(customFormValues[feat.id] || {}), category: e.target.value },
                        })}
                      />
                    </label>
                  </div>
                  <label>
                    Details / Feedback Message
                    <textarea
                      rows={3}
                      required
                      placeholder="Enter details or notes..."
                      value={customFormValues[feat.id]?.details || ''}
                      onChange={(e) => setCustomFormValues({
                        ...customFormValues,
                        [feat.id]: { ...(customFormValues[feat.id] || {}), details: e.target.value },
                      })}
                    />
                  </label>
                  <button type="submit" className="btn-primary">
                    📤 Submit Entry
                  </button>
                </form>

                <div className="custom-submissions-panel">
                  <h3>Recent Submissions ({(feat.formSubmissions || []).length})</h3>
                  {(feat.formSubmissions || []).length === 0 ? (
                    <p className="muted">No submissions recorded yet. Fill out the form above.</p>
                  ) : (
                    <ul className="submissions-list">
                      {(feat.formSubmissions || []).map((sub) => (
                        <li key={sub.id} className="submission-card">
                          <div>
                            <strong>{sub.data.name || 'Submission'}</strong> — <span className="badge-pill">{sub.data.category || 'General'}</span>
                            <p className="submission-text">{sub.data.details}</p>
                          </div>
                          <small className="muted">{sub.date}</small>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}

            {/* Feature Type: METRICS & KPI */}
            {feat.type === 'metrics' && (
              <div className="custom-metrics-container">
                <div className="dashboard-grid">
                  {feat.items.map((item) => (
                    <div key={item.id} className="dashboard-card feat-metric-card">
                      <span className="stat-label">{item.title}</span>
                      <strong>{item.value || '100%'}</strong>
                      <small className="stat-sub">{item.subtitle}</small>
                      <button type="button" onClick={() => handleDeleteCustomItem(feat.id, item.id)} className="btn-del-corner" title="Remove metric">✕</button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Feature Type: NOTES & SCRATCHPAD */}
            {feat.type === 'notes' && (
              <div className="custom-notes-container">
                <div className="notes-add-row">
                  <input
                    type="text"
                    placeholder="Write a quick note or key insight..."
                    value={customItemInput[feat.id] || ''}
                    onChange={(e) => setCustomItemInput({ ...customItemInput, [feat.id]: e.target.value })}
                    onKeyDown={(e) => { if (e.key === 'Enter') handleAddCustomItem(feat.id); }}
                  />
                  <button type="button" onClick={() => handleAddCustomItem(feat.id)} className="btn-primary">
                    📝 Post Note
                  </button>
                </div>
                <div className="notes-grid">
                  {feat.items.map((item) => (
                    <div key={item.id} className="note-card">
                      <p className="note-body">{item.title}</p>
                      <div className="note-footer">
                        <small>{item.date}</small>
                        <button type="button" onClick={() => handleDeleteCustomItem(feat.id, item.id)} className="btn-del-sm">✕</button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        ))}

        {/* Media Gallery */}
        <section id="media-gallery" className="content-block">
          <h2>Media Gallery</h2>
          {media.length === 0 ? (
            <p className="muted">No media items uploaded yet. Click "Add Media" in the top bar.</p>
          ) : (
            <div className="media-grid">
              {media.map((item) => {
                const isImg = item.type.startsWith('image/');
                const isVid = item.type.startsWith('video/');
                return (
                  <div key={item.id} className="media-card">
                    {isImg ? (
                      <img src={item.url} alt={item.name} className="media-image" />
                    ) : isVid ? (
                      <video src={item.url} controls className="media-video" />
                    ) : (
                      <div className="media-file">
                        <span className="media-icon">📄</span>
                        <span>{item.name}</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* Quick Access */}
        <section id="quick-access" className="content-block">
          <div className="panel">
            <h2>Quick Access</h2>
            <p className="muted signed-in-msg">
              ✅ Open workspace. You have full edit access to this site.
            </p>
          </div>
        </section>
      </main>

      {/* MODAL 1: Create New Record */}
      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <form className="modal" onSubmit={handleCreate} onClick={(e) => e.stopPropagation()}>
            <h2>Create New Record</h2>
            <label>
              Name / Title
              <input
                autoFocus
                type="text"
                value={createName}
                onChange={(e) => setCreateName(e.target.value)}
                placeholder="e.g. Alex Johnson"
                required
              />
            </label>
            <label>
              Role / Category / Department
              <input
                type="text"
                value={createRole}
                onChange={(e) => setCreateRole(e.target.value)}
                placeholder="e.g. Lead Doctor, Active Student, Admin..."
              />
            </label>
            <div className="modal-actions">
              <button type="button" className="btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
              <button type="submit" className="btn-primary">Create Record</button>
            </div>
          </form>
        </div>
      )}

      {/* MODAL 2: Edit Existing Record */}
      {editRecord && (
        <div className="modal-overlay" onClick={() => setEditRecord(null)}>
          <form className="modal" onSubmit={handleSaveEdit} onClick={(e) => e.stopPropagation()}>
            <h2>✏️ Edit Record #{editRecord.id.toString().slice(-4)}</h2>
            <label>
              Name / Title
              <input
                autoFocus
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                required
              />
            </label>
            <label>
              Role / Category / Details
              <input
                type="text"
                value={editRole}
                onChange={(e) => setEditRole(e.target.value)}
              />
            </label>
            <div className="modal-actions">
              <button type="button" className="btn-ghost" onClick={() => setEditRecord(null)}>Cancel</button>
              <button type="submit" className="btn-primary">Save Changes</button>
            </div>
          </form>
        </div>
      )}

      {/* MODAL 3: In-Website Feature Studio (Add Custom Feature / AI Copilot) */}
      {showFeatureStudio && (
        <div className="modal-overlay" onClick={() => setShowFeatureStudio(false)}>
          <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-tabs">
              <h2>➕ Feature Studio: Add New Feature to Website</h2>
              <div className="modal-tabs">
                <button
                  type="button"
                  onClick={() => setFeatureTab('builder')}
                  className={`modal-tab-btn ${featureTab === 'builder' ? 'active' : ''}`}
                >
                  🛠 Feature Builder
                </button>
                <button
                  type="button"
                  onClick={() => setFeatureTab('ai')}
                  className={`modal-tab-btn ${featureTab === 'ai' ? 'active' : ''}`}
                >
                  🤖 AI Feature Copilot
                </button>
              </div>
            </div>

            {featureTab === 'builder' ? (
              <form onSubmit={handleAddFeature}>
                <div className="form-row-2">
                  <label>
                    Feature Title / Name
                    <input
                      autoFocus
                      type="text"
                      required
                      placeholder="e.g. Doctor Rosters, Invoices, Feedback..."
                      value={newFeatureName}
                      onChange={(e) => setNewFeatureName(e.target.value)}
                    />
                  </label>
                  <label>
                    Feature Type
                    <select
                      value={newFeatureType}
                      onChange={(e) => setNewFeatureType(e.target.value as any)}
                      className="input-select"
                    >
                      <option value="table">📋 Data Table / Records Manager</option>
                      <option value="kanban">📌 Kanban Workflow Board</option>
                      <option value="form">📝 Form &amp; Feedback Collector</option>
                      <option value="metrics">📈 KPI &amp; Analytics Cards</option>
                      <option value="notes">💡 Scratchpad &amp; Quick Notes</option>
                    </select>
                  </label>
                </div>

                <div className="form-row-2">
                  <label>
                    Choose Icon
                    <div className="icon-picker">
                      {['⚡', '📊', '📝', '💰', '📅', '👥', '🛒', '⚙️', '🎯', '🚀', '💬', '📦', '🏥', '🎓', '🛠️'].map((ic) => (
                        <button
                          key={ic}
                          type="button"
                          onClick={() => setNewFeatureIcon(ic)}
                          className={`icon-btn ${newFeatureIcon === ic ? 'selected' : ''}`}
                        >
                          {ic}
                        </button>
                      ))}
                    </div>
                  </label>

                  <label>
                    Description / Purpose
                    <input
                      type="text"
                      placeholder="Brief note about this feature..."
                      value={newFeatureDesc}
                      onChange={(e) => setNewFeatureDesc(e.target.value)}
                    />
                  </label>
                </div>

                <div className="modal-actions">
                  <button type="button" className="btn-ghost" onClick={() => setShowFeatureStudio(false)}>Cancel</button>
                  <button type="submit" className="btn-primary">✨ Add Feature to Website</button>
                </div>
              </form>
            ) : (
              <div className="ai-feature-copilot">
                <p className="muted">Type what feature you want to add, or choose a 1-click popular preset:</p>
                <div className="preset-grid">
                  <button
                    type="button"
                    onClick={() => handleApplyPreset('Invoice & Payment Tracker', '💰', 'table', 'Track billing, transactions, and client payment invoices')}
                    className="preset-chip"
                  >
                    💰 Invoice &amp; Payment Tracker
                  </button>
                  <button
                    type="button"
                    onClick={() => handleApplyPreset('Appointment / Roster Board', '📅', 'kanban', 'Manage scheduled shifts, patient visits, or bookings')}
                    className="preset-chip"
                  >
                    📅 Appointment / Roster Board
                  </button>
                  <button
                    type="button"
                    onClick={() => handleApplyPreset('Customer Feedback Collector', '📝', 'form', 'Collect reviews, inquiries, and customer feedback')}
                    className="preset-chip"
                  >
                    📝 Customer Feedback Collector
                  </button>
                  <button
                    type="button"
                    onClick={() => handleApplyPreset('Live KPI & Performance Metrics', '📈', 'metrics', 'Display key operational metrics and revenue gauges')}
                    className="preset-chip"
                  >
                    📈 Live KPI &amp; Performance Metrics
                  </button>
                  <button
                    type="button"
                    onClick={() => handleApplyPreset('Task & Sprint Kanban', '📋', 'kanban', 'To Do, In Progress, and Completed sprint task cards')}
                    className="preset-chip"
                  >
                    📋 Task &amp; Sprint Kanban
                  </button>
                </div>

                <div className="ai-prompt-box">
                  <label>
                    Custom Prompt for AI Feature Generator
                    <textarea
                      rows={3}
                      placeholder="e.g. Add an employee clock-in tracker with shift status and attendance timestamps..."
                      value={aiPrompt}
                      onChange={(e) => setAiPrompt(e.target.value)}
                    />
                  </label>
                  <div className="modal-actions">
                    <button type="button" className="btn-ghost" onClick={() => setShowFeatureStudio(false)}>Cancel</button>
                    <button type="button" onClick={handleAiGenerateFeature} className="btn-primary btn-glow">
                      ⚡ Generate &amp; Add Feature
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODAL 4: Website Customizer & Theme Studio */}
      {showCustomizer && (
        <div className="modal-overlay" onClick={() => setShowCustomizer(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>🎨 Website &amp; Theme Customizer</h2>
            <label>
              Website / Brand Name
              <input
                type="text"
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
                placeholder="e.g. Apex Health Portal"
              />
            </label>

            <label>
              Tagline / Subtitle
              <input
                type="text"
                value={appSubtitle}
                onChange={(e) => setAppSubtitle(e.target.value)}
                placeholder="e.g. Next-Gen Enterprise Solution"
              />
            </label>

            <label>
              Accent Color Palette
              <div className="palette-grid">
                {[
                  { id: 'cyan', label: 'Cyber Cyan', color: '#38bdf8' },
                  { id: 'indigo', label: 'Royal Indigo', color: '#6366f1' },
                  { id: 'emerald', label: 'Emerald Mint', color: '#10b981' },
                  { id: 'amber', label: 'Sunset Amber', color: '#f59e0b' },
                  { id: 'rose', label: 'Rose Coral', color: '#f43f5e' },
                  { id: 'purple', label: 'Neon Purple', color: '#a855f7' },
                ].map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => setAccentColor(c.id)}
                    className={`color-swatch ${accentColor === c.id ? 'selected' : ''}`}
                    style={{ backgroundColor: c.color }}
                    title={c.label}
                  >
                    {accentColor === c.id ? '✓' : ''}
                  </button>
                ))}
              </div>
            </label>

            <div className="form-row-2">
              <label>
                Theme Mode
                <div className="btn-group">
                  <button
                    type="button"
                    onClick={() => setThemeMode('dark')}
                    className={`btn-toggle ${themeMode === 'dark' ? 'active' : ''}`}
                  >
                    🌙 Dark
                  </button>
                  <button
                    type="button"
                    onClick={() => setThemeMode('light')}
                    className={`btn-toggle ${themeMode === 'light' ? 'active' : ''}`}
                  >
                    ☀️ Light
                  </button>
                </div>
              </label>
            </div>

            <div className="modal-actions">
              <button type="button" onClick={handleResetDefaults} className="btn-danger-ghost">
                🔄 Reset to Defaults
              </button>
              <button
                type="button"
                onClick={() => {
                  saveToStorage();
                  setShowCustomizer(false);
                  notify('Website customizations saved successfully!');
                }}
                className="btn-primary"
              >
                💾 Save &amp; Apply
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Quick Action Studio Button */}
      <button
        type="button"
        onClick={() => setShowFeatureStudio(true)}
        className="floating-studio-btn"
        title="Open Feature Studio to add new features"
      >
        ✨ Add Feature
      </button>
    </div>
  );
};

export default App;
