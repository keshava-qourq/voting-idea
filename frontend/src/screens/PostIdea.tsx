// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";

import * as UI from "@/lib/ui";
import { Icons } from "@/lib/icons";
import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const { Button, Input, Textarea, Label } = UI;

const TITLE_MAX = 80;
const DESC_MAX = 280;

function Ornament() {
  return (
    <div
      aria-hidden="true"
      className="flex items-center justify-center gap-3 my-6"
      style={{ color: brand.accentColor }}
    >
      <span style={{ flex: 1, height: 1, backgroundColor: brand.accentColor }} />
      <span
        style={{
          width: 10,
          height: 10,
          transform: "rotate(45deg)",
          border: "1px solid " + brand.primaryColor,
          backgroundColor: brand.accentColor,
        }}
      />
      <span style={{ flex: 1, height: 1, backgroundColor: brand.accentColor }} />
    </div>
  );
}

export default function Screen() {
  const navigate = useNavigate();
  const [member, setMember] = React.useState(false);
  const [title, setTitle] = React.useState("");
  const [desc, setDesc] = React.useState("");
  const [errors, setErrors] = React.useState({});
  const [promptTried, setPromptTried] = React.useState(false);
  const [posted, setPosted] = React.useState(false);
  const promptRef = React.useRef(null);

  React.useEffect(() => {
    if (!posted) return undefined;
    const t = setTimeout(() => navigate("board"), 1400);
    return () => clearTimeout(t);
  }, [posted]);

  React.useEffect(() => {
    if (promptTried && promptRef.current) promptRef.current.focus();
  }, [promptTried]);

  const tl = title.length;
  const dl = desc.length;

  function validate() {
    const e = {};
    if (!title.trim()) e.title = "Add a title so colleagues know what the idea is.";
    else if (tl > TITLE_MAX)
      e.title =
        "The title is " +
        (tl - TITLE_MAX) +
        " characters over the limit of " +
        TITLE_MAX +
        ". Shorten it to post.";
    if (!desc.trim()) e.desc = "Add a short description so colleagues can judge the idea.";
    else if (dl > DESC_MAX)
      e.desc =
        "The description is " +
        (dl - DESC_MAX) +
        " characters over the limit of " +
        DESC_MAX +
        ". Shorten it to post.";
    return e;
  }

  function onSubmit(ev) {
    ev.preventDefault();
    if (!member) {
      setPromptTried(true);
      return;
    }
    const e = validate();
    setErrors(e);
    if (Object.keys(e).length === 0) setPosted(true);
  }

  const ink = brand.primaryColor;
  const gold = brand.accentColor;
  const soft = { color: ink, opacity: 0.8 };
  const errColor = "firebrick";
  const label = {
    fontFamily: brand.fontHeading,
    letterSpacing: "0.14em",
    textTransform: "uppercase",
    fontSize: 13,
    color: ink,
    fontWeight: 600,
  };
  const primaryBtn = {
    backgroundColor: ink,
    color: gold,
    border: "1px solid " + ink,
    borderRadius: 0,
    letterSpacing: "0.16em",
    textTransform: "uppercase",
    fontFamily: brand.fontHeading,
    minHeight: 48,
    width: "100%",
    fontSize: 14,
  };
  const ghostBtn = {
    backgroundColor: "transparent",
    color: ink,
    border: "1px solid " + ink,
    borderRadius: 0,
    letterSpacing: "0.16em",
    textTransform: "uppercase",
    fontFamily: brand.fontHeading,
    minHeight: 48,
    width: "100%",
    fontSize: 14,
  };
  const fieldStyle = (bad) => ({
    borderRadius: 0,
    backgroundColor: "white",
    color: ink,
    border: "1px solid " + (bad ? errColor : ink),
    fontFamily: brand.fontBody,
    fontSize: 16,
    width: "100%",
    padding: "12px 12px",
  });

  return (
    <div
      style={{
        backgroundColor: brand.backgroundColor,
        color: ink,
        fontFamily: brand.fontBody,
        minHeight: "100%",
      }}
      className="px-4 py-8 sm:py-12"
    >
      <style>{`
        .gp-focus:focus-visible, .gp-focus input:focus-visible, .gp-focus textarea:focus-visible { outline: 3px solid ${ink}; outline-offset: 3px; }
        .gp-field:focus-visible { outline: 3px solid ${ink}; outline-offset: 2px; box-shadow: 0 0 0 5px ${gold}; }
        .gp-btn { transition: background-color .18s ease, color .18s ease, transform .18s ease; }
        .gp-btn:not(:disabled):hover { transform: translateY(-1px); }
        .gp-btn:disabled { opacity: .55; cursor: not-allowed; }
        .gp-prim:not(:disabled):hover { background-color: ${gold} !important; color: ${ink} !important; }
        .gp-ghost:not(:disabled):hover { background-color: ${ink} !important; color: ${gold} !important; }
        @keyframes gp-in { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
        .gp-in { animation: gp-in .28s ease both; }
        @media (prefers-reduced-motion: reduce) { .gp-in { animation: none; } .gp-btn { transition: none; } .gp-btn:not(:disabled):hover { transform: none; } }
      `}</style>

      <div className="mx-auto" style={{ maxWidth: 640 }}>
        {/* Double frame: outer primary outline offset outside the gold frame */}
        <div
          style={{
            outline: "1px solid " + ink,
            outlineOffset: 6,
            border: "1px solid " + gold,
            backgroundColor: brand.backgroundColor,
          }}
          className="p-6 sm:p-12 mx-1.5"
        >
          <div className="text-center">
            <p style={{ ...label, fontSize: 12, opacity: 0.8, letterSpacing: "0.28em" }}>
              The Ideas Board
            </p>
            <h1
              data-wf="b-0-0"
              className="mt-3"
              style={{
                fontFamily: brand.fontHeading,
                textTransform: "uppercase",
                letterSpacing: "0.18em",
                fontSize: "clamp(26px, 6vw, 38px)",
                lineHeight: 1.15,
                fontWeight: 700,
                color: ink,
              }}
            >
              Post an Idea
            </h1>
          </div>

          <Ornament />

          {!member && (
            <section aria-label="Log in required" className="text-center mb-8">
              <p
                data-wf="b-1-0"
                ref={promptRef}
                tabIndex={-1}
                role={promptTried ? "alert" : undefined}
                className="gp-focus"
                style={{
                  fontSize: 16,
                  lineHeight: 1.5,
                  color: ink,
                  fontWeight: promptTried ? 700 : 400,
                }}
              >
                Log in or sign up to post an idea.
              </p>
              {promptTried && (
                <p
                  className="gp-in mt-2 inline-flex items-center gap-2 justify-center"
                  style={{ fontSize: 14, color: ink }}
                >
                  <Icons.AlertCircle aria-hidden="true" width={16} height={16} />
                  Nothing was posted. What you typed below is kept for when you are back.
                </p>
              )}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-6">
                <div data-wf="b-2-0">
                  <Button
                    type="button"
                    className="gp-btn gp-prim gp-focus"
                    style={primaryBtn}
                    onClick={() => navigate("log-in")}
                  >
                    Log in
                  </Button>
                </div>
                <div data-wf="b-2-1">
                  <Button
                    type="button"
                    className="gp-btn gp-ghost gp-focus"
                    style={ghostBtn}
                    onClick={() => navigate("sign-up")}
                  >
                    Sign up
                  </Button>
                </div>
              </div>
              <Ornament />
            </section>
          )}

          <form data-wf="b-3-0" onSubmit={onSubmit} noValidate aria-labelledby="new-idea-heading">
            <h2
              id="new-idea-heading"
              className="text-center"
              style={{
                fontFamily: brand.fontHeading,
                textTransform: "uppercase",
                letterSpacing: "0.2em",
                fontSize: 20,
                fontWeight: 600,
              }}
            >
              New idea
            </h2>
            <p className="text-center mt-2" style={{ fontSize: 14, ...soft }}>
              {member
                ? "Your idea joins the board with zero votes. Ideas cannot be edited or deleted once posted."
                : "You can draft here, but posting needs an account."}
            </p>

            <div className="mt-8">
              <div className="flex items-baseline justify-between gap-3">
                <Label htmlFor="idea-title" style={label}>
                  Title
                </Label>
                <span
                  style={{
                    fontSize: 13,
                    fontVariantNumeric: "tabular-nums",
                    fontFamily: "ui-monospace, Menlo, monospace",
                    color: tl > TITLE_MAX ? errColor : ink,
                    fontWeight: tl > TITLE_MAX ? 700 : 400,
                  }}
                >
                  {tl} / {TITLE_MAX}
                </span>
              </div>
              <Input
                id="idea-title"
                data-wf="i-3-0-0"
                className="gp-field mt-2"
                style={fieldStyle(!!errors.title)}
                value={title}
                disabled={posted}
                onChange={(e) => {
                  setTitle(e.target.value);
                  if (errors.title) setErrors({ ...errors, title: undefined });
                }}
                aria-invalid={errors.title ? "true" : "false"}
                aria-describedby={"title-help" + (errors.title ? " title-err" : "")}
                autoComplete="off"
              />
              <p id="title-help" className="mt-2" style={{ fontSize: 13, ...soft }}>
                Up to {TITLE_MAX} characters. A short, plain name for the idea.
              </p>
              {errors.title && (
                <p
                  id="title-err"
                  role="alert"
                  className="gp-in mt-2 flex items-start gap-2"
                  style={{ fontSize: 14, color: errColor, fontWeight: 600 }}
                >
                  <Icons.AlertCircle
                    aria-hidden="true"
                    width={16}
                    height={16}
                    style={{ marginTop: 2, flexShrink: 0 }}
                  />
                  <span>{errors.title}</span>
                </p>
              )}
            </div>

            <div className="mt-6">
              <div className="flex items-baseline justify-between gap-3">
                <Label htmlFor="idea-desc" style={label}>
                  Short description
                </Label>
                <span
                  style={{
                    fontSize: 13,
                    fontVariantNumeric: "tabular-nums",
                    fontFamily: "ui-monospace, Menlo, monospace",
                    color: dl > DESC_MAX ? errColor : ink,
                    fontWeight: dl > DESC_MAX ? 700 : 400,
                  }}
                >
                  {dl} / {DESC_MAX}
                </span>
              </div>
              <Textarea
                id="idea-desc"
                data-wf="i-3-0-1"
                className="gp-field mt-2"
                rows={5}
                style={{ ...fieldStyle(!!errors.desc), resize: "vertical" }}
                value={desc}
                disabled={posted}
                onChange={(e) => {
                  setDesc(e.target.value);
                  if (errors.desc) setErrors({ ...errors, desc: undefined });
                }}
                aria-invalid={errors.desc ? "true" : "false"}
                aria-describedby={"desc-help" + (errors.desc ? " desc-err" : "")}
              />
              <p id="desc-help" className="mt-2" style={{ fontSize: 13, ...soft }}>
                Up to {DESC_MAX} characters. What it is and why it would help the team.
              </p>
              {errors.desc && (
                <p
                  id="desc-err"
                  role="alert"
                  className="gp-in mt-2 flex items-start gap-2"
                  style={{ fontSize: 14, color: errColor, fontWeight: 600 }}
                >
                  <Icons.AlertCircle
                    aria-hidden="true"
                    width={16}
                    height={16}
                    style={{ marginTop: 2, flexShrink: 0 }}
                  />
                  <span>{errors.desc}</span>
                </p>
              )}
            </div>

            {posted && (
              <div
                role="status"
                className="gp-in mt-6 flex items-center justify-center gap-2 text-center p-4"
                style={{
                  border: "1px solid " + ink,
                  backgroundColor: gold,
                  color: ink,
                  fontWeight: 600,
                }}
              >
                <Icons.CheckCircle aria-hidden="true" width={18} height={18} />
                <span>Idea posted with zero votes. Taking you to the board…</span>
              </div>
            )}

            <Ornament />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 items-center">
              <div data-wf="b-4-0">
                <Button
                  type="submit"
                  disabled={posted}
                  className="gp-btn gp-prim gp-focus"
                  style={primaryBtn}
                >
                  {posted ? "Posting…" : "Submit idea"}
                </Button>
              </div>
              <div data-wf="b-4-1" className="text-center">
                <button
                  type="button"
                  onClick={() => navigate("board")}
                  className="gp-focus inline-flex items-center justify-center gap-2"
                  style={{
                    minHeight: 48,
                    padding: "0 16px",
                    color: ink,
                    background: "none",
                    border: "none",
                    textDecoration: "underline",
                    textUnderlineOffset: 4,
                    textDecorationColor: gold,
                    textDecorationThickness: 2,
                    letterSpacing: "0.16em",
                    textTransform: "uppercase",
                    fontFamily: brand.fontHeading,
                    fontSize: 14,
                    cursor: "pointer",
                  }}
                >
                  <Icons.ArrowLeft aria-hidden="true" width={16} height={16} />
                  Cancel
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
