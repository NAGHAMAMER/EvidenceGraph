const CLIENT_ID_STORAGE_KEY =
  "evidencegraph.client-id";

let cachedClientId = null;

function isValidUuid(value) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
    value,
  );
}

function createClientId() {
  if (
    globalThis.crypto &&
    typeof globalThis.crypto.randomUUID === "function"
  ) {
    return globalThis.crypto.randomUUID();
  }

  const bytes = new Uint8Array(16);

  if (
    globalThis.crypto &&
    typeof globalThis.crypto.getRandomValues === "function"
  ) {
    globalThis.crypto.getRandomValues(bytes);
  } else {
    for (let index = 0; index < bytes.length; index += 1) {
      bytes[index] = Math.floor(Math.random() * 256);
    }
  }

  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;

  const hexadecimal = Array.from(
    bytes,
    (byte) => byte.toString(16).padStart(2, "0"),
  );

  return [
    hexadecimal.slice(0, 4).join(""),
    hexadecimal.slice(4, 6).join(""),
    hexadecimal.slice(6, 8).join(""),
    hexadecimal.slice(8, 10).join(""),
    hexadecimal.slice(10, 16).join(""),
  ].join("-");
}

export function getClientId() {
  if (cachedClientId) {
    return cachedClientId;
  }

  try {
    const storedClientId = window.localStorage.getItem(
      CLIENT_ID_STORAGE_KEY,
    );

    if (storedClientId && isValidUuid(storedClientId)) {
      cachedClientId = storedClientId;
      return cachedClientId;
    }
  } catch {
    // Continue with an in-memory identity.
  }

  cachedClientId = createClientId();

  try {
    window.localStorage.setItem(
      CLIENT_ID_STORAGE_KEY,
      cachedClientId,
    );
  } catch {
    // The identity still works for the current page session.
  }

  return cachedClientId;
}
