import React from 'react';
import { LANG_NAMES, type LangCode } from './languages';

interface Props { lang: LangCode; onChange: (code: LangCode) => void; }

const LanguageSwitcher: React.FC<Props> = ({ lang, onChange }) => (
  <div className="lang-switcher">
    <select value={lang} onChange={(e) => onChange(e.target.value as LangCode)}>
      {Object.entries(LANG_NAMES).map(([code, name]) => (
        <option key={code} value={code}>{name}</option>
      ))}
    </select>
  </div>
);

export default LanguageSwitcher;
