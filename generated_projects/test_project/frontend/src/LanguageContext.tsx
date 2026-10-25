import React, { createContext, useContext, useState, type ReactNode } from 'react';
import { translations, type LangCode } from './languages';

const DEFAULT_LANG: LangCode = 'en';

interface LanguageContextValue {
  lang: LangCode;
  setLang: (code: LangCode) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [lang, setLang] = useState<LangCode>(DEFAULT_LANG);
  const t = (key: string) => translations[lang][key] || key;
  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextValue => {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    const fallback = (key: string) => translations[DEFAULT_LANG][key] || key;
    return { lang: DEFAULT_LANG, setLang: () => {}, t: fallback };
  }
  return ctx;
};
