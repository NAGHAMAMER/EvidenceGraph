import { useMemo, useState } from "react";
import {
  ErrorOutlineRounded,
  FactCheckRounded,
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

import EvidenceGraph from "./EvidenceGraph";
import EvidenceList from "./EvidenceList";
import PaperList from "./PaperList";
import WebSourceList from "./WebSourceList";
import { getTextDirection } from "../utils/language";

function TabPanel({
  activeTab,
  index,
  children,
}) {
  return (
    <Box
      role="tabpanel"
      hidden={activeTab !== index}
      sx={{ pt: 2.5 }}
    >
      {activeTab === index && children}
    </Box>
  );
}

function ResearchResults({ result }) {
  const [
    tabSelection,
    setTabSelection,
  ] = useState({
    turnId: result?.turn_id,
    value: 0,
  });

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

  const activeTab =
    tabSelection.turnId === result.turn_id
      ? tabSelection.value
      : 0;

  function selectTab(value) {
    setTabSelection({
      turnId: result.turn_id,
      value,
    });
  }

  function handleSourceSelect(sourceId) {
    const targetTab =
      sourceId.startsWith("P") ? 1 : 2;

    selectTab(targetTab);

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
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.4,
      }}
      sx={{ mt: 3 }}
    >
      <Paper
        elevation={0}
        sx={{
          borderRadius: 4,
          overflow: "hidden",
          border: "1px solid",
          borderColor:
            "rgba(148, 163, 184, 0.18)",
          backgroundColor:
            "rgba(15, 23, 42, 0.88)",
        }}
      >
        <Box
          sx={{
            p: {
              xs: 2,
              md: 2.75,
            },
          }}
        >
          <Stack
            direction={{
              xs: "column",
              md: "row",
            }}
            sx={{
              gap: 1.5,
              alignItems: {
                xs: "flex-start",
                md: "center",
              },
              justifyContent: "space-between",
            }}
          >
            <Box>
              <Stack
                direction="row"
                spacing={1}
                sx={{ alignItems: "center" }}
              >
                <FactCheckRounded color="primary" />

                <Typography
                  variant="h5"
                  fontWeight={820}
                >
                  Evidence details
                </Typography>
              </Stack>

              <Typography
                variant="body2"
                dir="auto"
                color="text.secondary"
                sx={{
                  mt: 0.75,
                  lineHeight: 1.6,
                }}
              >
                Evidence and sources for turn{" "}
                {result.turn_index}.
              </Typography>
            </Box>

            <Stack
              direction="row"
              useFlexGap
              sx={{
                flexWrap: "wrap",
                gap: 0.75,
              }}
            >
              <Chip
                label={
                  `${result.evidence.length} claims`
                }
                size="small"
                color="primary"
                variant="outlined"
              />

              <Chip
                label={
                  `${result.papers.length} papers`
                }
                size="small"
                variant="outlined"
              />

              <Chip
                label={
                  `${result.web_sources.length} web`
                }
                size="small"
                variant="outlined"
              />
            </Stack>
          </Stack>
        </Box>

        <Divider />

        <Tabs
          value={activeTab}
          onChange={(_, newValue) =>
            selectTab(newValue)
          }
          variant="scrollable"
          scrollButtons="auto"
          aria-label="Research evidence sections"
          sx={{
            px: {
              xs: 0.5,
              md: 1.5,
            },
            "& .MuiTab-root": {
              minHeight: 54,
              textTransform: "none",
              fontWeight: 700,
            },
          }}
        >
          <Tab
            icon={<FactCheckRounded />}
            iconPosition="start"
            label={
              `Evidence (${result.evidence.length})`
            }
          />

          <Tab
            icon={<ScienceRounded />}
            iconPosition="start"
            label={
              `Papers (${result.papers.length})`
            }
          />

          <Tab
            icon={<PublicRounded />}
            iconPosition="start"
            label={
              `Web (${result.web_sources.length})`
            }
          />

          <Tab
            icon={<TranslateRounded />}
            iconPosition="start"
            label="Details"
          />
        </Tabs>

        <Divider />

        <Box
          sx={{
            p: {
              xs: 2,
              md: 2.75,
            },
          }}
        >
          <TabPanel
            activeTab={activeTab}
            index={0}
          >
            {result.evidence.length > 0 ? (
              <>
                <EvidenceGraph
                  key={result.turn_id}
                  result={result}
                  onSourceSelect={
                    handleSourceSelect
                  }
                />

                <EvidenceList
                  evidence={result.evidence}
                  direction={direction}
                  onSourceSelect={
                    handleSourceSelect
                  }
                />
              </>
            ) : (
              <Alert
                severity="info"
                variant="outlined"
              >
                No structured evidence claims were
                generated for this turn.
              </Alert>
            )}
          </TabPanel>

          <TabPanel
            activeTab={activeTab}
            index={1}
          >
            {result.papers.length > 0 ? (
              <PaperList papers={result.papers} />
            ) : (
              <Alert
                severity="info"
                variant="outlined"
              >
                No scientific papers were returned for
                this turn.
              </Alert>
            )}
          </TabPanel>

          <TabPanel
            activeTab={activeTab}
            index={2}
          >
            {result.web_sources.length > 0 ? (
              <WebSourceList
                sources={result.web_sources}
              />
            ) : (
              <Alert
                severity="info"
                variant="outlined"
              >
                No web sources were returned for this
                turn.
              </Alert>
            )}
          </TabPanel>

          <TabPanel
            activeTab={activeTab}
            index={3}
          >
            <Stack spacing={2.5}>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
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
                  sx={{
                    alignItems: "flex-start",
                  }}
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
                    sx={{
                      alignItems: "center",
                      mb: 1.25,
                    }}
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
                    sx={{
                      alignItems: "center",
                      mb: 1.25,
                    }}
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
                    {result.errors.map(
                      (error, index) => (
                        <Alert
                          key={`${error}-${index}`}
                          severity="error"
                          variant="outlined"
                        >
                          {error}
                        </Alert>
                      ),
                    )}
                  </Stack>
                </Box>
              )}

              {(
                result.limitations?.length === 0 &&
                result.errors?.length === 0
              ) && (
                <Alert
                  severity="success"
                  variant="outlined"
                >
                  No additional limitations or partial
                  service errors were reported.
                </Alert>
              )}
            </Stack>
          </TabPanel>
        </Box>
      </Paper>
    </Box>
  );
}

export default ResearchResults;
