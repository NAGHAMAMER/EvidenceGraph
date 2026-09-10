import {
  CancelOutlined,
  CheckCircleOutlineRounded,
  CompareArrowsRounded,
  HelpOutlineRounded,
} from "@mui/icons-material";
import {
  Box,
  Chip,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { motion } from "framer-motion";

const STANCE_CONFIG = {
  supports: {
    label: "Supports",
    color: "#22c55e",
    background: "rgba(34, 197, 94, 0.1)",
    icon: CheckCircleOutlineRounded,
  },
  contradicts: {
    label: "Contradicts",
    color: "#f43f5e",
    background: "rgba(244, 63, 94, 0.1)",
    icon: CancelOutlined,
  },
  mixed: {
    label: "Mixed evidence",
    color: "#f59e0b",
    background: "rgba(245, 158, 11, 0.1)",
    icon: CompareArrowsRounded,
  },
  uncertain: {
    label: "Uncertain",
    color: "#94a3b8",
    background: "rgba(148, 163, 184, 0.1)",
    icon: HelpOutlineRounded,
  },
};

const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const cardVariants = {
  hidden: {
    opacity: 0,
    y: 16,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.35,
    },
  },
};

function EvidenceList({
  evidence = [],
  direction = "ltr",
  onSourceSelect,
}) {
  if (evidence.length === 0) {
    return null;
  }

  return (
    <Box component="section">
      <Typography variant="h5" fontWeight={800}>
        Evidence claims
      </Typography>

      <Typography
  variant="body2"
  color="text.secondary"
  sx={{ mt: 0.5, mb: 2.5 }}
>
  Key claims synthesized from the sources used to generate
  the answer.
</Typography>

      <Stack
        component={motion.div}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        spacing={1.5}
      >
        {evidence.map((item, index) => {
          const config =
            STANCE_CONFIG[item.stance] ??
            STANCE_CONFIG.uncertain;

          const StatusIcon = config.icon;

          return (
            <Paper
              component={motion.article}
              variants={cardVariants}
              whileHover={{
                y: -3,
                transition: { duration: 0.18 },
              }}
              key={`${item.claim}-${index}`}
              elevation={0}
              sx={{
                p: { xs: 2, md: 2.5 },
                borderRadius: 3,
                border: "1px solid",
                borderColor: `${config.color}40`,
                backgroundColor: config.background,
              }}
            >
              <Stack spacing={1.5}>
                <Stack
                  direction="row"
                  justifyContent="space-between"
                  alignItems="flex-start"
                  gap={2}
                >
                  <Typography
                    variant="body1"
                    dir={direction}
                    sx={{
                      flex: 1,
                      textAlign:
                        direction === "rtl"
                          ? "right"
                          : "left",
                      lineHeight: 1.8,
                      fontWeight: 600,
                    }}
                  >
                    {item.claim}
                  </Typography>

                  <Chip
                    icon={
                      <StatusIcon
                        sx={{
                          color: `${config.color} !important`,
                        }}
                      />
                    }
                    label={config.label}
                    size="small"
                    sx={{
                      flexShrink: 0,
                      color: config.color,
                      border: "1px solid",
                      borderColor: `${config.color}50`,
                      backgroundColor: `${config.color}12`,
                    }}
                  />
                </Stack>

                {item.source_ids?.length > 0 && (
                  <Stack
                    direction="row"
                    useFlexGap
                    flexWrap="wrap"
                    gap={0.75}
                    alignItems="center"
                  >
                    <Typography
                      variant="caption"
                      color="text.secondary"
                    >
                      Sources:
                    </Typography>

                    {item.source_ids.map((sourceId) => (
                      <Chip
                        key={sourceId}
                        label={sourceId}
                        size="small"
                        clickable={Boolean(onSourceSelect)}
                        onClick={() =>
                          onSourceSelect?.(sourceId)
                        }
                        sx={{
                          fontWeight: 750,
                          fontFamily: "monospace",
                          transition:
                            "transform 160ms ease",
                          "&:hover": {
                            transform: "scale(1.06)",
                          },
                        }}
                      />
                    ))}
                  </Stack>
                )}
              </Stack>
            </Paper>
          );
        })}
      </Stack>
    </Box>
  );
}

export default EvidenceList;
