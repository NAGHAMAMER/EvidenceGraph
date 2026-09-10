import { useMemo, useState } from "react";
import {
  AutoAwesomeRounded,
  ErrorOutlineRounded,
  FactCheckRounded,
  LanguageRounded,
  PublicRounded,
  ScienceRounded,
  TranslateRounded,
  WarningAmberRounded,
} from "@mui/icons-material";
import {
  Alert,
  Box,
  Chip,
  Divider,
  Paper,
  Stack,
  Tab,
  Tabs,
  Typography,
} from "@mui/material";
import { motion } from "framer-motion";

import { getTextDirection } from "../utils/language";
import EvidenceList from "./EvidenceList";
import PaperList from "./PaperList";
import WebSourceList from "./WebSourceList";

function TabPanel({ activeTab, index, children }) {
  return (
    <Box
      role="tabpanel"
      hidden={activeTab !== index}
      sx={{ pt: 3 }}
    >
      {activeTab === index && children}
    </Box>
  );
}

function ResearchResults({ result }) {
  const [activeTab, setActiveTab] = useState(0);

  const direction = useMemo(
    () =>
      getTextDirection(
        result?.language_code,
        result?.answer,
      ),
    [result],
  );



  if (!result) {
    return null;
  }

  function handleSourceSelect(sourceId) {
    const targetTab = sourceId.startsWith("P") ? 2 : 3;

    setActiveTab(targetTab);

    window.setTimeout(() => {
      document
        .getElementById(`source-${sourceId}`)
        ?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
    }, 150);
  }

  return (
    <Box
      component={motion.section}
      initial={{ opacity: 0, y: 28 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55 }}
      sx={{ mt: 4 }}
    >
      <Paper
        elevation={0}
        sx={{
          borderRadius: 5,
          overflow: "hidden",
          border: "1px solid",
          borderColor: "rgba(148, 163, 184, 0.18)",
          backgroundColor: "rgba(15, 23, 42, 0.9)",
          boxShadow: "0 28px 80px rgba(2, 8, 23, 0.3)",
        }}
      >
        <Box sx={{ p: { xs: 2.5, md: 4 } }}>
          <Stack
            direction={{
              xs: "column",
              md: "row",
            }}
            justifyContent="space-between"
            gap={2}
          >
            <Box>
              <Stack
                direction="row"
                alignItems="center"
                spacing={1}
              >
                <AutoAwesomeRounded color="primary" />

                <Typography variant="h4" fontWeight={850}>
                  Research result
                </Typography>
              </Stack>

              <Typography
                variant="body2"
                dir="auto"
                color="text.secondary"
                sx={{ mt: 1 }}
              >
                {result.question}
              </Typography>
            </Box>

            <Stack
              direction="row"
              useFlexGap
              flexWrap="wrap"
              gap={1}
            >
              <Chip
                icon={<LanguageRounded />}
                label={result.detected_language}
                color="primary"
                variant="outlined"
              />

              <Chip
                icon={<ScienceRounded />}
                label={`${result.papers.length} papers`}
                variant="outlined"
              />

              <Chip
                icon={<PublicRounded />}
                label={`${result.web_sources.length} web sources`}
                variant="outlined"
              />
            </Stack>
          </Stack>
        </Box>

        <Divider />

        <Tabs
          value={activeTab}
          onChange={(_, newValue) =>
            setActiveTab(newValue)
          }
          variant="scrollable"
          scrollButtons="auto"
          aria-label="Research result sections"
          sx={{
            px: { xs: 1, md: 2 },
            "& .MuiTab-root": {
              minHeight: 64,
              textTransform: "none",
              fontWeight: 700,
            },
          }}
        >
          <Tab
            icon={<AutoAwesomeRounded />}
            iconPosition="start"
            label="Answer"
          />

          <Tab
            icon={<FactCheckRounded />}
            iconPosition="start"
            label={`Evidence (${result.evidence.length})`}
          />

          <Tab
            icon={<ScienceRounded />}
            iconPosition="start"
            label={`Papers (${result.papers.length})`}
          />

          <Tab
            icon={<PublicRounded />}
            iconPosition="start"
            label={`Web (${result.web_sources.length})`}
          />
        </Tabs>

        <Divider />

        <Box sx={{ p: { xs: 2.5, md: 4 } }}>
          <TabPanel activeTab={activeTab} index={0}>
            <Stack spacing={3}>
              <Box>
                <Typography
                  variant="overline"
                  color="primary.main"
                  fontWeight={800}
                >
                  Synthesized answer
                </Typography>

                <Typography
                  variant="body1"
                  dir={direction}
                  sx={{
                    mt: 1,
                    whiteSpace: "pre-line",
                    textAlign:
                      direction === "rtl"
                        ? "right"
                        : "left",
                    lineHeight: 2,
                    fontSize: "1.05rem",
                  }}
                >
                  {result.answer}
                </Typography>
              </Box>

              <Paper
                elevation={0}
                sx={{
                  p: 2.5,
                  borderRadius: 3,
                  border: "1px solid",
                  borderColor:
                    "rgba(99, 102, 241, 0.22)",
                  backgroundColor:
                    "rgba(99, 102, 241, 0.07)",
                }}
              >
                <Stack
                  direction="row"
                  spacing={1}
                  alignItems="flex-start"
                >
                  <TranslateRounded
                    color="secondary"
                    sx={{ mt: 0.25 }}
                  />

                  <Box>
                    <Typography
                      variant="body2"
                      fontWeight={750}
                    >
                      Optimized English research query
                    </Typography>

                    <Typography
                      variant="body2"
                      sx={{
                        mt: 0.75,
                        color: "text.secondary",
                        lineHeight: 1.7,
                      }}
                    >
                      {result.english_query}
                    </Typography>
                  </Box>
                </Stack>
              </Paper>

              {result.limitations?.length > 0 && (
                <Box>
                  <Stack
                    direction="row"
                    spacing={1}
                    alignItems="center"
                    sx={{ mb: 1.5 }}
                  >
                    <WarningAmberRounded color="warning" />

                    <Typography
                      variant="h6"
                      fontWeight={750}
                    >
                      Limitations
                    </Typography>
                  </Stack>

                  <Stack spacing={1}>
                    {result.limitations.map(
                      (limitation, index) => (
                        <Alert
                          key={`${limitation}-${index}`}
                          severity="warning"
                          variant="outlined"
                          sx={{
                            "& .MuiAlert-message": {
                              width: "100%",
                            },
                          }}
                        >
                          <Typography dir="auto">
                            {limitation}
                          </Typography>
                        </Alert>
                      ),
                    )}
                  </Stack>
                </Box>
              )}

              {result.errors?.length > 0 && (
                <Box>
                  <Stack
                    direction="row"
                    spacing={1}
                    alignItems="center"
                    sx={{ mb: 1.5 }}
                  >
                    <ErrorOutlineRounded color="error" />

                    <Typography
                      variant="h6"
                      fontWeight={750}
                    >
                      Partial service errors
                    </Typography>
                  </Stack>

                  <Stack spacing={1}>
                    {result.errors.map((error, index) => (
                      <Alert
                        key={`${error}-${index}`}
                        severity="error"
                        variant="outlined"
                      >
                        {error}
                      </Alert>
                    ))}
                  </Stack>
                </Box>
              )}
            </Stack>
          </TabPanel>

          <TabPanel activeTab={activeTab} index={1}>
            <EvidenceList
              evidence={result.evidence}
              direction={direction}
              onSourceSelect={handleSourceSelect}
            />
          </TabPanel>

          <TabPanel activeTab={activeTab} index={2}>
            <PaperList papers={result.papers} />
          </TabPanel>

          <TabPanel activeTab={activeTab} index={3}>
            <WebSourceList sources={result.web_sources} />
          </TabPanel>
        </Box>
      </Paper>
    </Box>
  );
}

export default ResearchResults;
