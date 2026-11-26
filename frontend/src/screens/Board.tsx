// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";

import { api } from "@/api/client";
import { clearSessionToken, getSessionToken, subscribeSession } from "@/lib/api";
import { Icons } from "@/lib/icons";
import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";

const PRODUCT = "Voting Idea";
const SCREEN = "Ideas Board";

export default function Screen() {
  const navigate = useNavigate();
  // undefined while GET /ideas is pending, null when it failed.
  const [ideas, setIdeas] = React.useState(undefined);
  React.useEffect(() => {
    let current = true;
    api
      .GET("/ideas")
      .then(({ data }) => {
        if (current) setIdeas(data ?? null);
      })
      .catch(() => {
        if (current) setIdeas(null);
      });
    return () => {
      current = false;
    };
  }, []);
  const loggedIn = React.useSyncExternalStore(subscribeSession, getSessionToken) !== null;
  const [voting, setVoting] = React.useState(null);
  const [voteFailed, setVoteFailed] = React.useState(false);

  // Votes are permanent upvotes: the only action is to add one. The list is re-ranked
  // like the server ranks it: most votes first, ties newest first.
  const upvote = async (idea) => {
    if (!loggedIn) {
      navigate("log-in");
      return;
    }
    setVoting(idea.id);
    setVoteFailed(false);
    try {
      const { data, response } = await api.POST("/ideas/{idea_id}/vote", {
        params: { path: { idea_id: idea.id } },
      });
      if (response && response.status === 401) {
        clearSessionToken();
      } else if (data) {
        setIdeas((current) =>
          (current ?? [])
            .map((item) =>
              item.id === data.ideaId
                ? { ...item, voteCount: data.voteCount, voted: data.voted }
                : item,
            )
            .sort(
              (a, b) =>
                b.voteCount - a.voteCount ||
                (a.createdAt < b.createdAt ? 1 : a.createdAt > b.createdAt ? -1 : 0),
            ),
        );
      } else {
        setVoteFailed(true);
      }
    } catch {
      setVoteFailed(true);
    } finally {
      setVoting(null);
    }
  };
  const frame = {
    border: `1px solid ${brand.accentColor}`,
    outline: `1px solid ${brand.primaryColor}`,
    outlineOffset: 3,
    borderRadius: brand.radius,
  };
  const caps = {
    fontFamily: brand.fontHeading,
    textTransform: "uppercase",
    letterSpacing: "0.3em",
  };
  const focusCls = "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2";
  const rule = (
    <div aria-hidden className="flex items-center gap-3">
      <span className="h-px flex-1" style={{ backgroundColor: brand.accentColor }} />
      <span className="text-xs" style={{ color: brand.accentColor }}>
        ◆
      </span>
      <span className="h-px flex-1" style={{ backgroundColor: brand.accentColor }} />
    </div>
  );

  return (
    <div className="space-y-8" style={{ color: brand.primaryColor, fontFamily: brand.fontBody }}>
      <style>{`@media (prefers-reduced-motion: no-preference){.deco-btn{transition:opacity .15s ease}.deco-btn:hover{opacity:.85}}`}</style>
      <header className="space-y-4 text-center">
        <h1 data-testid="ideas-board-title" className="text-3xl" style={caps}>
          {SCREEN}
        </h1>
        <p
          className="text-[10px] uppercase tracking-[0.35em]"
          style={{ color: brand.neutralColor }}
        >
          {PRODUCT}
        </p>
        {rule}
      </header>

      {loggedIn ? null : (
        <section
          data-wf="b-1-0"
          data-testid="log-in-or-sign-up-to-vote-modal"
          aria-labelledby="vote-prompt"
          className="mx-auto max-w-xl p-7 text-center"
          style={frame}
        >
          <h2 id="vote-prompt" className="text-sm" style={caps}>
            Log in or sign up to vote
          </h2>
          <div
            aria-hidden
            className="mx-auto mt-3 h-px w-12"
            style={{ backgroundColor: brand.accentColor }}
          />
          <div className="mt-5 flex flex-col justify-center gap-4 sm:flex-row">
            <button
              type="button"
              data-wf="i-1-0-0"
              data-testid="log-in-link"
              onClick={() => navigate("log-in")}
              className={`deco-btn h-11 min-w-[8rem] px-6 text-xs uppercase tracking-[0.25em] ${focusCls}`}
              style={{
                backgroundColor: brand.primaryColor,
                color: brand.accentColor,
                border: `1px solid ${brand.primaryColor}`,
                borderRadius: brand.radius,
                outlineColor: brand.primaryColor,
              }}
            >
              Log in
            </button>
            <button
              type="button"
              data-wf="i-1-0-1"
              data-testid="sign-up-link"
              onClick={() => navigate("sign-up")}
              className={`deco-btn h-11 min-w-[8rem] px-6 text-xs uppercase tracking-[0.25em] ${focusCls}`}
              style={{
                backgroundColor: "transparent",
                color: brand.primaryColor,
                border: `1px solid ${brand.primaryColor}`,
                borderRadius: brand.radius,
                outlineColor: brand.primaryColor,
              }}
            >
              Sign up
            </button>
          </div>
        </section>
      )}

      <section data-wf="b-2-0" aria-labelledby="ranked-heading" className="space-y-4">
        <h2 id="ranked-heading" className="text-center text-sm" style={caps}>
          Ideas ranked by votes
        </h2>
        {ideas === undefined ? (
          <p role="status" className="text-center text-sm">
            Loading ideas…
          </p>
        ) : null}
        {ideas === null ? (
          <p role="alert" className="text-center text-sm">
            Could not load the ideas.
          </p>
        ) : null}
        {voteFailed ? (
          <p role="alert" className="text-center text-sm">
            Could not record your vote.
          </p>
        ) : null}
        {ideas && ideas.length > 0 ? (
          <ul data-testid="ideas-ranked-by-votes-list" className="grid gap-7">
            {ideas.map((idea) => (
              <li
                key={idea.id}
                className="flex flex-col items-center gap-4 p-7 text-center sm:flex-row sm:text-left"
                style={frame}
              >
                <div className="flex-1">
                  <h3 className="text-sm" style={caps}>
                    {idea.title}
                  </h3>
                  <div
                    aria-hidden
                    className="mt-3 h-px w-12 sm:mx-0 mx-auto"
                    style={{ backgroundColor: brand.accentColor }}
                  />
                  <p className="mt-3 text-sm">{idea.description}</p>
                </div>
                <p
                  className="text-2xl"
                  style={{ fontFamily: brand.fontHeading, fontVariantNumeric: "tabular-nums" }}
                >
                  {idea.voteCount}{" "}
                  <span className="text-[10px] uppercase tracking-[0.25em]">
                    {idea.voteCount === 1 ? "vote" : "votes"}
                  </span>
                </p>
                {idea.voted ? (
                  <span
                    className="flex items-center gap-2 text-[10px] uppercase tracking-[0.25em]"
                    style={{ color: brand.accentColor }}
                  >
                    <Icons.Check aria-hidden="true" />
                    You have voted
                  </span>
                ) : (
                  <button
                    type="button"
                    data-wf={idea.id}
                    onClick={() => upvote(idea)}
                    disabled={voting === idea.id}
                    aria-label={
                      loggedIn ? `Vote for ${idea.title}` : `Vote for ${idea.title} — log in first`
                    }
                    className={`deco-btn flex h-11 w-11 items-center justify-center ${focusCls}`}
                    style={{
                      backgroundColor: brand.primaryColor,
                      color: brand.accentColor,
                      borderRadius: brand.radius,
                      outlineColor: brand.primaryColor,
                    }}
                  >
                    <Icons.Plus aria-hidden="true" />
                  </button>
                )}
              </li>
            ))}
          </ul>
        ) : null}
      </section>

      {ideas && ideas.length === 0 ? (
        <button
          type="button"
          data-wf="b-3-0"
          data-testid="no-ideas-yet-post-the-first-idea-empty"
          onClick={() => navigate("post-idea")}
          className={`deco-btn mx-auto block w-full max-w-xl p-7 text-center ${focusCls}`}
          style={{
            ...frame,
            backgroundColor: "transparent",
            color: brand.primaryColor,
            outlineColor: brand.primaryColor,
          }}
        >
          <span className="block text-sm" style={caps}>
            No ideas yet. Post the first idea!
          </span>
          <span
            aria-hidden
            className="mx-auto mt-3 block h-px w-12"
            style={{ backgroundColor: brand.accentColor }}
          />
          <span className="mt-3 block text-[10px] uppercase tracking-[0.25em]">
            Go to Post an Idea
          </span>
        </button>
      ) : null}
    </div>
  );
}
