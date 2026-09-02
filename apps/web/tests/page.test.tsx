import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Home from "@/app/page";

describe("ReviewFlow application shell", () => {
  it("presents an accessible and honest planning-stage page", () => {
    render(<Home />);

    const main = screen.getByRole("main");
    expect(main).toHaveAttribute("id", "main-content");
    expect(main).toHaveAttribute("tabindex", "-1");

    expect(
      within(main).getByRole("heading", {
        level: 1,
        name: "Clear decisions start with a clear review trail.",
      }),
    ).toBeVisible();
    expect(screen.getByRole("link", { name: "Skip to main content" })).toHaveAttribute(
      "href",
      "#main-content",
    );
    expect(screen.getByText("This release is foundation-only.")).toBeVisible();
    expect(
      screen.getByText("Product workflows are not available yet.", { exact: false }),
    ).toBeVisible();
    expect(screen.getByRole("heading", { level: 2, name: "What exists today" })).toBeVisible();

    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(screen.queryByRole("navigation")).not.toBeInTheDocument();
  });
});
