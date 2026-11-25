// @ts-nocheck -- generated from the approved design under its JS runtime contract; not hand-written TypeScript.
/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";

import * as UI from "@/lib/ui";
import { Icons } from "@/lib/icons";
import { brand } from "@/lib/brand";
import { useNavigate } from "@/lib/navigate";

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const { Button, Input, Label } = UI;

const REGISTERED_EMAILS = [
  'maren.holt@brightwell.co',
  'dev.okafor@brightwell.co',
  'sofia.lindqvist@gmail.com',
  'tomas.reyes@northpier.io',
];

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function Diamond({ color }) {
  return (
    <div aria-hidden="true" className="flex items-center justify-center gap-3 w-full">
      <span style={{ flex: 1, height: 1, backgroundColor: color }} />
      <span style={{ width: 8, height: 8, backgroundColor: color, transform: 'rotate(45deg)', display: 'inline-block' }} />
      <span style={{ flex: 1, height: 1, backgroundColor: color }} />
    </div>
  );
}

export default function Screen() {
  const navigate = useNavigate();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [errors, setErrors] = React.useState({});
  const [created, setCreated] = React.useState(false);

  const primary = brand.primaryColor;
  const accent = brand.accentColor;

  const validate = () => {
    const next = {};
    const trimmed = email.trim();
    if (!trimmed) {
      next.email = 'Enter your email address.';
    } else if (!EMAIL_PATTERN.test(trimmed)) {
      next.email = 'This email address looks incomplete. Use the form name@example.com.';
    } else if (REGISTERED_EMAILS.includes(trimmed.toLowerCase())) {
      next.email = 'This email is already registered. Log in instead, or use a different address.';
    }
    if (!password) {
      next.password = 'Enter a password to protect your account.';
    }
    return next;
  };

  const submit = (e) => {
    e.preventDefault();
    if (created) return;
    const next = validate();
    setErrors(next);
    if (Object.keys(next).length === 0) {
      setCreated(true);
      navigate('board');
    }
  };

  const fieldStyle = (hasError) => ({
    borderRadius: 0,
    border: `1px solid ${primary}`,
    borderLeftWidth: hasError ? 6 : 1,
    backgroundColor: brand.backgroundColor,
    color: primary,
    height: 48,
    fontFamily: brand.fontBody,
    fontSize: 16,
  });

  const labelStyle = {
    fontFamily: brand.fontHeading,
    letterSpacing: '0.18em',
    textTransform: 'uppercase',
    fontSize: 12,
    color: primary,
    fontWeight: 600,
  };

  const ErrorLine = ({ id, children }) => (
    <p id={id} role="alert" className="flex items-start gap-2 mt-2" style={{ color: primary, fontSize: 14, lineHeight: 1.5, fontWeight: 600 }}>
      <span aria-hidden="true" style={{ marginTop: 2, flexShrink: 0 }}><Icons.AlertCircle width={16} height={16} /></span>
      <span>{children}</span>
    </p>
  );

  return (
    <main
      className="min-h-screen w-full flex items-center justify-center px-4 py-12"
      style={{ backgroundColor: brand.backgroundColor, color: primary, fontFamily: brand.fontBody }}
    >
      <style>{`
        .gb-field:focus-visible, .gb-btn:focus-visible, .gb-link:focus-visible { outline: 3px solid ${primary}; outline-offset: 3px; }
        .gb-btn { transition: background-color .2s ease, color .2s ease; }
        .gb-btn:hover { background-color: ${accent} !important; color: ${primary} !important; }
        .gb-btn:active { transform: translateY(1px); }
        .gb-link { text-decoration: underline; text-underline-offset: 4px; }
        .gb-link:hover { text-decoration-thickness: 2px; }
        .gb-msg { animation: gbIn .25s ease; }
        @keyframes gbIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: none; } }
        @media (prefers-reduced-motion: reduce) { .gb-msg { animation: none; } .gb-btn { transition: none; } }
      `}</style>

      <div style={{ width: '100%', maxWidth: 480, padding: 8 }}>
        {/* double frame: accent hairline, primary outline offset outside */}
        <div style={{ border: `1px solid ${accent}`, outline: `1px solid ${primary}`, outlineOffset: 6, padding: '48px 32px 40px', backgroundColor: brand.backgroundColor }}>
          <div data-wf="b-0-0" className="text-center">
            <p aria-hidden="true" style={{ fontFamily: brand.fontHeading, letterSpacing: '0.3em', fontSize: 12, textTransform: 'uppercase', marginBottom: 16 }}>
              Idea Voting Board
            </p>
            <h1 style={{ fontFamily: brand.fontHeading, textTransform: 'uppercase', letterSpacing: '0.14em', fontSize: 32, lineHeight: 1.2, fontWeight: 700 }}>
              Create your account
            </h1>
            <p style={{ fontSize: 15, lineHeight: 1.5, marginTop: 12 }}>
              An email and a password. Nothing else is asked, and there is no verification step.
            </p>
          </div>

          <div style={{ margin: '32px 0' }}><Diamond color={accent} /></div>

          <section data-wf="b-1-0" aria-labelledby="signup-heading">
            <h2 id="signup-heading" className="text-center" style={{ fontFamily: brand.fontHeading, textTransform: 'uppercase', letterSpacing: '0.24em', fontSize: 18, fontWeight: 600, marginBottom: 24 }}>
              Sign up
            </h2>
            <form id="signup-form" onSubmit={submit} noValidate>
              <div style={{ marginBottom: 24 }}>
                <Label htmlFor="signup-email" style={labelStyle}>Email</Label>
                <div style={{ height: 8 }} />
                <Input
                  data-wf="i-1-0-0"
                  id="signup-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  className="gb-field"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  aria-invalid={errors.email ? 'true' : 'false'}
                  aria-describedby={errors.email ? 'signup-email-error' : 'signup-email-hint'}
                  style={fieldStyle(!!errors.email)}
                />
                {errors.email ? (
                  <div className="gb-msg"><ErrorLine id="signup-email-error">{errors.email}</ErrorLine></div>
                ) : (
                  <p id="signup-email-hint" style={{ fontSize: 13, marginTop: 8, lineHeight: 1.5 }}>
                    Any email address works. Other members never see it.
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="signup-password" style={labelStyle}>Password</Label>
                <div style={{ height: 8 }} />
                <Input
                  data-wf="i-1-0-1"
                  id="signup-password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  className="gb-field"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  aria-invalid={errors.password ? 'true' : 'false'}
                  aria-describedby={errors.password ? 'signup-password-error' : 'signup-password-hint'}
                  style={fieldStyle(!!errors.password)}
                />
                {errors.password ? (
                  <div className="gb-msg"><ErrorLine id="signup-password-error">{errors.password}</ErrorLine></div>
                ) : (
                  <p id="signup-password-hint" style={{ fontSize: 13, marginTop: 8, lineHeight: 1.5 }}>
                    Stored only as a salted hash, never in readable form.
                  </p>
                )}
              </div>
            </form>
          </section>

          <div data-wf="b-2-0" style={{ marginTop: 32 }}>
            <Button
              data-wf="b-2-0"
              type="submit"
              form="signup-form"
              className="gb-btn"
              disabled={created}
              style={{
                width: '100%',
                minHeight: 52,
                borderRadius: 0,
                backgroundColor: primary,
                color: accent,
                border: `1px solid ${primary}`,
                fontFamily: brand.fontHeading,
                letterSpacing: '0.24em',
                textTransform: 'uppercase',
                fontSize: 14,
                fontWeight: 700,
                cursor: created ? 'default' : 'pointer',
              }}
            >
              {created ? 'Account created' : 'Sign up'}
            </Button>
            {created && (
              <p role="status" className="gb-msg flex items-center justify-center gap-2" style={{ marginTop: 16, fontSize: 14, fontWeight: 600 }}>
                <Icons.CheckCircle width={16} height={16} aria-hidden="true" />
                You are logged in. Opening the board.
              </p>
            )}
          </div>

          <div style={{ margin: '32px 0 24px' }}><Diamond color={accent} /></div>

          <div className="text-center">
            <button
              data-wf="b-3-0"
              type="button"
              className="gb-link"
              onClick={() => navigate('log-in')}
              style={{ color: primary, fontSize: 15, minHeight: 44, padding: '0 8px', background: 'none', border: 0, cursor: 'pointer', fontWeight: 600 }}
            >
              Already have an account? Log in
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
