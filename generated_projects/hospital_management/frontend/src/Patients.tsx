import React, { useState, useEffect } from 'react';

interface Props {
  onCountChange?: (count: number) => void;
}

export interface PatientsRecord {
  id: number;
  name: string;
  f2: string;
  f3: string;
  status: string;
  category?: string;
  createdAt?: string;
}

const Patients: React.FC<Props> = ({ onCountChange }) => {
  const STORAGE_KEY = "res_data_hospital_management_system_patients";
  const [records, setRecords] = useState<PatientsRecord[]>([]);
  const [search, setSearch] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [newName, setNewName] = useState('');
  const [newF2, setNewF2] = useState('');
  const [newF3, setNewF3] = useState('');
  const [newStatus, setNewStatus] = useState('Active');

  const [editItem, setEditItem] = useState<PatientsRecord | null>(null);
  const [editName, setEditName] = useState('');
  const [editF2, setEditF2] = useState('');
  const [editF3, setEditF3] = useState('');
  const [editStatus, setEditStatus] = useState('');
  const [msg, setMsg] = useState<string | null>(null);

  const notify = (text: string) => {
    setMsg(text);
    setTimeout(() => setMsg(null), 3500);
  };

  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const restored = JSON.parse(saved);
        if (Array.isArray(restored)) {
          setRecords(restored);
          onCountChange?.(restored.length);
        }
      }
    } catch {
      // ignore
    }
  }, []);

  const save = (next: PatientsRecord[]) => {
    setRecords(next);
    onCountChange?.(next.length);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    } catch {
      // ignore
    }
  };

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    const item: PatientsRecord = {
      id: Date.now(),
      name: newName.trim(),
      f2: newF2.trim() || 'General',
      f3: newF3.trim() || 'Standard',
      status: newStatus.trim() || 'Active',
      category: newF2.trim() || 'General',
      createdAt: new Date().toLocaleDateString(),
    };
    const next = [item, ...records];
    save(next);
    setShowAdd(false);
    setNewName('');
    setNewF2('');
    setNewF3('');
    notify('Created "' + item.name + '" successfully!');
  };

  const openEdit = (it: PatientsRecord) => {
    setEditItem(it);
    setEditName(it.name);
    setEditF2(it.f2 || it.category || '');
    setEditF3(it.f3 || '');
    setEditStatus(it.status || 'Active');
  };

  const handleSaveEdit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editItem || !editName.trim()) return;
    const next = records.map((it) =>
      it.id === editItem.id
        ? {
            ...it,
            name: editName.trim(),
            f2: editF2.trim() || it.f2,
            f3: editF3.trim() || it.f3,
            category: editF2.trim() || it.category,
            status: editStatus.trim() || it.status,
          }
        : it
    );
    save(next);
    setEditItem(null);
    notify('Updated "' + editName + '" successfully!');
  };

  const handleDelete = (id: number) => {
    if (window.confirm('Remove this Patient record?')) {
      const next = records.filter((it) => it.id !== id);
      save(next);
      notify('Record removed from workspace.');
    }
  };

  const filtered = records.filter((it) =>
    (it.name || '').toLowerCase().includes(search.toLowerCase()) ||
    (it.f2 || it.category || '').toLowerCase().includes(search.toLowerCase()) ||
    (it.status || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="resource-card entity-manager-block">
      <div className="section-head-row">
        <div>
          <h2>Patients <span className="badge-pill">{records.length}</span></h2>
          <p className="muted">Manage, edit, or remove patients in your workspace.</p>
        </div>
        <div className="action-btn-group">
          <input
            type="text"
            placeholder="Filter records…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-sm"
            style={{ width: '160px' }}
          />
          <button type="button" onClick={() => setShowAdd(true)} className="btn-sm btn-primary">
            + Add Patient
          </button>
        </div>
      </div>

      {msg && <div className="banner toast-banner" style={{ margin: '10px 0' }}>{msg}</div>}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Patients Name</th>
              <th>Category</th>
              <th>Detail / Metric</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan={6} className="muted text-center py-4">No records found. Click "Add Patient" to create one.</td></tr>
            ) : (
              filtered.map((it, idx) => (
                <tr key={it.id}>
                  <td>{idx + 1}</td>
                  <td><strong>{it.name}</strong></td>
                  <td><span className="badge-pill">{it.f2 || it.category || 'General'}</span></td>
                  <td>{it.f3 || '—'}</td>
                  <td><span className="status-pill status-active">{it.status || 'Active'}</span></td>
                  <td>
                    <div className="action-btn-group">
                      <button type="button" onClick={() => openEdit(it)} className="btn-sm btn-edit" title="Edit record">
                        Edit
                      </button>
                      <button type="button" onClick={() => handleDelete(it.id)} className="btn-sm btn-del" title="Remove record">
                        Remove
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Add Modal */}
      {showAdd && (
        <div className="modal-overlay modal-backdrop" onClick={() => setShowAdd(false)}>
          <form className="modal modal-card" onSubmit={handleAdd} onClick={(e) => e.stopPropagation()}>
            <h2>+ Add New Patient</h2>
            <label>Patients Name *
              <input autoFocus type="text" required value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Enter title/name" />
            </label>
            <label>Category
              <input type="text" value={newF2} onChange={(e) => setNewF2(e.target.value)} placeholder="Enter category" />
            </label>
            <label>Detail / Metric
              <input type="text" value={newF3} onChange={(e) => setNewF3(e.target.value)} placeholder="Enter detail / metric" />
            </label>
            <label>Status
              <input type="text" value={newStatus} onChange={(e) => setNewStatus(e.target.value)} placeholder="e.g. Active" />
            </label>
            <div className="modal-actions form-actions">
              <button type="button" className="btn-ghost btn-outline" onClick={() => setShowAdd(false)}>Cancel</button>
              <button type="submit" className="btn-primary">Add Patient</button>
            </div>
          </form>
        </div>
      )}

      {/* Edit Modal */}
      {editItem && (
        <div className="modal-overlay modal-backdrop" onClick={() => setEditItem(null)}>
          <form className="modal modal-card" onSubmit={handleSaveEdit} onClick={(e) => e.stopPropagation()}>
            <h2>Edit Patient #{editItem.id.toString().slice(-4)}</h2>
            <label>Patients Name *
              <input autoFocus type="text" required value={editName} onChange={(e) => setEditName(e.target.value)} />
            </label>
            <label>Category
              <input type="text" value={editF2} onChange={(e) => setEditF2(e.target.value)} />
            </label>
            <label>Detail / Metric
              <input type="text" value={editF3} onChange={(e) => setEditF3(e.target.value)} />
            </label>
            <label>Status
              <input type="text" value={editStatus} onChange={(e) => setEditStatus(e.target.value)} />
            </label>
            <div className="modal-actions form-actions">
              <button type="button" className="btn-ghost btn-outline" onClick={() => setEditItem(null)}>Cancel</button>
              <button type="submit" className="btn-primary">Save Changes</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default Patients;
