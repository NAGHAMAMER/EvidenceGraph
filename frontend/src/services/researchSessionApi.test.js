import {
  deleteResearchSession,
  getResearchHistory,
  getResearchSession,
  runResearchFollowUp,
} from "./researchApi";

const RESEARCH_ID =
  "ba56478c-35d2-457d-b4be-721100fc9110";

const CLIENT_ID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function createJsonResponse(
  data,
  {
    ok = true,
    status = 200,
  } = {},
) {
  return {
    ok,
    status,
    headers: {
      get: () => "application/json",
    },
    json: vi.fn().mockResolvedValue(data),
  };
}

describe("research session API", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("submits a follow-up question", async () => {
    const expectedResponse = {
      research_id: RESEARCH_ID,
      turn_index: 2,
      performed_search: false,
    };

    fetch.mockResolvedValueOnce(
      createJsonResponse(expectedResponse),
    );

    const result = await runResearchFollowUp(
      RESEARCH_ID,
      {
        question: "  What about its limitations?  ",
        limit: 3,
      },
    );

    expect(result).toEqual(expectedResponse);

    expect(fetch).toHaveBeenCalledWith(
      (
        "http://localhost:8000/api/v1/research/" +
        `${RESEARCH_ID}/follow-up`
      ),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-Client-ID": expect.stringMatching(
            CLIENT_ID_PATTERN,
          ),
        }),
        body: JSON.stringify({
          question: "What about its limitations?",
          limit: 3,
        }),
        signal: expect.any(AbortSignal),
      }),
    );
  });

  test("loads paginated research history", async () => {
    const expectedResponse = {
      total: 0,
      limit: 10,
      offset: 20,
      sessions: [],
    };

    fetch.mockResolvedValueOnce(
      createJsonResponse(expectedResponse),
    );

    const result = await getResearchHistory({
      limit: 10,
      offset: 20,
    });

    expect(result).toEqual(expectedResponse);

    expect(fetch).toHaveBeenCalledWith(
      (
        "http://localhost:8000/api/v1/research/" +
        "history?limit=10&offset=20"
      ),
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({
          Accept: "application/json",
          "X-Client-ID": expect.stringMatching(
            CLIENT_ID_PATTERN,
          ),
        }),
        signal: expect.any(AbortSignal),
      }),
    );
  });

  test("loads the latest saved research turn", async () => {
    const expectedResponse = {
      research_id: RESEARCH_ID,
      total_turns: 3,
      has_more_turns: true,
      next_before_turn_index: 3,
      turns: [
        {
          turn_index: 3,
        },
      ],
    };

    fetch.mockResolvedValueOnce(
      createJsonResponse(expectedResponse),
    );

    const result = await getResearchSession(
      RESEARCH_ID,
    );

    expect(result).toEqual(expectedResponse);

    expect(fetch).toHaveBeenCalledWith(
      (
        "http://localhost:8000/api/v1/research/" +
        `${RESEARCH_ID}?turn_limit=1`
      ),
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({
          Accept: "application/json",
          "X-Client-ID": expect.stringMatching(
            CLIENT_ID_PATTERN,
          ),
        }),
        signal: expect.any(AbortSignal),
      }),
    );
  });

  test("loads previous research turns turns", async () => {
    const expectedResponse = {
      research_id: RESEARCH_ID,
      total_turns: 5,
      has_more_turns: true,
      next_before_turn_index: 2,
      turns: [
        {
          turn_index: 2,
        },
        {
          turn_index: 3,
        },
        {
          turn_index: 4,
        },
      ],
    };

    fetch.mockResolvedValueOnce(
      createJsonResponse(expectedResponse),
    );

    const result = await getResearchSession(
      RESEARCH_ID,
      {
        turnLimit: 3,
        beforeTurnIndex: 5,
      },
    );

    expect(result).toEqual(expectedResponse);

    expect(fetch).toHaveBeenCalledWith(
      (
        "http://localhost:8000/api/v1/research/" +
        `${RESEARCH_ID}?turn_limit=3&before_turn_index=5`
      ),
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({
          Accept: "application/json",
          "X-Client-ID": expect.stringMatching(
            CLIENT_ID_PATTERN,
          ),
        }),
        signal: expect.any(AbortSignal),
      }),
    );
  });

  test("deletes a saved research session", async () => {
    const expectedResponse = {
      research_id: RESEARCH_ID,
      message: "Research session deleted successfully.",
    };

    fetch.mockResolvedValueOnce(
      createJsonResponse(expectedResponse),
    );

    const result = await deleteResearchSession(
      RESEARCH_ID,
    );

    expect(result).toEqual(expectedResponse);

    expect(fetch).toHaveBeenCalledWith(
      (
        "http://localhost:8000/api/v1/research/" +
        RESEARCH_ID
      ),
      expect.objectContaining({
        method: "DELETE",
        headers: expect.objectContaining({
          Accept: "application/json",
          "X-Client-ID": expect.stringMatching(
            CLIENT_ID_PATTERN,
          ),
        }),
        signal: expect.any(AbortSignal),
      }),
    );
  });
});
