import { useState } from "react";
import {
  ArticleRounded,
  CalendarMonthRounded,
  FormatQuoteRounded,
  OpenInNewRounded,
  UnfoldMoreRounded,
  VerifiedRounded,
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

function formatAuthors(authors = []) {
  if (authors.length === 0) {
    return "Authors unavailable";
  }

  const names = authors
    .slice(0, 3)
    .map((author) => author.name);

  if (authors.length > 3) {
    names.push(`+${authors.length - 3} more`);
  }

  return names.join(", ");
}

function PaperCard({ paper, sourceId }) {
  const [expanded, setExpanded] = useState(false);
  const reduceMotion = useReducedMotion();

  const score = Math.max(
    0,
    Math.min(100, (paper.semantic_score ?? 0) * 100),
  );

  const paperUrl =
    paper.url ??
    (paper.doi
      ? `https://doi.org/${paper.doi}`
      : null);

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
        borderColor: "rgba(34, 211, 238, 0.18)",
        background:
          "linear-gradient(145deg, rgba(15,23,42,0.92), rgba(30,41,59,0.78))",
        transition:
          "border-color 180ms ease, box-shadow 180ms ease",
        "&:hover": {
          borderColor: "rgba(34, 211, 238, 0.42)",
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
            <ArticleRounded color="primary" />

            <Box>
              <Typography
                variant="caption"
                color="primary.main"
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
                {paper.title}
              </Typography>
            </Box>
          </Stack>

          {paperUrl && (
            <Tooltip title="Open original source">
              <Link
                href={paperUrl}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Open original paper"
                sx={{
                  display: "inline-flex",
                  p: 1,
                  flexShrink: 0,
                  borderRadius: 2,
                  color: "text.secondary",
                  "&:hover": {
                    color: "primary.main",
                    backgroundColor:
                      "rgba(34, 211, 238, 0.08)",
                  },
                }}
              >
                <OpenInNewRounded fontSize="small" />
              </Link>
            </Tooltip>
          )}
        </Stack>

        <Typography
          variant="body2"
          dir="auto"
          color="text.secondary"
          sx={{ lineHeight: 1.7 }}
        >
          {formatAuthors(paper.authors)}
        </Typography>

        <Stack
          direction="row"
          useFlexGap
          flexWrap="wrap"
          gap={1}
        >
          {paper.publication_year && (
            <Chip
              icon={<CalendarMonthRounded />}
              label={paper.publication_year}
              size="small"
            />
          )}

          {paper.venue && (
            <Chip
              label={paper.venue}
              size="small"
              variant="outlined"
            />
          )}

          {paper.is_open_access === true && (
            <Chip
              icon={<VerifiedRounded />}
              label="Open access"
              size="small"
              color="success"
              variant="outlined"
            />
          )}

          <Chip
            icon={<FormatQuoteRounded />}
            label={`${paper.citation_count ?? 0} citations`}
            size="small"
            variant="outlined"
          />
        </Stack>

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
              Semantic relevance
            </Typography>

            <Typography
              variant="caption"
              fontWeight={800}
              color="primary.main"
            >
              {score.toFixed(1)}%
            </Typography>
          </Stack>

          <LinearProgress
            variant="determinate"
            value={score}
            sx={{
              height: 6,
              borderRadius: 10,
              backgroundColor:
                "rgba(148, 163, 184, 0.12)",
              "& .MuiLinearProgress-bar": {
                borderRadius: 10,
                background:
                  "linear-gradient(90deg, #22d3ee, #6366f1)",
              },
            }}
          />
        </Box>

        {paper.providers?.length > 0 && (
          <Stack
            direction="row"
            useFlexGap
            flexWrap="wrap"
            gap={0.75}
          >
            {paper.providers.map((provider) => (
              <Chip
                key={provider}
                label={provider}
                size="small"
                sx={{ textTransform: "capitalize" }}
              />
            ))}
          </Stack>
        )}

        {paper.abstract && (
          <>
            <Button
              size="small"
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
              {expanded ? "Hide abstract" : "Show abstract"}
            </Button>

            <Collapse in={expanded}>
              <Typography
                variant="body2"
                dir="auto"
                sx={{
                  pt: 1,
                  lineHeight: 1.85,
                  color: "text.secondary",
                }}
              >
                {paper.abstract}
              </Typography>
            </Collapse>
          </>
        )}
      </Stack>
    </Paper>
  );
}

function PaperList({ papers = [] }) {
  if (papers.length === 0) {
    return null;
  }

  return (
    <Box component="section">
      <Typography variant="h5" fontWeight={800}>
        Scientific papers
      </Typography>

      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mt: 0.5, mb: 2.5 }}
      >
        Semantically ranked results from OpenAlex and
        Crossref.
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
        {papers.map((paper, index) => (
          <PaperCard
            key={`${paper.id}-${index}`}
            paper={paper}
            sourceId={`P${index + 1}`}
          />
        ))}
      </Box>
    </Box>
  );
}

export default PaperList;
