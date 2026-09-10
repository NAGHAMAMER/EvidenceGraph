import { useMemo, useState } from "react";
import {
  AutoAwesomeRounded,
  ScienceRounded,
} from "@mui/icons-material";
import {
  Box,
  Button,
  Chip,
  Paper,
  Slider,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { motion } from "framer-motion";

import { getTextDirection } from "../utils/language";

const EXAMPLE_QUESTIONS = [
  {
    label: "English",
    question:
      "How does regular exercise affect symptoms of depression in adults?",
  },
  {
    label: "العربية",
    question:
      "ما تأثير الذكاء الاصطناعي في الكشف المبكر عن سرطان الثدي؟",
  },
  {
    label: "Français",
    question:
      "Quels sont les effets du changement climatique sur la santé humaine ?",
  },
];

function ResearchForm({ onSubmit, isLoading }) {
  const [question, setQuestion] = useState("");
  const [limit, setLimit] = useState(5);

  const direction = useMemo(
    () => getTextDirection("", question),
    [question],
  );

  const canSubmit =
    question.trim().length >= 2 && !isLoading;

  function handleSubmit(event) {
    event.preventDefault();

    if (!canSubmit) {
      return;
    }

    onSubmit({
      question: question.trim(),
      limit,
    });
  }

  return (
    <Box
      component={motion.form}
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55 }}
    >
      <Paper
        elevation={0}
        sx={{
          p: { xs: 2.5, md: 4 },
          border: "1px solid",
          borderColor: "rgba(148, 163, 184, 0.18)",
          borderRadius: 5,
          background:
            "linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.9))",
          backdropFilter: "blur(18px)",
          boxShadow: "0 24px 70px rgba(2, 8, 23, 0.32)",
        }}
      >
        <Stack spacing={3}>
         <Stack
  direction="row"
  spacing={1.5}
  sx={{ alignItems: "center" }}
>
            <ScienceRounded color="primary" />

            <Box>
              <Typography variant="h5" fontWeight={750}>
                Research a scientific question
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
              >
                Ask in any language. EvidenceGraph will
                research and answer in the same language.
              </Typography>
            </Box>
          </Stack>

          <TextField
            multiline
            minRows={5}
            fullWidth
            autoFocus
            label="Research question"
            placeholder="Enter a scientific research question..."
            value={question}
            disabled={isLoading}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            helperText={`${question.length}/1000 characters`}
            slotProps={{
              htmlInput: {
                maxLength: 1000,
                dir: direction,
              },
            }}
            sx={{
              "& textarea": {
                direction,
                textAlign:
                  direction === "rtl" ? "right" : "left",
                lineHeight: 1.8,
                fontSize: "1rem",
              },
            }}
          />

          <Box>
            <Typography
              variant="body2"
              fontWeight={650}
              gutterBottom
            >
              Number of research results: {limit}
            </Typography>

            <Slider
              value={limit}
              min={1}
              max={10}
              step={1}
              marks={[
                { value: 1, label: "1" },
                { value: 5, label: "5" },
                { value: 10, label: "10" },
              ]}
              disabled={isLoading}
              valueLabelDisplay="auto"
              onChange={(_, newValue) =>
                setLimit(newValue)
              }
              aria-label="Number of research results"
            />
          </Box>

          <Box>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mb: 1.25 }}
            >
              Try an example
            </Typography>
<Stack
  direction="row"
  useFlexGap
  sx={{
    flexWrap: "wrap",
    gap: 1,
  }}
>
              {EXAMPLE_QUESTIONS.map((example) => (
                <Chip
                  key={example.label}
                  label={example.label}
                  clickable
                  disabled={isLoading}
                  onClick={() =>
                    setQuestion(example.question)
                  }
                  sx={{
                    transition:
                      "transform 180ms ease, background 180ms ease",
                    "&:hover": {
                      transform: "translateY(-2px)",
                    },
                  }}
                />
              ))}
            </Stack>
          </Box>

          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={!canSubmit}
            startIcon={<AutoAwesomeRounded />}
            sx={{
              alignSelf: {
                xs: "stretch",
                sm: "flex-start",
              },
              minWidth: 210,
              minHeight: 52,
              borderRadius: 3,
              fontWeight: 750,
              textTransform: "none",
              background:
                "linear-gradient(135deg, #22d3ee, #6366f1)",
              boxShadow:
                "0 12px 30px rgba(99, 102, 241, 0.3)",
              transition:
                "transform 180ms ease, box-shadow 180ms ease",
              "&:hover": {
                transform: "translateY(-2px)",
                boxShadow:
                  "0 16px 38px rgba(99, 102, 241, 0.42)",
              },
            }}
          >
            {isLoading
              ? "Researching..."
              : "Start research"}
          </Button>
        </Stack>
      </Paper>
    </Box>
  );
}

export default ResearchForm;
