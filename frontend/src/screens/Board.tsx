// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";

import { Icons } from "@/lib/icons";
import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const { Search } = Icons;

const PRODUCT = "Voting Idea";
const SCREEN = "Ideas Board";

const CARDS = [
  ["Meridian Holdings", "Portfolio", "No. 041"],
  ["Aster & Co.", "Advisory", "No. 042"],
  ["Riverside Estate", "Portfolio", "No. 043"],
  ["Harbor Trust", "Custody", "No. 044"],
  ["Calder Group", "Advisory", "No. 045"],
  ["Beaumont Line", "Custody", "No. 046"],
];

const IDEAS = [
  { id: "i-2-0-0", title: "Dark mode for the dashboard", description: "Add a dark theme option.", votes: 42, created_at: "2026-11-02T09:00:00Z", icon: "plus" },
  { id: "i-2-0-1", title: "Weekly demo day", description: "Show progress every Friday.", votes: 31, created_at: "2026-11-09T09:00:00Z", icon: "plus" },
  { id: "i-2-0-2", title: "Quiet room booking", description: "Reserve focus rooms.", votes: 0, created_at: "2026-11-20T09:00:00Z", icon: "check" },
];

export default function Screen() {
  const navigate = useNavigate();
  const [query, setQuery] = React.useState("");
  const frame = { border: `1px solid ${brand.accentColor}`, outline: `1px solid ${brand.primaryColor}`, outlineOffset: 3, borderRadius: brand.radius };
  const caps = { fontFamily: brand.fontHeading, textTransform: "uppercase", letterSpacing: "0.3em" };
  const cards = CARDS.filter((c) => c[0].toLowerCase().includes(query.toLowerCase()));
  const ranked = [...IDEAS].sort((a, b) => b.votes - a.votes || new Date(b.created_at) - new Date(a.created_at));
  const focusCls = "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2";
  const rule = (
    <div aria-hidden className="flex items-center gap-3">
      <span className="h-px flex-1" style={{ backgroundColor: brand.accentColor }} />
      <span className="text-xs" style={{ color: brand.accentColor }}>◆</span>
      <span className="h-px flex-1" style={{ backgroundColor: brand.accentColor }} />
    </div>
  );

  return (
    <div className="space-y-8" style={{ color: brand.primaryColor, fontFamily: brand.fontBody }}>
      <style>{`@media (prefers-reduced-motion: no-preference){.deco-btn{transition:opacity .15s ease}.deco-btn:hover{opacity:.85}}`}</style>
      <header className="space-y-4 text-center">
        <h1 className="text-3xl" style={caps}>{SCREEN}</h1>
        <p className="text-[10px] uppercase tracking-[0.35em]" style={{ color: brand.neutralColor }}>{PRODUCT} — {cards.length} on the register</p>
        {rule}
      </header>

      <section data-wf="b-1-0" aria-labelledby="vote-prompt" className="mx-auto max-w-xl p-7 text-center" style={frame}>
        <h2 id="vote-prompt" className="text-sm" style={caps}>Log in or sign up to vote</h2>
        <div aria-hidden className="mx-auto mt-3 h-px w-12" style={{ backgroundColor: brand.accentColor }} />
        <div className="mt-5 flex flex-col justify-center gap-4 sm:flex-row">
          <button type="button" data-wf="i-1-0-0" onClick={() => navigate('log-in')} className={`deco-btn h-11 min-w-[8rem] px-6 text-xs uppercase tracking-[0.25em] ${focusCls}`} style={{ backgroundColor: brand.primaryColor, color: brand.accentColor, border: `1px solid ${brand.primaryColor}`, borderRadius: brand.radius, outlineColor: brand.primaryColor }}>Log in</button>
          <button type="button" data-wf="i-1-0-1" onClick={() => navigate('sign-up')} className={`deco-btn h-11 min-w-[8rem] px-6 text-xs uppercase tracking-[0.25em] ${focusCls}`} style={{ backgroundColor: "transparent", color: brand.primaryColor, border: `1px solid ${brand.primaryColor}`, borderRadius: brand.radius, outlineColor: brand.primaryColor }}>Sign up</button>
        </div>
      </section>

      <section data-wf="b-2-0" aria-labelledby="ranked-heading" className="space-y-4">
        <h2 id="ranked-heading" className="text-center text-sm" style={caps}>Ideas ranked by votes</h2>
        <ul className="grid gap-7">
          {ranked.map((idea) => (
            <li key={idea.id} className="flex flex-col items-center gap-4 p-7 text-center sm:flex-row sm:text-left" style={frame}>
              <div className="flex-1">
                <h3 className="text-sm" style={caps}>{idea.title}</h3>
                <div aria-hidden className="mt-3 h-px w-12 sm:mx-0 mx-auto" style={{ backgroundColor: brand.accentColor }} />
                <p className="mt-3 text-sm">{idea.description}</p>
              </div>
              <p className="text-2xl" style={{ fontFamily: brand.fontHeading, fontVariantNumeric: "tabular-nums" }}>
                {idea.votes} <span className="text-[10px] uppercase tracking-[0.25em]">{idea.votes === 1 ? "vote" : "votes"}</span>
              </p>
              <button type="button" data-wf={idea.id} onClick={() => navigate('log-in')} aria-label={`Vote for ${idea.title} — log in first`} className={`deco-btn flex h-11 w-11 items-center justify-center ${focusCls}`} style={{ backgroundColor: brand.primaryColor, color: brand.accentColor, borderRadius: brand.radius, outlineColor: brand.primaryColor }}>
                {idea.icon === "check" ? <Icons.Check aria-hidden="true" /> : <Icons.Plus aria-hidden="true" />}
              </button>
            </li>
          ))}
        </ul>
      </section>

      <button type="button" data-wf="b-3-0" onClick={() => navigate('post-idea')} className={`deco-btn mx-auto block w-full max-w-xl p-7 text-center ${focusCls}`} style={{ ...frame, backgroundColor: "transparent", color: brand.primaryColor, outlineColor: brand.primaryColor }}>
        <span className="block text-sm" style={caps}>No ideas yet. Post the first idea!</span>
        <span aria-hidden className="mx-auto mt-3 block h-px w-12" style={{ backgroundColor: brand.accentColor }} />
        <span className="mt-3 block text-[10px] uppercase tracking-[0.25em]">Go to Post an Idea</span>
      </button>

      <div className="mx-auto flex max-w-xl items-center gap-4">
        <input aria-label="Search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="SEARCH THE REGISTER" className="h-11 flex-1 bg-transparent px-4 text-center text-xs tracking-[0.25em] outline-none placeholder:opacity-60" style={{ border: `1px solid ${brand.accentColor}`, borderRadius: brand.radius, color: brand.primaryColor }} />
      </div>

      <div className="grid grid-cols-3 gap-7">
        {cards.map(([name, mandate, no]) => (
          <article key={no} className="p-7 text-center" style={frame}>
            <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full text-lg" style={{ border: `1px solid ${brand.accentColor}`, fontFamily: brand.fontHeading, color: brand.accentColor }}>{name[0]}</span>
            <h2 className="mt-4 text-sm" style={caps}>{name}</h2>
            <div aria-hidden className="mx-auto mt-3 h-px w-12" style={{ backgroundColor: brand.accentColor }} />
            <p className="mt-3 text-[10px] uppercase tracking-[0.25em]" style={{ color: brand.neutralColor }}>{mandate} — {no}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
