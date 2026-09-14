import {
  AutoAwesomeRounded,
  ExpandMoreRounded,
  ManageSearchRounded,
  MemoryRounded,
  OpenInNewRounded,
  PersonRounded,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { motion } from "framer-motion";

import { getTextDirection } from "../utils/language";

function ResearchConversation({
  session,
  selectedTurnId,
  isLoadingPrevious,
  onLoadPrevious,
  onSelectTurn,
}) {
  const turns = session?.turns ?? [];

  if (!session || turns.length === 0) {
    return null;
  }

  return (
    <Stack
      spacing={2.5}
      sx={{
        mt: 4,
        mb: 3,
      }}
    >
      <Stack
        direction={{
          xs: "column",
          sm: "row",
        }}
        spacing={1.5}
        sx={{
          alignItems: {
            xs: "stretch",
            sm: "center",
          },
          justifyContent: "space-between",
        }}
      >
        <Box>
          <Typography
            variant="h5"
            fontWeight={800}
          >
            Research conversation
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
          >
            {session.total_turns ?? turns.length}{" "}
            conversation{" "}
            {(session.total_turns ?? turns.length) === 1
              ? "turn"
              : "turns"}
          </Typography>
        </Box>

        {session.has_more_turns && (
          <Button
            variant="outlined"
            disabled={isLoadingPrevious}
            startIcon={
              isLoadingPrevious
                ? (
                    <CircularProgress
                      size={18}
                      color="inherit"
                    />
                  )
                : <ExpandMoreRounded />
            }
            onClick={onLoadPrevious}
            sx={{
              alignSelf: {
                xs: "stretch",
                sm: "center",
              },
              borderRadius: 3,
              textTransform: "none",
              fontWeight: 700,
            }}
          >
            {isLoadingPrevious
              ? "Loading previous messages..."
              : "Load previous messages"}
          </Button>
        )}
      </Stack>

      {turns.map((turn) => {
        const questionDirection = getTextDirection(
          turn.language_code,
          turn.question,
        );

        const answerDirection = getTextDirection(
          turn.language_code,
          turn.answer,
        );

        const isSelected =
          turn.turn_id === selectedTurnId;

        return (
          <Box
            component={motion.article}
            key={turn.turn_id}
            initial={{
              opacity: 0,
              y: 16,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              duration: 0.35,
            }}
          >
            <Stack spacing={1.5}>
              <Stack
                direction="row"
                spacing={1.25}
                sx={{
                  alignItems: "flex-start",
                  justifyContent: "flex-end",
                }}
              >
                <Paper
                  elevation={0}
                  sx={{
                    width: "fit-content",
                    maxWidth: {
                      xs: "92%",
                      md: "78%",
                    },
                    px: {
                      xs: 2,
                      md: 2.5,
                    },
                    py: 1.75,
                    borderRadius:
                      "22px 22px 6px 22px",
                    border: "1px solid",
                    borderColor:
                      "rgba(99, 102, 241, 0.34)",
                    background:
                      "linear-gradient(135deg, rgba(79,70,229,0.24), rgba(37,99,235,0.14))",
                  }}
                >
                  <Typography
                    variant="body1"
                    dir={questionDirection}
                    sx={{
                      textAlign:
                        questionDirection === "rtl"
                          ? "right"
                          : "left",
                      whiteSpace: "pre-wrap",
                      lineHeight: 1.75,
                    }}
                  >
                    {turn.question}
                  </Typography>
                </Paper>

                <Box
                  sx={{
                    display: "grid",
                    placeItems: "center",
                    flexShrink: 0,
                    width: 38,
                    height: 38,
                    borderRadius: "50%",
                    color: "#e0e7ff",
                    backgroundColor:
                      "rgba(99, 102, 241, 0.2)",
                    border:
                      "1px solid rgba(129, 140, 248, 0.3)",
                  }}
                >
                  <PersonRounded fontSize="small" />
                </Box>
              </Stack>

              <Stack
                direction="row"
                spacing={1.25}
                sx={{
                  alignItems: "flex-start",
                }}
              >
                <Box
                  sx={{
                    display: "grid",
                    placeItems: "center",
                    flexShrink: 0,
                    width: 38,
                    height: 38,
                    borderRadius: "50%",
                    color: "#020617",
                    background:
                      "linear-gradient(135deg, #22d3ee, #8b5cf6)",
                    boxShadow:
                      "0 8px 22px rgba(34, 211, 238, 0.2)",
                  }}
                >
                  <AutoAwesomeRounded fontSize="small" />
                </Box>

                <Paper
                  elevation={0}
                  sx={{
                    flex: 1,
                    minWidth: 0,
                    p: {
                      xs: 2,
                      md: 2.75,
                    },
                    borderRadius:
                      "22px 22px 22px 6px",
                    border: "1px solid",
                    borderColor: isSelected
                      ? "rgba(34, 211, 238, 0.5)"
                      : "rgba(148, 163, 184, 0.18)",
                    backgroundColor:
                      "rgba(15, 23, 42, 0.78)",
                    boxShadow: isSelected
                      ? "0 14px 40px rgba(34, 211, 238, 0.08)"
                      : "none",
                  }}
                >
                  <Stack spacing={1.75}>
                    <Typography
                      variant="body1"
                      dir={answerDirection}
                      sx={{
                        textAlign:
                          answerDirection === "rtl"
                            ? "right"
                            : "left",
                        whiteSpace: "pre-wrap",
                        lineHeight: 1.9,
                      }}
                    >
                      {turn.answer}
                    </Typography>

                    <Stack
                      direction="row"
                      useFlexGap
                      sx={{
                        flexWrap: "wrap",
                        gap: 1,
                        alignItems: "center",
                      }}
                    >
                      <Chip
                        size="small"
                        icon={
                          turn.performed_search
                            ? <ManageSearchRounded />
                            : <MemoryRounded />
                        }
                        label={
                          turn.performed_search
                            ? "New sources searched"
                            : "Answered from saved context"
                        }
                        color={
                          turn.performed_search
                            ? "primary"
                            : "secondary"
                        }
                        variant="outlined"
                      />

                      <Chip
                        size="small"
                        label={
                          `Turn ${turn.turn_index}`
                        }
                        variant="outlined"
                      />

                      <Chip
                        size="small"
                        label={
                          `${turn.papers?.length ?? 0} papers`
                        }
                        variant="outlined"
                      />

                      <Chip
                        size="small"
                        label={
                          `${turn.web_sources?.length ?? 0} web sources`
                        }
                        variant="outlined"
                      />

                      <Button
                        size="small"
                        variant={
                          isSelected
                            ? "contained"
                            : "text"
                        }
                        endIcon={<OpenInNewRounded />}
                        onClick={() =>
                          onSelectTurn(turn)
                        }
                        sx={{
                          ml: {
                            xs: 0,
                            sm: "auto",
                          },
                          textTransform: "none",
                          fontWeight: 700,
                          borderRadius: 2.5,
                        }}
                      >
                        {isSelected
                          ? "Evidence shown below"
                          : "View evidence"}
                      </Button>
                    </Stack>
                  </Stack>
                </Paper>
              </Stack>
            </Stack>
          </Box>
        );
      })}
    </Stack>
  );
}

export default ResearchConversation;
