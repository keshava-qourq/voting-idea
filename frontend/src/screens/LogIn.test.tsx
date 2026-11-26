import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "@/App";

const post = vi.hoisted(() => vi.fn());
const get = vi.hoisted(() => vi.fn());
vi.mock("@/api/client", () => ({ api: { POST: post, GET: get } }));

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

function fill(email: string, password: string) {
  fireEvent.change(screen.getByTestId("email-input"), { target: { value: email } });
  fireEvent.change(screen.getByTestId("password-input"), { target: { value: password } });
  fireEvent.click(screen.getByTestId("log-in-btn"));
}

describe("Log In", () => {
  beforeEach(() => {
    post.mockReset();
    get.mockReset();
    get.mockResolvedValue({ error: { detail: "Sign in first" }, response: { status: 401 } });
    window.localStorage.clear();
  });

  it("[AC-008] logs in, keeps the token and shows that I am logged in", async () => {
    const pwd = crypto.randomUUID();
    post.mockResolvedValue({
      data: {
        token: "t-" + crypto.randomUUID(),
        user: { id: "u1", email: "a@b.io", role: "user" },
      },
      response: { status: 200 },
    });
    renderAt("/log-in");
    expect(screen.getByTestId("log-in-title")).toBeInTheDocument();
    expect(screen.getByTestId("log-in-form")).toBeInTheDocument();
    expect(screen.getByText("Please log in to continue")).toBeInTheDocument();
    get.mockResolvedValue({
      data: { id: "u1", email: "a@b.io", role: "user" },
      response: { status: 200 },
    });
    fill("a@b.io", pwd);
    expect(await screen.findByText("Logged in as a@b.io")).toBeInTheDocument();
    expect(post).toHaveBeenCalledWith("/auth/login", { body: { email: "a@b.io", password: pwd } });
    expect(window.localStorage.getItem("session_token")).toMatch(/^t-/);
  });

  it("[AC-009] shows the generic message on a 401 and stays logged out", async () => {
    post.mockResolvedValue({
      error: { code: "INVALID_CREDENTIALS", message: "x" },
      response: { status: 401 },
    });
    renderAt("/log-in");
    fill("a@b.io", crypto.randomUUID());
    expect(await screen.findByText("Incorrect email or password")).toBeInTheDocument();
    expect(screen.getByTestId("log-in-form")).toBeInTheDocument();
    expect(window.localStorage.getItem("session_token")).toBeNull();
  });

  it("[AC-009] shows the same message for an unknown email and a wrong password", async () => {
    post.mockResolvedValue({ error: { message: "x" }, response: { status: 401 } });
    const first = renderAt("/log-in");
    fill("unknown@b.io", crypto.randomUUID());
    const one = (await screen.findByRole("alert")).textContent;
    first.unmount();
    renderAt("/log-in");
    fill("a@b.io", crypto.randomUUID());
    const two = (await screen.findByRole("alert")).textContent;
    expect(one).toBe(two);
  });

  it("[AC-009] shows an error and stays on the form when the server fails", async () => {
    post.mockRejectedValue(new Error("down"));
    renderAt("/log-in");
    fill("a@b.io", crypto.randomUUID());
    expect(await screen.findByText("Something went wrong. Try again.")).toBeInTheDocument();
    expect(screen.getByTestId("log-in-btn")).not.toBeDisabled();
  });

  it("[AC-010] drops the expired session and prompts me to log in on the post form", async () => {
    window.localStorage.setItem("session_token", "t-" + crypto.randomUUID());
    renderAt("/post-idea");
    expect(await screen.findByText("Log in or sign up to post an idea")).toBeInTheDocument();
    await waitFor(() => expect(window.localStorage.getItem("session_token")).toBeNull());
  });

  it("[AC-026] after prompting on the post form, login brings me back to the post form", async () => {
    post.mockResolvedValue({
      data: {
        token: "t-" + crypto.randomUUID(),
        user: { id: "u1", email: "a@b.io", role: "user" },
      },
      response: { status: 200 },
    });
    renderAt("/post-idea");
    await screen.findByText("Log in or sign up to post an idea");
    fireEvent.click(screen.getByTestId("log-in-btn"));
    expect(await screen.findByTestId("log-in-form")).toBeInTheDocument();
    get.mockResolvedValue({
      data: { id: "u1", email: "a@b.io", role: "user" },
      response: { status: 200 },
    });
    fill("a@b.io", crypto.randomUUID());
    expect(await screen.findByTestId("new-idea-form")).toBeInTheDocument();
    expect(screen.queryByText("Log in or sign up to post an idea")).not.toBeInTheDocument();
  });

  it("[AC-026] a plain login takes me to the board", async () => {
    post.mockResolvedValue({
      data: {
        token: "t-" + crypto.randomUUID(),
        user: { id: "u1", email: "a@b.io", role: "user" },
      },
      response: { status: 200 },
    });
    renderAt("/log-in");
    fill("a@b.io", crypto.randomUUID());
    expect(await screen.findByText("Ideas Board", { selector: "a" })).toBeInTheDocument();
    expect(screen.queryByTestId("log-in-form")).not.toBeInTheDocument();
  });

  it("[AC-011] offers no password reset option", () => {
    renderAt("/log-in");
    expect(screen.queryByText(/forgot/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/reset/i)).not.toBeInTheDocument();
  });

  it("[AC-008] the sign-up link opens the sign-up screen", () => {
    renderAt("/log-in");
    fireEvent.click(screen.getByTestId("new-here-sign-up-link"));
    expect(screen.getByTestId("create-your-account-title")).toBeInTheDocument();
  });
});

describe("Log In responsive layout", () => {
  beforeEach(() => {
    post.mockReset();
    get.mockReset();
    get.mockResolvedValue({ error: { detail: "Sign in first" }, response: { status: 401 } });
    window.localStorage.clear();
  });

  it("[AC-035] the card shrinks to a phone and the fields and button are tap sized", () => {
    const { container } = renderAt("/log-in");

    expect(container.querySelector('[data-layout="auth-card"]')!.className).toContain("px-5");
    expect(screen.getByTestId("email-input").className).toContain("h-11");
    expect(screen.getByTestId("password-input").className).toContain("h-11");
    expect(screen.getByTestId("log-in-btn")).toHaveStyle({ minHeight: "52px" });
    expect(screen.getByTestId("new-here-sign-up-link")).toHaveStyle({ minHeight: "44px" });
  });

  it("[AC-037] a log in still completes and opens the board", async () => {
    post.mockResolvedValue({
      data: {
        token: "t-" + crypto.randomUUID(),
        user: { id: "u1", email: "a@b.io", role: "user" },
      },
      response: { status: 200 },
    });
    renderAt("/log-in");
    fill("a@b.io", crypto.randomUUID());
    expect(await screen.findByTestId("ideas-board-title")).toBeInTheDocument();
  });
});
