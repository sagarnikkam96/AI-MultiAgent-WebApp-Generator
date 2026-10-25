import React from 'react';
import Login from './Login';
import Dashboard from './Dashboard';
import LanguageSwitcher from './LanguageSwitcher';
import { LanguageProvider, useLanguage } from './LanguageContext';
import SectionOne from './SectionOne';
import SectionTwo from './SectionTwo';

export interface AppRecord { id: number; name: string; field2: string; field3: string; createdAt: string; }

const InnerApp: React.FC = () => {
  const { lang, setLang, t } = useLanguage();
const [user,setUser]=React.useState<string|null>(null);
const [msg,setMsg]=React.useState<string|null>(null);
const [recs,setRecs]=React.useState<AppRecord[]>([]);
const [showCreate,setShow]=React.useState(false);
const [cN,setCN]=React.useState('');
const [c2,setC2]=React.useState('');
const [c3,setC3]=React.useState('');
const [media,setMedia]=React.useState<Array<{id:number;name:string;url:string;type:string}>>([]);
const [showMedia,setShowMedia]=React.useState(false);
const ntf=(x:string)=>{setMsg(x);window.setTimeout(()=>setMsg(null),4000);};
const login=(e:string)=>{setUser(e);ntf(t('welcomeBack').replace('{email}',e));};
const logout=()=>{setUser(null);ntf(t('signedOut'));};
const openC=()=>{if(!user){ntf(t('signInFirst'));return;}setCN('');setC2('');setC3('');setShow(true);};
const create=(e:React.FormEvent)=>{e.preventDefault();var n=cN.trim();if(!n)return;setRecs(p=>[{id:Date.now(),name:n,field2:c2.trim()||'General',field3:c3.trim()||'Active',createdAt:new Date().toLocaleString()},...p]);setShow(false);ntf(t('createdSuccess').replace('{name}',n));};
const insights=()=>{document.getElementById('insights-section')?.scrollIntoView({behavior:'smooth'});};
const handleMediaChange=(e:React.ChangeEvent<HTMLInputElement>)=>{const files=Array.from(e.target.files||[]);setMedia(p=>[...p,...files.map((f,i)=>({id:Date.now()+i,name:f.name,url:URL.createObjectURL(f),type:f.type}))]);e.target.value='';};

return (<div className="app-shell">
<aside className="sidebar">
<div className="brand">Test Media</div>
<nav className="nav-list">
<a href="#dashboard" className="active">{t('dashboard')}</a>
<a href="#section-1" className="">{t('overview')}</a>
<a href="#section-2" className="">{t('reports')}</a>
<a href="#quick-access">{t('quickAccess')}</a>
</nav>
<LanguageSwitcher lang={lang} onChange={setLang}/>
{user?(<div className="sidebar-user"><span className="avatar">{user[0]?.toUpperCase()}</span>
<div><strong>{user}</strong><button className="btn-ghost" onClick={logout}>{t('signOut')}</button></div></div>):
<p className="muted">{t('notSignedIn')}</p>}
</aside>
<main className="page-content">
<header className="topbar">
<h1>Test Media</h1>
<div className="top-actions">
<button onClick={openC}>{t('createNew')}</button>
<button onClick={()=>document.getElementById('media-input')?.click()} className="btn btn-ghost">{t('addMedia')}</button>
<input id="media-input" type="file" multiple accept="image/*,video/*,.pdf,.doc,.docx,.txt,.md" onChange={handleMediaChange} hidden />
<button onClick={insights}>{t('insights')}</button></div></header>
{msg&&<div className="banner">{msg}</div>}
<section id="dashboard" className="content-block"><Dashboard records={recs} /></section>
<section id="section-1" className="content-block"><SectionOne /></section>
<section id="section-2" className="content-block"><SectionTwo /></section>
<section id="insights-section" className="content-block"><h2>{t('insights')}</h2>
<p className="muted">{t('insightsSubtitle')}</p>
<table><thead><tr>
<th>Name</th>
<th>Type</th>
<th>Status</th>
<th>Created</th>
</tr></thead><tbody>
{recs.length===0?(<tr><td colSpan={4} className="muted">{t('noRecords')}</td></tr>):
recs.map((r,i)=>(<tr key={r.id}><td>{i+1}</td><td>{r.name}</td><td>{r.field2}</td><td>{r.createdAt}</td></tr>))}
</tbody></table></section>
<section id="media-gallery" className="content-block"><h2>{t('mediaGallery')}</h2>
{media.length===0?(<p className="muted">{t('noMedia')}</p>):(
<div className="media-grid">{media.map((item)=>{const isImg=item.type.startsWith('image/');const isVid=item.type.startsWith('video/');return (<div key={item.id} className="media-card">{isImg?<img src={item.url} alt={item.name} className="media-image" />:isVid?<video src={item.url} controls className="media-video" />:<div className="media-file"><span className="media-icon">📄</span><span>{item.name}</span></div>}</div>);})}</div>)}</section>
<section id="quick-access" className="content-block"><div className="panel"><h2>{t('quickAccess')}</h2>
{user?(<p className="muted signed-in-msg">{t('signedInMsg').replace('{user}',user)}</p>):(<Login onLogin={login}/>)}
</div></section></main>
{showCreate&&(<div className="modal-overlay" onClick={()=>setShow(false)}>
<form className="modal" onSubmit={create} onClick={e=>e.stopPropagation()}><h2>{t('createRecord')}</h2>
<label>{t('name')}</label><input autoFocus type="text" value={cN} onChange={e=>setCN(e.target.value)} placeholder=
  'e.g. Enter a title' required />
<label>{t('items')}</label><input type="text" value={c2} onChange={e=>setC2(e.target.value)} placeholder=
  'e.g. Add a detail' />
<label>{t('reports')}</label><input type="text" value={c3} onChange={e=>setC3(e.target.value)} placeholder=
  'e.g. Select status' />
<div className="modal-actions"><button type="button" className="btn-ghost" onClick={()=>setShow(false)}>{t('cancel')}</button>
<button type="submit">{t('create')}</button></div></form></div>)}
</div>);};

const App: React.FC = () => (
  <LanguageProvider>
    <InnerApp />
  </LanguageProvider>
);

export default App;

