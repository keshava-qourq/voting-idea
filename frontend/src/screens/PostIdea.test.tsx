import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import PostIdea from "@/screens/PostIdea";

const post = vi.hoisted(() => vi.fn());
const get = vi.hoisted(() => vi.fn());
vi.mock("@/api/client", () => ({ api: { POST: post, GET: get } }));

function renderScreen() {
  return render(
    <MemoryRouter initialEntries={["/post-idea"]}>
      <PostIdea />
    </MemoryRouter>,
  );
}

function loggedIn() {
  get.mockResolvedValue({
    data: { id: "u1", email: "a@b.io", role: "user" },
    response: { status: 200 },
  });
}

function submit(title: string, description: string) {
  fireEvent.change(screen.getByTestId("title-max-80-characters-input"), {
    target: { value: title },
  });
  fireEvent.change(screen.getByTestId("short-description-max-280-characte-input"), {
    target: { value: description },
  });
  fireEvent.click(screen.getByTestId("submit-idea-btn"));
}

describe("Post an Idea", () => {
  beforeEach(() => {
    post.mockReset();
    get.mockReset();
    loggedIn();
  });

  it("[AC-021] posts the title and description and confirms zero votes", async () => {
    post.mockResolvedValue({
      data: { id: "i1", title: "T", description: "D", voteCount: 0 },
      response: { status: 201 },
    });
    renderScreen();
    expect(screen.getByTestId("post-an-idea-title")).toBeInTheDocument();
    expect(screen.getByTestId("new-idea-form")).toBeInTheDocument();
    await waitFor(() => expect(get).toHaveBeenCalled());
    submit("Free coffee", "Coffee on Fridays");
    expect(await screen.findByText(/Idea posted with zero votes/)).toBeInTheDocument();
    expect(post).toHaveBeenCalledWith("/ideas", {
      body: { title: "Free coffee", description: "Coffee on Fridays" },
    });
  });

  it("[AC-022] shows which field is missing and saves nothing", async () => {
    renderScreen();
    await waitFor(() => expect(get).toHaveBeenCalled());
    submit("", "");
    expect(await screen.findByText("Title is required")).toBeInTheDocument();
    expect(screen.getByText("Description is required")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("[AC-022] flags only the empty description", async () => {
    renderScreen();
    await waitFor(() => expect(get).toHaveBeenCalled());
    submit("A title", "   ");
    expect(await screen.findByText("Description is required")).toBeInTheDocument();
    expect(screen.queryByText("Title is required")).not.toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("[AC-023] shows the limit messages and saves nothing", async () => {
    renderScreen();
    await waitFor(() => expect(get).toHaveBeenCalled());
    submit("t".repeat(81), "d".repeat(281));
    expect(await screen.findByText("Title must be 80 characters or fewer")).toBeInTheDocument();
    expect(screen.getByText("Description must be 280 characters or fewer")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it("[AC-021] shows an error and keeps the form when the server fails", async () => {
    post.mockRejectedValue(new Error("down"));
    renderScreen();
    await waitFor(() => expect(get).toHaveBeenCalled());
    submit("A title", "A description");
    expect(await screen.findByText("Something went wrong. Try again.")).toBeInTheDocument();
    expect(screen.getByTestId("submit-idea-btn")).not.toBeDisabled();
  });

  it("[AC-024] offers no edit or delete control", async () => {
    renderScreen();
    await waitFor(() => expect(get).toHaveBeenCalled());
    expect(screen.queryByText(/edit/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/delete/i)).not.toBeInTheDocument();
  });

  it("[AC-021] asks a visitor to log in or sign up and posts nothing", async () => {
    get.mockResolvedValue({ error: { detail: "Sign in first" }, response: { status: 401 } });
    renderScreen();
    expect(await screen.findByText("Log in or sign up to post an idea")).toBeInTheDocument();
    expect(screen.getByTestId("log-in-btn")).toBeInTheDocument();
    expect(screen.getByTestId("sign-up-btn")).toBeInTheDocument();
    submit("A title", "A description");
    expect(post).not.toHaveBeenCalled();
  });

  it("[AC-021] asks me to log in when the server refuses the post", async () => {
    post.mockResolvedValue({ error: { message: "x" }, response: { status: 401 } });
    renderScreen();
    await waitFor(() => expect(get).toHaveBeenCalled());
    submit("A title", "A description");
    expect(await screen.findByText("Log in or sign up to post an idea")).toBeInTheDocument();
  });
});
