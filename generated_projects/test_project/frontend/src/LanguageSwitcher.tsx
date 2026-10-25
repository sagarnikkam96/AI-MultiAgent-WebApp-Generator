import React from 'react';
import { useLanguage } from './LanguageContext';
const LanguageSwitcher: React.FC = () => {
  const { lang, setLang } = useLanguage();
  return <label className="language-control">Language<select aria-label="Language" value={lang} onChange={(event) => setLang(event.target.value as typeof lang)}><option value="en">English</option><option value="hi">हिन्दी</option><option value="kn">ಕನ್ನಡ</option><option value="mr">मराठी</option><option value="te">తెలుగు</option></select></label>;
};
export default LanguageSwitcher;
