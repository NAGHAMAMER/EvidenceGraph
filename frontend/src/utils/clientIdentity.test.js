const STORAGE_KEY = "evidencegraph.client-id";

const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

describe("client identity", () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.resetModules();
  });

  test("creates and stores a valid client identifier", async () => {
    const { getClientId } = await import(
      "./clientIdentity"
    );

    const clientId = getClientId();

    expect(clientId).toMatch(UUID_PATTERN);
    expect(
      window.localStorage.getItem(STORAGE_KEY),
    ).toBe(clientId);
  });

  test("returns the same identifier on repeated calls", async () => {
    const { getClientId } = await import(
      "./clientIdentity"
    );

    const firstClientId = getClientId();
    const secondClientId = getClientId();

    expect(secondClientId).toBe(firstClientId);
  });

  test("restores the identifier from local storage", async () => {
    const storedClientId =
      "7ae38d41-86c2-4f47-a315-572187c9bb68";

    window.localStorage.setItem(
      STORAGE_KEY,
      storedClientId,
    );

    const { getClientId } = await import(
      "./clientIdentity"
    );

    expect(getClientId()).toBe(storedClientId);
  });

  test("replaces an invalid stored identifier", async () => {
    window.localStorage.setItem(
      STORAGE_KEY,
      "invalid-client-id",
    );

    const { getClientId } = await import(
      "./clientIdentity"
    );

    const clientId = getClientId();

    expect(clientId).toMatch(UUID_PATTERN);
    expect(clientId).not.toBe("invalid-client-id");
    expect(
      window.localStorage.getItem(STORAGE_KEY),
    ).toBe(clientId);
  });
});
