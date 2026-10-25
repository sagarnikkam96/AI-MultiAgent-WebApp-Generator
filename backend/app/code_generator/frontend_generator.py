from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .code_generator import CodeGenerator, PromptProvider
from .code_schema import GeneratedFile
from .project_slug import project_slug
from .website_spec import (
    LANG_CODES,
    build_language_dictionaries,
    derive_website_spec,
    detect_website_key,
)
from ..visual_design.engine import PremiumDesignEngine


class FrontendGenerator(CodeGenerator):
    """Build a prompt-specific React application from shared domain blueprints."""

    _VISUAL_ASSETS: dict[str, tuple[tuple[str, str], tuple[str, str]]] = {
        "hospital": (
            ("https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=1000&q=85",
             "Doctors caring for a patient in a modern hospital"),
            ("https://images.unsplash.com/photo-1587745416684-47953f16f02f?auto=format&fit=crop&w=700&q=85",
             "Emergency ambulance ready for hospital transport"),
        ),
        "education": (
            ("https://images.unsplash.com/photo-1523050854058-8df90110c9f1?auto=format&fit=crop&w=1000&q=85",
             "Students celebrating on a university campus"),
            ("https://images.unsplash.com/photo-1507842217343-583bb727c9f?auto=format&fit=crop&w=700&q=85",
             "Bookshelves in a college library"),
        ),
        "hospitality": (
            ("https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1000&q=85",
             "Contemporary hotel exterior beside a pool"),
            ("https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=700&q=85",
             "Calm, well-appointed hotel guest room"),
        ),
        "ecommerce": (
            ("https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1000&q=85",
             "Modern retail store displaying curated products"),
            ("https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=700&q=85",
             "Product detail photographed for an online catalog"),
        ),
        "railway": (
            ("https://images.unsplash.com/photo-1474487548417-781cb71495f3?auto=format&fit=crop&w=1000&q=85",
             "Passenger train traveling along a railway"),
            ("https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=700&q=85",
             "Green forest landscape along a railway journey"),
        ),
        "transit": (
            ("https://images.unsplash.com/photo-1570125909232-eb263c188f7e?auto=format&fit=crop&w=1000&q=85",
             "Modern transit city bus on route"),
            ("https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=700&q=85",
             "Public transport bus passenger terminal"),
        ),
        "temple": (
            ("https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1000&q=85",
             "Majestic temple architecture and spiritual sanctuary"),
            ("https://images.unsplash.com/photo-1609766857041-ed402ea8069a?auto=format&fit=crop&w=700&q=85",
             "Sacred temple bells and heritage sanctum"),
        ),
        "agriculture": (
            ("https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=1000&q=85",
             "Lush green agricultural farm fields"),
            ("https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&w=700&q=85",
             "Fresh crops and farmer agricultural produce"),
        ),
        "finance": (
            ("https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1000&q=85",
             "Modern financial center and analytics dashboard"),
            ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=700&q=85",
             "Global investment market graphs and banking"),
        ),
        "food_delivery": (
            ("https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1000&q=85",
             "Gourmet dining dish prepared in kitchen"),
            ("https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=700&q=85",
             "Fresh artisan pizza and dining delivery"),
        ),
        "real_estate": (
            ("https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=85",
             "Contemporary luxury villa and property"),
            ("https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=700&q=85",
             "Modern interior architecture and living estate"),
        ),
        "fitness": (
            ("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1000&q=85",
             "Modern athletic fitness training gym"),
            ("https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=700&q=85",
             "Weights and training equipment in health club"),
        ),
        "task": (
            ("https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?auto=format&fit=crop&w=1000&q=85",
             "Agile project planning checklist and workspace"),
            ("https://images.unsplash.com/photo-1507925921958-8a62f3d1a50d?auto=format&fit=crop&w=700&q=85",
             "Project task notes and sprint kanban board"),
        ),
    }

    _DOMAIN_BRANDING = {
        "hospital": ("Healthcare & Clinical Management", "Coordinated Patient Care, Medical Staff & Hospital Workflows"),
        "education": ("Campus & Learning Operations", "Keep academic programs, people, and campus services connected."),
        "hospitality": ("Guest & Hotel Operations", "Bring stays, rooms, bookings, and guest services into one view."),
        "ecommerce": ("Commerce Operations", "Manage products, orders, and customer activity in one workspace."),
        "food_delivery": ("Restaurant & Delivery Operations", "Coordinate menus, orders, restaurants, and delivery teams."),
        "finance": ("Financial Operations", "A clear workspace for accounts, transactions, and financial services."),
        "inventory": ("Inventory Operations", "Track stock, suppliers, and movement across your inventory."),
        "real_estate": ("Property Operations", "Organize listings, properties, clients, and viewings."),
        "travel": ("Travel Operations", "Coordinate destinations, itineraries, bookings, and travelers."),
        "fitness": ("Fitness & Membership Operations", "Keep members, classes, trainers, and plans in sync."),
        "task": ("Project & Task Operations", "Keep projects, teams, priorities, and work moving forward."),
        "railway": ("Railway & Transit Operations", "Coordinate trains, routes, stations, and schedules in one operational view."),
        "transit": ("City Transit & Fleet Operations", "Coordinate city bus routes, vehicle fleets, and transit schedules in one view."),
        "temple": ("Temple & Devotional Operations", "Coordinate pooja bookings, devotee records, donations, and sacred events."),
        "agriculture": ("Agriculture & Farm Operations", "Coordinate crop cultivation, farmers, equipment, and seasonal harvest yields."),
    }

    _BRAND_PATHS = {
        "hospital": 'd="M29 15h6v8h8v6h-8v8h-6v-8h-8v-6h8z"',
        "education": 'd="M14 20c7-4 15-4 22 0v24c-7-4-15-4-22 0z"',
        "hospitality": 'd="M18 39h28v7H18z"',
        "railway": 'd="M22 15h20v25H22z"',
        "transit": 'd="M20 16h24v22H20z M24 38v4 M40 38v4"',
        "ecommerce": 'd="M18 22h28l-3 23H21z"',
        "temple": 'd="M32 12l14 12H18z M22 24v18h20V24 M28 42v-8h8v8"',
        "agriculture": 'd="M32 44V20 M32 28c-6-4-10 0-10 4s4 4 10 2 M32 22c6-4 10 0 10 4s-4 4-10 2"',
        "generic": 'd="M18 18h28v28H18z"',
    }

    def generate(self, project_name: str, requirements: str) -> str:
        prompt = self._build_generation_prompt(project_name, requirements)
        return self._strip_markdown_fences(self._generate_text(prompt)).strip()

    def generate_files(
        self,
        prompt_provider: PromptProvider,
        project_name: str = "",
        requirements: Any = None,
        language: str = "en",
    ) -> list[GeneratedFile]:
        prompt = prompt_provider.get_prompt()
        raw_prompt = getattr(prompt_provider, "prompt", None)
        if isinstance(raw_prompt, str) and raw_prompt.strip():
            prompt = raw_prompt.strip()
        name = project_name.strip() or prompt.strip() or "Generated Project"
        return self._build_frontend_files(prompt, name, language=language)

    def _build_frontend_files(
        self, prompt: str, project_name: str = "", language: str = "en"
    ) -> list[GeneratedFile]:
        display_name = project_name.strip() or prompt.strip() or "Generated Project"
        spec = derive_website_spec(prompt, display_name)
        slug = self._project_slug(display_name)
        root = f"generated_projects/{slug}/frontend"
        files = [
            GeneratedFile(path=f"{root}/src/App.tsx", content=self._build_app_tsx(prompt, display_name, spec)),
            GeneratedFile(path=f"{root}/src/Login.tsx", content=self._build_login_tsx(display_name)),
            GeneratedFile(path=f"{root}/src/Dashboard.tsx", content=self.generate_dashboard_tsx(
                display_name, prompt, entities=spec.get("components", []),
                domain_key=spec.get("key", "generic"), entity_labels=spec.get("module_labels", {}),
            )),
            GeneratedFile(path=f"{root}/src/main.tsx", content=self.generate_main_tsx()),
            GeneratedFile(path=f"{root}/src/styles.css", content=self.generate_styles_css(prompt)),
            GeneratedFile(path=f"{root}/src/languages.ts", content=self._build_languages_ts(spec)),
            GeneratedFile(path=f"{root}/src/LanguageContext.tsx", content=self._build_language_context_tsx(language)),
            GeneratedFile(path=f"{root}/src/LanguageSwitcher.tsx", content=self._build_language_switcher_tsx()),
            GeneratedFile(path=f"{root}/src/assets/brand-mark.svg", content=self._build_brand_mark_svg(spec)),
            GeneratedFile(path=f"{root}/.env.example", content="VITE_API_BASE_URL=http://127.0.0.1:8001\n"),
            GeneratedFile(path=f"{root}/package.json", content=self.generate_package_json(display_name, prompt)),
            GeneratedFile(path=f"{root}/index.html", content=self.generate_index_html(display_name, prompt)),
            GeneratedFile(path=f"{root}/tsconfig.json", content=self.generate_tsconfig_json()),
            GeneratedFile(path=f"{root}/tsconfig.node.json", content=self.generate_tsconfig_node_json()),
            GeneratedFile(path=f"{root}/vite.config.ts", content=self.generate_vite_config_ts()),
        ]
        for component in spec.get("components", []):
            files.append(GeneratedFile(
                path=f"{root}/src/{component}.tsx",
                content=self.generate_resource_component(
                    f"{component}.tsx", display_name, prompt,
                    display_label=spec.get("module_labels", {}).get(component),
                    language=language,
                ),
            ))
        return files

    @staticmethod
    def _project_slug(value: str) -> str:
        return project_slug(value)

    def _build_app_tsx(self, prompt: str, project_name: str, spec: dict[str, Any]) -> str:
        key = str(spec.get("key", "generic"))
        components = list(spec.get("components", []))
        nav = [item for item in spec.get("nav", []) if item.get("component") != "Dashboard"]
        labels = spec.get("module_labels", {})
        branding, default_tagline = self._DOMAIN_BRANDING.get(
            key,
            ("Custom Operations Workspace", "A clear workspace shaped around your requirements."),
        )
        if key == "generic":
            labels_in_order = list(labels.values())
            default_tagline = (
                f"Manage {', '.join(labels_in_order[:4])}"
                if labels_in_order
                else f"A focused application for {project_name}."
            )
        hero_images = self._VISUAL_ASSETS.get(key, ())
        primary_label = labels.get(components[0], components[0]) if components else str(spec.get("record", {}).get("name_label", {}).get("en", "Record"))
        count_keys = {component: self._count_key(component) for component in components}
        entity_seed = {count_key: 0 for count_key in count_keys.values()}
        initial_accent = self._resolve_domain_palette(prompt)["accent"]

        imports = [
            "import React, { useState, useEffect } from 'react';",
"import AiChat from './components/AiChat';",
            "import brandMark from './assets/brand-mark.svg';",
            "import Login from './Login';",
            "import Dashboard from './Dashboard';",
            "import LanguageSwitcher from './LanguageSwitcher';",
            "import { LanguageProvider, useLanguage } from './LanguageContext';",
        ]
        imports.extend(f"import {component} from './{component}';" for component in components)
        import_text = "\n".join(imports)

        module_config = json.dumps([
            {"component": name, "label": labels.get(name, name), "href": f"#{item.get('id', 'dashboard')}"}
            for name, item in zip(components, nav)
        ], ensure_ascii=False)

        component_render = "\n".join(
            f'        <section id="{item.get("id", f"section-{index}")}" className="content-block">'
            f'<{component} onCountChange={{(count) => setEntityCounts((current) => ({{ ...current, {count_keys[component]!r}: count }}))}} />'
            f'</section>'
            for index, (component, item) in enumerate(zip(components, nav), 1)
        )

        visual = []
        for image_url, image_alt in hero_images:
            visual.append(
                f'            <img className="domain-hero-image" src={json.dumps(image_url)} alt={json.dumps(image_alt)} loading="lazy" />'
            )
        if not visual:
            for index, component in enumerate(components[:3], 1):
                visual.extend([
                    '            <article className="domain-hero-art-card">',
                    f'              <span>MODULE {index:02d}</span>',
                    f'              <strong>{{{json.dumps(labels.get(component, component), ensure_ascii=False)}}}</strong>',
                    '              <i aria-hidden="true" />',
                    '            </article>',
                ])
        visual_class = "domain-hero-visual" + (" domain-hero-art" if not hero_images else "")

        app_name_json = json.dumps(project_name, ensure_ascii=False)
        tagline_json = json.dumps(default_tagline, ensure_ascii=False)
        storage_key_val = f"website_custom_{self._project_slug(project_name)}"

        nav_markup = "\n".join(
            f'          <a href="#{item.get("id", f"section-{idx}")}" className={{active === "{item.get("id", f"section-{idx}")}" ? "active" : ""}} onClick={{() => setActive("{item.get("id", f"section-{idx}")}")}}>{{{json.dumps(labels.get(component, item.get("label", {}).get("en", component)), ensure_ascii=False)}}}</a>'
            for idx, (component, item) in enumerate(zip(components, nav), 1)
        )

        return f'''{import_text}

export interface AppRecord {{
  id: number;
  name: string;
  field2: string;
  field3: string;
  createdAt: string;
}}

export interface CustomFeatureItem {{
  id: number;
  title: string;
  subtitle?: string;
  status?: string;
  value?: string;
  date: string;
  createdAt?: string;
}}

export interface CustomFeature {{
  id: string;
  name: string;
  icon: string;
  description: string;
  type: 'table' | 'kanban' | 'form' | 'metrics' | 'notes';
  kind?: string;
  items: CustomFeatureItem[];
  formSubmissions?: Array<{{ id: number; data: Record<string, string>; date: string }}>;
}}

const modules = {module_config};
const initialCounts: Record<string, number> = {json.dumps(entity_seed)};
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\\/+$/, '') || 'http://127.0.0.1:8001';
const STORAGE_KEY = '{storage_key_val}';
const defaultSiteName = {app_name_json};
const defaultTagline = {tagline_json};

const palettes = [
  {{ name: 'Cyan', id: 'cyan', value: '#38bdf8', dark: ['#0d1b24', '#132833', '#1a3542'], light: ['#d7ebff', '#c3e0ff', '#a7cefa'] }},
  {{ name: 'Indigo', id: 'indigo', value: '#7868e8', dark: ['#161528', '#201e38', '#2a2750'], light: ['#e2e0ff', '#ccc8ff', '#b3adfa'] }},
  {{ name: 'Emerald', id: 'emerald', value: '#10b981', dark: ['#0f201c', '#172e28', '#204037'], light: ['#d8f3e5', '#c0ead5', '#a2ddc0'] }},
  {{ name: 'Amber', id: 'amber', value: '#f59e0b', dark: ['#211b12', '#302518', '#41321e'], light: ['#f9e8c7', '#f4d9a7', '#eac781'] }},
  {{ name: 'Rose', id: 'rose', value: '#d47b83', dark: ['#24171d', '#35212b', '#492b39'], light: ['#f8dfe4', '#f1cbd3', '#e6aeb9'] }},
  {{ name: 'Purple', id: 'purple', value: '#a855f7', dark: ['#1d1727', '#2a2038', '#3a2a50'], light: ['#eee0ff', '#ddc5ff', '#c8a6f4'] }},
];

const InnerApp: React.FC = () => {{
  const {{ t }} = useLanguage();
  const [appName, setAppName] = useState(t('appLabel') || defaultSiteName);
  const [appSubtitle, setAppSubtitle] = useState('Autonomous Web Application');
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const themeMode = theme;
  const setThemeMode = setTheme;
  const [accentColor, setAccentColor] = useState('{initial_accent}');
  const [user, setUser] = useState<string | null>(() => {{
    try {{
      const active = localStorage.getItem('website_active_user');
      if (!active) return null;
      const parsed = JSON.parse(active);
      return parsed?.name || parsed?.email || active;
    }} catch {{
      return localStorage.getItem('website_active_user');
    }}
  }});
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
  const [editCustomItem, setEditCustomItem] = useState<{{ featId: string; item: CustomFeatureItem }} | null>(null);
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
  const [customItemInput, setCustomItemInput] = useState<Record<string, string>>({{}});
  const featureItemDrafts = customItemInput;
  const setFeatureItemDrafts = setCustomItemInput;
  const [customFormValues, setCustomFormValues] = useState<Record<string, Record<string, string>>>({{}});
  const [reportSearch, setReportSearch] = useState('');
  const [media, setMedia] = useState<Array<{{ id: number; name: string; url: string; type: string }}>>([]);

  const selectedPalette = palettes.find((palette) => palette.value === accentColor) ?? palettes[0];
  const reportRecords = recs.filter((record) =>
    `${{record.name}} ${{record.field2}} ${{record.field3}}`.toLocaleLowerCase().includes(reportSearch.toLocaleLowerCase())
  );

  const ntf = (text: string) => {{
    setMsg(text);
    window.setTimeout(() => setMsg(null), 4500);
  }};

  useEffect(() => {{
    let cancelled = false;
    fetch(`${{API_BASE_URL}}/counts`)
      .then((response) => {{
        if (!response.ok) throw new Error(`Database count request failed (${{response.status}}).`);
        return response.json() as Promise<Record<string, unknown>>;
      }})
      .then((payload) => {{
        const counts: Record<string, number> = {{}};
        for (const [key, value] of Object.entries(payload)) {{
          if (typeof value === 'number' && Number.isInteger(value) && value >= 0) {{
            counts[key] = value;
          }}
        }}
        if (!cancelled && Object.keys(counts).length > 0) {{
          setDatabaseCounts(counts);
          setDatabaseCountError(null);
        }}
      }})
      .catch((error: unknown) => {{
        if (!cancelled) {{
          setDatabaseCountError(error instanceof Error ? error.message : 'Database counts are unavailable.');
        }}
      }});
    return () => {{ cancelled = true; }};
  }}, []);

  useEffect(() => {{
    const isLight = theme === 'light';
    const [pageColor, cardColor, innerColor] = selectedPalette[theme === 'light' ? 'light' : 'dark'];
    const variables: Record<string, string> = {{
      '--accent-primary': selectedPalette.value,
      '--accent-glow': `color-mix(in srgb, ${{selectedPalette.value}} 24%, transparent)`,
      '--bg-page': pageColor,
      '--bg-card': cardColor,
      '--bg-inner': innerColor,
      '--border-color': `color-mix(in srgb, ${{selectedPalette.value}} 22%, transparent)`,
      '--text-main': isLight ? '#1d2933' : '#f5f2e9',
      '--text-muted': isLight ? '#586775' : '#b6c0c4',
    }};
    for (const target of [document.documentElement, document.body, document.querySelector<HTMLElement>('.app-shell')]) {{
      if (!target) continue;
      for (const [property, value] of Object.entries(variables)) target.style.setProperty(property, value);
    }}
  }}, [accentColor, selectedPalette, theme]);

  useEffect(() => {{
    try {{
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {{
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
      }}
      setStorageReady(true);
    }} catch (error) {{
      setStorageError(error instanceof Error ? error.message : 'Saved website settings could not be loaded.');
    }}
  }}, []);

  useEffect(() => {{
    if (!storageReady) return;
    try {{
      localStorage.setItem(STORAGE_KEY, JSON.stringify({{
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
      }}));
      setStorageError(null);
    }} catch (error) {{
      setStorageError(error instanceof Error ? error.message : 'Website changes could not be saved in this browser.');
    }}
  }}, [storageReady, appName, appSubtitle, themeMode, accentColor, recs, customFeatures]);

  const login = (name: string, email?: string) => {{
    const display = name || email || 'User';
    setUser(display);
    try {{
      localStorage.setItem('website_active_user', JSON.stringify({{ name: display, email: email || '' }}));
    }} catch {{}}
    ntf(t('welcomeBack').replace('{{email}}', display));
  }};

  const logout = () => {{
    setUser(null);
    try {{
      localStorage.removeItem('website_active_user');
    }} catch {{}}
    ntf(t('signedOut'));
  }};

  const openC = () => {{
    if (!user) {{
      ntf(t('signInFirst'));
      return;
    }}
    setCN('');
    setC2('');
    setC3('');
    setShowCreate(true);
  }};

  const create = (e: React.FormEvent) => {{
    e.preventDefault();
    const n = cN.trim();
    if (!n) return;
    const newRec: AppRecord = {{
      id: Date.now(),
      name: n,
      field2: c2.trim() || 'General',
      field3: c3.trim() || 'Active',
      createdAt: new Date().toLocaleDateString(),
    }};
    const next = [newRec, ...recs];
    setRecs(next);
    setShowCreate(false);
    ntf(t('createdSuccess').replace('{{name}}', n));
  }};

  const openEdit = (r: AppRecord) => {{
    setEditRecord(r);
    setEN(r.name);
    setE2(r.field2);
    setE3(r.field3);
  }};

  const handleSaveEdit = (e: React.FormEvent) => {{
    e.preventDefault();
    if (!editRecord || !eN.trim()) return;
    const next = recs.map((r) =>
      r.id === editRecord.id ? {{ ...r, name: eN.trim(), field2: e2.trim() || r.field2, field3: e3.trim() || r.field3 }} : r
    );
    setRecs(next);
    setEditRecord(null);
    ntf('Record updated successfully!');
  }};

  const handleDeleteRecord = (id: number) => {{
    const next = recs.filter((r) => r.id !== id);
    setRecs(next);
    ntf('Record removed from workspace.');
  }};

  const handleAddFeature = (e?: React.FormEvent) => {{
    if (e) e.preventDefault();
    const name = newFeatureName.trim();
    if (!name) return;

    const feature: CustomFeature = {{
      id: `feat-${{Date.now()}}`,
      name,
      icon: newFeatureIcon || '⚡',
      description: newFeatureDesc.trim() || `Custom ${{newFeatureType}} module for ${{name}}`,
      type: newFeatureType,
      kind: newFeatureType,
      items: [],
      formSubmissions: [],
    }};

    setCustomFeatures((current) => [...current, feature]);
    setNewFeatureName('');
    setNewFeatureDesc('');
    setShowFeatureStudio(false);
    ntf('✨ Feature "' + name + '" added successfully to your website!');
  }};

  const handleApplyPreset = (presetName: string, icon: string, type: 'table' | 'kanban' | 'form' | 'metrics' | 'notes', desc: string) => {{
    setNewFeatureName(presetName);
    setNewFeatureIcon(icon);
    setNewFeatureType(type);
    setNewFeatureDesc(desc);
    setFeatureTab('builder');
  }};

  const handleAiGenerateFeature = () => {{
    const promptText = aiPrompt.trim();
    if (!promptText) return;

    let detectedType: 'table' | 'kanban' | 'form' | 'metrics' | 'notes' = 'table';
    let icon = '⚡';
    const lower = promptText.toLowerCase();

    if (lower.includes('kanban') || lower.includes('task') || lower.includes('sprint') || lower.includes('todo')) {{
      detectedType = 'kanban';
      icon = '📋';
    }} else if (lower.includes('form') || lower.includes('feedback') || lower.includes('survey') || lower.includes('inquiry')) {{
      detectedType = 'form';
      icon = '📝';
    }} else if (lower.includes('metric') || lower.includes('kpi') || lower.includes('analytics') || lower.includes('revenue') || lower.includes('stats')) {{
      detectedType = 'metrics';
      icon = '📈';
    }} else if (lower.includes('note') || lower.includes('memo') || lower.includes('scratchpad') || lower.includes('idea')) {{
      detectedType = 'notes';
      icon = '💡';
    }} else if (lower.includes('invoice') || lower.includes('payment') || lower.includes('bill')) {{
      icon = '💰';
    }} else if (lower.includes('schedule') || lower.includes('calendar') || lower.includes('booking') || lower.includes('appointment')) {{
      icon = '📅';
    }}

    const title = promptText.charAt(0).toUpperCase() + promptText.slice(1, 40);

    const feature: CustomFeature = {{
      id: `feat-${{Date.now()}}`,
      name: title,
      icon,
      description: `AI-generated feature based on prompt: "${{promptText}}"`,
      type: detectedType,
      kind: detectedType,
      items: [],
      formSubmissions: [],
    }};

    const next = [...customFeatures, feature];
    setCustomFeatures(next);
    setAiPrompt('');
    setShowFeatureStudio(false);
    ntf('🤖 AI successfully created and injected "' + title + '" into your website!');
  }};

  const handleDeleteFeature = (featId: string) => {{
    setCustomFeatures((current) => current.filter((f) => f.id !== featId));
    ntf('Feature section removed.');
  }};

  const handleMoveKanban = (featId: string, itemId: number, newStatus: string) => {{
    const next = customFeatures.map((f) => {{
      if (f.id !== featId) return f;
      return {{
        ...f,
        items: f.items.map((it) => (it.id === itemId ? {{ ...it, status: newStatus }} : it)),
      }};
    }});
    setCustomFeatures(next);
  }};

  const handleAddCustomItem = (featId: string) => {{
    const title = (customItemInput[featId] || '').trim();
    if (!title) return;
    const next = customFeatures.map((f) => {{
      if (f.id !== featId) return f;
      const newItem: CustomFeatureItem = {{
        id: Date.now(),
        title,
        status: f.type === 'kanban' ? 'todo' : 'Active',
        subtitle: 'Custom Item',
        value: 'New',
        date: 'Just now',
        createdAt: new Date().toLocaleDateString(),
      }};
      return {{ ...f, items: [newItem, ...f.items] }};
    }});
    setCustomFeatures(next);
    setCustomItemInput({{ ...customItemInput, [featId]: '' }});
  }};

  const handleDeleteCustomItem = (featId: string, itemId: number) => {{
    const next = customFeatures.map((f) => {{
      if (f.id !== featId) return f;
      return {{ ...f, items: f.items.filter((it) => it.id !== itemId) }};
    }});
    setCustomFeatures(next);
  }};

  const handleSubmitCustomForm = (featId: string, e: React.FormEvent) => {{
    e.preventDefault();
    const current = customFormValues[featId] || {{}};
    if (Object.keys(current).length === 0) return;
    const next = customFeatures.map((f) => {{
      if (f.id !== featId) return f;
      const sub = {{
        id: Date.now(),
        data: {{ ...current }},
        date: new Date().toLocaleString(),
      }};
      return {{ ...f, formSubmissions: [sub, ...(f.formSubmissions || [])] }};
    }});
    setCustomFeatures(next);
    setCustomFormValues({{ ...customFormValues, [featId]: {{}} }});
    ntf('Form submission recorded successfully!');
  }};

  const handleResetDefaults = () => {{
    if (window.confirm('Reset all website edits and custom features back to default generated state?')) {{
      localStorage.removeItem(STORAGE_KEY);
      setAppName(t('appLabel') || defaultSiteName);
      setAppSubtitle('Autonomous Web Application');
      setThemeMode('dark');
      setAccentColor('{initial_accent}');
      setCustomFeatures([]);
      setRecs([]);
      setShowCustomizer(false);
      ntf('Website restored to original state.');
    }}
  }};

  const handleMediaChange = (e: React.ChangeEvent<HTMLInputElement>) => {{
    const files = Array.from(e.target.files || []);
    setMedia((current) => [
      ...current,
      ...files.map((file, i) => ({{ id: Date.now() + i, name: file.name, url: URL.createObjectURL(file), type: file.type }})),
    ]);
    e.target.value = '';
    ntf(`Added ${{files.length}} media file(s).`);
  }};

  const insights = () => {{
    setActive('reports');
    document.getElementById('reports')?.scrollIntoView({{ behavior: 'smooth' }});
  }};

  return (
    <div className={{`app-shell theme-${{selectedPalette.id || 'cyan'}} ${{theme === 'light' ? 'light-mode' : 'dark-mode'}}`}}>
      {{/* Sidebar Navigation */}}
      <aside className="sidebar">
        <a className="brand" href="#dashboard">
          <img className="brand-icon" src={{brandMark}} alt="" />
          <div>
            <div className="brand-name">{{appName}}</div>
            <small className="brand-sub">{{appSubtitle}}</small>
          </div>
        </a>

        <nav className="nav-list" aria-label="Application navigation">
          <a href="#dashboard" className={{active === 'dashboard' ? 'active' : ''}} onClick={{() => setActive('dashboard')}}>
            {{t('dashboard')}}
          </a>
{nav_markup}
          <a href="#reports" className={{active === 'reports' ? 'active' : ''}} onClick={{() => setActive('reports')}}>
            {{t('insights')}} ({{recs.length}})
          </a>
          {{customFeatures.map((feature) => (
            <a key={{feature.id}} href={{`#${{feature.id}}`}} className={{`custom-nav-link ${{active === feature.id ? 'active' : ''}}`}} onClick={{() => setActive(feature.id)}}>
              <span>{{feature.icon}}</span> {{feature.name}}
            </a>
          ))}}
          <a href="#media-gallery" className={{active === 'media-gallery' ? 'active' : ''}} onClick={{() => setActive('media-gallery')}}>
            {{t('mediaGallery')}}
          </a>
          <a href="#quick-access" className={{active === 'quick-access' ? 'active' : ''}} onClick={{() => setActive('quick-access')}}>
            {{t('quickAccess')}}
          </a>
        </nav>

        <div className="sidebar-action-box">
          <button type="button" onClick={{() => setShowFeatureStudio(true)}} className="btn-feature-add btn-feature">
            ➕ Add Feature / Module
          </button>
          <button type="button" onClick={{() => setShowCustomizer(true)}} className="btn-customizer btn-outline">
            🎨 Customize Website
          </button>
          <button type="button" onClick={{() => setShowAiChat(true)}} className="btn-ai-chat btn-outline">
            🤖 AI Chat
          </button>
        </div>

        <LanguageSwitcher />

        {{user ? (
          <div className="sidebar-user">
            <span className="avatar">{{user[0]?.toUpperCase()}}</span>
            <div>
              <strong>{{user}}</strong>
              <button type="button" className="btn-ghost" onClick={{logout}}>{{t('signOut')}}</button>
            </div>
          </div>
        ) : (
          <p className="muted">{{t('notSignedIn')}}</p>
        )}}
      </aside>
        {{showAiChat && <AiChat onClose={{() => setShowAiChat(false)}} />}}

      {{/* Main Page Area */}}
      <main className="page-content">
        <header className="topbar">
          <div>
            <h1>{{appName}}</h1>
            <p className="topbar-subtitle">{{appSubtitle}}</p>
          </div>

          <div className="top-actions" aria-label="Quick actions">
            {{user ? (
              <div className="topbar-user-badge">
                <span>👤 <strong>{{user}}</strong></span>
                <button type="button" onClick={{logout}} className="btn-xs btn-del" title="Sign Out">Sign Out</button>
              </div>
            ) : (
              <a href="#quick-access" className="btn-xs btn-primary btn-outline">Sign in / Register</a>
            )}}
            <button type="button" onClick={{() => setShowFeatureStudio(true)}} className="btn-glow-feature btn-feature">
              ➕ Add New Feature
            </button>
            <button type="button" onClick={{openC}} className="btn-primary">
              ＋ Create New
            </button>
            <button type="button" onClick={{() => setShowCustomizer(true)}} className="btn-outline">
              🎨 Customize Site
            </button>
            <button type="button" onClick={{() => document.getElementById('media-upload')?.click()}} className="btn-ghost btn-outline">
              📎 Add Media
            </button>
            <input id="media-upload" type="file" multiple accept="image/*,video/*,.pdf,.doc,.docx,.txt,.md" onChange={{handleMediaChange}} hidden />
            <a href="#reports" onClick={{insights}} className="btn-ghost btn-outline">
              Reports &amp; Insights
            </a>
          </div>
        </header>

        {{msg && <div className="banner toast-banner">{{msg}}</div>}}
        {{storageError && <p className="form-error" role="alert">Browser storage: {{storageError}}</p>}}

        {{/* Domain Hero Welcome Banner: dynamically themed to the input domain */}}
        <div className="domain-hero-banner">
          <div className="domain-hero-left">
            <div className="domain-hero-badge">{branding}</div>
            <h2 className="domain-hero-title">{{appName}} Workspace</h2>
            <p className="domain-hero-desc">{default_tagline}</p>
            <div className="domain-hero-actions">
              <button type="button" className="btn-primary" onClick={{openC}}>＋ Add {primary_label.rstrip('s')}</button>
              <a className="btn-outline" href={{modules[0]?.href || '#dashboard'}}>Explore modules</a>
            </div>
          </div>
          <div className="{visual_class}">
{chr(10).join(visual)}
          </div>
          <div className="domain-hero-stats">
            <div className="domain-stat-card">
              <strong className="domain-stat-val">
                {{databaseCounts ? (databaseCounts.total ?? Object.values(databaseCounts).reduce((sum, count) => sum + count, 0)) : Object.values(entityCounts).reduce((sum, count) => sum + count, 0) + recs.length}}
              </strong>
              <span className="domain-stat-lbl">{{databaseCounts ? 'Database records' : 'Total Records'}}</span>
              <small className="muted text-xs">Records saved in this browser</small>
            </div>
            <div className="domain-stat-card">
              <strong className="domain-stat-val">{{Object.keys(entityCounts).length + customFeatures.length}}</strong>
              <span className="domain-stat-lbl">Modules</span>
              <small className="muted text-xs">Application modules</small>
            </div>
            <div className="domain-stat-card">
              <strong className="domain-stat-val">{{user ? 'Active' : 'Guest'}}</strong>
              <span className="domain-stat-lbl">Auth Status</span>
              <small className="muted text-xs">Session</small>
            </div>
          </div>
        </div>

        {{databaseCountError && <p className="muted" role="status">Database counts are unavailable: {{databaseCountError}}</p>}}

        {{/* Dashboard Section */}}
        <section id="dashboard" className="content-block">
          <Dashboard records={{recs}} entityCounts={{databaseCounts ?? entityCounts}} databaseCountError={{databaseCountError}} countsSource={{databaseCounts ? 'database' : 'browser'}} />
        </section>

        {{/* Resource Module Sections */}}
{component_render}

        {{/* Reports & Insights Section */}}
        <section id="reports" className="content-block report-block insights-section">
          <div className="section-head-row">
            <div>
              <p className="eyebrow">Workspace activity</p>
              <h2>Reports &amp; Insights</h2>
              <p className="muted">{{t('insightsSubtitle')}}</p>
            </div>
            <div className="action-btn-group">
              <label className="search-field">Search records
                <input
                  type="search"
                  value={{reportSearch}}
                  onChange={{(e) => setReportSearch(e.target.value)}}
                  placeholder="Search name, category, or status"
                  className="input-sm"
                />
              </label>
              <button type="button" onClick={{openC}} className="btn-sm btn-primary">
                ＋ {{t('createNew')}}
              </button>
            </div>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>{primary_label}</th>
                  <th>Category</th>
                  <th>Detail / Metric</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {{reportRecords.length === 0 ? (
                  <tr><td colSpan={{6}} className="muted text-center py-4">{{recs.length === 0 ? t('noRecords') : 'No matching records found.'}}</td></tr>
                ) : (
                  reportRecords.map((r, i) => (
                    <tr key={{r.id}}>
                      <td>{{i + 1}}</td>
                      <td><strong>{{r.name}}</strong></td>
                      <td><span className="badge-pill">{{r.field2}}</span></td>
                      <td>{{r.field3}}</td>
                      <td><span className="status-pill status-active">Active</span></td>
                      <td>
                        <div className="action-btn-group">
                          <button type="button" onClick={{() => openEdit(r)}} className="btn-sm btn-edit" title="Edit this record">
                            ✏️ Edit
                          </button>
                          <button type="button" onClick={{() => handleDeleteRecord(r.id)}} className="btn-sm btn-del" title="Delete record">
                            🗑
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}}
              </tbody>
            </table>
          </div>
        </section>

        {{/* Dynamic User Custom Feature Sections */}}
        {{customFeatures.map((feature) => {{
          const feat = feature;
          return (
          <section key={{feat.id}} id={{feat.id}} className="content-block custom-feature-section">
            <div className="section-head-row">
              <div className="feat-title-group">
                <span className="feat-large-icon">{{feat.icon}}</span>
                <div>
                  <p className="eyebrow">Custom module · {{feat.type}}</p>
                  <h2>{{feat.name}}</h2>
                  <p className="muted">{{feat.description}}</p>
                </div>
              </div>
              <div className="action-btn-group">
                <button type="button" onClick={{() => {{ setEditFeat(feat); setEditFeatName(feat.name); setEditFeatDesc(feat.description); setEditFeatIcon(feat.icon); }}}} className="btn-sm btn-edit" title="Edit module">
                  ✏️ Edit Module
                </button>
                <button type="button" onClick={{() => handleDeleteFeature(feat.id)}} className="btn-sm btn-del" title="Remove entire module">
                  🗑 Remove Module
                </button>
              </div>
            </div>

            {{feat.type === 'kanban' && (
              <div className="kanban-container">
                <div className="kanban-add-bar">
                  <input
                    type="text"
                    placeholder={{`Add task to ${{feat.name}}...`}}
                    value={{customItemInput[feat.id] || ''}}
                    onChange={{(e) => setCustomItemInput({{ ...customItemInput, [feat.id]: e.target.value }})}}
                    onKeyDown={{(e) => {{ if (e.key === 'Enter') handleAddCustomItem(feat.id); }}}}
                    className="input-sm"
                  />
                  <button type="button" onClick={{() => handleAddCustomItem(feat.id)}} className="btn-sm btn-primary">＋ Add Card</button>
                </div>
                <div className="kanban-board">
                  <div className="kanban-col">
                    <div className="kanban-col-head"><span>📋 To Do</span><span className="col-count">{{feat.items.filter((i) => i.status === 'todo').length}}</span></div>
                    <div className="kanban-col-body">
                      {{feat.items.filter((i) => i.status === 'todo').map((it) => (
                        <div key={{it.id}} className="kanban-card">
                          <div className="kanban-card-title">{{it.title}}</div>
                          <div className="kanban-card-meta"><small>{{it.date}}</small><div className="kanban-card-btns"><button type="button" onClick={{() => handleMoveKanban(feat.id, it.id, 'in-progress')}}>→ In Progress</button><button type="button" onClick={{() => handleDeleteCustomItem(feat.id, it.id)}} className="text-danger">✕</button></div></div>
                        </div>
                      ))}}
                    </div>
                  </div>
                  <div className="kanban-col">
                    <div className="kanban-col-head"><span>⚡ In Progress</span><span className="col-count">{{feat.items.filter((i) => i.status === 'in-progress').length}}</span></div>
                    <div className="kanban-col-body">
                      {{feat.items.filter((i) => i.status === 'in-progress').map((it) => (
                        <div key={{it.id}} className="kanban-card in-progress">
                          <div className="kanban-card-title">{{it.title}}</div>
                          <div className="kanban-card-meta"><small>{{it.date}}</small><div className="kanban-card-btns"><button type="button" onClick={{() => handleMoveKanban(feat.id, it.id, 'todo')}}>← Back</button><button type="button" onClick={{() => handleMoveKanban(feat.id, it.id, 'done')}} className="btn-done">✓ Done</button><button type="button" onClick={{() => handleDeleteCustomItem(feat.id, it.id)}} className="text-danger">✕</button></div></div>
                        </div>
                      ))}}
                    </div>
                  </div>
                  <div className="kanban-col">
                    <div className="kanban-col-head"><span>✅ Completed</span><span className="col-count">{{feat.items.filter((i) => i.status === 'done').length}}</span></div>
                    <div className="kanban-col-body">
                      {{feat.items.filter((i) => i.status === 'done').map((it) => (
                        <div key={{it.id}} className="kanban-card done">
                          <div className="kanban-card-title"><s>{{it.title}}</s></div>
                          <div className="kanban-card-meta"><small>{{it.date}}</small><div className="kanban-card-btns"><button type="button" onClick={{() => handleMoveKanban(feat.id, it.id, 'in-progress')}}>← Reopen</button><button type="button" onClick={{() => handleDeleteCustomItem(feat.id, it.id)}} className="text-danger">✕</button></div></div>
                        </div>
                      ))}}
                    </div>
                  </div>
                </div>
              </div>
            )}}

            {{feat.type === 'table' && (
              <div className="custom-table-container">
                <div className="custom-table-add-bar">
                  <input
                    type="text"
                    placeholder={{`New item name for ${{feat.name}}...`}}
                    value={{customItemInput[feat.id] || ''}}
                    onChange={{(e) => setCustomItemInput({{ ...customItemInput, [feat.id]: e.target.value }})}}
                    onKeyDown={{(e) => {{ if (e.key === 'Enter') handleAddCustomItem(feat.id); }}}}
                    className="input-sm"
                  />
                  <button type="button" onClick={{() => handleAddCustomItem(feat.id)}} className="btn-sm btn-primary">＋ Add Item</button>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead><tr><th>Item Name</th><th>Category</th><th>Status</th><th>Date</th><th>Action</th></tr></thead>
                    <tbody>
                      {{feat.items.length === 0 ? (
                        <tr><td colSpan={{5}} className="muted text-center py-3">No items yet. Type above and click Add Item.</td></tr>
                      ) : (
                        feat.items.map((it) => (
                          <tr key={{it.id}}>
                            <td><strong>{{it.title}}</strong></td>
                            <td><span className="badge-pill">{{it.subtitle || 'General'}}</span></td>
                            <td><span className="status-pill status-active">{{it.status || 'Active'}}</span></td>
                            <td>{{it.date}}</td>
                            <td><button type="button" onClick={{() => handleDeleteCustomItem(feat.id, it.id)}} className="btn-sm btn-del">🗑</button></td>
                          </tr>
                        ))
                      )}}
                    </tbody>
                  </table>
                </div>
              </div>
            )}}

            {{feat.type === 'form' && (
              <div className="custom-form-container">
                <form onSubmit={{(e) => handleSubmitCustomForm(feat.id, e)}} className="custom-form-panel">
                  <h3>Submit Entry to {{feat.name}}</h3>
                  <div className="form-row-2">
                    <label>Name / Title<input type="text" required placeholder="e.g. John Doe" value={{customFormValues[feat.id]?.name || ''}} onChange={{(e) => setCustomFormValues({{ ...customFormValues, [feat.id]: {{ ...(customFormValues[feat.id] || {{}}), name: e.target.value }} }})}} /></label>
                    <label>Category<input type="text" placeholder="e.g. Support" value={{customFormValues[feat.id]?.category || ''}} onChange={{(e) => setCustomFormValues({{ ...customFormValues, [feat.id]: {{ ...(customFormValues[feat.id] || {{}}), category: e.target.value }} }})}} /></label>
                  </div>
                  <label>Details / Message<textarea rows={{3}} required placeholder="Enter message or request..." value={{customFormValues[feat.id]?.details || ''}} onChange={{(e) => setCustomFormValues({{ ...customFormValues, [feat.id]: {{ ...(customFormValues[feat.id] || {{}}), details: e.target.value }} }})}} /></label>
                  <button type="submit" className="btn-primary">📤 Submit Entry</button>
                </form>
                <div className="custom-submissions-panel">
                  <h3>Submissions ({{(feat.formSubmissions || []).length}})</h3>
                  {{(feat.formSubmissions || []).length === 0 ? (
                    <p className="muted">No submissions yet. Use the form above to record entries.</p>
                  ) : (
                    <ul className="submissions-list">
                      {{(feat.formSubmissions || []).map((sub) => (
                        <li key={{sub.id}} className="submission-card">
                          <div><strong>{{sub.data.name || 'Entry'}}</strong> — <span className="badge-pill">{{sub.data.category || 'General'}}</span><p className="submission-text">{{sub.data.details}}</p></div>
                          <small className="muted">{{sub.date}}</small>
                        </li>
                      ))}}
                    </ul>
                  )}}
                </div>
              </div>
            )}}

            {{feat.type === 'metrics' && (
              <div className="dashboard-grid">
                {{feat.items.map((it) => (
                  <div key={{it.id}} className="dashboard-card feat-metric-card">
                    <span className="stat-label">{{it.title}}</span>
                    <strong>{{it.value || '100%'}}</strong>
                    <small className="stat-sub">{{it.subtitle}}</small>
                    <button type="button" onClick={{() => handleDeleteCustomItem(feat.id, it.id)}} className="btn-del-corner">✕</button>
                  </div>
                ))}}
              </div>
            )}}

            {{feat.type === 'notes' && (
              <div className="custom-notes-container">
                <div className="notes-add-row">
                  <input type="text" placeholder="Write a quick note..." value={{customItemInput[feat.id] || ''}} onChange={{(e) => setCustomItemInput({{ ...customItemInput, [feat.id]: e.target.value }})}} onKeyDown={{(e) => {{ if (e.key === 'Enter') handleAddCustomItem(feat.id); }}}} />
                  <button type="button" onClick={{() => handleAddCustomItem(feat.id)}} className="btn-primary">📝 Post Note</button>
                </div>
                <div className="notes-grid">
                  {{feat.items.map((it) => (
                    <div key={{it.id}} className="note-card">
                      <p className="note-body">{{it.title}}</p>
                      <div className="note-footer"><small>{{it.date}}</small><button type="button" onClick={{() => handleDeleteCustomItem(feat.id, it.id)}} className="btn-del-sm">✕</button></div>
                    </div>
                  ))}}
                </div>
              </div>
            )}}
          </section>
        ); }})}}

        {{/* Media Gallery Section */}}
        <section id="media-gallery" className="content-block">
          <div className="section-head-row">
            <div>
              <p className="eyebrow">Workspace files</p>
              <h2>Media gallery</h2>
              <p className="muted">Files you add are shown for this browser session.</p>
            </div>
            <label className="btn-outline upload-label" htmlFor="media-upload">＋ Add Media</label>
          </div>
          {{media.length === 0 ? (
            <p className="muted empty-state">No media files added yet. Choose a file to build this gallery.</p>
          ) : (
            <div className="media-grid">
              {{media.map((item) => (
                <article key={{item.id}} className="media-card media-item">
                  {{item.type.startsWith('image/') ? (
                    <img src={{item.url}} alt={{item.name}} className="media-image" />
                  ) : item.type.startsWith('video/') ? (
                    <video src={{item.url}} controls className="media-video" />
                  ) : (
                    <div className="media-file"><span className="media-icon">📄</span><span>{{item.name}}</span></div>
                  )}}
                  <div>
                    <strong>{{item.name}}</strong>
                    <button type="button" onClick={{() => setMedia(media.filter((m) => m.id !== item.id))}} className="btn-sm btn-del">Remove</button>
                  </div>
                </article>
              ))}}
            </div>
          )}}
        </section>

        {{/* Quick Access Section */}}
        <section id="quick-access" className="content-block auth-block">
          <div className="panel">
            <h2>{{t('quickAccess')}}</h2>
            {{user ? (
              <p className="muted signed-in-msg">{{t('signedInMsg').replace('{{user}}', user)}}</p>
            ) : (
              <Login onLogin={{login}} onSignIn={{login}} />
            )}}
          </div>
        </section>
      </main>

      {{/* MODAL 1: Create Record */}}
      {{showCreate && (
        <div className="modal-overlay modal-backdrop" onClick={{() => setShowCreate(false)}}>
          <form className="modal modal-card" onSubmit={{create}} onClick={{(e) => e.stopPropagation()}}>
            <h2>{{t('createRecord')}}</h2>
            <label htmlFor="record-name">{primary_label} Name *
              <input id="record-name" autoFocus type="text" value={{cN}} onChange={{(e) => setCN(e.target.value)}} placeholder="Enter title/name" required />
            </label>
            <label>Category
              <input type="text" value={{c2}} onChange={{(e) => setC2(e.target.value)}} placeholder="Enter category" />
            </label>
            <label>Detail / Metric
              <input type="text" value={{c3}} onChange={{(e) => setC3(e.target.value)}} placeholder="Enter detail or metric" />
            </label>
            <div className="modal-actions form-actions">
              <button type="button" className="btn-ghost btn-outline" onClick={{() => setShowCreate(false)}}>{{t('cancel')}}</button>
              <button type="submit" className="btn-primary">{{t('create')}}</button>
            </div>
          </form>
        </div>
      )}}

      {{/* MODAL 2: Edit Record */}}
      {{editRecord && (
        <div className="modal-overlay modal-backdrop" onClick={{() => setEditRecord(null)}}>
          <form className="modal modal-card" onSubmit={{handleSaveEdit}} onClick={{(e) => e.stopPropagation()}}>
            <h2>✏️ Edit Record #{{editRecord.id.toString().slice(-4)}}</h2>
            <label>Name / Title
              <input autoFocus type="text" value={{eN}} onChange={{(e) => setEN(e.target.value)}} required />
            </label>
            <label>Category
              <input type="text" value={{e2}} onChange={{(e) => setE2(e.target.value)}} />
            </label>
            <label>Detail / Metric
              <input type="text" value={{e3}} onChange={{(e) => setE3(e.target.value)}} />
            </label>
            <div className="modal-actions form-actions">
              <button type="button" className="btn-ghost btn-outline" onClick={{() => setEditRecord(null)}}>{{t('cancel')}}</button>
              <button type="submit" className="btn-primary">Save Changes</button>
            </div>
          </form>
        </div>
      )}}

      {{/* MODAL 3: In-Website Feature Studio */}}
      {{showFeatureStudio && (
        <div className="modal-overlay modal-backdrop" onClick={{() => setShowFeatureStudio(false)}}>
          <div className="modal modal-lg modal-card" onClick={{(e) => e.stopPropagation()}}>
            <div className="modal-header-tabs">
              <p className="eyebrow">Extend your workspace</p>
              <h2>➕ Feature Studio: Add a feature module</h2>
              <div className="modal-tabs">
                <button type="button" onClick={{() => setFeatureTab('builder')}} className={{`modal-tab-btn ${{featureTab === 'builder' ? 'active' : ''}}`}}>🛠 Feature Builder</button>
                <button type="button" onClick={{() => setFeatureTab('ai')}} className={{`modal-tab-btn ${{featureTab === 'ai' ? 'active' : ''}}`}}>🤖 AI Feature Copilot</button>
              </div>
            </div>

            {{featureTab === 'builder' ? (
              <form onSubmit={{handleAddFeature}}>
                <div className="form-row-2">
                  <label htmlFor="feature-name">Module name
                    <input id="feature-name" autoFocus type="text" required placeholder="e.g. Invoices, Roster, Maintenance..." value={{newFeatureName}} onChange={{(e) => setNewFeatureName(e.target.value)}} />
                  </label>
                  <label htmlFor="feature-kind">Module format
                    <select id="feature-kind" value={{newFeatureType}} onChange={{(e) => setNewFeatureType(e.target.value as any)}} className="input-select">
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
                      {{['⚡', '📊', '📝', '💰', '📅', '👥', '🛒', '⚙️', '🎯', '🚀', '💬', '📦', '🏥', '🎓', '🛠️'].map((ic) => (
                        <button key={{ic}} type="button" onClick={{() => setNewFeatureIcon(ic)}} className={{`icon-btn ${{newFeatureIcon === ic ? 'selected' : ''}}`}}>{{ic}}</button>
                      ))}}
                    </div>
                  </label>
                  <label htmlFor="feature-description">Description
                    <input id="feature-description" type="text" placeholder="What will this module help manage?" value={{newFeatureDesc}} onChange={{(e) => setNewFeatureDesc(e.target.value)}} />
                  </label>
                </div>
                <div className="modal-actions form-actions">
                  <button type="button" className="btn-ghost btn-outline" onClick={{() => setShowFeatureStudio(false)}}>{{t('cancel')}}</button>
                  <button type="submit" className="btn-primary">Add module</button>
                </div>
              </form>
            ) : (
              <div className="ai-feature-copilot">
                <p className="muted">Choose a 1-click popular preset, or type what feature you need:</p>
                <div className="preset-grid">
                  <button type="button" onClick={{() => handleApplyPreset('Invoice & Payment Tracker', '💰', 'table', 'Track billing, transactions, and client payment invoices')}} className="preset-chip">💰 Invoice &amp; Payment Tracker</button>
                  <button type="button" onClick={{() => handleApplyPreset('Appointment / Roster Board', '📅', 'kanban', 'Manage scheduled shifts, patient visits, or bookings')}} className="preset-chip">📅 Appointment / Roster Board</button>
                  <button type="button" onClick={{() => handleApplyPreset('Customer Feedback Collector', '📝', 'form', 'Collect reviews, inquiries, and customer feedback')}} className="preset-chip">📝 Customer Feedback Collector</button>
                  <button type="button" onClick={{() => handleApplyPreset('Live KPI & Performance Metrics', '📈', 'metrics', 'Display key operational metrics and revenue gauges')}} className="preset-chip">📈 Live KPI &amp; Performance Metrics</button>
                  <button type="button" onClick={{() => handleApplyPreset('Task & Sprint Kanban', '📋', 'kanban', 'To Do, In Progress, and Completed sprint task cards')}} className="preset-chip">📋 Task &amp; Sprint Kanban</button>
                </div>
                <div className="ai-prompt-box">
                  <label>Custom Prompt for AI Feature Generator
                    <textarea rows={{3}} placeholder="e.g. Add a staff schedule planner with shifts and timestamps..." value={{aiPrompt}} onChange={{(e) => setAiPrompt(e.target.value)}} />
                  </label>
                  <div className="modal-actions form-actions">
                    <button type="button" className="btn-ghost btn-outline" onClick={{() => setShowFeatureStudio(false)}}>{{t('cancel')}}</button>
                    <button type="button" onClick={{handleAiGenerateFeature}} className="btn-primary btn-glow">⚡ Generate &amp; Add Feature</button>
                  </div>
                </div>
              </div>
            )}}
          </div>
        </div>
      )}}

      {{/* MODAL 4: Website Customizer & Theme Studio */}}
      {{showCustomizer && (
        <div className="modal-overlay modal-backdrop" onClick={{() => setShowCustomizer(false)}}>
          <div className="modal modal-card" onClick={{(e) => e.stopPropagation()}} role="dialog" aria-modal="true" aria-labelledby="customizer-title">
            <p className="eyebrow">Personalize this workspace</p>
            <h2 id="customizer-title">Website &amp; Theme Customizer</h2>
            <label htmlFor="site-name">Brand name
              <input id="site-name" type="text" value={{appName}} onChange={{(e) => setAppName(e.target.value)}} placeholder="e.g. Apex Health Portal" />
            </label>
            <label htmlFor="site-tagline">Tagline
              <input id="site-tagline" type="text" value={{appSubtitle}} onChange={{(e) => setAppSubtitle(e.target.value)}} placeholder="e.g. Next-Gen Enterprise Solution" />
            </label>
            <fieldset className="palette-picker">
              <legend>Accent palette</legend>
              <div className="palette-grid">
                {{palettes.map((palette) => (
                  <button
                    key={{palette.value}}
                    type="button"
                    onClick={{() => setAccentColor(palette.value)}}
                    className={{`palette-swatch color-swatch ${{accentColor === palette.value ? 'selected' : ''}}`}}
                    style={{{{ backgroundColor: palette.value }}}}
                    title={{palette.name}}
                    aria-label={{palette.name}}
                    aria-pressed={{accentColor === palette.value}}
                  >
                    {{accentColor === palette.value ? '✓' : ''}}
                  </button>
                ))}}
              </div>
            </fieldset>
            <fieldset className="theme-picker" style={{{{ marginTop: '14px' }}}}>
              <legend>Appearance</legend>
              <div className="form-actions btn-group">
                <button type="button" onClick={{() => setTheme('dark')}} className={{`btn-toggle ${{theme === 'dark' ? 'btn-primary active' : 'btn-outline'}}`}} aria-pressed={{theme === 'dark'}}>🌙 Dark</button>
                <button type="button" onClick={{() => setTheme('light')}} className={{`btn-toggle ${{theme === 'light' ? 'btn-primary active' : 'btn-outline'}}`}} aria-pressed={{theme === 'light'}}>☀️ Light</button>
              </div>
            </fieldset>
            <div className="modal-actions form-actions" style={{{{ marginTop: '20px' }}}}>
              <button type="button" onClick={{handleResetDefaults}} className="btn-danger-ghost btn-danger">Reset defaults</button>
              <button type="button" onClick={{() => {{ setShowCustomizer(false); ntf('Website customizations saved successfully!'); }}}} className="btn-primary">Save &amp; apply</button>
            </div>
          </div>
        </div>
      )}}

      {{/* Floating Action Studio Launcher */}}
      <button
        type="button"
        onClick={{() => setShowFeatureStudio(true)}}
        className="floating-studio-btn floating-feature"
        title="Open Feature Studio to add new features"
        aria-label="Add a feature module"
      >
        ✨ <span>Add Feature</span>
      </button>
    </div>
  );
}};

export default App;
'''

    @staticmethod
    def _count_key(component: str) -> str:
        special = {"Cart": "cartitems", "Menu": "menuitems", "AdoptionApplications": "adoptionapplications"}
        if component in special:
            return special[component]
        snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", component).casefold()
        if snake_case.endswith("y") and not snake_case.endswith(("ay", "ey", "oy", "uy")):
            snake_case = snake_case[:-1] + "ies"
        elif not snake_case.endswith("s"):
            snake_case += "s"
        return snake_case.replace("_", "")

    def generate_dashboard_tsx(
        self,
        project_name: str,
        requirements: str,
        language: str = "en",
        entities: list[str] | None = None,
        domain_key: str | None = None,
        entity_labels: dict[str, str] | None = None,
    ) -> str:
        spec = derive_website_spec(requirements, project_name)
        domain_key = domain_key or spec.get("key", "generic")
        entities = entities or []
        entity_labels = entity_labels or {}
        if domain_key == "generic":
            stats_source = "[{ label: 'Database Records', key: 'total' }]"
        else:
            stats = [{"label": entity_labels.get(entity, entity), "key": self._count_key(entity)} for entity in entities]
            stats_source = json.dumps(stats, ensure_ascii=False)
        primary = entities[0] if entities else None
        primary_label = entity_labels.get(primary, primary) if primary else "Records"
        empty_plural = primary_label.lower()
        if empty_plural and not empty_plural.endswith("s"):
            empty_plural += "s"

        return f'''import React from 'react';
import type {{ AppRecord }} from './App';

interface DashboardProps {{
  records: AppRecord[];
  entityCounts?: Record<string, number>;
  databaseCountError?: string | null;
  countsSource: 'database' | 'browser';
}}

const stats = {stats_source};

const Dashboard: React.FC<DashboardProps> = ({{ records, entityCounts, databaseCountError, countsSource }}) => {{
  return (
    <div className="dashboard-content">
      {{databaseCountError && <p className="muted" role="status">Database counts are unavailable: {{databaseCountError}}</p>}}
      <div className="dashboard-grid">
        {{stats.map((stat) => (
          <article className="dashboard-card" key={{stat.key}}>
            <span className="stat-label">{{stat.label}}</span>
            <strong className="stat-value">{{entityCounts?.[stat.key] ?? '—'}}</strong>
            <span className="stat-sub">{{countsSource === 'database' ? 'From the application database' : 'Saved in this browser'}}</span>
          </article>
        ))}}
      </div>

      <div className="dashboard-record-section recent-section">
        <div className="section-head-row">
          <div>
            <p className="eyebrow">Activity</p>
            <h2>{primary_label} added recently</h2>
          </div>
          <span className="badge-pill">{{records.length}} in this session</span>
        </div>
        {{records.length === 0 ? (
          <div className="empty-state">
            <span aria-hidden="true">+</span>
            <strong>No {empty_plural} have been added yet.</strong>
            <p className="muted">Create your first record to start building this workspace.</p>
          </div>
        ) : (
          <ul className="resource-list recent-list">
            {{records.slice(0, 4).map((r) => (
              <li key={{r.id}}>
                <span className="record-mark">{{r.name.slice(0, 1).toUpperCase()}}</span>
                <span>
                  <strong>{{r.name}}</strong> - {{r.field2}} - <small className="muted">{{r.createdAt}}</small>
                </span>
              </li>
            ))}}
          </ul>
        )}}
      </div>
    </div>
  );
}};

export default Dashboard;
'''


    def generate_resource_component(
        self,
        filename: str,
        project_name: str,
        requirements: str,
        language: str = "en",
        display_label: str | None = None,
    ) -> str:
        component = Path(filename).stem
        label = display_label or component
        singular = self._singularize(label)
        plural = self._pluralize(singular)
        title = self._resource_title(component, label, requirements)
        storage = f"res_data_{self._project_slug(project_name)}_{component.casefold()}"
        entity_name_col = f"{singular} Name" if " " in singular else f"{label} Name"

        return f'''import React, {{ useState, useEffect }} from 'react';

interface Props {{
  onCountChange?: (count: number) => void;
}}

export interface {component}Record {{
  id: number;
  name: string;
  f2: string;
  f3: string;
  status: string;
  category?: string;
  createdAt?: string;
}}

const {component}: React.FC<Props> = ({{ onCountChange }}) => {{
  const STORAGE_KEY = {json.dumps(storage)};
  const [records, setRecords] = useState<{component}Record[]>([]);
  const [search, setSearch] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [newName, setNewName] = useState('');
  const [newF2, setNewF2] = useState('');
  const [newF3, setNewF3] = useState('');
  const [newStatus, setNewStatus] = useState('Active');

  const [editItem, setEditItem] = useState<{component}Record | null>(null);
  const [editName, setEditName] = useState('');
  const [editF2, setEditF2] = useState('');
  const [editF3, setEditF3] = useState('');
  const [editStatus, setEditStatus] = useState('');
  const [msg, setMsg] = useState<string | null>(null);

  const notify = (text: string) => {{
    setMsg(text);
    setTimeout(() => setMsg(null), 3500);
  }};

  useEffect(() => {{
    try {{
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {{
        const restored = JSON.parse(saved);
        if (Array.isArray(restored)) {{
          setRecords(restored);
          onCountChange?.(restored.length);
        }}
      }}
    }} catch {{
      // ignore
    }}
  }}, []);

  const save = (next: {component}Record[]) => {{
    setRecords(next);
    onCountChange?.(next.length);
    try {{
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    }} catch {{
      // ignore
    }}
  }};

  const handleAdd = (e: React.FormEvent) => {{
    e.preventDefault();
    if (!newName.trim()) return;
    const item: {component}Record = {{
      id: Date.now(),
      name: newName.trim(),
      f2: newF2.trim() || 'General',
      f3: newF3.trim() || 'Standard',
      status: newStatus.trim() || 'Active',
      category: newF2.trim() || 'General',
      createdAt: new Date().toLocaleDateString(),
    }};
    const next = [item, ...records];
    save(next);
    setShowAdd(false);
    setNewName('');
    setNewF2('');
    setNewF3('');
    notify('Created "' + item.name + '" successfully!');
  }};

  const openEdit = (it: {component}Record) => {{
    setEditItem(it);
    setEditName(it.name);
    setEditF2(it.f2 || it.category || '');
    setEditF3(it.f3 || '');
    setEditStatus(it.status || 'Active');
  }};

  const handleSaveEdit = (e: React.FormEvent) => {{
    e.preventDefault();
    if (!editItem || !editName.trim()) return;
    const next = records.map((it) =>
      it.id === editItem.id
        ? {{
            ...it,
            name: editName.trim(),
            f2: editF2.trim() || it.f2,
            f3: editF3.trim() || it.f3,
            category: editF2.trim() || it.category,
            status: editStatus.trim() || it.status,
          }}
        : it
    );
    save(next);
    setEditItem(null);
    notify('Updated "' + editName + '" successfully!');
  }};

  const handleDelete = (id: number) => {{
    if (window.confirm('Remove this {singular} record?')) {{
      const next = records.filter((it) => it.id !== id);
      save(next);
      notify('Record removed from workspace.');
    }}
  }};

  const filtered = records.filter((it) =>
    (it.name || '').toLowerCase().includes(search.toLowerCase()) ||
    (it.f2 || it.category || '').toLowerCase().includes(search.toLowerCase()) ||
    (it.status || '').toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="resource-card entity-manager-block">
      <div className="section-head-row">
        <div>
          <h2>{title} <span className="badge-pill">{{records.length}}</span></h2>
          <p className="muted">Manage, edit, or remove {plural.lower()} in your workspace.</p>
        </div>
        <div className="action-btn-group">
          <input
            type="text"
            placeholder="Filter records…"
            value={{search}}
            onChange={{(e) => setSearch(e.target.value)}}
            className="input-sm"
            style={{{{ width: '160px' }}}}
          />
          <button type="button" onClick={{() => setShowAdd(true)}} className="btn-sm btn-primary">
            + Add {singular}
          </button>
        </div>
      </div>

      {{msg && <div className="banner toast-banner" style={{{{ margin: '10px 0' }}}}>{{msg}}</div>}}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>{entity_name_col}</th>
              <th>Category</th>
              <th>Detail / Metric</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {{filtered.length === 0 ? (
              <tr><td colSpan={{6}} className="muted text-center py-4">No records found. Click "Add {singular}" to create one.</td></tr>
            ) : (
              filtered.map((it, idx) => (
                <tr key={{it.id}}>
                  <td>{{idx + 1}}</td>
                  <td><strong>{{it.name}}</strong></td>
                  <td><span className="badge-pill">{{it.f2 || it.category || 'General'}}</span></td>
                  <td>{{it.f3 || '—'}}</td>
                  <td><span className="status-pill status-active">{{it.status || 'Active'}}</span></td>
                  <td>
                    <div className="action-btn-group">
                      <button type="button" onClick={{() => openEdit(it)}} className="btn-sm btn-edit" title="Edit record">
                        Edit
                      </button>
                      <button type="button" onClick={{() => handleDelete(it.id)}} className="btn-sm btn-del" title="Remove record">
                        Remove
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}}
          </tbody>
        </table>
      </div>

      {{/* Add Modal */}}
      {{showAdd && (
        <div className="modal-overlay modal-backdrop" onClick={{() => setShowAdd(false)}}>
          <form className="modal modal-card" onSubmit={{handleAdd}} onClick={{(e) => e.stopPropagation()}}>
            <h2>+ Add New {singular}</h2>
            <label>{entity_name_col} *
              <input autoFocus type="text" required value={{newName}} onChange={{(e) => setNewName(e.target.value)}} placeholder="Enter title/name" />
            </label>
            <label>Category
              <input type="text" value={{newF2}} onChange={{(e) => setNewF2(e.target.value)}} placeholder="Enter category" />
            </label>
            <label>Detail / Metric
              <input type="text" value={{newF3}} onChange={{(e) => setNewF3(e.target.value)}} placeholder="Enter detail / metric" />
            </label>
            <label>Status
              <input type="text" value={{newStatus}} onChange={{(e) => setNewStatus(e.target.value)}} placeholder="e.g. Active" />
            </label>
            <div className="modal-actions form-actions">
              <button type="button" className="btn-ghost btn-outline" onClick={{() => setShowAdd(false)}}>Cancel</button>
              <button type="submit" className="btn-primary">Add {singular}</button>
            </div>
          </form>
        </div>
      )}}

      {{/* Edit Modal */}}
      {{editItem && (
        <div className="modal-overlay modal-backdrop" onClick={{() => setEditItem(null)}}>
          <form className="modal modal-card" onSubmit={{handleSaveEdit}} onClick={{(e) => e.stopPropagation()}}>
            <h2>Edit {singular} #{{editItem.id.toString().slice(-4)}}</h2>
            <label>{entity_name_col} *
              <input autoFocus type="text" required value={{editName}} onChange={{(e) => setEditName(e.target.value)}} />
            </label>
            <label>Category
              <input type="text" value={{editF2}} onChange={{(e) => setEditF2(e.target.value)}} />
            </label>
            <label>Detail / Metric
              <input type="text" value={{editF3}} onChange={{(e) => setEditF3(e.target.value)}} />
            </label>
            <label>Status
              <input type="text" value={{editStatus}} onChange={{(e) => setEditStatus(e.target.value)}} />
            </label>
            <div className="modal-actions form-actions">
              <button type="button" className="btn-ghost btn-outline" onClick={{() => setEditItem(null)}}>Cancel</button>
              <button type="submit" className="btn-primary">Save Changes</button>
            </div>
          </form>
        </div>
      )}}
    </div>
  );
}};

export default {component};
'''

    @staticmethod
    def _singularize(label: str) -> str:
        words = label.split()
        if words:
            last = words[-1]
            if last.casefold().endswith("ies"):
                words[-1] = last[:-3] + "y"
            elif last.casefold().endswith("s") and not last.casefold().endswith(("ss", "us", "is")):
                words[-1] = last[:-1]
        return " ".join(words) or "Record"

    @staticmethod
    def _pluralize(label: str) -> str:
        if label.casefold().endswith("y"):
            return label[:-1] + "ies"
        return label if label.casefold().endswith("s") else label + "s"

    @staticmethod
    def _resource_title(component: str, label: str, prompt: str) -> str:
        domain = detect_website_key(prompt)
        if domain == "railway":
            rail_titles = {"Trains": "Train Fleet", "Schedules": "Train Schedules"}
            if component in rail_titles:
                return rail_titles[component]
        return label

    def _build_login_tsx(self, project_name: str) -> str:
        return f'''import React, {{ useState, useEffect }} from 'react';

interface LoginProps {{
  onLogin?: (name: string, email?: string) => void;
  onSignIn?: (email: string) => void;
}}

interface StoredUser {{
  name: string;
  email: string;
  password: string;
}}

const Login: React.FC<LoginProps> = ({{ onLogin, onSignIn }}) => {{
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<string | null>(null);

  useEffect(() => {{
    try {{
      const active = localStorage.getItem('website_active_user');
      if (active) {{
        let display = active;
        try {{
          const parsed = JSON.parse(active);
          display = parsed?.name || parsed?.email || active;
        }} catch {{
          display = active;
        }}
        setCurrentUser(display);
        onLogin?.(display, display);
        onSignIn?.(display);
      }}
    }} catch {{
      // ignore
    }}
  }}, []);

  const getUsers = (): StoredUser[] => {{
    try {{
      const data = localStorage.getItem('website_users');
      return data ? JSON.parse(data) : [];
    }} catch {{
      return [];
    }}
  }};

  const handleRegister = (e: React.FormEvent) => {{
    e.preventDefault();
    setError(null);
    setSuccess(null);
    const trimmedName = name.trim();
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedName) {{
      setError('Please enter your full name.');
      return;
    }}
    if (!trimmedEmail || !trimmedEmail.includes('@')) {{
      setError('Please enter a valid email address.');
      return;
    }}
    if (password.length < 6) {{
      setError('Password must be at least 6 characters.');
      return;
    }}
    if (password !== confirmPassword) {{
      setError('Passwords do not match.');
      return;
    }}
    const users = getUsers();
    if (users.some((u) => u.email.toLowerCase() === trimmedEmail)) {{
      setError('An account with this email already exists. Please sign in.');
      return;
    }}
    const newUser: StoredUser = {{ name: trimmedName, email: trimmedEmail, password }};
    const nextUsers = [...users, newUser];
    localStorage.setItem('website_users', JSON.stringify(nextUsers));
    localStorage.setItem('website_active_user', JSON.stringify({{ name: trimmedName, email: trimmedEmail }}));
    setCurrentUser(trimmedName);
    onLogin?.(trimmedName, trimmedEmail);
    onSignIn?.(trimmedEmail);
    setSuccess('Registration successful! Welcome to your workspace.');
  }};

  const handleLogin = (e: React.FormEvent) => {{
    e.preventDefault();
    setError(null);
    setSuccess(null);
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail) {{
      setError('Please enter your email.');
      return;
    }}
    if (!password) {{
      setError('Please enter your password.');
      return;
    }}
    const users = getUsers();
    const found = users.find((u) => u.email === trimmedEmail);
    if (!found) {{
      const displayName = trimmedEmail.split('@')[0] || 'User';
      localStorage.setItem('website_active_user', JSON.stringify({{ name: displayName, email: trimmedEmail }}));
      setCurrentUser(displayName);
      onLogin?.(displayName, trimmedEmail);
      onSignIn?.(trimmedEmail);
      setSuccess('Signed in successfully.');
      return;
    }}
    if (found.password !== password) {{
      setError('Incorrect password. Please try again.');
      return;
    }}
    localStorage.setItem('website_active_user', JSON.stringify({{ name: found.name, email: found.email }}));
    setCurrentUser(found.name);
    onLogin?.(found.name, found.email);
    onSignIn?.(found.email);
    setSuccess('Welcome back, ' + found.name + '!');
  }};

  const handleSignOut = () => {{
    localStorage.removeItem('website_active_user');
    setCurrentUser(null);
  }};

  return (
    <div className="auth-layout panel">
      {{currentUser ? (
        <div className="user-session-card">
          <div className="session-status-badge">&bull; Active Session</div>
          <h3>Signed in as <strong>{{currentUser}}</strong></h3>
          <p className="muted">You have administrative access to create, edit, and manage records.</p>
          <div className="form-actions" style={{{{ justifyContent: 'center', marginTop: '16px' }}}}>
            <button type="button" onClick={{handleSignOut}} className="btn-outline btn-del">Sign Out</button>
          </div>
        </div>
      ) : (
        <>
          <div className="gen-auth-tabs">
            <button
              type="button"
              className={{`gen-auth-tab ${{mode === 'login' ? 'active' : ''}}`}}
              onClick={{() => {{ setMode('login'); setError(null); setSuccess(null); }}}}
            >
              Sign In
            </button>
            <button
              type="button"
              className={{`gen-auth-tab ${{mode === 'register' ? 'active' : ''}}`}}
              onClick={{() => {{ setMode('register'); setError(null); setSuccess(null); }}}}
            >
              Register
            </button>
          </div>

          {{error && <div className="gen-auth-alert gen-auth-alert-err">{{error}}</div>}}
          {{success && <div className="gen-auth-alert gen-auth-alert-ok">{{success}}</div>}}

          {{mode === 'login' ? (
            <form onSubmit={{handleLogin}} className="gen-login-form">
              <label>Email Address
                <input
                  type="email"
                  required
                  placeholder="name@example.com"
                  value={{email}}
                  onChange={{(e) => setEmail(e.target.value)}}
                />
              </label>
              <label>Password
                <input
                  type="password"
                  required
                  placeholder="Enter password"
                  value={{password}}
                  onChange={{(e) => setPassword(e.target.value)}}
                />
              </label>
              <button type="submit" className="btn-primary" style={{{{ marginTop: '8px' }}}}>Sign In</button>
              <p className="auth-hint-text">
                Don&apos;t have an account? 
                <button type="button" onClick={{() => setMode('register')}} className="text-link">Register here</button>
              </p>
            </form>
          ) : (
            <form onSubmit={{handleRegister}} className="gen-login-form">
              <label>Full Name
                <input
                  type="text"
                  required
                  placeholder="e.g. John Doe"
                  value={{name}}
                  onChange={{(e) => setName(e.target.value)}}
                />
              </label>
              <label>Email Address
                <input
                  type="email"
                  required
                  placeholder="name@example.com"
                  value={{email}}
                  onChange={{(e) => setEmail(e.target.value)}}
                />
              </label>
              <label>Password
                <input
                  type="password"
                  required
                  placeholder="At least 6 characters"
                  value={{password}}
                  onChange={{(e) => setPassword(e.target.value)}}
                />
              </label>
              <label>Confirm Password
                <input
                  type="password"
                  required
                  placeholder="Confirm your password"
                  value={{confirmPassword}}
                  onChange={{(e) => setConfirmPassword(e.target.value)}}
                />
              </label>
              <button type="submit" className="btn-primary" style={{{{ marginTop: '8px' }}}}>Create Account</button>
              <p className="auth-hint-text">
                Already registered?{{' '}}
                <button type="button" onClick={{() => setMode('login')}} className="text-link">Sign In</button>
              </p>
            </form>
          )}}
        </>
      )}}
    </div>
  );
}};

export default Login;
'''

    def _resolve_domain_palette(self, prompt: str) -> dict[str, str]:
        key = detect_website_key(prompt)
        accents = {
            "hospital": ("cyan", "#38bdf8"),
            "education": ("indigo", "#7868e8"),
            "hospitality": ("rose", "#d47b83"),
            "ecommerce": ("amber", "#dfa339"),
            "railway": ("cyan", "#38bdf8"),
            "transit": ("cyan", "#38bdf8"),
            "temple": ("amber", "#f59e0b"),
            "agriculture": ("emerald", "#10b981"),
            "food_delivery": ("rose", "#e17c59"),
            "finance": ("cyan", "#4da7b5"),
            "inventory": ("indigo", "#6885d6"),
            "real_estate": ("amber", "#b9955b"),
            "travel": ("cyan", "#4e9fba"),
            "fitness": ("emerald", "#55a978"),
            "task": ("indigo", "#7776d8"),
            "generic": ("purple", "#9273d6"),
        }
        theme, accent = accents.get(key, accents["generic"])
        branding, tagline = self._DOMAIN_BRANDING.get(key, ("Custom Operations Workspace", "A clear workspace shaped around your requirements."))
        spec = derive_website_spec(prompt)
        if key == "generic" and spec.get("module_labels"):
            tagline = f"Manage {', '.join(list(spec['module_labels'].values())[:4])} in one focused application."
        return {
            "theme_class": f"theme-{theme}",
            "accent": accent,
            "hero_badge": branding,
            "hero_tagline": tagline,
        }

    def _build_brand_mark_svg(self, spec: dict[str, Any]) -> str:
        key = str(spec.get("key", "generic"))
        path = self._BRAND_PATHS.get(key, self._BRAND_PATHS["generic"])
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Application mark">'
            '<rect width="64" height="64" rx="20" fill="#172231"/>'
            f'<path {path} fill="none" stroke="{self._resolve_domain_palette(key)["accent"]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
            '</svg>'
        )

    def generate_styles_css(self, prompt: str) -> str:
        palette = self._resolve_domain_palette(prompt)
        base = f''':root {{
  color-scheme: dark;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --bg-page: #04111d;
  --bg-card: rgba(8, 26, 44, 0.88);
  --bg-inner: rgba(13, 38, 64, 0.75);
  --border-color: rgba(56, 189, 248, 0.18);
  --text-main: #f1f5f9;
  --text-muted: #94a3b8;
  --accent-primary: {palette["accent"]};
  --accent-glow: rgba(6, 182, 212, 0.3);
  --accent-gradient: linear-gradient(135deg, {palette["accent"]}, #10b981);
  background: var(--bg-page);
  color: var(--text-main);
  line-height: 1.5;
}}
/* Accent Themes */
.theme-cyan {{ --accent-primary: #38bdf8; --accent-gradient: linear-gradient(135deg, #38bdf8, #818cf8); --accent-glow: rgba(56, 189, 248, 0.25); }}
.theme-indigo {{ --accent-primary: #6366f1; --accent-gradient: linear-gradient(135deg, #6366f1, #a855f7); --accent-glow: rgba(99, 102, 241, 0.25); }}
.theme-emerald {{ --accent-primary: #10b981; --accent-gradient: linear-gradient(135deg, #10b981, #06b6d4); --accent-glow: rgba(16, 185, 129, 0.25); }}
.theme-amber {{ --accent-primary: #f59e0b; --accent-gradient: linear-gradient(135deg, #f59e0b, #ea580c); --accent-glow: rgba(245, 158, 11, 0.25); }}
.theme-rose {{ --accent-primary: #f43f5e; --accent-gradient: linear-gradient(135deg, #f43f5e, #fb7185); --accent-glow: rgba(244, 63, 94, 0.25); }}
.theme-purple {{ --accent-primary: #a855f7; --accent-gradient: linear-gradient(135deg, #a855f7, #ec4899); --accent-glow: rgba(168, 85, 247, 0.25); }}
/* Light Mode */
.light-mode, .app-shell.light-mode {{
  --bg-page: #f8fafc;
  --bg-card: #ffffff;
  --bg-inner: #f1f5f9;
  --border-color: rgba(148, 163, 184, 0.25);
  --text-main: #0f172a;
  --text-muted: #64748b;
  color-scheme: light;
}}
* {{ box-sizing: border-box; }}
html, body, #root {{ min-height: 100%; margin: 0; padding: 0; }}
body {{ margin: 0; background: radial-gradient(circle at top, var(--accent-glow), transparent 36%), var(--bg-page); color: var(--text-main); }}
button, input, select, textarea {{ font: inherit; }}
.app-shell {{ display: grid; grid-template-columns: 290px 1fr; gap: 24px; min-height: 100vh; padding: 24px; }}
@media (max-width: 980px) {{
  .app-shell {{ grid-template-columns: 1fr; padding: 16px; }}
  .grid-block {{ grid-template-columns: 1fr; }}
  .dashboard-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}
.sidebar {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 28px; padding: 28px; display: flex; flex-direction: column; gap: 20px; }}
.brand {{ display: flex; align-items: center; gap: 12px; margin-bottom: 8px; text-decoration: none; color: inherit; }}
.brand-icon {{ width: 42px; height: 42px; flex: 0 0 auto; filter: drop-shadow(0 5px 12px var(--accent-glow)); }}
.brand-name {{ font-size: 1.3rem; font-weight: 800; letter-spacing: -0.03em; }}
.brand-sub {{ font-size: 0.75rem; color: var(--text-muted); }}
.nav-list {{ display: flex; flex-direction: column; gap: 8px; }}
.nav-list a {{ color: var(--text-muted); text-decoration: none; padding: 10px 16px; border-radius: 14px; transition: all 0.2s ease; display: flex; align-items: center; gap: 8px; }}
.nav-list a:hover, .nav-list a.active {{ background: var(--accent-glow); color: var(--accent-primary); font-weight: 600; }}
.custom-nav-link {{ border-left: 2px solid var(--accent-primary); }}
.sidebar-action-box {{ display: flex; flex-direction: column; gap: 8px; margin-top: auto; padding-top: 12px; border-top: 1px solid var(--border-color); }}
.btn-feature-add {{ background: var(--accent-gradient) !important; color: white !important; font-weight: 700; border-radius: 14px; padding: 12px 14px; border: none; cursor: pointer; }}
.btn-customizer {{ background: var(--bg-inner) !important; color: var(--text-main) !important; border: 1px solid var(--border-color); border-radius: 14px; padding: 10px 14px; cursor: pointer; }}
.sidebar-user {{ display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 12px; background: var(--bg-inner); border: 1px solid var(--border-color); }}
.sidebar-user .avatar {{ width: 32px; height: 32px; border-radius: 50%; background: var(--accent-primary); color: white; display: grid; place-items: center; font-weight: 700; }}
.page-content {{ display: flex; flex-direction: column; gap: 24px; min-width: 0; }}
.topbar {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 24px 28px; border-radius: 28px; background: var(--bg-card); border: 1px solid var(--border-color); }}
.topbar h1 {{ margin: 0; font-size: clamp(1.6rem, 2vw, 2.2rem); }}
.topbar-subtitle {{ margin: 4px 0 0; color: var(--text-muted); font-size: 0.9rem; }}
.top-actions {{ display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }}
.top-actions button, button {{ border: none; cursor: pointer; background: var(--accent-gradient); color: white; padding: 10px 18px; border-radius: 12px; font-weight: 600; transition: transform 0.15s ease, filter 0.15s ease; }}
button:hover {{ transform: translateY(-1px); filter: brightness(1.08); }}
.btn-primary {{ background: var(--accent-gradient) !important; color: white !important; }}
.btn-outline {{ background: transparent !important; border: 1px solid var(--border-color) !important; color: var(--text-main) !important; }}
.btn-ghost {{ background: var(--bg-inner) !important; color: var(--text-main) !important; border: 1px solid var(--border-color) !important; }}
.btn-glow-feature {{ background: linear-gradient(135deg, #10b981, #06b6d4) !important; color: white !important; box-shadow: 0 0 16px rgba(16, 185, 129, 0.35); }}
.btn-feature {{ background: color-mix(in srgb, var(--accent-primary) 16%, var(--bg-card)); border: 1px solid color-mix(in srgb, var(--accent-primary) 38%, var(--border-color)); color: var(--text-main); }}
.btn-sm {{ padding: 6px 12px !important; font-size: 0.85rem !important; border-radius: 8px !important; }}
.btn-xs {{ padding: 5px 10px !important; font-size: 0.8rem !important; border-radius: 6px !important; text-decoration: none; display: inline-flex; align-items: center; }}
.btn-edit {{ background: rgba(56, 189, 248, 0.15) !important; color: #38bdf8 !important; border: 1px solid rgba(56, 189, 248, 0.3) !important; }}
.btn-del {{ background: rgba(244, 63, 94, 0.15) !important; color: #f43f5e !important; border: 1px solid rgba(244, 63, 94, 0.3) !important; }}
.btn-danger {{ background: rgba(244, 63, 94, 0.15) !important; color: #f43f5e !important; border: 1px solid rgba(244, 63, 94, 0.3) !important; }}
.btn-del-sm {{ background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 2px 6px; }}
.btn-del-sm:hover {{ color: #f43f5e; }}
.content-block {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 28px; padding: 24px; }}
.grid-block {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; }}
.dashboard-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px; }}
@media (max-width: 640px) {{ .dashboard-grid {{ grid-template-columns: 1fr; }} }}
.dashboard-card, .resource-card, .panel {{ background: var(--bg-inner); border-radius: 24px; padding: 22px; border: 1px solid var(--border-color); }}
.stat-label {{ display: block; color: var(--text-muted); margin-bottom: 8px; font-size: 0.85rem; }}
.stat-value {{ font-size: 1.65rem; font-weight: 800; }}
.stat-sub {{ display: block; color: var(--text-muted); margin-top: 6px; font-size: 0.75rem; }}
.section-head-row {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }}
.section-head-row h2 {{ margin: 0; font-size: 1.25rem; display: flex; align-items: center; gap: 10px; }}
.feat-title-group {{ display: flex; align-items: center; gap: 14px; }}
.feat-large-icon {{ font-size: 2rem; }}
.table-wrap {{ width: 100%; overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; margin: 0; }}
th, td {{ text-align: left; padding: 14px 16px; border-bottom: 1px solid var(--border-color); }}
th {{ color: var(--text-muted); font-weight: 600; font-size: 0.85rem; }}
tr:hover {{ background: rgba(148, 163, 184, 0.05); }}
.badge-pill {{ display: inline-block; padding: 4px 10px; border-radius: 999px; background: var(--bg-inner); border: 1px solid var(--border-color); font-size: 0.75rem; font-weight: 600; }}
.status-pill {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }}
.status-active {{ background: rgba(16, 185, 129, 0.15); color: #10b981; }}
.action-btn-group {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }}
/* Domain Hero Banner Styles */
.domain-hero-banner {{ display: flex; justify-content: space-between; align-items: center; gap: 24px; padding: 28px 32px; border-radius: 28px; background: linear-gradient(135deg, var(--bg-card), var(--bg-inner)); border: 1px solid var(--border-color); position: relative; overflow: hidden; box-shadow: 0 12px 36px rgba(0,0,0,0.28); }}
@media (max-width: 900px) {{ .domain-hero-banner {{ flex-direction: column; align-items: flex-start; }} }}
.domain-hero-left {{ display: flex; flex-direction: column; gap: 8px; z-index: 1; }}
.domain-hero-visual {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; width: clamp(190px, 24vw, 280px); flex: 0 0 auto; }}
.domain-hero-image {{ width: 100%; height: 170px; object-fit: cover; border-radius: 18px; border: 1px solid var(--border-color); box-shadow: 0 12px 30px rgba(0,0,0,0.25); }}
@media (max-width: 900px) {{ .domain-hero-visual {{ width: 100%; }} .domain-hero-image {{ height: 150px; }} }}
.domain-hero-art {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
.domain-hero-art-card {{ display: flex; flex-direction: column; justify-content: space-between; min-width: 0; padding: 16px; border: 1px solid var(--border-color); border-radius: 14px; background: var(--bg-inner); }}
.domain-hero-art-card span {{ color: var(--text-muted); font-size: 0.68rem; letter-spacing: 0.1em; }}
.domain-hero-art-card strong {{ overflow-wrap: anywhere; font-size: 1.1rem; }}
.domain-hero-art-card i {{ width: 36px; height: 3px; border-radius: 4px; background: var(--accent-primary); }}
.domain-hero-badge {{ display: inline-block; padding: 6px 14px; border-radius: 999px; background: var(--accent-glow); color: var(--accent-primary); font-size: 0.8rem; font-weight: 700; letter-spacing: 0.04em; width: fit-content; border: 1px solid var(--accent-primary); }}
.domain-hero-title {{ margin: 0; font-size: clamp(1.8rem, 2.5vw, 2.4rem); font-weight: 800; letter-spacing: -0.03em; color: var(--text-main); }}
.domain-hero-desc {{ margin: 0; color: var(--text-muted); font-size: 0.95rem; max-width: 580px; line-height: 1.6; }}
.domain-hero-actions {{ display: flex; align-items: center; gap: 10px; margin-top: 6px; }}
.domain-hero-stats {{ display: flex; gap: 16px; flex-wrap: wrap; z-index: 1; }}
.domain-stat-card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 18px; padding: 14px 20px; display: flex; flex-direction: column; min-width: 120px; text-align: center; }}
.domain-stat-val {{ font-size: 1.5rem; font-weight: 800; color: var(--accent-primary); }}
.domain-stat-lbl {{ font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 4px; }}
/* Entity Manager & CRUD Styles */
.entity-manager-block {{ display: flex; flex-direction: column; gap: 18px; }}
.btn-edit-sm, .btn-del-corner {{ background: var(--bg-inner); border: 1px solid var(--border-color); color: var(--text-muted); border-radius: 8px; cursor: pointer; padding: 4px 8px; font-size: 0.75rem; }}
.btn-edit-sm:hover {{ color: var(--accent-primary); border-color: var(--accent-primary); }}
.btn-del-corner {{ position: absolute; top: 12px; right: 12px; width: 26px; height: 26px; display: grid; place-items: center; border-radius: 50%; padding: 0; }}
.btn-del-corner:hover {{ color: #f43f5e; border-color: #f43f5e; background: rgba(244, 63, 94, 0.12); }}
/* Real Login Component Styles in Generated Site */
.gen-auth-tabs {{ display: grid; grid-template-columns: 1fr 1fr; background: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 12px; padding: 4px; margin-bottom: 20px; gap: 6px; }}
.gen-auth-tab {{ background: transparent; border: none; color: var(--text-muted); padding: 8px 14px; border-radius: 8px; font-weight: 600; font-size: 0.85rem; cursor: pointer; transition: all 0.2s ease; }}
.gen-auth-tab.active {{ background: var(--accent-gradient); color: white; box-shadow: 0 4px 14px var(--accent-glow); }}
.gen-auth-alert {{ padding: 12px 14px; border-radius: 10px; font-size: 0.82rem; margin-bottom: 14px; }}
.gen-auth-alert-err {{ background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.35); color: #fb7185; }}
.gen-auth-alert-ok {{ background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); color: #6ee7b7; }}
.gen-login-form {{ display: flex; flex-direction: column; gap: 14px; }}
.auth-hint-text {{ margin-top: 10px; font-size: 0.8rem; color: var(--text-muted); text-align: center; }}
.text-link {{ background: none; border: none; color: var(--accent-primary); font-weight: 600; cursor: pointer; text-decoration: underline; padding: 0 4px; }}
.user-session-card {{ text-align: center; padding: 32px 24px; }}
.session-status-badge {{ display: inline-block; padding: 6px 14px; border-radius: 999px; background: rgba(16, 185, 129, 0.15); color: #10b981; font-weight: 700; font-size: 0.8rem; margin-bottom: 12px; border: 1px solid rgba(16, 185, 129, 0.3); }}
/* Kanban Board Styles */
.kanban-container {{ display: flex; flex-direction: column; gap: 16px; }}
.kanban-add-bar, .custom-table-add-bar {{ display: flex; gap: 10px; }}
.kanban-add-bar input, .custom-table-add-bar input {{ flex: 1; }}
.kanban-board {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }}
@media (max-width: 860px) {{ .kanban-board {{ grid-template-columns: 1fr; }} }}
.kanban-col {{ background: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 20px; padding: 16px; display: flex; flex-direction: column; gap: 12px; min-height: 220px; }}
.kanban-col-head {{ display: flex; align-items: center; justify-content: space-between; font-weight: 700; font-size: 0.9rem; padding-bottom: 8px; border-bottom: 1px solid var(--border-color); }}
.col-count {{ background: var(--bg-card); padding: 2px 8px; border-radius: 999px; font-size: 0.75rem; }}
.kanban-col-body {{ display: flex; flex-direction: column; gap: 10px; }}
.kanban-card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 14px; padding: 12px; display: flex; flex-direction: column; gap: 8px; position: relative; }}
.kanban-card.in-progress {{ border-left: 3px solid #38bdf8; }}
.kanban-card.done {{ border-left: 3px solid #10b981; opacity: 0.85; }}
.kanban-card-title {{ font-weight: 600; font-size: 0.9rem; }}
.kanban-card-meta {{ display: flex; align-items: center; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); }}
.kanban-card-btns {{ display: flex; align-items: center; gap: 4px; }}
.kanban-card-btns button {{ padding: 4px 8px; font-size: 0.75rem; border-radius: 6px; background: var(--bg-inner); color: var(--text-main); border: 1px solid var(--border-color); }}
.kanban-card-btns button.btn-done {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border-color: rgba(16, 185, 129, 0.3); }}
/* Form Module Styles */
.custom-form-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
@media (max-width: 860px) {{ .custom-form-container {{ grid-template-columns: 1fr; }} }}
.custom-form-panel, .custom-submissions-panel {{ background: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 20px; padding: 20px; }}
.submissions-list {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; max-height: 280px; overflow-y: auto; }}
.submission-card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; padding: 12px; display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }}
.submission-text {{ margin: 6px 0 0; font-size: 0.85rem; color: var(--text-muted); }}
/* Notes Module Styles */
.custom-notes-container {{ display: flex; flex-direction: column; gap: 16px; }}
.notes-add-row {{ display: flex; gap: 10px; }}
.notes-add-row input {{ flex: 1; }}
.notes-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }}
.note-card {{ background: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 16px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; position: relative; }}
.note-body {{ margin: 0; font-size: 0.95rem; }}
.note-footer {{ display: flex; align-items: center; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); }}
/* Modals & Forms */
label {{ display: flex; flex-direction: column; gap: 8px; margin-bottom: 14px; color: var(--text-main); font-size: 0.9rem; font-weight: 500; }}
input, select, textarea {{ width: 100%; padding: 12px 14px; border-radius: 14px; border: 1px solid var(--border-color); background: var(--bg-inner); color: var(--text-main); box-sizing: border-box; }}
input:focus, select:focus, textarea:focus {{ outline: none; border-color: var(--accent-primary); box-shadow: 0 0 0 3px var(--accent-glow); }}
.form-row-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
@media (max-width: 600px) {{ .form-row-2 {{ grid-template-columns: 1fr; }} }}
.modal-overlay, .modal-backdrop {{ position: fixed; inset: 0; background: rgba(2, 6, 23, 0.75); backdrop-filter: blur(4px); display: grid; place-items: center; padding: 20px; z-index: 999; }}
.modal, .modal-card {{ width: min(520px, 100%); background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 28px; padding: 28px; max-height: 90vh; overflow-y: auto; }}
.modal-lg {{ width: min(720px, 100%); }}
.modal h2, .modal-card h2 {{ margin: 0 0 18px; font-size: 1.3rem; }}
.modal-actions, .form-actions {{ display: flex; justify-content: flex-end; align-items: center; gap: 10px; margin-top: 18px; }}
.modal-header-tabs {{ margin-bottom: 18px; }}
.modal-tabs {{ display: flex; gap: 10px; margin-top: 12px; }}
.modal-tab-btn {{ background: var(--bg-inner); color: var(--text-muted); border: 1px solid var(--border-color); padding: 8px 16px; border-radius: 10px; cursor: pointer; }}
.modal-tab-btn.active {{ background: var(--accent-gradient); color: white; border-color: transparent; }}
.icon-picker {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.icon-btn {{ width: 38px; height: 38px; display: grid; place-items: center; background: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 10px; font-size: 1.1rem; cursor: pointer; padding: 0; }}
.icon-btn.selected {{ border-color: var(--accent-primary); background: var(--accent-glow); transform: scale(1.08); }}
.preset-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; margin: 14px 0; }}
.preset-chip {{ background: var(--bg-inner); color: var(--text-main); border: 1px solid var(--border-color); padding: 10px 14px; border-radius: 12px; text-align: left; font-size: 0.85rem; cursor: pointer; transition: all 0.15s ease; }}
.preset-chip:hover {{ border-color: var(--accent-primary); transform: translateY(-1px); }}
.palette-grid {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 6px; }}
.color-swatch, .palette-swatch {{ width: 38px; height: 38px; border-radius: 50%; border: 2px solid transparent; cursor: pointer; display: grid; place-items: center; color: white; font-weight: 700; font-size: 0.85rem; padding: 0; }}
.color-swatch.selected, .palette-swatch.selected {{ border-color: white; transform: scale(1.1); box-shadow: 0 0 10px rgba(255,255,255,0.4); }}
.btn-group {{ display: flex; gap: 8px; }}
.btn-toggle {{ flex: 1; background: var(--bg-inner); color: var(--text-muted); border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 10px; cursor: pointer; }}
.btn-toggle.active {{ background: var(--accent-gradient); color: white; border-color: transparent; }}
.btn-danger-ghost {{ background: transparent !important; color: #f43f5e !important; border: 1px solid rgba(244, 63, 94, 0.3) !important; padding: 10px 16px; border-radius: 12px; margin-right: auto; }}
.toast-banner {{ padding: 14px 18px; border-radius: 16px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.18), rgba(56, 189, 248, 0.14)); border: 1px solid rgba(16, 185, 129, 0.35); color: #a7f3d0; font-weight: 600; }}
.floating-studio-btn, .floating-feature {{ position: fixed; bottom: 28px; right: 28px; background: var(--accent-gradient); color: white; font-weight: 700; font-size: 0.95rem; padding: 14px 22px; border-radius: 999px; box-shadow: 0 8px 24px var(--accent-glow); border: none; cursor: pointer; z-index: 80; display: flex; align-items: center; gap: 8px; transition: transform 0.2s ease; }}
.floating-studio-btn:hover, .floating-feature:hover {{ transform: scale(1.05); }}
.media-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; }}
.media-card, .media-item {{ background: var(--bg-inner); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; padding: 8px; display: flex; flex-direction: column; align-items: center; }}
.media-image, .media-video {{ width: 100%; border-radius: 12px; max-height: 180px; object-fit: cover; }}
.media-file {{ padding: 24px 12px; display: flex; flex-direction: column; align-items: center; gap: 8px; font-size: 0.85rem; }}
.media-icon {{ font-size: 2rem; }}
.eyebrow {{ margin: 0 0 7px; color: var(--accent-primary); font-size: .72rem; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }}
.muted {{ color: var(--text-muted); }}
.text-xs {{ font-size: 0.75rem; }}
.empty-state {{ padding: 24px 12px; color: var(--text-muted); }}
.recent-section {{ margin-top: 24px; padding: 18px; border: 1px solid var(--border-color); border-radius: 16px; }}
.recent-list {{ display: grid; gap: 10px; padding: 0; list-style: none; }}
.recent-list li {{ display: flex; align-items: center; gap: 12px; }}
.record-mark {{ display: grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; background: var(--bg-inner); color: var(--accent-primary); }}
.form-error {{ color: #fb7185; }}
'''
        design = PremiumDesignEngine()
        direction = design.create_art_direction(prompt)
        return base + "\n" + design.create_css(direction)

    def _build_languages_ts(self, spec: dict[str, Any]) -> str:
        dictionaries = build_language_dictionaries(spec)
        for item in spec.get("nav", []):
            labels = item.get("label", {})
            english = labels.get("en")
            if not english:
                continue
            key = re.sub(r"[^a-z0-9]+", "", english.casefold())
            for code in LANG_CODES:
                dictionaries[code][key] = labels.get(code, english)
        quote = lambda value: "'" + value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n") + "'"
        locale_blocks = []
        for code, values in dictionaries.items():
            entries = ",\n".join(f"    {quote(key)}: {quote(value)}" for key, value in values.items())
            locale_blocks.append(f"  {quote(code)}: {{\n{entries}\n  }}")
        return "export const translations = {\n" + ",\n".join(locale_blocks) + "\n} as const;\nexport type LangCode = keyof typeof translations;\n"

    @staticmethod
    def _build_language_context_tsx(language: str = "en") -> str:
        default_language = language if language in LANG_CODES else "en"
        return f'''import React, {{ createContext, useContext, useMemo, useState, type ReactNode }} from 'react';
import {{ translations, type LangCode }} from './languages';
interface LanguageContextValue {{ lang: LangCode; setLang: (lang: LangCode) => void; t: (key: string) => string; }}
const LanguageContext = createContext<LanguageContextValue | null>(null);
export const LanguageProvider: React.FC<{{ children: ReactNode }}> = ({{ children }}) => {{
  const [lang, setLang] = useState<LangCode>('{default_language}');
  const value = useMemo(() => ({{ lang, setLang, t: (key: string) => (translations[lang] as Record<string, string>)[key] ?? key }}), [lang]);
  return <LanguageContext.Provider value={{value}}>{{children}}</LanguageContext.Provider>;
}};
export const useLanguage = () => {{ const value = useContext(LanguageContext); if (!value) throw new Error('LanguageProvider is required.'); return value; }};
'''

    @staticmethod
    def _build_language_switcher_tsx() -> str:
        return '''import React from 'react';
import { useLanguage } from './LanguageContext';
const LanguageSwitcher: React.FC = () => {
  const { lang, setLang } = useLanguage();
  return <label className="language-control">Language<select aria-label="Language" value={lang} onChange={(event) => setLang(event.target.value as typeof lang)}><option value="en">English</option><option value="hi">हिन्दी</option><option value="kn">ಕನ್ನಡ</option><option value="mr">मराठी</option><option value="te">తెలుగు</option></select></label>;
};
export default LanguageSwitcher;
'''

    @staticmethod
    def generate_main_tsx() -> str:
        return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
'''

    @staticmethod
    def generate_package_json(project_name: str, requirements: str = "") -> str:
        name = re.sub(r"[^a-z0-9-]+", "-", project_name.casefold()).strip("-") or "generated-app"
        return json.dumps({
            "name": name, "private": True, "version": "0.0.1", "type": "module",
            "scripts": {"dev": "vite", "build": "tsc -b && vite build", "preview": "vite preview"},
            "dependencies": {"react": "^18.3.1", "react-dom": "^18.3.1"},
            "devDependencies": {
                "@types/react": "^18.3.12", "@types/react-dom": "^18.3.1", "@types/node": "^20.0.0",
                "@vitejs/plugin-react": "^4.3.1", "typescript": "^5.6.3", "vite": "^5.4.10", "tslib": "^2.8.1",
            },
        }, indent=2)

    @staticmethod
    def generate_index_html(project_name: str, requirements: str = "") -> str:
        title = project_name or "Generated Application"
        return f'<!doctype html>\n<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><meta name="theme-color" content="#11151c" /><title>{title}</title></head><body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>\n'

    @staticmethod
    def generate_tsconfig_json() -> str:
        return json.dumps({
            "compilerOptions": {"target": "ES2020", "useDefineForClassFields": True, "lib": ["DOM", "DOM.Iterable", "ES2020"], "allowJs": False, "skipLibCheck": True, "esModuleInterop": True, "allowSyntheticDefaultImports": True, "strict": True, "forceConsistentCasingInFileNames": True, "module": "ESNext", "moduleResolution": "Bundler", "resolveJsonModule": True, "isolatedModules": True, "noEmit": True, "jsx": "react-jsx", "incremental": True, "types": ["vite/client"]},
            "include": ["src"], "references": [{"path": "./tsconfig.node.json"}],
        }, indent=2)

    @staticmethod
    def generate_tsconfig_node_json() -> str:
        return json.dumps({"compilerOptions": {"composite": True, "skipLibCheck": True, "module": "ESNext", "moduleResolution": "Bundler", "allowSyntheticDefaultImports": True, "types": ["node"]}, "include": ["vite.config.ts"]}, indent=2)

    @staticmethod
    def generate_vite_config_ts() -> str:
        return "import { defineConfig } from 'vite';\nimport react from '@vitejs/plugin-react';\nexport default defineConfig({ plugins: [react()] });\n"

    def _build_generation_prompt(self, project_name: str, requirements: str) -> str:
        return f"Generate a React application named {project_name} for these requirements: {requirements}. Return TypeScript source only."

    def generate_tsx(
        self, project_name: str, requirements: str, filename: str | None = None
    ) -> str:
        component_name = Path(filename).name if filename else "Component"
        prompt = (
            f"Generate a React + TypeScript component named {component_name} for {project_name}. "
            f"Requirements: {requirements}. Return only valid TypeScript source."
        )
        return self._strip_markdown_fences(self._generate_text(prompt)).strip()

    @staticmethod
    def _strip_markdown_fences(generated_text: str) -> str:
        cleaned = re.sub(r"```(?:tsx?|typescript)?\s*", "", generated_text, flags=re.IGNORECASE)
        return re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE)
