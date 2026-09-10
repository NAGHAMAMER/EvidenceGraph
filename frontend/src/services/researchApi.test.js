import {
  afterEach,
  describe,
  expect,
  test,
  vi,
} from "vitest";

import { runResearch } from "./researchApi";

function createJsonResponse({
  ok,
  status,
  data,
}) {
  return {
    ok,
    status,
    headers: {
      get: vi.fn(() => "application/json"),
    },
    json: vi.fn().mockResolvedValue(data),
  };
}

describe("runResearch", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  test("returns research data after a successful request", async () => {
    const result = {
      question: "What is semantic search?",
      answer: "Semantic search compares meaning.",
      evidence: [],
      papers: [],
      web_sources: [],
    };

    globalThis.fetch = vi.fn().mockResolvedValue(
      createJsonResponse({
        ok: true,
        status: 200,
        data: result,
      }),
    );

    await expect(
      runResearch({
        question: "  What is semantic search?  ",
        limit: 5,
      }),
    ).resolves.toEqual(result);

    expect(globalThis.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/research",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          question: "What is semantic search?",
          limit: 5,
        }),
      }),
    );
  });

  test("returns the backend message for a timeout", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      createJsonResponse({
        ok: false,
        status: 504,
        data: {
          detail:
            "An external research service timed out.",
        },
      }),
    );

    await expect(
      runResearch({
        question: "Research question",
        limit: 5,
      }),
    ).rejects.toMatchObject({
      message:
        "An external research service timed out.",
      status: 504,
    });
  });

  test("returns a friendly connection error", async () => {
    globalThis.fetch = vi
      .fn()
      .mockRejectedValue(new TypeError("Failed to fetch"));

    await expect(
      runResearch({
        question: "Research question",
        limit: 5,
      }),
    ).rejects.toThrow(
      "Could not connect to the EvidenceGraph API.",
    );
  });
});
