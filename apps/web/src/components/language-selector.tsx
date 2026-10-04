"use client";

import { useEffect, useId, useMemo, useState, type KeyboardEvent } from "react";
import { Check, Languages, Search } from "lucide-react";
import { cn } from "@/lib/cn";

export interface LanguageOption {
  code: string;
  nativeName: string;
  englishName: string;
  direction?: "ltr" | "rtl";
}

export const foundationLanguages: LanguageOption[] = [
  { code: "en", nativeName: "English", englishName: "English" },
  { code: "hi", nativeName: "हिन्दी", englishName: "Hindi" },
  { code: "mr", nativeName: "मराठी", englishName: "Marathi" },
  { code: "bn", nativeName: "বাংলা", englishName: "Bengali" },
  { code: "gu", nativeName: "ગુજરાતી", englishName: "Gujarati" },
  { code: "pa", nativeName: "ਪੰਜਾਬੀ", englishName: "Punjabi" },
  { code: "ta", nativeName: "தமிழ்", englishName: "Tamil" },
  { code: "te", nativeName: "తెలుగు", englishName: "Telugu" },
  { code: "kn", nativeName: "ಕನ್ನಡ", englishName: "Kannada" },
  { code: "ml", nativeName: "മലയാളം", englishName: "Malayalam" },
  { code: "or", nativeName: "ଓଡ଼ିଆ", englishName: "Odia" },
  { code: "ur", nativeName: "اردو", englishName: "Urdu", direction: "rtl" },
];

export function LanguageSelector({
  languages = foundationLanguages,
  defaultCode = "en",
  onChange,
}: {
  languages?: LanguageOption[];
  defaultCode?: string;
  onChange?: (code: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(defaultCode);
  const [activeIndex, setActiveIndex] = useState(0);
  const labelId = useId();
  const listId = useId();
  const filtered = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    return languages.filter((language) =>
      `${language.nativeName} ${language.englishName}`
        .toLocaleLowerCase()
        .includes(normalized),
    );
  }, [languages, query]);
  const safeActiveIndex =
    filtered.length === 0
      ? -1
      : Math.min(Math.max(activeIndex, 0), filtered.length - 1);

  useEffect(() => {
    setActiveIndex((current) =>
      filtered.length === 0
        ? -1
        : Math.min(Math.max(current, 0), filtered.length - 1),
    );
  }, [filtered]);

  const choose = (language: LanguageOption) => {
    setSelected(language.code);
    onChange?.(language.code);
    setQuery("");
    setActiveIndex(0);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (
      filtered.length > 0 &&
      (event.key === "ArrowDown" || event.key === "ArrowUp")
    ) {
      event.preventDefault();
      const delta = event.key === "ArrowDown" ? 1 : -1;
      setActiveIndex(() => {
        const current =
          safeActiveIndex < 0 ? (delta > 0 ? -1 : 0) : safeActiveIndex;
        return (current + delta + filtered.length) % filtered.length;
      });
    }
    if (event.key === "Enter" && filtered[safeActiveIndex]) {
      event.preventDefault();
      choose(filtered[safeActiveIndex]);
    }
    if (event.key === "Escape" && query) {
      event.preventDefault();
      setQuery("");
      setActiveIndex(0);
    }
  };

  const selectedLanguage = languages.find(
    (language) => language.code === selected,
  );

  return (
    <div className="language-selector">
      <label id={labelId} htmlFor={`${listId}-search`}>
        <Languages aria-hidden="true" /> Language
      </label>
      <p className="language-selector__selected" aria-live="polite">
        Selected:{" "}
        <strong dir={selectedLanguage?.direction}>
          {selectedLanguage?.nativeName}
        </strong>
        {selectedLanguage?.nativeName !== selectedLanguage?.englishName
          ? ` · ${selectedLanguage?.englishName}`
          : ""}
      </p>
      <div className="language-selector__search">
        <Search aria-hidden="true" />
        <input
          id={`${listId}-search`}
          type="search"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setActiveIndex(0);
          }}
          onKeyDown={onKeyDown}
          role="combobox"
          aria-autocomplete="list"
          aria-expanded="true"
          aria-controls={listId}
          aria-activedescendant={
            safeActiveIndex >= 0
              ? `${listId}-option-${filtered[safeActiveIndex].code}`
              : undefined
          }
          aria-describedby={`${listId}-help`}
          placeholder="Search languages"
        />
      </div>
      <p id={`${listId}-help`} className="language-selector__help">
        Options stay visible while you search. Use Up and Down to move, Enter to
        select, or Escape to clear the search.
      </p>
      <ul
        id={listId}
        role="listbox"
        aria-labelledby={labelId}
        className="language-selector__list"
      >
        {filtered.map((language, index) => (
          <li key={language.code} role="presentation">
            <button
              type="button"
              role="option"
              id={`${listId}-option-${language.code}`}
              tabIndex={-1}
              aria-selected={selected === language.code}
              className={cn(index === safeActiveIndex && "is-active")}
              onClick={() => choose(language)}
            >
              <span dir={language.direction}>{language.nativeName}</span>
              <small>{language.englishName}</small>
              {selected === language.code ? <Check aria-hidden="true" /> : null}
            </button>
          </li>
        ))}
      </ul>
      {filtered.length === 0 ? (
        <p role="status">No language names match this search.</p>
      ) : null}
      <p className="language-selector__truth">
        Control shell only · linguistic validation pending
      </p>
    </div>
  );
}
