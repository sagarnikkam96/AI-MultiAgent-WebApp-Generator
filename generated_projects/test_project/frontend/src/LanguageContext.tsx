import React, { createContext, useContext, useMemo, useState, type ReactNode } from 'react';
import { translations, type LangCode } from './languages';
interface LanguageContextValue { lang: LangCode; setLang: (lang: LangCode) => void; t: (key: string) => string; }
const LanguageContext = createContext<LanguageContextValue | null>(null);
export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [lang, setLang] = useState<LangCode>('en');
  const value = useMemo(() => ({ lang, setLang, t: (key: string) => (translations[lang] as Record<string, string>)[key] ?? key }), [lang]);
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
};
export const useLanguage = () => { const value = useContext(LanguageContext); if (!value) throw new Error('LanguageProvider is required.'); return value; };
