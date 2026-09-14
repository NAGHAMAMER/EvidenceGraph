import { useMemo, useState } from "react";
import {
  ChatRounded,
  SendRounded,
} from "@mui/icons-material";
import {
  Box,
  Button,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { motion } from "framer-motion";

import { getTextDirection } from "../utils/language";

function FollowUpForm({
  onSubmit,
  isLoading,
}) {
  const [question, setQuestion] = useState("");
  const [limit, setLimit] = useState(5);

  const direction = useMemo(
    () => getTextDirection("", question),
    [question],
  );

  const canSubmit =
    question.trim().length >= 2 && !isLoading;

  async function handleSubmit(event) {
    event.preventDefault();

    if (!canSubmit) {
      return;
    }

    const submittedQuestion = question.trim();

    const wasSuccessful = await onSubmit({
      question: submittedQuestion,
      limit,
    });

    if (wasSuccessful) {
      setQuestion("");
    }
  }

  return (
    <Paper
      component={motion.form}
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      elevation={0}
      sx={{
        mt: 3,
        p: {
          xs: 2,
          md: 3,
        },
        borderRadius: 4,
        border: "1px solid",
        borderColor: "rgba(34, 211, 238, 0.25)",
        background:
          "linear-gradient(145deg, rgba(15,23,42,0.96), rgba(30,41,59,0.88))",
      }}
    >
      <Stack spacing={2}>
        <Stack
          direction="row"
          spacing={1}
          sx={{ alignItems: "center" }}
        >
          <ChatRounded color="primary" />

          <Box>
            <Typography variant="h6">
              Continue this research
            </Typography>

            <Typography
              variant="body2"
              color="text.secondary"
            >
              The agent will use saved evidence or search
              again when more information is needed.
            </Typography>
          </Box>
        </Stack>

        <TextField
          fullWidth
          multiline
          minRows={3}
          label="Follow-up question"
          placeholder="Ask about the answer, evidence, or a related topic..."
          value={question}
          disabled={isLoading}
          onChange={(event) =>
            setQuestion(event.target.value)
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
              lineHeight: 1.8,
            },
          }}
        />

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
          <TextField
            select
            size="small"
            label="Result limit"
            value={limit}
            disabled={isLoading}
            onChange={(event) =>
              setLimit(Number(event.target.value))
            }
            sx={{
              minWidth: {
                xs: "100%",
                sm: 150,
              },
            }}
          >
            {[1, 2, 3, 5, 7, 10].map((value) => (
              <MenuItem key={value} value={value}>
                {value} sources
              </MenuItem>
            ))}
          </TextField>

          <Button
            type="submit"
            variant="contained"
            disabled={!canSubmit}
            endIcon={<SendRounded />}
            sx={{
              minWidth: 190,
              minHeight: 48,
              textTransform: "none",
              background:
                "linear-gradient(135deg, #22d3ee, #6366f1)",
            }}
          >
            {isLoading
              ? "Researching follow-up..."
              : "Ask follow-up"}
          </Button>
        </Stack>
      </Stack>
    </Paper>
  );
}

export default FollowUpForm;
