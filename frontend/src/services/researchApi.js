import { getClientId } from "../utils/clientIdentity";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ??
  "http://localhost:8000/api/v1"
).replace(/\/$/, "");

const REQUEST_TIMEOUT_MS = 135_000;

const DEFAULT_ERROR_MESSAGES = {
  404: "The requested research session was not found.",
  422: "Please check the question and result limit.",
  502: "The research agent could not complete the request.",
  503: "The research data service is temporarily unavailable.",
  504: "An external research service timed out. Please try again.",
};

async function readResponse(response) {
  const contentType =
    response.headers.get("content-type") ?? "";

  if (!contentType.includes("application/json")) {
    return null;
  }

  return response.json();
}

async function requestJson(
  path,
  {
    method = "GET",
    body,
  } = {},
) {
  const controller = new AbortController();

  const timeoutId = window.setTimeout(() => {
    controller.abort();
  }, REQUEST_TIMEOUT_MS);

  const headers = {
    Accept: "application/json",
    "X-Client-ID": getClientId(),
  };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}${path}`,
      {
        method,
        headers,
        body:
          body === undefined
            ? undefined
            : JSON.stringify(body),
        signal: controller.signal,
      },
    );

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

function buildResearchPayload({ question, limit }) {
  return {
    question: question.trim(),
    limit: Number(limit),
  };
}

export function runResearch({ question, limit }) {
  return requestJson(
    "/research",
    {
      method: "POST",
      body: buildResearchPayload({
        question,
        limit,
      }),
    },
  );
}

export function runResearchFollowUp(
  researchId,
  {
    question,
    limit,
  },
) {
  const encodedResearchId =
    encodeURIComponent(researchId);

  return requestJson(
    `/research/${encodedResearchId}/follow-up`,
    {
      method: "POST",
      body: buildResearchPayload({
        question,
        limit,
      }),
    },
  );
}

export function getResearchHistory({
  limit = 20,
  offset = 0,
} = {}) {
  const query = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });

  return requestJson(
    `/research/history?${query.toString()}`,
  );
}

export function getResearchSession(
  researchId,
  {
    turnLimit = 1,
    beforeTurnIndex,
  } = {},
) {
  const encodedResearchId =
    encodeURIComponent(researchId);

  const query = new URLSearchParams({
    turn_limit: String(turnLimit),
  });

  if (beforeTurnIndex !== undefined) {
    query.set(
      "before_turn_index",
      String(beforeTurnIndex),
    );
  }

  return requestJson(
    (
      `/research/${encodedResearchId}` +
      `?${query.toString()}`
    ),
  );
}

export function deleteResearchSession(researchId) {
  const encodedResearchId =
    encodeURIComponent(researchId);

  return requestJson(
    `/research/${encodedResearchId}`,
    {
      method: "DELETE",
    },
  );
}
