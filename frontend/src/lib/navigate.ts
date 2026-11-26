import { useNavigate as useRouterNavigate } from "react-router-dom";

/**
 * `navigate(route)` in the preview posted a message to the host. Here it is
 * real routing, so the route slug the screen was written against has to
 * become the router path the scaffold mounted it at. This mirrors
 * `route_to_url_path` on the Python side; the two must agree or a link goes
 * nowhere.
 */
export function toPath(route: string): string {
  const trimmed = route.trim().replace(/^\/+|\/+$/g, "");
  if (!trimmed) return "/";
  return (
    "/" +
    trimmed
      .split("/")
      .map((segment) =>
        segment.startsWith(":")
          ? segment
          : segment
              .toLowerCase()
              .replace(/[^a-z0-9]+/g, "-")
              .replace(/^-|-$/g, ""),
      )
      .join("/")
  );
}

/** `state` rides along with the navigation, e.g. `{ from: "post-idea" }` to come back after login. */
export function useNavigate(): (route: string, state?: unknown) => void {
  const navigate = useRouterNavigate();
  return (route: string, state?: unknown) =>
    navigate(toPath(route), state === undefined ? undefined : { state });
}
