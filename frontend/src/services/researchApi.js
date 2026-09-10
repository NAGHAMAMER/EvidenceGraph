const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000/api/v1"
).replace(/\/$/, "");

const REQUEST_TIMEOUT_MS = 135_000;

const DEFAULT_ERROR_MESSAGES = {
  422: "Please check the question and result limit.",
  502: "The research agent could not complete the request.",
  504: "An external research service timed out. Please try again.",
};

async function readResponse(response) {
  const contentType = response.headers.get("content-type") ?? "";

  if (!contentType.includes("application/json")) {
    return null;
  }

  return response.json();
}

export async function runResearch({ question, limit }) {
  const controller = new AbortController();

  const timeoutId = window.setTimeout(() => {
    controller.abort();
  }, REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}/research`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: question.trim(),
        limit: Number(limit),
      }),
      signal: controller.signal,
    });

    const data = await readResponse(response);

    if (!response.ok) {
      const message =
        data?.detail ??
        DEFAULT_ERROR_MESSAGES[response.status] ??
        "An unexpected error occurred.";

      const error = new Error(message);
      error.status = response.status;
      throw error;
    }

    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(
        "The request took too long. Please try again.",
      );
    }

    if (error instanceof TypeError) {
      throw new Error(
        "Could not connect to the EvidenceGraph API.",
      );
    }

    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}
