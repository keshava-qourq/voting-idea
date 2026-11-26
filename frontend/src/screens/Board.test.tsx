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

  it("[AC-033] a visitor who tries to vote is prompted to log in and can go to the log in screen", async () => {
    mockGet([idea("Dark mode", 3)]);
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: /Vote for Dark mode/ }));
    fireEvent.click(await screen.findByTestId("log-in-link"));

    expect(await screen.findByTestId("log-in-btn")).toBeInTheDocument();
  });

  it("[AC-033] a visitor can go to the sign up screen from the prompt", async () => {
    mockGet([idea("Dark mode", 3)]);
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: /Vote for Dark mode/ }));
    fireEvent.click(await screen.findByTestId("sign-up-link"));

    expect(screen.queryByTestId("ideas-board-title")).toBeNull();
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
    if (path === "/auth/me" && getSessionToken()) {
      return Promise.resolve({
        data: { id: "u1", email: "a@b.io", role: "user" },
        response: { status: 200 },
      });
    }
    return Promise.resolve({ error: { detail: "Sign in first" }, response: { status: 401 } });
  });
}

describe("Board upvote", () => {
  beforeEach(() => {
    get.mockReset();
    post.mockReset();
    window.localStorage.clear();
  });

  function loginAndVote(voteCount: number) {
    post.mockResolvedValue({
      data: { ideaId: "id-Beta", voteCount, voted: true },
      response: { status: 200 },
    });
  }

  it("[AC-027] adds exactly one vote, shows 'You have voted' and re-ranks the board", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet([idea("Alpha", 3), idea("Beta", 3)]);
    loginAndVote(4);
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: "Vote for Beta" }));

    expect(await screen.findByText("You have voted")).toBeInTheDocument();
    expect(post).toHaveBeenCalledWith("/ideas/{idea_id}/vote", {
      params: { path: { idea_id: "id-Beta" } },
    });
    const list = screen.getByTestId("ideas-ranked-by-votes-list");
    expect(Array.from(list.querySelectorAll("h3")).map((h) => h.textContent)).toEqual([
      "Beta",
      "Alpha",
    ]);
    expect(list.querySelectorAll("li")[0].textContent).toContain("4 votes");
    expect(list.querySelectorAll("li")[1].textContent).toContain("3 votes");
  });

  it("[AC-027] hides the log in or sign up modal from a logged-in user", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet([idea("Alpha", 3)]);
    renderAt("/board");

    await screen.findByTestId("ideas-ranked-by-votes-list");
    expect(screen.queryByTestId("log-in-or-sign-up-to-vote-modal")).toBeNull();
  });

  it("[AC-034] a visitor sees vote counts and vote controls before any prompt", async () => {
    mockGet([idea("Alpha", 3)]);
    renderAt("/board");

    const list = await screen.findByTestId("ideas-ranked-by-votes-list");
    expect(list).toHaveTextContent("3 votes");
    expect(screen.getByRole("button", { name: /Vote for Alpha/ })).toBeEnabled();
    expect(screen.queryByTestId("log-in-or-sign-up-to-vote-modal")).toBeNull();
  });

  it("[AC-033] a visitor's vote attempt shows the prompt, sends no vote and keeps the count", async () => {
    mockGet([idea("Alpha", 3)]);
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: /Vote for Alpha/ }));

    expect(await screen.findByTestId("log-in-or-sign-up-to-vote-modal")).toHaveTextContent(
      "Log in or sign up to vote",
    );
    expect(screen.getByTestId("log-in-link")).toBeInTheDocument();
    expect(screen.getByTestId("sign-up-link")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
    expect(screen.getByTestId("ideas-ranked-by-votes-list")).toHaveTextContent("3 votes");
    expect(screen.queryByText("You have voted")).toBeNull();
  });

  it("[AC-028] accepts a vote on an idea I posted myself and counts it", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet([idea("Beta", 0)]);
    loginAndVote(1);
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: "Vote for Beta" }));

    expect(await screen.findByText("You have voted")).toBeInTheDocument();
    expect(screen.getByTestId("ideas-ranked-by-votes-list").textContent).toContain("1 vote");
  });

  it("[AC-029] offers no way to remove the vote or downvote once I have voted", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet([idea("Beta", 2)]);
    loginAndVote(3);
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: "Vote for Beta" }));
    await screen.findByText("You have voted");

    const item = screen.getByTestId("ideas-ranked-by-votes-list").querySelector("li")!;
    expect(item.querySelector("button")).toBeNull();
    expect(screen.queryByRole("button", { name: /vote|remove|undo|down/i })).toBeNull();
  });

  it("[AC-027] shows an error and keeps the count when the vote fails", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet([idea("Beta", 2)]);
    post.mockRejectedValue(new Error("network"));
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: "Vote for Beta" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Could not record your vote.");
    expect(screen.queryByText("You have voted")).toBeNull();
    expect(screen.getByTestId("ideas-ranked-by-votes-list").textContent).toContain("2 votes");
  });

  it("[AC-027] an expired session shows the log in or sign up modal again", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet([idea("Beta", 2)]);
    post.mockResolvedValue({ error: { detail: "Sign in first" }, response: { status: 401 } });
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: "Vote for Beta" }));

    expect(await screen.findByTestId("log-in-or-sign-up-to-vote-modal")).toBeInTheDocument();
    expect(getSessionToken()).toBeNull();
  });
});

describe("Board one vote per idea", () => {
  beforeEach(() => {
    get.mockReset();
    post.mockReset();
    window.localStorage.clear();
  });

  it("[AC-030] shows that I have voted and replaces the vote control on that idea", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet([idea("Alpha", 5, true), idea("Beta", 1)]);
    renderAt("/board");

    const list = await screen.findByTestId("ideas-ranked-by-votes-list");
    const items = list.querySelectorAll("li");
    expect(items[0]).toHaveTextContent("You have voted");
    expect(items[0].querySelector("button")).toBeNull();
    expect(items[1]).not.toHaveTextContent("You have voted");
    expect(items[1].querySelector("button")).not.toBeNull();
  });

  it("[AC-031] sends one request when the vote control is double-clicked", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet([idea("Beta", 2)]);
    let resolve: (value: unknown) => void = () => {};
    post.mockReturnValue(new Promise((r) => (resolve = r)));
    renderAt("/board");

    const button = await screen.findByRole("button", { name: "Vote for Beta" });
    fireEvent.click(button);
    fireEvent.click(button);
    expect(post).toHaveBeenCalledTimes(1);
    expect(button).toBeDisabled();

    resolve({ data: { ideaId: "id-Beta", voteCount: 3, voted: true }, response: { status: 200 } });
    expect(await screen.findByText("You have voted")).toBeInTheDocument();
    expect(post).toHaveBeenCalledTimes(1);
    expect(screen.getByTestId("ideas-ranked-by-votes-list").textContent).toContain("3 votes");
  });

  it("[AC-031] keeps the count when the server answers a repeat vote with the same count", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet([idea("Beta", 2)]);
    post.mockResolvedValue({
      data: { ideaId: "id-Beta", voteCount: 2, voted: true },
      response: { status: 200 },
    });
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: "Vote for Beta" }));

    expect(await screen.findByText("You have voted")).toBeInTheDocument();
    expect(screen.getByTestId("ideas-ranked-by-votes-list").textContent).toContain("2 votes");
  });

  it("[AC-032] accepts a vote on a different idea after voting on one", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet([idea("Alpha", 5, true), idea("Beta", 1)]);
    post.mockResolvedValue({
      data: { ideaId: "id-Beta", voteCount: 2, voted: true },
      response: { status: 200 },
    });
    renderAt("/board");

    fireEvent.click(await screen.findByRole("button", { name: "Vote for Beta" }));

    await waitFor(() => expect(screen.getAllByText("You have voted")).toHaveLength(2));
    expect(post).toHaveBeenCalledWith("/ideas/{idea_id}/vote", {
      params: { path: { idea_id: "id-Beta" } },
    });
    expect(screen.queryByRole("button", { name: /Vote for/ })).toBeNull();
  });
});

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

  it("[AC-019] shows the title, short description and vote count of every idea, zero included", async () => {
    mockGet([idea("Alpha", 5), idea("Beta", 0)]);
    renderAt("/board");

    const list = await screen.findByTestId("ideas-ranked-by-votes-list");
    const items = list.querySelectorAll("li");
    expect(items).toHaveLength(2);
    expect(items[0]).toHaveTextContent("Alpha");
    expect(items[0]).toHaveTextContent("About Alpha");
    expect(items[0]).toHaveTextContent("5 votes");
    expect(items[1]).toHaveTextContent("Beta");
    expect(items[1]).toHaveTextContent("About Beta");
    expect(items[1]).toHaveTextContent("0 votes");
  });

  it("[AC-020] shows no edit, delete, comment or category control on any idea", async () => {
    mockGet([idea("Alpha", 5, true), idea("Beta", 0)]);
    renderAt("/board");

    const list = await screen.findByTestId("ideas-ranked-by-votes-list");
    const forbidden = /edit|delete|remove|comment|categor/i;
    for (const item of Array.from(list.querySelectorAll("li"))) {
      expect(item.querySelector("input, textarea, select, a")).toBeNull();
      for (const control of Array.from(item.querySelectorAll("button"))) {
        expect(control.getAttribute("aria-label") ?? control.textContent).not.toMatch(forbidden);
      }
    }
    expect(screen.queryByRole("button", { name: forbidden })).toBeNull();
    expect(screen.queryByRole("textbox")).toBeNull();
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

describe("Board personal data", () => {
  beforeEach(() => {
    get.mockReset();
    post.mockReset();
    window.localStorage.clear();
  });

  // Even if the server sent an author email by mistake, the board must not display it.
  function ideasWithAuthorEmail() {
    return [
      { ...idea("Alpha", 2), authorEmail: "alice@example.com", email: "alice@example.com" },
      { ...idea("Beta", 1), authorEmail: "bob@example.org", email: "bob@example.org" },
    ];
  }

  it("[AC-042] shows no email address to a visitor", async () => {
    mockGet(ideasWithAuthorEmail());
    renderAt("/board");

    await screen.findByText("Alpha");
    expect(screen.getByText("Beta")).toBeInTheDocument();
    const list = screen.getByTestId("ideas-ranked-by-votes-list");
    expect(list.textContent).not.toMatch(/@/);
    expect(document.body.textContent).not.toContain("alice@example.com");
    expect(document.body.textContent).not.toContain("bob@example.org");
  });

  it("[AC-042] shows no other user's email address to a signed-in user", async () => {
    setSessionToken("t-" + crypto.randomUUID());
    mockGet(ideasWithAuthorEmail());
    renderAt("/board");

    await screen.findByText("Alpha");
    const list = screen.getByTestId("ideas-ranked-by-votes-list");
    expect(list.textContent).not.toMatch(/@/);
    expect(document.body.textContent).not.toContain("alice@example.com");
    expect(document.body.textContent).not.toContain("bob@example.org");
  });
});
