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

function ResearchForm({
  onSubmit,
  isLoading,
  initialQuestion = "",
}) {
  const [question, setQuestion] = useState(
    initialQuestion,
  );
  const [limit, setLimit] = useState(5);

  const hasInitialQuestion =
    initialQuestion.trim().length > 0;

  const direction = useMemo(
    () => getTextDirection("", question),
    [question],
  );

  const canSubmit =
    question.trim().length >= 2 && !isLoading;

  async function handleSubmit(event) {
    event.preventDefault();

    if (!canSubmit || hasInitialQuestion) {
      return;
    }

    await onSubmit({
      question: question.trim(),
      limit,
    });
  }

  if (hasInitialQuestion) {
    return (
      <Paper
        elevation={0}
        sx={{
          p: {
            xs: 2,
            md: 2.5,
          },
          border: "1px solid",
          borderColor:
            "rgba(148, 163, 184, 0.18)",
          borderRadius: 4,
          backgroundColor:
            "rgba(15, 23, 42, 0.72)",
        }}
      >
        <Stack spacing={1.5}>
          <Stack
            direction="row"
            spacing={1}
            sx={{ alignItems: "center" }}
          >
            <ScienceRounded
              color="primary"
              fontSize="small"
            />

            <Typography
              variant="subtitle1"
              fontWeight={750}
            >
              Original research question
            </Typography>
          </Stack>

          <TextField
            multiline
            minRows={2}
            maxRows={4}
            fullWidth
            value={question}
            slotProps={{
              htmlInput: {
                readOnly: true,
                dir: direction,
              },
            }}
            sx={{
              "& textarea": {
                direction,
                textAlign:
                  direction === "rtl"
                    ? "right"
                    : "left",
                lineHeight: 1.7,
              },
            }}
          />
        </Stack>
      </Paper>
    );
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
    >
      <Paper
        elevation={0}
        sx={{
          p: {
            xs: 2.25,
            md: 3,
          },
          border: "1px solid",
          borderColor:
            "rgba(148, 163, 184, 0.18)",
          borderRadius: 4,
          background:
            "linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.88))",
          boxShadow:
            "0 18px 55px rgba(2, 8, 23, 0.24)",
        }}
      >
        <Stack spacing={2.25}>
          <Box>
            <Stack
              direction="row"
              spacing={1}
              sx={{
                alignItems: "center",
                mb: 0.5,
              }}
            >
              <ScienceRounded color="primary" />

              <Typography
                variant="h5"
                fontWeight={780}
              >
                Start new research
              </Typography>
            </Stack>

            <Typography
              variant="body2"
              color="text.secondary"
            >
              Ask in any language and receive a sourced
              answer in the same language.
            </Typography>
          </Box>

          <TextField
            multiline
            minRows={3}
            maxRows={7}
            fullWidth
            autoFocus
            label="Research question"
            placeholder="Enter a scientific research question..."
            value={question}
            disabled={isLoading}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            helperText={
              `${question.length}/1000 characters`
            }
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
                  direction === "rtl"
                    ? "right"
                    : "left",
                lineHeight: 1.75,
              },
            }}
          />

          <Box>
            <Stack
              direction={{
                xs: "column",
                sm: "row",
              }}
              spacing={2}
              sx={{
                alignItems: {
                  xs: "stretch",
                  sm: "center",
                },
              }}
            >
              <Box sx={{ flex: 1 }}>
                <Typography
                  variant="body2"
                  fontWeight={650}
                  gutterBottom
                >
                  Results per source: {limit}
                </Typography>

                <Slider
                  value={limit}
                  min={1}
                  max={10}
                  step={1}
                  disabled={isLoading}
                  valueLabelDisplay="auto"
                  onChange={(_, newValue) =>
                    setLimit(newValue)
                  }
                  aria-label="Number of results per source"
                />
              </Box>

              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={!canSubmit}
                startIcon={<AutoAwesomeRounded />}
                sx={{
                  minWidth: 190,
                  minHeight: 48,
                  borderRadius: 3,
                  fontWeight: 750,
                  textTransform: "none",
                  background:
                    "linear-gradient(135deg, #22d3ee, #6366f1)",
                }}
              >
                {isLoading
                  ? "Researching..."
                  : "Start research"}
              </Button>
            </Stack>
          </Box>

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
                size="small"
              />
            ))}
          </Stack>
        </Stack>
      </Paper>
    </Box>
  );
}

export default ResearchForm;