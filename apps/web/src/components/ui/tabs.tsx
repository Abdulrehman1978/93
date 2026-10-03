"use client";

import {
  useId,
  useRef,
  useState,
  type KeyboardEvent,
  type ReactNode,
} from "react";
import { cn } from "@/lib/cn";

export interface TabItem {
  id: string;
  label: string;
  content: ReactNode;
}

export function Tabs({ items, label }: { items: TabItem[]; label: string }) {
  const [activeId, setActiveId] = useState(items[0]?.id ?? "");
  const baseId = useId();
  const refs = useRef<Array<HTMLButtonElement | null>>([]);

  const move = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    const direction =
      event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    if (!direction) return;
    event.preventDefault();
    const next = (index + direction + items.length) % items.length;
    setActiveId(items[next].id);
    refs.current[next]?.focus();
  };

  return (
    <div className="tabs">
      <div role="tablist" aria-label={label} className="tabs__list">
        {items.map((item, index) => (
          <button
            key={item.id}
            ref={(node) => {
              refs.current[index] = node;
            }}
            type="button"
            role="tab"
            id={`${baseId}-tab-${item.id}`}
            aria-controls={`${baseId}-panel-${item.id}`}
            aria-selected={activeId === item.id}
            tabIndex={activeId === item.id ? 0 : -1}
            className={cn("tabs__tab", activeId === item.id && "is-active")}
            onClick={() => setActiveId(item.id)}
            onKeyDown={(event) => move(event, index)}
          >
            {item.label}
          </button>
        ))}
      </div>
      {items.map((item) => (
        <div
          key={item.id}
          role="tabpanel"
          id={`${baseId}-panel-${item.id}`}
          aria-labelledby={`${baseId}-tab-${item.id}`}
          hidden={activeId !== item.id}
          className="tabs__panel"
        >
          {item.content}
        </div>
      ))}
    </div>
  );
}
