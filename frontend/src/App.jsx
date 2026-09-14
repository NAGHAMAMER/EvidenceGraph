import {
  lazy,
  Suspense,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  GitHub,
  HubRounded,
  MenuRounded,
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

import FollowUpForm from "./components/FollowUpForm";
import ResearchConversation from "./components/ResearchConversation";
import ResearchForm from "./components/ResearchForm";
import ResearchHistory from "./components/ResearchHistory";
import ResearchProgress from "./components/ResearchProgress";
import {
  deleteResearchSession,
  getResearchHistory,
  getResearchSession,
  runResearch,
  runResearchFollowUp,
} from "./services/researchApi";

const ResearchResults = lazy(
  () => import("./components/ResearchResults"),
);

const SIDEBAR_WIDTH = 300;
const PREVIOUS_TURNS_BATCH_SIZE = 3;

function resultToStoredTurn(result) {
  return {
    turn_id: result.turn_id,
    turn_index: result.turn_index,
    question: result.question,
    detected_language: result.detected_language,
    language_code: result.language_code,
    english_query: result.english_query,
    answer: result.answer,
    evidence: result.evidence,
    limitations: result.limitations,
    scientific_total: result.scientific_total,
    scientific_providers:
      result.scientific_providers,
    papers: result.papers,
    web_total: result.web_total,
    web_sources: result.web_sources,
    used_existing_context:
      result.used_existing_context,
    performed_search: result.performed_search,
    errors: result.errors,
    created_at: new Date().toISOString(),
  };
}

function createSessionFromResult(result) {
  const createdAt = new Date().toISOString();

  return {
    research_id: result.research_id,
    initial_question: result.question,
    detected_language: result.detected_language,
    language_code: result.language_code,
    created_at: createdAt,
    updated_at: createdAt,
    total_turns: 1,
    has_more_turns: false,
    next_before_turn_index: null,
    turns: [
      {
        ...resultToStoredTurn(result),
        created_at: createdAt,
      },
    ],
  };
}

function storedTurnToResult(session, turn) {
  return {
    research_id: session.research_id,
    ...turn,
  };
}

function mergeTurns(...turnGroups) {
  const turnsById = new Map();

  for (const turnGroup of turnGroups) {
    for (const turn of turnGroup ?? []) {
      turnsById.set(turn.turn_id, turn);
    }
  }

  return Array.from(turnsById.values()).sort(
    (firstTurn, secondTurn) =>
      firstTurn.turn_index - secondTurn.turn_index,
  );
}

function getPaginationFromLoadedTurns(
  turns,
  totalTurns,
) {
  const oldestTurnIndex =
    turns[0]?.turn_index ?? null;

  const hasMoreTurns =
    oldestTurnIndex !== null &&
    oldestTurnIndex > 1 &&
    turns.length < totalTurns;

  return {
    hasMoreTurns,
    nextBeforeTurnIndex: hasMoreTurns
      ? oldestTurnIndex
      : null,
  };
}

function App() {
  const [result, setResult] = useState(null);
  const [activeSession, setActiveSession] =
    useState(null);
  const [history, setHistory] = useState([]);

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] =
    useState(true);
  const [isSessionLoading, setIsSessionLoading] =
    useState(false);
  const [
    isPreviousTurnsLoading,
    setIsPreviousTurnsLoading,
  ] = useState(false);
  const [
    deletingResearchId,
    setDeletingResearchId,
  ] = useState("");
  const [mobileSidebarOpen, setMobileSidebarOpen] =
    useState(false);
  const [
    newResearchVersion,
    setNewResearchVersion,
  ] = useState(0);

  const conversationRef = useRef(null);
  const evidenceRef = useRef(null);

  const refreshHistory = useCallback(async () => {
    setIsHistoryLoading(true);

    try {
      const historyResult =
        await getResearchHistory({
          limit: 50,
          offset: 0,
        });

      setHistory(historyResult.sessions);
    } catch (requestError) {
      setError(
        requestError.message ||
          "Research history could not be loaded.",
      );
    } finally {
      setIsHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    let isActive = true;

    getResearchHistory({
      limit: 50,
      offset: 0,
    })
      .then((historyResult) => {
        if (isActive) {
          setHistory(historyResult.sessions);
        }
      })
      .catch((requestError) => {
        if (isActive) {
          setError(
            requestError.message ||
              "Research history could not be loaded.",
          );
        }
      })
      .finally(() => {
        if (isActive) {
          setIsHistoryLoading(false);
        }
      });

    return () => {
      isActive = false;
    };
  }, []);

  function scrollToConversation() {
    window.setTimeout(() => {
      conversationRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 180);
  }

  function scrollToEvidence() {
    window.setTimeout(() => {
      evidenceRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }, 120);
  }

  function handleNewResearch() {
    setResult(null);
    setActiveSession(null);
    setError("");

    setNewResearchVersion(
      (currentVersion) => currentVersion + 1,
    );

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  async function handleResearch(request) {
    setError("");
    setResult(null);
    setActiveSession(null);
    setIsLoading(true);

    try {
      const researchResult =
        await runResearch(request);

      setResult(researchResult);
      setActiveSession(
        createSessionFromResult(researchResult),
      );

      await refreshHistory();
      scrollToConversation();

      return true;
    } catch (requestError) {
      setError(
        requestError.message ||
          "The research request could not be completed.",
      );

      return false;
    } finally {
      setIsLoading(false);
    }
  }

  async function handleFollowUp(request) {
    const researchId =
      activeSession?.research_id ??
      result?.research_id;

    if (!researchId) {
      setError(
        "Select or create a research session first.",
      );

      return false;
    }

    setError("");
    setIsLoading(true);

    try {
      const followUpResult =
        await runResearchFollowUp(
          researchId,
          request,
        );

      setResult(followUpResult);

      try {
        const updatedSession =
          await getResearchSession(researchId);

        setActiveSession((currentSession) => {
          if (
            !currentSession ||
            currentSession.research_id !==
              researchId
          ) {
            return updatedSession;
          }

          const mergedTurns = mergeTurns(
            currentSession.turns,
            updatedSession.turns,
          );

          const pagination =
            getPaginationFromLoadedTurns(
              mergedTurns,
              updatedSession.total_turns,
            );

          return {
            ...currentSession,
            ...updatedSession,
            initial_question:
              currentSession.initial_question,
            turns: mergedTurns,
            has_more_turns:
              pagination.hasMoreTurns,
            next_before_turn_index:
              pagination.nextBeforeTurnIndex,
          };
        });
      } catch {
        setActiveSession((currentSession) => {
          if (!currentSession) {
            return createSessionFromResult(
              followUpResult,
            );
          }

          const mergedTurns = mergeTurns(
            currentSession.turns,
            [
              resultToStoredTurn(
                followUpResult,
              ),
            ],
          );

          const currentTotalTurns =
            currentSession.total_turns ??
            currentSession.turns.length;

          const totalTurns = Math.max(
            currentTotalTurns + 1,
            followUpResult.turn_index,
          );

          const pagination =
            getPaginationFromLoadedTurns(
              mergedTurns,
              totalTurns,
            );

          return {
            ...currentSession,
            updated_at: new Date().toISOString(),
            total_turns: totalTurns,
            turns: mergedTurns,
            has_more_turns:
              pagination.hasMoreTurns,
            next_before_turn_index:
              pagination.nextBeforeTurnIndex,
          };
        });
      }

      await refreshHistory();
      scrollToConversation();

      return true;
    } catch (requestError) {
      setError(
        requestError.message ||
          "The follow-up request could not be completed.",
      );

      return false;
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSessionSelect(researchId) {
    if (
      isSessionLoading ||
      researchId === activeSession?.research_id
    ) {
      setMobileSidebarOpen(false);
      return;
    }

    setError("");
    setIsSessionLoading(true);
    setMobileSidebarOpen(false);

    try {
      const session =
        await getResearchSession(researchId);

      setActiveSession(session);

      const latestTurn =
        session.turns[session.turns.length - 1];

      setResult(
        latestTurn
          ? storedTurnToResult(
              session,
              latestTurn,
            )
          : null,
      );

      scrollToConversation();
    } catch (requestError) {
      setError(
        requestError.message ||
          "The research session could not be loaded.",
      );
    } finally {
      setIsSessionLoading(false);
    }
  }

  async function handleLoadPreviousTurns() {
    if (
      !activeSession ||
      !activeSession.has_more_turns ||
      !activeSession.next_before_turn_index ||
      isPreviousTurnsLoading
    ) {
      return;
    }

    const researchId =
      activeSession.research_id;

    setError("");
    setIsPreviousTurnsLoading(true);

    try {
      const previousTurnsResult =
        await getResearchSession(
          researchId,
          {
            turnLimit:
              PREVIOUS_TURNS_BATCH_SIZE,
            beforeTurnIndex:
              activeSession
                .next_before_turn_index,
          },
        );

      setActiveSession((currentSession) => {
        if (
          !currentSession ||
          currentSession.research_id !==
            researchId
        ) {
          return currentSession;
        }

        return {
          ...currentSession,
          total_turns:
            previousTurnsResult.total_turns,
          has_more_turns:
            previousTurnsResult.has_more_turns,
          next_before_turn_index:
            previousTurnsResult
              .next_before_turn_index,
          turns: mergeTurns(
            previousTurnsResult.turns,
            currentSession.turns,
          ),
        };
      });
    } catch (requestError) {
      setError(
        requestError.message ||
          "Previous messages could not be loaded.",
      );
    } finally {
      setIsPreviousTurnsLoading(false);
    }
  }

  function handleConversationTurnSelect(turn) {
    if (!activeSession) {
      return;
    }

    setResult(
      storedTurnToResult(
        activeSession,
        turn,
      ),
    );

    scrollToEvidence();
  }

  async function handleSessionDelete(researchId) {
    const shouldDelete = window.confirm(
      "Delete this research session and all its turns?",
    );

    if (!shouldDelete) {
      return;
    }

    setError("");
    setDeletingResearchId(researchId);

    try {
      await deleteResearchSession(researchId);

      if (
        researchId === activeSession?.research_id
      ) {
        setActiveSession(null);
        setResult(null);
      }

      await refreshHistory();
    } catch (requestError) {
      setError(
        requestError.message ||
          "The research session could not be deleted.",
      );
    } finally {
      setDeletingResearchId("");
    }
  }

  const researchFormKey =
    activeSession?.research_id ??
    `new-research-${newResearchVersion}`;

  const initialResearchQuestion =
    activeSession?.initial_question ?? "";

  return (
    <Box sx={{ minHeight: "100vh" }}>
      <ResearchHistory
        sessions={history}
        selectedResearchId={
          activeSession?.research_id
        }
        isLoading={isHistoryLoading}
        deletingResearchId={deletingResearchId}
        mobileOpen={mobileSidebarOpen}
        onMobileClose={() =>
          setMobileSidebarOpen(false)
        }
        onSelect={handleSessionSelect}
        onDelete={handleSessionDelete}
        onNewResearch={handleNewResearch}
      />

      <Box
        sx={{
          minHeight: "100vh",
          ml: {
            xs: 0,
            lg: `${SIDEBAR_WIDTH}px`,
          },
        }}
      >
        <Box
          component="header"
          sx={{
            position: "sticky",
            top: 0,
            zIndex: 20,
            borderBottom: "1px solid",
            borderColor: "divider",
            backgroundColor:
              "rgba(2, 6, 23, 0.86)",
            backdropFilter: "blur(18px)",
          }}
        >
          <Container maxWidth="lg">
            <Stack
              direction="row"
              sx={{
                minHeight: 64,
                alignItems: "center",
                justifyContent: "space-between",
              }}
            >
              <Stack
                direction="row"
                spacing={1}
                sx={{ alignItems: "center" }}
              >
                <IconButton
                  aria-label="Open research history"
                  onClick={() =>
                    setMobileSidebarOpen(true)
                  }
                  sx={{
                    display: {
                      xs: "inline-flex",
                      lg: "none",
                    },
                  }}
                >
                  <MenuRounded />
                </IconButton>

                <Box
                  sx={{
                    display: "grid",
                    placeItems: "center",
                    width: 36,
                    height: 36,
                    borderRadius: 2.5,
                    color: "#020617",
                    background:
                      "linear-gradient(135deg, #22d3ee, #8b5cf6)",
                  }}
                >
                  <HubRounded fontSize="small" />
                </Box>

                <Typography
                  variant="subtitle1"
                  fontWeight={800}
                >
                  EvidenceGraph
                </Typography>
              </Stack>

              <Stack
                direction="row"
                spacing={0.75}
                sx={{ alignItems: "center" }}
              >
                <Chip
                  icon={<ScienceRounded />}
                  label="Evidence connected"
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
                  size="small"
                >
                  <GitHub />
                </IconButton>
              </Stack>
            </Stack>
          </Container>
        </Box>

        <Container
          component="main"
          maxWidth="lg"
          sx={{
            py: {
              xs: 2.5,
              md: 4,
            },
          }}
        >
          {!activeSession && (
            <Box
              sx={{
                maxWidth: 760,
                mb: {
                  xs: 2.5,
                  md: 3,
                },
              }}
            >
              <Typography
                variant="h3"
                component="h1"
                sx={{
                  fontSize: {
                    xs: "2rem",
                    md: "2.8rem",
                  },
                  lineHeight: 1.12,
                  background:
                    "linear-gradient(135deg, #f8fafc 20%, #67e8f9 60%, #a78bfa 95%)",
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  color: "transparent",
                }}
              >
                Ask a question. Follow the evidence.
              </Typography>

              <Typography
                variant="body1"
                color="text.secondary"
                sx={{
                  mt: 1.25,
                  lineHeight: 1.7,
                }}
              >
                Multilingual scientific and web research
                with sourced answers.
              </Typography>
            </Box>
          )}

          <Box
            sx={{
              maxWidth: 980,
              mx: "auto",
            }}
          >
            <ResearchForm
              key={researchFormKey}
              initialQuestion={
                initialResearchQuestion
              }
              onSubmit={handleResearch}
              isLoading={isLoading}
            />

            <ResearchProgress
              isVisible={
                isLoading || isSessionLoading
              }
            />

            {error && (
              <Alert
                severity="error"
                variant="outlined"
                onClose={() => setError("")}
                sx={{
                  mt: 2,
                  borderRadius: 3,
                  backgroundColor:
                    "rgba(244, 63, 94, 0.06)",
                }}
              >
                <Typography fontWeight={700}>
                  Request failed
                </Typography>

                <Typography
                  variant="body2"
                  sx={{ mt: 0.5 }}
                >
                  {error}
                </Typography>
              </Alert>
            )}

            <Box ref={conversationRef}>
              <ResearchConversation
                session={activeSession}
                selectedTurnId={result?.turn_id}
                isLoadingPrevious={
                  isPreviousTurnsLoading
                }
                onLoadPrevious={
                  handleLoadPreviousTurns
                }
                onSelectTurn={
                  handleConversationTurnSelect
                }
              />
            </Box>

            {result && activeSession && (
              <FollowUpForm
                onSubmit={handleFollowUp}
                isLoading={isLoading}
              />
            )}

            <Box ref={evidenceRef}>
              {result && (
                <Suspense
                  fallback={
                    <Typography
                      color="text.secondary"
                      textAlign="center"
                      sx={{ py: 3 }}
                    >
                      Preparing evidence...
                    </Typography>
                  }
                >
                  <ResearchResults result={result} />
                </Suspense>
              )}
            </Box>
          </Box>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
