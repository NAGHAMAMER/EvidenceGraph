import {
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import {
  createTheme,
  ThemeProvider,
} from "@mui/material/styles";
import {
  describe,
  expect,
  test,
  vi,
} from "vitest";

import ResearchForm from "./ResearchForm";

const testTheme = createTheme({
  components: {
    MuiButtonBase: {
      defaultProps: {
        disableRipple: true,
      },
    },
  },
});

function renderResearchForm({
  onSubmit = vi.fn(),
  isLoading = false,
} = {}) {
  return render(
    <ThemeProvider theme={testTheme}>
      <ResearchForm
        onSubmit={onSubmit}
        isLoading={isLoading}
      />
    </ThemeProvider>,
  );
}

describe("ResearchForm", () => {
  test("submits a trimmed question with the default limit", () => {
    const handleSubmit = vi.fn();

    renderResearchForm({
      onSubmit: handleSubmit,
    });

    const questionInput =
      screen.getByLabelText("Research question");

    fireEvent.change(questionInput, {
      target: {
        value: "  What is semantic search?  ",
      },
    });

    const submitButton = screen.getByRole("button", {
      name: "Start research",
    });

    fireEvent.submit(submitButton.closest("form"));

    expect(handleSubmit).toHaveBeenCalledTimes(1);

    expect(handleSubmit).toHaveBeenCalledWith({
      question: "What is semantic search?",
      limit: 5,
    });
  });

  test("fills the question from an Arabic example", () => {
    renderResearchForm();

    fireEvent.click(
      screen.getByRole("button", {
        name: "العربية",
      }),
    );

    const questionInput =
      screen.getByLabelText("Research question");

    expect(questionInput.value).toContain(
      "الذكاء الاصطناعي",
    );

    expect(questionInput).toHaveAttribute(
      "dir",
      "rtl",
    );
  });

  test("disables submission while research is running", () => {
    renderResearchForm({
      isLoading: true,
    });

    expect(
      screen.getByRole("button", {
        name: "Researching...",
      }),
    ).toBeDisabled();

    expect(
      screen.getByLabelText("Research question"),
    ).toBeDisabled();
  });
});
