import React, { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { coreTranslations, homeActionTranslations, LANG_NAMES, translations, type LangCode } from './i18n';

interface LanguageContextValue {
  lang: LangCode;
  setLang: (code: LangCode) => void;
  t: (key: string, vars?: Record<string, string>) => string;
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [lang, setLang] = useState<LangCode>(() => {
    const savedLanguage = window.localStorage.getItem('output-language');
    return savedLanguage && savedLanguage in LANG_NAMES ? savedLanguage as LangCode : 'en';
  });

  useEffect(() => {
    window.localStorage.setItem('output-language', lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ur' || lang === 'sd' || lang === 'ks' ? 'rtl' : 'ltr';
  }, [lang]);

  const t = (key: string, vars?: Record<string, string>) => {
    let text = homeActionTranslations[lang]?.[key]
      || coreTranslations[lang]?.[key]
      || translations[lang]?.[key]
      || homeActionTranslations.en?.[key]
      || translations.en[key]
      || key;
    if (vars) {
      Object.entries(vars).forEach(([k, v]) => {
        text = text.replace(`{${k}}`, v);
      });
    }
    return text;
  };
  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextValue => {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    const fallback = (key: string, vars?: Record<string, string>) => {
      let text = homeActionTranslations.en?.[key] || coreTranslations.en?.[key] || translations.en[key] || key;
      if (vars) {
        Object.entries(vars).forEach(([k, v]) => {
          text = text.replace(`{${k}}`, v);
        });
      }
      return text;
    };
    return { lang: 'en', setLang: () => {}, t: fallback };
  }
  return ctx;
};
