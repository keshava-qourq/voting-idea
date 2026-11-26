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
    mockGet([idea("Dark mode", 3)]);
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: /Vote for Dark mode/ }));

    expect(await screen.findByTestId("log-in-btn")).toBeInTheDocument();
  });
});

function idea(title: string, voteCount: number, voted = false) {
  return {
    id: "id-" + title,
    title,
    description: "About " + title,
    voteCount,
    createdAt: "2026-11-02T09:00:00Z",
    voted,
  };
}

// GET /ideas answers with the given ideas; every other GET is a visitor's 401.
function mockGet(ideas: ReturnType<typeof idea>[] | "fail") {
  get.mockImplementation((path: string) => {
    if (path === "/ideas") {
      return ideas === "fail"
        ? Promise.reject(new Error("network"))
        : Promise.resolve({ data: ideas, response: { status: 200 } });
    }
    return Promise.resolve({ error: { detail: "Sign in first" }, response: { status: 401 } });
  });
}

describe("Board ranked list", () => {
  beforeEach(() => {
    get.mockReset();
    window.localStorage.clear();
  });

  it("[AC-014] lists the ideas in the order the API returns them, without logging in", async () => {
    mockGet([idea("Alpha", 9), idea("Beta", 4), idea("Gamma", 0)]);
    renderAt("/board");

    const list = await screen.findByTestId("ideas-ranked-by-votes-list");
    const titles = Array.from(list.querySelectorAll("h3")).map((h) => h.textContent);
    expect(titles).toEqual(["Alpha", "Beta", "Gamma"]);
    expect(get).toHaveBeenCalledWith("/ideas");
    expect(screen.queryByTestId("no-ideas-yet-post-the-first-idea-empty")).toBeNull();
  });

  it("[AC-017] keeps tied ideas in the API order, newest first, and does not re-sort them", async () => {
    const newest = { ...idea("Zulu", 3), createdAt: "2026-11-03T09:00:00Z" };
    const middle = { ...idea("Mike", 3), createdAt: "2026-11-02T09:00:00Z" };
    const oldest = { ...idea("Alpha", 3), createdAt: "2026-11-01T09:00:00Z" };
    mockGet([idea("Top", 8), newest, middle, oldest, idea("Low", 1)]);
    renderAt("/board");

    const list = await screen.findByTestId("ideas-ranked-by-votes-list");
    const titles = Array.from(list.querySelectorAll("h3")).map((h) => h.textContent);
    expect(titles).toEqual(["Top", "Zulu", "Mike", "Alpha", "Low"]);
  });

  it("[AC-018] lists the newer idea above the older one after it gains a vote and the board is reloaded", async () => {
    const older = { ...idea("Older", 2), createdAt: "2026-11-01T09:00:00Z" };
    const newer = { ...idea("Newer", 2), createdAt: "2026-11-02T09:00:00Z" };
    mockGet([newer, older]);
    const first = renderAt("/board");
    let list = await screen.findByTestId("ideas-ranked-by-votes-list");
    expect(Array.from(list.querySelectorAll("h3")).map((h) => h.textContent)).toEqual([
      "Newer",
      "Older",
    ]);
    first.unmount();

    mockGet([{ ...newer, voteCount: 3 }, older]);
    renderAt("/board");
    list = await screen.findByTestId("ideas-ranked-by-votes-list");
    expect(Array.from(list.querySelectorAll("h3")).map((h) => h.textContent)).toEqual([
      "Newer",
      "Older",
    ]);
    expect(list.querySelectorAll("li")[0].textContent).toContain("3 votes");
  });

  it("[AC-015] shows each idea with its current vote count", async () => {
    mockGet([idea("Alpha", 5), idea("Beta", 1)]);
    renderAt("/board");

    const list = await screen.findByTestId("ideas-ranked-by-votes-list");
    const items = list.querySelectorAll("li");
    expect(items[0].textContent).toContain("5 votes");
    expect(items[1].textContent).toContain("1 vote");
  });

  it("[AC-015] marks an idea I have voted for", async () => {
    mockGet([idea("Alpha", 5, true), idea("Beta", 1)]);
    renderAt("/board");

    expect(await screen.findByText("You have voted")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Vote for Alpha/ })).toBeNull();
    expect(screen.getByRole("button", { name: /Vote for Beta/ })).toBeInTheDocument();
  });

  it("[AC-016] shows the empty-state message when no ideas exist", async () => {
    mockGet([]);
    renderAt("/board");

    const empty = await screen.findByTestId("no-ideas-yet-post-the-first-idea-empty");
    expect(empty).toHaveTextContent("No ideas yet. Post the first idea!");
    expect(screen.queryByTestId("ideas-ranked-by-votes-list")).toBeNull();
  });

  it("[AC-016] shows no empty-state message while the ideas load or when they fail", async () => {
    mockGet("fail");
    renderAt("/board");

    expect(screen.queryByTestId("no-ideas-yet-post-the-first-idea-empty")).toBeNull();
    expect(await screen.findByRole("alert")).toHaveTextContent("Could not load the ideas.");
    expect(screen.queryByTestId("no-ideas-yet-post-the-first-idea-empty")).toBeNull();
  });
});
