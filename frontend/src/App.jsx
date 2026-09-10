import {
  lazy,
  Suspense,
  useRef,
  useState,
} from "react";
import {
  GitHub,
  HubRounded,
  ScienceRounded,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Chip,
  Container,
  IconButton,
  Link,
  Stack,
  Typography,
} from "@mui/material";
import { motion } from "framer-motion";

import HeroVisual from "./components/HeroVisual";
import ResearchForm from "./components/ResearchForm";
import ResearchProgress from "./components/ResearchProgress";
import { runResearch } from "./services/researchApi";

const ResearchResults = lazy(
  () => import("./components/ResearchResults"),
);

function App() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const resultsRef = useRef(null);

  async function handleResearch(request) {
    setError("");
    setResult(null);
    setIsLoading(true);

    try {
      const researchResult = await runResearch(request);

      setResult(researchResult);

      window.setTimeout(() => {
        resultsRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 180);
    } catch (requestError) {
      setError(
        requestError.message ||
          "The research request could not be completed.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Box sx={{ minHeight: "100vh" }}>
      <Box
        component="header"
        sx={{
          position: "sticky",
          top: 0,
          zIndex: 20,
          borderBottom: "1px solid",
          borderColor: "divider",
          backgroundColor: "rgba(2, 6, 23, 0.78)",
          backdropFilter: "blur(18px)",
        }}
      >
        <Container maxWidth="xl">
          <Stack
            direction="row"
            sx={{
              minHeight: 72,
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <Stack
              direction="row"
              spacing={1.25}
              sx={{
                alignItems: "center",
              }}
            >
              <Box
                sx={{
                  display: "grid",
                  placeItems: "center",
                  width: 42,
                  height: 42,
                  borderRadius: 3,
                  color: "#020617",
                  background:
                    "linear-gradient(135deg, #22d3ee, #8b5cf6)",
                  boxShadow:
                    "0 8px 24px rgba(34, 211, 238, 0.24)",
                }}
              >
                <HubRounded />
              </Box>

              <Box>
                <Typography
                  variant="h6"
                  fontWeight={850}
                  lineHeight={1.1}
                >
                  EvidenceGraph
                </Typography>

                <Typography
                  variant="caption"
                  color="text.secondary"
                >
                  Multilingual research agent
                </Typography>
              </Box>
            </Stack>

            <Stack
              direction="row"
              spacing={1}
              sx={{
                alignItems: "center",
              }}
            >
              <Chip
                icon={<ScienceRounded />}
                label="Research workspace"
                size="small"
                variant="outlined"
                sx={{
                  display: {
                    xs: "none",
                    sm: "inline-flex",
                  },
                }}
              />

              <IconButton
                component={Link}
                href="https://github.com/NAGHAMAMER/EvidenceGraph"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Open EvidenceGraph on GitHub"
                color="inherit"
              >
                <GitHub />
              </IconButton>
            </Stack>
          </Stack>
        </Container>
      </Box>

      <Container
        component="main"
        maxWidth="xl"
        sx={{
          py: {
            xs: 4,
            md: 7,
          },
        }}
      >
        <Box
          component={motion.div}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
          sx={{
            maxWidth: 820,
            mb: {
              xs: 3,
              md: 4,
            },
          }}
        >
          <Chip
            label="Scientific research, connected"
            color="primary"
            variant="outlined"
            sx={{ mb: 2 }}
          />

          <Typography
            variant="h2"
            component="h1"
            sx={{
              fontSize: {
                xs: "2.25rem",
                sm: "3rem",
                md: "4rem",
              },
              lineHeight: 1.08,
              background:
                "linear-gradient(135deg, #f8fafc 20%, #67e8f9 55%, #a78bfa 95%)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              color: "transparent",
            }}
          >
            Ask a question.
            <br />
            Follow the evidence.
          </Typography>

          <Typography
            variant="body1"
            color="text.secondary"
            sx={{
              mt: 2,
              maxWidth: 720,
              lineHeight: 1.8,
            }}
          >
            Search scientific papers and the web, rank
            evidence semantically, and receive a sourced
            answer in the language of your question.
          </Typography>
        </Box>

        <HeroVisual />

        <Box
          sx={{
            maxWidth: 1000,
            mx: "auto",
            mt: {
              xs: 3,
              md: 4,
            },
          }}
        >
          <ResearchForm
            onSubmit={handleResearch}
            isLoading={isLoading}
          />

          <ResearchProgress isVisible={isLoading} />

          {error && (
            <Alert
              severity="error"
              variant="outlined"
              onClose={() => setError("")}
              sx={{
                mt: 3,
                borderRadius: 3,
                backgroundColor:
                  "rgba(244, 63, 94, 0.06)",
              }}
            >
              <Typography fontWeight={700}>
                Research request failed
              </Typography>

              <Typography
                variant="body2"
                sx={{ mt: 0.5 }}
              >
                {error}
              </Typography>
            </Alert>
          )}
        </Box>

        <Box ref={resultsRef}>
          {result && (
            <Suspense
              fallback={
                <Typography
                  color="text.secondary"
                  textAlign="center"
                  sx={{ py: 4 }}
                >
                  Preparing research results...
                </Typography>
              }
            >
              <ResearchResults result={result} />
            </Suspense>
          )}
        </Box>
      </Container>

      <Box
        component="footer"
        sx={{
          py: 3,
          borderTop: "1px solid",
          borderColor: "divider",
        }}
      >
        <Container maxWidth="xl">
          <Typography
            variant="body2"
            color="text.secondary"
            textAlign="center"
          >
            EvidenceGraph combines OpenAlex, Crossref,
            Tavily, semantic search, and agentic research.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
