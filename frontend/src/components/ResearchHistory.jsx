import {
  AddRounded,
  ChatBubbleOutlineRounded,
  CloseRounded,
  DeleteOutlineRounded,
  HistoryRounded,
  HubRounded,
} from "@mui/icons-material";
import {
  Box,
  Button,
  CircularProgress,
  Divider,
  Drawer,
  IconButton,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import { motion } from "framer-motion";

const SIDEBAR_WIDTH = 300;

function formatDate(value) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function SidebarContent({
  sessions,
  selectedResearchId,
  isLoading,
  deletingResearchId,
  showCloseButton,
  onSelect,
  onDelete,
  onNewResearch,
  onClose,
}) {
  function handleSelect(researchId) {
    onSelect(researchId);
    onClose();
  }

  function handleNewResearch() {
    onNewResearch();
    onClose();
  }

  return (
    <Stack
      sx={{
        width: "100%",
        height: "100%",
        overflow: "hidden",
      }}
    >
      <Stack
        direction="row"
        spacing={1.25}
        sx={{
          px: 2,
          minHeight: 72,
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Stack
          direction="row"
          spacing={1.25}
          sx={{ alignItems: "center" }}
        >
          <Box
            sx={{
              display: "grid",
              placeItems: "center",
              width: 40,
              height: 40,
              flexShrink: 0,
              borderRadius: 2.5,
              color: "#020617",
              background:
                "linear-gradient(135deg, #22d3ee, #8b5cf6)",
              boxShadow:
                "0 8px 24px rgba(34, 211, 238, 0.2)",
            }}
          >
            <HubRounded />
          </Box>

          <Box>
            <Typography
              variant="subtitle1"
              fontWeight={850}
              lineHeight={1.1}
            >
              EvidenceGraph
            </Typography>

            <Typography
              variant="caption"
              color="text.secondary"
            >
              Research workspace
            </Typography>
          </Box>
        </Stack>

        {showCloseButton && (
          <IconButton
            onClick={onClose}
            aria-label="Close research history"
          >
            <CloseRounded />
          </IconButton>
        )}
      </Stack>

      <Divider />

      <Box sx={{ p: 1.5 }}>
        <Button
          fullWidth
          variant="outlined"
          startIcon={<AddRounded />}
          onClick={handleNewResearch}
          sx={{
            minHeight: 48,
            justifyContent: "flex-start",
            px: 2,
            textTransform: "none",
            borderColor:
              "rgba(34, 211, 238, 0.35)",
            backgroundColor:
              "rgba(34, 211, 238, 0.05)",
          }}
        >
          New research
        </Button>
      </Box>

      <Stack
        direction="row"
        spacing={1}
        sx={{
          px: 2,
          py: 1,
          alignItems: "center",
        }}
      >
        <HistoryRounded
          color="primary"
          sx={{ fontSize: 19 }}
        />

        <Typography
          variant="overline"
          color="text.secondary"
          fontWeight={800}
        >
          Research history
        </Typography>
      </Stack>

      <Box
        sx={{
          flex: 1,
          overflowY: "auto",
          px: 1.25,
          pb: 2,
        }}
      >
        {isLoading && (
          <Stack
            direction="row"
            spacing={1.5}
            sx={{
              alignItems: "center",
              justifyContent: "center",
              py: 4,
            }}
          >
            <CircularProgress size={21} />

            <Typography
              variant="body2"
              color="text.secondary"
            >
              Loading...
            </Typography>
          </Stack>
        )}

        {!isLoading && sessions.length === 0 && (
          <Box
            sx={{
              p: 2,
              mt: 1,
              borderRadius: 3,
              border: "1px dashed",
              borderColor: "divider",
            }}
          >
            <Typography
              variant="body2"
              color="text.secondary"
              textAlign="center"
            >
              Saved research sessions will appear here.
            </Typography>
          </Box>
        )}

        {!isLoading && sessions.length > 0 && (
          <Stack spacing={0.75}>
            {sessions.map((session) => {
              const isSelected =
                session.research_id ===
                selectedResearchId;

              const isDeleting =
                deletingResearchId ===
                session.research_id;

              return (
                <Box
                  key={session.research_id}
                  component={motion.div}
                  layout
                  role="button"
                  tabIndex={0}
                  onClick={() =>
                    handleSelect(
                      session.research_id,
                    )
                  }
                  onKeyDown={(event) => {
                    if (
                      event.key === "Enter" ||
                      event.key === " "
                    ) {
                      event.preventDefault();

                      handleSelect(
                        session.research_id,
                      );
                    }
                  }}
                  sx={{
                    p: 1.4,
                    cursor: "pointer",
                    borderRadius: 2.5,
                    border: "1px solid",
                    borderColor: isSelected
                      ? "rgba(34, 211, 238, 0.45)"
                      : "transparent",
                    backgroundColor: isSelected
                      ? "rgba(34, 211, 238, 0.1)"
                      : "transparent",
                    transition:
                      "background 180ms ease, border-color 180ms ease",
                    "&:hover": {
                      backgroundColor:
                        "rgba(148, 163, 184, 0.08)",
                    },
                  }}
                >
                  <Stack
                    direction="row"
                    spacing={1}
                    sx={{
                      alignItems: "flex-start",
                      justifyContent:
                        "space-between",
                    }}
                  >
                    <Box sx={{ minWidth: 0 }}>
                      <Typography
                        variant="body2"
                        fontWeight={
                          isSelected ? 750 : 600
                        }
                        dir="auto"
                        sx={{
                          display: "-webkit-box",
                          overflow: "hidden",
                          WebkitBoxOrient: "vertical",
                          WebkitLineClamp: 2,
                          lineHeight: 1.5,
                        }}
                      >
                        {session.initial_question}
                      </Typography>

                      <Stack
                        direction="row"
                        spacing={0.65}
                        sx={{
                          mt: 0.8,
                          alignItems: "center",
                          color: "text.secondary",
                        }}
                      >
                        <ChatBubbleOutlineRounded
                          sx={{ fontSize: 15 }}
                        />

                        <Typography variant="caption">
                          {session.turn_count}{" "}
                          {session.turn_count === 1
                            ? "turn"
                            : "turns"}
                        </Typography>
                      </Stack>

                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{
                          display: "block",
                          mt: 0.35,
                          fontSize: "0.68rem",
                        }}
                      >
                        {formatDate(
                          session.updated_at,
                        )}
                      </Typography>
                    </Box>

                    <Tooltip title="Delete session">
                      <span>
                        <IconButton
                          size="small"
                          color="error"
                          disabled={isDeleting}
                          aria-label={
                            "Delete research session"
                          }
                          onClick={(event) => {
                            event.stopPropagation();

                            onDelete(
                              session.research_id,
                            );
                          }}
                        >
                          {isDeleting ? (
                            <CircularProgress
                              size={17}
                              color="inherit"
                            />
                          ) : (
                            <DeleteOutlineRounded
                              sx={{ fontSize: 18 }}
                            />
                          )}
                        </IconButton>
                      </span>
                    </Tooltip>
                  </Stack>
                </Box>
              );
            })}
          </Stack>
        )}
      </Box>
    </Stack>
  );
}

function ResearchHistory({
  sessions = [],
  selectedResearchId,
  isLoading,
  deletingResearchId,
  mobileOpen,
  onMobileClose,
  onSelect,
  onDelete,
  onNewResearch,
}) {
  const sharedProps = {
    sessions,
    selectedResearchId,
    isLoading,
    deletingResearchId,
    onSelect,
    onDelete,
    onNewResearch,
    onClose: onMobileClose,
  };

  return (
    <>
      <Box
        component="aside"
        sx={{
          display: {
            xs: "none",
            lg: "flex",
          },
          position: "fixed",
          inset: "0 auto 0 0",
          zIndex: 30,
          width: SIDEBAR_WIDTH,
          borderRight: "1px solid",
          borderColor: "divider",
          backgroundColor:
            "rgba(8, 15, 30, 0.98)",
          backdropFilter: "blur(20px)",
        }}
      >
        <SidebarContent
          {...sharedProps}
          showCloseButton={false}
        />
      </Box>

      <Drawer
        anchor="left"
        open={mobileOpen}
        onClose={onMobileClose}
        slotProps={{
          paper: {
            sx: {
              width: SIDEBAR_WIDTH,
              maxWidth: "88vw",
              borderRight: "1px solid",
              borderColor: "divider",
              backgroundColor: "#08101f",
              backgroundImage: "none",
            },
          },
        }}
      >
        <SidebarContent
          {...sharedProps}
          showCloseButton
        />
      </Drawer>
    </>
  );
}

export default ResearchHistory;
