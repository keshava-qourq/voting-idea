import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import SignUp from "./SignUp";

const post = vi.hoisted(() => vi.fn());
vi.mock("@/api/client", () => ({ api: { POST: post } }));

function renderScreen() {
  return render(
    <MemoryRouter initialEntries={["/sign-up"]}>
      <Routes>
        <Route path="/sign-up" element={<SignUp />} />
        <Route path="/board" element={<p>board page</p>} />
        <Route path="/log-in" element={<p>log in page</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

function fill(email: string, password: string) {
  fireEvent.change(screen.getByTestId("email-input"), { target: { value: email } });
  fireEvent.change(screen.getByTestId("password-input"), { target: { value: password } });
  fireEvent.click(screen.getByTestId("sign-up-btn"));
}

describe("SignUp", () => {
  beforeEach(() => {
    post.mockReset();
    window.localStorage.clear();
  });

  it("[AC-001] creates the account, keeps the token and opens the board", async () => {
    const pwd = crypto.randomUUID();
    post.mockResolvedValue({
      data: { token: "t-" + crypto.randomUUID(), user_id: "u1", email: "a@b.io" },
      response: { status: 201 },
    });
    renderScreen();
    fill("a@b.io", pwd);
    expect(await screen.findByText("board page")).toBeInTheDocument();
    expect(post).toHaveBeenCalledWith("/auth/signup", { body: { email: "a@b.io", password: pwd } });
    expect(window.localStorage.getItem("session_token")).toMatch(/^t-/);
  });

  it("[AC-002] shows the already-registered message on a 409", async () => {
    post.mockResolvedValue({
      error: { code: "EMAIL_ALREADY_REGISTERED", message: "x", field: "email" },
      response: { status: 409 },
    });
    renderScreen();
    fill("Taken@Example.com", crypto.randomUUID());
    expect(await screen.findByText("This email is already registered")).toBeInTheDocument();
    expect(screen.queryByText("board page")).not.toBeInTheDocument();
  });

  it("[AC-003] shows the email message for an invalid email and sends nothing", () => {
    renderScreen();
    fill("not-an-email", crypto.randomUUID());
    expect(screen.getByText("Enter a valid email address")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("[AC-003] shows the password message for an empty password and sends nothing", () => {
    renderScreen();
    fill("a@b.io", "");
    expect(screen.getByText("Password is required")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("[AC-003] shows the password message when the server names the password field", async () => {
    post.mockResolvedValue({
      error: { code: "PASSWORD_REQUIRED", message: "x", field: "password" },
      response: { status: 422 },
    });
    renderScreen();
    fill("a@b.io", " ");
    expect(await screen.findByText("Password is required")).toBeInTheDocument();
  });

  it("[AC-004] accepts an email at any domain", async () => {
    post.mockResolvedValue({
      data: { token: "t", user_id: "u2", email: "x@random-domain.xyz" },
      response: { status: 201 },
    });
    renderScreen();
    fill("x@random-domain.xyz", crypto.randomUUID());
    expect(await screen.findByText("board page")).toBeInTheDocument();
  });

  it("[AC-005] shows no verification step and goes straight to the app", async () => {
    post.mockResolvedValue({
      data: { token: "t", user_id: "u3", email: "a@b.io" },
      response: { status: 201 },
    });
    renderScreen();
    expect(screen.getByTestId("create-your-account-title")).toBeInTheDocument();
    expect(screen.getByTestId("sign-up-form")).toBeInTheDocument();
    fill("a@b.io", crypto.randomUUID());
    await waitFor(() => expect(screen.getByText("board page")).toBeInTheDocument());
  });

  it("[AC-001] shows an error and stays on the form when the server is down", async () => {
    post.mockResolvedValue({ error: { detail: "down" }, response: { status: 503 } });
    renderScreen();
    fill("a@b.io", crypto.randomUUID());
    expect(await screen.findByText("Something went wrong. Try again.")).toBeInTheDocument();
    expect(screen.getByTestId("sign-up-btn")).not.toBeDisabled();
  });

  it("[AC-001] the log-in link opens the log-in screen", () => {
    renderScreen();
    fireEvent.click(screen.getByTestId("already-have-an-account-log-in-link"));
    expect(screen.getByText("log in page")).toBeInTheDocument();
  });
});
