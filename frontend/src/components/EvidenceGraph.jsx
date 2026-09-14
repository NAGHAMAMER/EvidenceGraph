import { useMemo, useState } from "react";
import {
  AccountTreeRounded,
  ExpandLessRounded,
  ExpandMoreRounded,
  OpenInNewRounded,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Chip,
  Collapse,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { motion } from "framer-motion";

const GRAPH_WIDTH = 1040;
const NODE_WIDTH = 210;
const NODE_HEIGHT = 68;

const STANCE_COLORS = {
  supports: "#22c55e",
  contradicts: "#f43f5e",
  mixed: "#f59e0b",
  uncertain: "#94a3b8",
};

function shortenText(value, maximumLength = 42) {
  const text = String(value ?? "").trim();

  if (text.length <= maximumLength) {
    return text;
  }

  return `${text.slice(0, maximumLength - 1)}…`;
}

function distributeVertically(
  index,
  count,
  height,
) {
  if (count <= 1) {
    return height / 2;
  }

  const margin = 70;

  return (
    margin +
    (
      index *
      (height - margin * 2)
    ) /
      (count - 1)
  );
}

function GraphNode({
  x,
  y,
  eyebrow,
  label,
  color,
  isSelected,
  onSelect,
}) {
  function handleKeyDown(event) {
    if (
      event.key === "Enter" ||
      event.key === " "
    ) {
      event.preventDefault();
      onSelect();
    }
  }

  return (
    <motion.g
      role="button"
      tabIndex={0}
      aria-label={`${eyebrow}: ${label}`}
      onClick={onSelect}
      onKeyDown={handleKeyDown}
      initial={{
        opacity: 0,
        scale: 0.94,
      }}
      animate={{
        opacity: 1,
        scale: 1,
      }}
      whileHover={{
        scale: 1.025,
      }}
      transition={{
        duration: 0.25,
      }}
      style={{
        cursor: "pointer",
        transformOrigin: `${x}px ${y}px`,
      }}
    >
      <rect
        x={x - NODE_WIDTH / 2}
        y={y - NODE_HEIGHT / 2}
        width={NODE_WIDTH}
        height={NODE_HEIGHT}
        rx={16}
        fill={
          isSelected
            ? `${color}24`
            : "rgba(15, 23, 42, 0.96)"
        }
        stroke={color}
        strokeWidth={isSelected ? 3 : 1.5}
      />

      <text
        x={x}
        y={y - 8}
        textAnchor="middle"
        fill={color}
        fontSize="12"
        fontWeight="800"
        pointerEvents="none"
      >
        {eyebrow}
      </text>

      <text
        x={x}
        y={y + 15}
        textAnchor="middle"
        fill="#e2e8f0"
        fontSize="12"
        fontWeight="600"
        pointerEvents="none"
      >
        {shortenText(label)}
      </text>
    </motion.g>
  );
}

function EvidenceGraph({
  result,
  onSourceSelect,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedNode, setSelectedNode] =
    useState(null);

  const graph = useMemo(() => {
    const papers = (result?.papers ?? []).map(
      (paper, index) => ({
        id: `P${index + 1}`,
        type: "paper",
        title: paper.title,
        description:
          paper.abstract ||
          paper.venue ||
          "Scientific paper",
      }),
    );

    const webSources = (
      result?.web_sources ?? []
    ).map((source, index) => ({
      id: `W${index + 1}`,
      type: "web",
      title: source.title,
      description:
        source.content || "Web source",
    }));

    const allSources = [
      ...papers,
      ...webSources,
    ];

    const sourcesById = new Map(
      allSources.map((source) => [
        source.id,
        source,
      ]),
    );

    const claims = (result?.evidence ?? []).map(
      (evidence, index) => ({
        id: `C${index + 1}`,
        type: "claim",
        title: evidence.claim,
        description: evidence.claim,
        stance: evidence.stance,
        sourceIds: (
          evidence.source_ids ?? []
        ).filter((sourceId) =>
          sourcesById.has(sourceId)
        ),
      }),
    );

    const referencedSourceIds = new Set(
      claims.flatMap(
        (claim) => claim.sourceIds,
      ),
    );

    const referencedSources = allSources.filter(
      (source) =>
        referencedSourceIds.has(source.id),
    );

    const largestColumnSize = Math.max(
      claims.length,
      referencedSources.length,
      1,
    );

    const height = Math.max(
      340,
      largestColumnSize * 100,
    );

    const questionNode = {
      id: "Q",
      type: "question",
      title: result?.question ?? "",
      description: result?.question ?? "",
      x: 130,
      y: height / 2,
    };

    const claimNodes = claims.map(
      (claim, index) => ({
        ...claim,
        x: 500,
        y: distributeVertically(
          index,
          claims.length,
          height,
        ),
      }),
    );

    const sourceNodes = referencedSources.map(
      (source, index) => ({
        ...source,
        x: 890,
        y: distributeVertically(
          index,
          referencedSources.length,
          height,
        ),
      }),
    );

    const claimNodesById = new Map(
      claimNodes.map((claim) => [
        claim.id,
        claim,
      ]),
    );

    const sourceNodesById = new Map(
      sourceNodes.map((source) => [
        source.id,
        source,
      ]),
    );

    const questionEdges = claimNodes.map(
      (claim) => ({
        id: `Q-${claim.id}`,
        fromX:
          questionNode.x + NODE_WIDTH / 2,
        fromY: questionNode.y,
        toX: claim.x - NODE_WIDTH / 2,
        toY: claim.y,
        color:
          STANCE_COLORS[claim.stance] ??
          STANCE_COLORS.uncertain,
      }),
    );

    const sourceEdges = claims.flatMap(
      (claim) =>
        claim.sourceIds.flatMap((sourceId) => {
          const claimNode =
            claimNodesById.get(claim.id);

          const sourceNode =
            sourceNodesById.get(sourceId);

          if (!claimNode || !sourceNode) {
            return [];
          }

          return [
            {
              id: `${claim.id}-${sourceId}`,
              fromX:
                claimNode.x +
                NODE_WIDTH / 2,
              fromY: claimNode.y,
              toX:
                sourceNode.x -
                NODE_WIDTH / 2,
              toY: sourceNode.y,
              color:
                STANCE_COLORS[claim.stance] ??
                STANCE_COLORS.uncertain,
            },
          ];
        }),
    );

    return {
      height,
      questionNode,
      claimNodes,
      sourceNodes,
      edges: [
        ...questionEdges,
        ...sourceEdges,
      ],
    };
  }, [result]);

  if ((result?.evidence ?? []).length === 0) {
    return null;
  }

  function selectNode(node) {
    setSelectedNode(node);
  }

  return (
    <Paper
      component="section"
      elevation={0}
      sx={{
        mb: 3,
        border: "1px solid",
        borderColor:
          "rgba(34, 211, 238, 0.22)",
        borderRadius: 3,
        overflow: "hidden",
        backgroundColor:
          "rgba(2, 8, 23, 0.38)",
      }}
    >
      <Button
        fullWidth
        onClick={() =>
          setIsOpen((current) => !current)
        }
        startIcon={<AccountTreeRounded />}
        endIcon={
          isOpen
            ? <ExpandLessRounded />
            : <ExpandMoreRounded />
        }
        sx={{
          justifyContent: "flex-start",
          px: 2.5,
          py: 1.75,
          borderRadius: 0,
          textTransform: "none",
          fontWeight: 800,
          color: "text.primary",
          "& .MuiButton-endIcon": {
            ml: "auto",
          },
        }}
      >
        Interactive evidence graph
      </Button>

      <Collapse in={isOpen}>
        <Box
          sx={{
            px: {
              xs: 1.5,
              md: 2.5,
            },
            pb: 2.5,
          }}
        >
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 1.5,
            }}
          >
            Select a question, claim, or source to inspect
            its role in the generated answer.
          </Typography>

          <Stack
            direction="row"
            useFlexGap
            sx={{
              flexWrap: "wrap",
              gap: 0.75,
              mb: 1.5,
            }}
          >
            <Chip
              size="small"
              label="Supports"
              sx={{
                color: STANCE_COLORS.supports,
              }}
            />

            <Chip
              size="small"
              label="Contradicts"
              sx={{
                color: STANCE_COLORS.contradicts,
              }}
            />

            <Chip
              size="small"
              label="Mixed"
              sx={{
                color: STANCE_COLORS.mixed,
              }}
            />

            <Chip
              size="small"
              label="Uncertain"
              sx={{
                color: STANCE_COLORS.uncertain,
              }}
            />
          </Stack>

          <Box
            sx={{
              overflowX: "auto",
              borderRadius: 2.5,
              border: "1px solid",
              borderColor:
                "rgba(148, 163, 184, 0.12)",
              background:
                "radial-gradient(circle at center, rgba(30,41,59,0.72), rgba(2,6,23,0.96))",
            }}
          >
            <Box
              component="svg"
              viewBox={
                `0 0 ${GRAPH_WIDTH} ${graph.height}`
              }
              aria-label="Evidence relationship graph"
              sx={{
                display: "block",
                width: {
                  xs: 900,
                  md: "100%",
                },
                minWidth: 900,
                minHeight: 320,
              }}
            >
              <text
                x="130"
                y="30"
                textAnchor="middle"
                fill="#94a3b8"
                fontSize="13"
                fontWeight="700"
              >
                QUESTION
              </text>

              <text
                x="500"
                y="30"
                textAnchor="middle"
                fill="#94a3b8"
                fontSize="13"
                fontWeight="700"
              >
                CLAIMS
              </text>

              <text
                x="890"
                y="30"
                textAnchor="middle"
                fill="#94a3b8"
                fontSize="13"
                fontWeight="700"
              >
                SOURCES
              </text>

              {graph.edges.map((edge) => (
                <motion.path
                  key={edge.id}
                  d={
                    `M ${edge.fromX} ${edge.fromY} ` +
                    `C ${edge.fromX + 90} ${edge.fromY}, ` +
                    `${edge.toX - 90} ${edge.toY}, ` +
                    `${edge.toX} ${edge.toY}`
                  }
                  fill="none"
                  stroke={edge.color}
                  strokeWidth="2"
                  strokeOpacity="0.62"
                  initial={{
                    pathLength: 0,
                    opacity: 0,
                  }}
                  animate={{
                    pathLength: 1,
                    opacity: 1,
                  }}
                  transition={{
                    duration: 0.7,
                  }}
                />
              ))}

              <GraphNode
                x={graph.questionNode.x}
                y={graph.questionNode.y}
                eyebrow="Question"
                label={graph.questionNode.title}
                color="#22d3ee"
                isSelected={
                  selectedNode?.id ===
                  graph.questionNode.id
                }
                onSelect={() =>
                  selectNode(
                    graph.questionNode
                  )
                }
              />

              {graph.claimNodes.map((claim) => (
                <GraphNode
                  key={claim.id}
                  x={claim.x}
                  y={claim.y}
                  eyebrow={
                    `${claim.id} · ${claim.stance}`
                  }
                  label={claim.title}
                  color={
                    STANCE_COLORS[claim.stance] ??
                    STANCE_COLORS.uncertain
                  }
                  isSelected={
                    selectedNode?.id === claim.id
                  }
                  onSelect={() =>
                    selectNode(claim)
                  }
                />
              ))}

              {graph.sourceNodes.map((source) => (
                <GraphNode
                  key={source.id}
                  x={source.x}
                  y={source.y}
                  eyebrow={
                    `${source.id} · ${source.type}`
                  }
                  label={source.title}
                  color="#a78bfa"
                  isSelected={
                    selectedNode?.id === source.id
                  }
                  onSelect={() =>
                    selectNode(source)
                  }
                />
              ))}
            </Box>
          </Box>

          {selectedNode && (
            <Paper
              elevation={0}
              sx={{
                mt: 1.5,
                p: 2,
                borderRadius: 2.5,
                border: "1px solid",
                borderColor:
                  "rgba(148, 163, 184, 0.18)",
                backgroundColor:
                  "rgba(15, 23, 42, 0.76)",
              }}
            >
              <Stack spacing={1.25}>
                <Typography
                  variant="caption"
                  color="primary.main"
                  fontWeight={800}
                  sx={{
                    textTransform: "uppercase",
                  }}
                >
                  {selectedNode.type}
                  {selectedNode.id
                    ? ` · ${selectedNode.id}`
                    : ""}
                </Typography>

                <Typography
                  variant="body1"
                  dir="auto"
                  fontWeight={650}
                  sx={{
                    lineHeight: 1.7,
                  }}
                >
                  {selectedNode.description}
                </Typography>

                {(
                  selectedNode.type === "paper" ||
                  selectedNode.type === "web"
                ) && (
                  <Button
                    size="small"
                    variant="outlined"
                    endIcon={<OpenInNewRounded />}
                    onClick={() =>
                      onSourceSelect?.(
                        selectedNode.id
                      )
                    }
                    sx={{
                      alignSelf: "flex-start",
                      textTransform: "none",
                      borderRadius: 2.5,
                    }}
                  >
                    Open source details
                  </Button>
                )}
              </Stack>
            </Paper>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
}

export default EvidenceGraph;
