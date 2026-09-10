import {
  AutoAwesomeRounded,
  LanguageRounded,
  PublicRounded,
  ScienceRounded,
} from "@mui/icons-material";
import {
  Box,
  LinearProgress,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import {
  AnimatePresence,
  motion,
} from "framer-motion";

const RESEARCH_STAGES = [
  {
    label: "Understanding the question",
    description: "Detecting language and optimizing the query",
    icon: LanguageRounded,
  },
  {
    label: "Searching scientific papers",
    description: "Retrieving evidence from OpenAlex and Crossref",
    icon: ScienceRounded,
  },
  {
    label: "Searching the web",
    description: "Finding relevant web evidence with Tavily",
    icon: PublicRounded,
  },
  {
    label: "Synthesizing the answer",
    description: "Connecting evidence and generating the response",
    icon: AutoAwesomeRounded,
  },
];

function ResearchProgress({ isVisible }) {
  return (
    <AnimatePresence>
      {isVisible && (
        <Paper
          component={motion.section}
          initial={{ opacity: 0, y: 20, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -10, scale: 0.98 }}
          transition={{ duration: 0.35 }}
          elevation={0}
          aria-live="polite"
          sx={{
            p: { xs: 2.5, md: 3.5 },
            mt: 3,
            borderRadius: 4,
            border: "1px solid",
            borderColor: "rgba(34, 211, 238, 0.2)",
            background:
              "linear-gradient(145deg, rgba(15,23,42,0.97), rgba(30,41,59,0.92))",
            overflow: "hidden",
          }}
        >
          <Stack spacing={2.5}>
            <Box>
              <Typography variant="h6" fontWeight={750}>
                EvidenceGraph is researching
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
              >
                Scientific and web sources are being
                analyzed. This may take a moment.
              </Typography>
            </Box>

            <LinearProgress
              sx={{
                height: 7,
                borderRadius: 10,
                backgroundColor:
                  "rgba(148, 163, 184, 0.14)",
                "& .MuiLinearProgress-bar": {
                  borderRadius: 10,
                  background:
                    "linear-gradient(90deg, #22d3ee, #8b5cf6)",
                },
              }}
            />

            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: {
                  xs: "1fr",
                  sm: "repeat(2, 1fr)",
                  lg: "repeat(4, 1fr)",
                },
                gap: 1.5,
              }}
            >
              {RESEARCH_STAGES.map(
                (stage, index) => {
                  const Icon = stage.icon;

                  return (
                    <Box
                      component={motion.div}
                      key={stage.label}
                      animate={{
                        opacity: [0.5, 1, 0.5],
                        y: [0, -3, 0],
                      }}
                      transition={{
                        duration: 2.4,
                        repeat: Infinity,
                        delay: index * 0.45,
                        ease: "easeInOut",
                      }}
                      sx={{
                        p: 2,
                        borderRadius: 3,
                        border: "1px solid",
                        borderColor:
                          "rgba(148, 163, 184, 0.14)",
                        backgroundColor:
                          "rgba(15, 23, 42, 0.55)",
                      }}
                    >
                      <Icon
                        sx={{
                          mb: 1,
                          color:
                            index % 2 === 0
                              ? "primary.main"
                              : "secondary.main",
                        }}
                      />

                      <Typography
                        variant="body2"
                        fontWeight={700}
                      >
                        {stage.label}
                      </Typography>

                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{
                          display: "block",
                          mt: 0.5,
                          lineHeight: 1.55,
                        }}
                      >
                        {stage.description}
                      </Typography>
                    </Box>
                  );
                },
              )}
            </Box>
          </Stack>
        </Paper>
      )}
    </AnimatePresence>
  );
}

export default ResearchProgress;
