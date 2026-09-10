import { useState } from "react";
import {
  LanguageRounded,
  OpenInNewRounded,
  UnfoldMoreRounded,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Chip,
  Collapse,
  LinearProgress,
  Link,
  Paper,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import {
  motion,
  useReducedMotion,
} from "framer-motion";

function getDomain(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "Web source";
  }
}

function WebSourceCard({ source, sourceId }) {
  const [expanded, setExpanded] = useState(false);
  const reduceMotion = useReducedMotion();

  const hasScore = typeof source.score === "number";

  const relevance = hasScore
    ? Math.max(0, Math.min(100, source.score * 100))
    : null;

  return (
    <Paper
      id={`source-${sourceId}`}
      component={motion.article}
      initial={reduceMotion ? false : { opacity: 0, y: 18 }}
      whileInView={
        reduceMotion ? undefined : { opacity: 1, y: 0 }
      }
      viewport={{ once: true, amount: 0.15 }}
      whileHover={
        reduceMotion
          ? undefined
          : {
              y: -4,
              transition: { duration: 0.18 },
            }
      }
      elevation={0}
      sx={{
        p: { xs: 2, md: 2.5 },
        scrollMarginTop: 24,
        borderRadius: 4,
        border: "1px solid",
        borderColor: "rgba(139, 92, 246, 0.2)",
        background:
          "linear-gradient(145deg, rgba(15,23,42,0.92), rgba(46,32,78,0.46))",
        transition:
          "border-color 180ms ease, box-shadow 180ms ease",
        "&:hover": {
          borderColor: "rgba(139, 92, 246, 0.5)",
          boxShadow: "0 18px 42px rgba(2, 8, 23, 0.28)",
        },
      }}
    >
      <Stack spacing={2}>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="flex-start"
          gap={2}
        >
          <Stack direction="row" spacing={1.25}>
            <LanguageRounded color="secondary" />

            <Box>
              <Typography
                variant="caption"
                color="secondary.main"
                fontWeight={800}
              >
                {sourceId}
              </Typography>

              <Typography
                variant="h6"
                component="h3"
                dir="auto"
                sx={{
                  mt: 0.25,
                  lineHeight: 1.45,
                  fontWeight: 750,
                }}
              >
                {source.title}
              </Typography>
            </Box>
          </Stack>

          <Tooltip title="Open original source">
            <Link
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Open original web source"
              sx={{
                display: "inline-flex",
                p: 1,
                flexShrink: 0,
                borderRadius: 2,
                color: "text.secondary",
                "&:hover": {
                  color: "secondary.main",
                  backgroundColor:
                    "rgba(139, 92, 246, 0.1)",
                },
              }}
            >
              <OpenInNewRounded fontSize="small" />
            </Link>
          </Tooltip>
        </Stack>

        <Stack
          direction="row"
          useFlexGap
          flexWrap="wrap"
          gap={1}
        >
          <Chip
            label={getDomain(source.url)}
            size="small"
            variant="outlined"
          />

          <Chip
            label="Web"
            size="small"
            color="secondary"
            variant="outlined"
          />
        </Stack>

        {relevance !== null && (
          <Box>
            <Stack
              direction="row"
              justifyContent="space-between"
              sx={{ mb: 0.75 }}
            >
              <Typography
                variant="caption"
                color="text.secondary"
              >
                Search relevance
              </Typography>

              <Typography
                variant="caption"
                fontWeight={800}
                color="secondary.main"
              >
                {relevance.toFixed(1)}%
              </Typography>
            </Stack>

            <LinearProgress
              variant="determinate"
              value={relevance}
              color="secondary"
              sx={{
                height: 6,
                borderRadius: 10,
                backgroundColor:
                  "rgba(148, 163, 184, 0.12)",
                "& .MuiLinearProgress-bar": {
                  borderRadius: 10,
                  background:
                    "linear-gradient(90deg, #8b5cf6, #ec4899)",
                },
              }}
            />
          </Box>
        )}

        {source.content && (
          <>
            <Button
              size="small"
              color="secondary"
              endIcon={
                <UnfoldMoreRounded
                  sx={{
                    transform: expanded
                      ? "rotate(180deg)"
                      : "rotate(0)",
                    transition: "transform 180ms ease",
                  }}
                />
              }
              onClick={() => setExpanded((value) => !value)}
              sx={{
                alignSelf: "flex-start",
                textTransform: "none",
              }}
            >
              {expanded
                ? "Hide source content"
                : "Show source content"}
            </Button>

            <Collapse in={expanded}>
              <Typography
                variant="body2"
                dir="auto"
                sx={{
                  pt: 1,
                  lineHeight: 1.85,
                  color: "text.secondary",
                  whiteSpace: "pre-line",
                }}
              >
                {source.content}
              </Typography>
            </Collapse>
          </>
        )}
      </Stack>
    </Paper>
  );
}

function WebSourceList({ sources = [] }) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <Box component="section">
      <Typography variant="h5" fontWeight={800}>
        Web sources
      </Typography>

      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mt: 0.5, mb: 2.5 }}
      >
        Additional evidence retrieved from the web using
        Tavily.
      </Typography>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            xl: "repeat(2, minmax(0, 1fr))",
          },
          gap: 2,
        }}
      >
        {sources.map((source, index) => (
          <WebSourceCard
            key={`${source.url}-${index}`}
            source={source}
            sourceId={`W${index + 1}`}
          />
        ))}
      </Box>
    </Box>
  );
}

export default WebSourceList;
