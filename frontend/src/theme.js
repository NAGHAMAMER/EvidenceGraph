import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",

    primary: {
      main: "#22d3ee",
      light: "#67e8f9",
      dark: "#0891b2",
      contrastText: "#020617",
    },

    secondary: {
      main: "#8b5cf6",
      light: "#a78bfa",
      dark: "#6d28d9",
      contrastText: "#ffffff",
    },

    success: {
      main: "#22c55e",
    },

    warning: {
      main: "#f59e0b",
    },

    error: {
      main: "#f43f5e",
    },

    background: {
      default: "#020617",
      paper: "#0f172a",
    },

    text: {
      primary: "#f8fafc",
      secondary: "#94a3b8",
    },

    divider: "rgba(148, 163, 184, 0.16)",
  },

  shape: {
    borderRadius: 16,
  },

  typography: {
    fontFamily: [
      "Inter",
      "Segoe UI",
      "Tahoma",
      "Arial",
      "sans-serif",
    ].join(","),

    fontSize: 16,

    h1: {
      fontWeight: 850,
      letterSpacing: "-0.04em",
    },

    h2: {
      fontWeight: 820,
      letterSpacing: "-0.035em",
    },

    h3: {
      fontWeight: 800,
      letterSpacing: "-0.025em",
    },

    h4: {
      fontWeight: 800,
      letterSpacing: "-0.02em",
    },

    h5: {
      fontWeight: 750,
    },

    h6: {
      fontWeight: 720,
    },

    button: {
      fontWeight: 700,
    },
  },

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        html: {
          scrollBehavior: "smooth",
        },

        body: {
          minWidth: 320,
          minHeight: "100vh",
          margin: 0,
          backgroundColor: "#020617",
          backgroundImage: `
            radial-gradient(
              circle at 15% 10%,
              rgba(34, 211, 238, 0.11),
              transparent 28%
            ),
            radial-gradient(
              circle at 85% 5%,
              rgba(139, 92, 246, 0.12),
              transparent 30%
            ),
            linear-gradient(
              180deg,
              #020617 0%,
              #071426 48%,
              #020617 100%
            )
          `,
          backgroundAttachment: "fixed",
        },

        "::selection": {
          color: "#020617",
          backgroundColor: "#67e8f9",
        },

        "*": {
          boxSizing: "border-box",
        },

        "a, button, input, textarea": {
          font: "inherit",
        },
      },
    },

    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          minHeight: 44,
        },
      },
    },

    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 14,
          backgroundColor: "rgba(2, 8, 23, 0.48)",

          "& .MuiOutlinedInput-notchedOutline": {
            borderColor: "rgba(148, 163, 184, 0.24)",
          },

          "&:hover .MuiOutlinedInput-notchedOutline": {
            borderColor: "rgba(34, 211, 238, 0.5)",
          },

          "&.Mui-focused .MuiOutlinedInput-notchedOutline": {
            borderWidth: 1,
          },
        },
      },
    },

    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          backgroundColor: "rgba(148, 163, 184, 0.08)",
        },
      },
    },

    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          fontSize: "0.8rem",
          borderRadius: 8,
          backgroundColor: "#1e293b",
        },
      },
    },

    MuiTabs: {
      styleOverrides: {
        indicator: {
          height: 3,
          borderRadius: "3px 3px 0 0",
          background:
            "linear-gradient(90deg, #22d3ee, #8b5cf6)",
        },
      },
    },

    MuiTab: {
      styleOverrides: {
        root: {
          color: "#94a3b8",

          "&.Mui-selected": {
            color: "#f8fafc",
          },
        },
      },
    },
  },
});

export default theme;
