import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "@/App";
import { getSessionToken, setSessionToken } from "@/lib/api";

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

describe("Board log out", () => {
  beforeEach(() => {
    post.mockReset();
    get.mockReset();
    window.localStorage.clear();
  });

  it("[AC-012] ends the session and shows the board as a visitor", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    get.mockResolvedValue({
      data: { id: "u1", email: "a@b.io", role: "user" },
      response: { status: 200 },
    });
    post.mockResolvedValue({ data: { detail: "ok" }, response: { status: 200 } });
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: "Log out" }));

    await waitFor(() => expect(post).toHaveBeenCalledWith("/auth/logout"));
    await waitFor(() => expect(screen.queryByRole("button", { name: "Log out" })).toBeNull());
    expect(getSessionToken()).toBeNull();
    expect(screen.getByTestId("ideas-board-title")).toBeInTheDocument();
    expect(screen.getByTestId("log-in-or-sign-up-to-vote-modal")).toBeInTheDocument();
    expect(screen.getByTestId("log-in-link")).toBeInTheDocument();
    expect(screen.getByTestId("sign-up-link")).toBeInTheDocument();
    expect(screen.queryByText(/Logged in as/)).toBeNull();
  });

  it("[AC-012] still ends the local session when the server cannot be reached", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    get.mockResolvedValue({
      data: { id: "u1", email: "a@b.io", role: "user" },
      response: { status: 200 },
    });
    post.mockRejectedValue(new Error("network"));
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: "Log out" }));

    await waitFor(() => expect(screen.queryByRole("button", { name: "Log out" })).toBeNull());
    expect(getSessionToken()).toBeNull();
  });

  it("[AC-013] after logging out, going back to post an idea prompts me to log in", async () => {
    get.mockResolvedValue({ error: { detail: "Sign in first" }, response: { status: 401 } });
    renderAt("/post-idea");

    expect(await screen.findByTestId("log-in-btn")).toBeInTheDocument();
    expect(screen.queryByTestId("ideas-board-title")).toBeNull();
  });

  it("[AC-013] a visitor who tries to vote is sent to log in", async () => {
    get.mockResolvedValue({ error: { detail: "Sign in first" }, response: { status: 401 } });
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: /Vote for Dark mode/ }));

    expect(await screen.findByTestId("log-in-btn")).toBeInTheDocument();
  });
});
