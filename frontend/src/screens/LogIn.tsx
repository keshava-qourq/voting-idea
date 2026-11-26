// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";
import { useLocation } from "react-router-dom";

import * as UI from "@/lib/ui";
import { Icons } from "@/lib/icons";
import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";
import { api } from "@/api/client";
import { setSessionToken } from "@/lib/api";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const { Input, Label } = UI;

// One message for an unknown email and a wrong password: it never says which was wrong.
const LOGIN_FAILED = "Incorrect email or password";
const GENERIC_ERROR = "Something went wrong. Try again.";

export default function Screen() {
  const navigate = useNavigate();
  const location = useLocation();
  // Where the visitor was headed when prompted to log in: the post form, else the board.
  const returnTo = location.state && location.state.from === "post-idea" ? "post-idea" : "board";
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [formError, setFormError] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  const ink = brand.primaryColor;
  const gold = brand.accentColor;

  const submit = async (ev) => {
    ev.preventDefault();
    if (loading) return;
    setFormError("");
    setLoading(true);
    try {
      const { data, response } = await api.POST("/auth/login", {
        body: { email: email.trim(), password },
      });
      if (data) {
        setSessionToken(data.token);
        navigate(returnTo);
        return;
      }
      const status = response && response.status;
      setFormError(status === 401 || status === 422 ? LOGIN_FAILED : GENERIC_ERROR);
    } catch {
      setFormError(GENERIC_ERROR);
    } finally {
      setLoading(false);
    }
  };

  const Rule = () => (
    <div
      aria-hidden="true"
      style={{ display: "flex", alignItems: "center", gap: 12, width: "100%" }}
    >
      <span style={{ flex: 1, height: 1, backgroundColor: gold }} />
      <span style={{ width: 8, height: 8, backgroundColor: ink, transform: "rotate(45deg)" }} />
      <span style={{ flex: 1, height: 1, backgroundColor: gold }} />
    </div>
  );

  const fieldStyle = (bad) => ({
    borderRadius: 0,
    minHeight: 48,
    backgroundColor: "transparent",
    border: "1px solid " + ink,
    color: ink,
    outline: bad ? "2px solid " + ink : undefined,
    outlineOffset: bad ? 2 : undefined,
    fontFamily: brand.fontBody,
  });

  const labelStyle = {
    display: "block",
    marginBottom: 8,
    fontSize: 12,
    letterSpacing: "0.2em",
    textTransform: "uppercase",
    fontWeight: 600,
    color: ink,
  };

  const msgStyle = {
    display: "flex",
    gap: 8,
    alignItems: "flex-start",
    marginTop: 8,
    fontSize: 13,
    lineHeight: 1.5,
    color: ink,
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: brand.backgroundColor,
        color: ink,
        fontFamily: brand.fontBody,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "48px 24px",
      }}
    >
      <style>{`
        .gb-focus:focus-visible { outline: 2px solid ${ink}; outline-offset: 3px; }
        .gb-input:focus-visible { outline: 2px solid ${ink} !important; outline-offset: 3px !important; }
        .gb-primary { transition: background-color .2s ease, color .2s ease, letter-spacing .2s ease; }
        .gb-primary:hover:not(:disabled) { background-color: ${gold} !important; color: ${ink} !important; }
        .gb-primary:active:not(:disabled) { transform: translateY(1px); }
        .gb-link { background: none; border: 0; cursor: pointer; text-decoration: underline; text-underline-offset: 6px; text-decoration-color: ${gold}; text-decoration-thickness: 1px; transition: text-decoration-color .2s ease; }
        .gb-link:hover { text-decoration-color: ${ink}; }
        @keyframes gb-rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
        @keyframes gb-spin { to { transform: rotate(405deg); } }
        .gb-rise { animation: gb-rise .5s ease both; }
        .gb-msg { animation: gb-rise .25s ease both; }
        .gb-diamond { animation: gb-spin 1s linear infinite; }
        @media (prefers-reduced-motion: reduce) {
          .gb-rise, .gb-msg, .gb-diamond { animation: none !important; }
          .gb-primary, .gb-link { transition: none !important; }
        }
      `}</style>

      <main style={{ width: "100%", maxWidth: 460 }} className="gb-rise">
        {/* outer primary outline, offset from the gold frame */}
        <div style={{ border: "1px solid " + ink, padding: 6 }}>
          <div
            style={{
              border: "1px solid " + gold,
              padding: "48px 32px 32px",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center",
              gap: 24,
            }}
          >
            <div
              data-wf="b-0-0"
              style={{
                width: "100%",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 16,
              }}
            >
              <span
                aria-hidden="true"
                style={{
                  fontSize: 12,
                  letterSpacing: "0.4em",
                  textTransform: "uppercase",
                  fontFamily: brand.fontHeading,
                  paddingLeft: "0.4em",
                }}
              >
                Idea Voting Board
              </span>
              <h1
                data-testid="log-in-title"
                style={{
                  fontFamily: brand.fontHeading,
                  fontSize: 36,
                  lineHeight: 1.2,
                  fontWeight: 700,
                  letterSpacing: "0.24em",
                  textTransform: "uppercase",
                  margin: 0,
                  paddingLeft: "0.24em",
                }}
              >
                Log in
              </h1>
              <Rule />
            </div>

            <div data-wf="b-1-0" style={{ width: "100%" }}>
              <p style={{ margin: 0, fontSize: 16, lineHeight: 1.5 }}>Please log in to continue</p>
              <p style={{ margin: "8px 0 0", fontSize: 13, lineHeight: 1.5 }}>
                Voting and posting need an account. You will return to the board once you are in.
              </p>
            </div>

            <form
              id="login-form"
              data-testid="log-in-form"
              data-wf="b-2-0"
              aria-label="Log in"
              onSubmit={submit}
              noValidate
              style={{
                width: "100%",
                textAlign: "left",
                display: "flex",
                flexDirection: "column",
                gap: 24,
              }}
            >
              {formError && (
                <div
                  role="alert"
                  className="gb-msg"
                  style={{
                    display: "flex",
                    gap: 12,
                    alignItems: "flex-start",
                    padding: 16,
                    border: "1px solid " + ink,
                    borderLeftWidth: 4,
                    fontSize: 14,
                    lineHeight: 1.5,
                  }}
                >
                  <Icons.AlertCircle
                    aria-hidden="true"
                    width={20}
                    height={20}
                    style={{ flexShrink: 0, marginTop: 1 }}
                  />
                  <div>
                    <strong
                      style={{
                        display: "block",
                        letterSpacing: "0.12em",
                        textTransform: "uppercase",
                        fontSize: 12,
                        marginBottom: 4,
                      }}
                    >
                      Could not log you in
                    </strong>
                    <span>{formError}</span>
                  </div>
                </div>
              )}

              <div>
                <Label htmlFor="login-email" style={labelStyle}>
                  Email
                </Label>
                <Input
                  id="login-email"
                  data-wf="i-2-0-0"
                  className="gb-input"
                  type="email"
                  name="email"
                  autoComplete="email"
                  value={email}
                  data-testid="email-input"
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  style={fieldStyle(!!formError)}
                />
              </div>

              <div>
                <Label htmlFor="login-password" style={labelStyle}>
                  Password
                </Label>
                <Input
                  id="login-password"
                  data-wf="i-2-0-1"
                  className="gb-input"
                  type="password"
                  name="password"
                  autoComplete="current-password"
                  value={password}
                  data-testid="password-input"
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  style={fieldStyle(!!formError)}
                />
              </div>
            </form>

            <div data-wf="b-3-0" style={{ width: "100%" }}>
              <button
                type="submit"
                form="login-form"
                data-testid="log-in-btn"
                data-wf="i-3-0"
                disabled={loading}
                aria-busy={loading ? "true" : "false"}
                className="gb-primary gb-focus"
                style={{
                  width: "100%",
                  minHeight: 52,
                  backgroundColor: ink,
                  color: gold,
                  border: "1px solid " + ink,
                  borderRadius: 0,
                  fontFamily: brand.fontHeading,
                  fontSize: 14,
                  fontWeight: 700,
                  letterSpacing: "0.28em",
                  textTransform: "uppercase",
                  cursor: loading ? "progress" : "pointer",
                  opacity: loading ? 0.85 : 1,
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 12,
                }}
              >
                {loading && (
                  <span
                    aria-hidden="true"
                    className="gb-diamond"
                    style={{
                      width: 8,
                      height: 8,
                      backgroundColor: gold,
                      transform: "rotate(45deg)",
                      display: "inline-block",
                    }}
                  />
                )}
                {loading ? "Checking" : "Log in"}
              </button>
            </div>

            <div
              data-wf="b-4-0"
              style={{
                width: "100%",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 16,
              }}
            >
              <Rule />
              <button
                type="button"
                data-testid="new-here-sign-up-link"
                data-wf="i-4-0"
                className="gb-link gb-focus"
                onClick={() => navigate("sign-up")}
                style={{
                  minHeight: 44,
                  padding: "0 12px",
                  fontSize: 14,
                  color: ink,
                  fontFamily: brand.fontBody,
                }}
              >
                New here? Sign up
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
