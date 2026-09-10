import {
  AutoAwesomeRounded,
  HubRounded,
  PublicRounded,
  ScienceRounded,
} from "@mui/icons-material";
import {
  Box,
  Chip,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import {
  motion,
  useReducedMotion,
} from "framer-motion";

function HeroVisual() {
  const reduceMotion = useReducedMotion();

  return (
    <Paper
      component={motion.aside}
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.65 }}
      elevation={0}
      sx={{
        position: "relative",
        width: "100%",
        height: "100%",
        minHeight: {
          xs: 320,
          sm: 400,
          lg: 560,
        },
        borderRadius: 5,
        overflow: "hidden",
        border: "1px solid",
        borderColor: "rgba(99, 102, 241, 0.25)",
        backgroundColor: "#071426",
        boxShadow:
          "0 24px 70px rgba(2, 8, 23, 0.34)",
      }}
    >
      <Box
        component={motion.img}
        src="/evidence-network.png"
        alt="Scientific papers connected in an evidence graph"
        animate={
          reduceMotion
            ? undefined
            : {
                scale: [1, 1.035, 1],
              }
        }
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        sx={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          objectPosition: "center",
        }}
      />

      <Box
        sx={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(180deg, rgba(2,8,23,0.05) 15%, rgba(2,8,23,0.92) 100%)",
        }}
      />

      <Stack
        spacing={2}
        sx={{
          position: "absolute",
          insetInline: 0,
          bottom: 0,
          p: {
            xs: 2.5,
            md: 3.5,
          },
        }}
      >
        <Stack
          direction="row"
          spacing={1}
          sx={{
            alignItems: "center",
          }}
        >
          <HubRounded color="primary" />

          <Typography variant="h5" fontWeight={800}>
            Evidence, connected
          </Typography>
        </Stack>

        <Typography
          variant="body2"
          sx={{
            maxWidth: 520,
            color: "rgba(226, 232, 240, 0.82)",
            lineHeight: 1.7,
          }}
        >
          EvidenceGraph combines scientific literature,
          web research, and semantic analysis into one
          traceable answer.
        </Typography>

        <Stack
          direction="row"
          useFlexGap
          sx={{
            flexWrap: "wrap",
            gap: 1,
          }}
        >
          <Chip
            icon={<ScienceRounded />}
            label="Scientific papers"
            size="small"
            sx={{
              backgroundColor:
                "rgba(8, 145, 178, 0.2)",
              backdropFilter: "blur(10px)",
            }}
          />

          <Chip
            icon={<PublicRounded />}
            label="Web sources"
            size="small"
            sx={{
              backgroundColor:
                "rgba(99, 102, 241, 0.2)",
              backdropFilter: "blur(10px)",
            }}
          />

          <Chip
            icon={<AutoAwesomeRounded />}
            label="AI synthesis"
            size="small"
            sx={{
              backgroundColor:
                "rgba(139, 92, 246, 0.2)",
              backdropFilter: "blur(10px)",
            }}
          />
        </Stack>
      </Stack>
    </Paper>
  );
}

export default HeroVisual;
