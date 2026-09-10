import { describe, expect, test } from "vitest";

import { getTextDirection } from "./language";

describe("getTextDirection", () => {
  test("returns rtl for Arabic language", () => {
    expect(getTextDirection("ar")).toBe("rtl");
  });

  test("returns rtl for Arabic text without language code", () => {
    expect(
      getTextDirection("", "ما تأثير الذكاء الاصطناعي؟"),
    ).toBe("rtl");
  });

  test("returns ltr for English language", () => {
    expect(getTextDirection("en")).toBe("ltr");
  });

  test("supports regional language codes", () => {
    expect(getTextDirection("ar-SY")).toBe("rtl");
    expect(getTextDirection("en-US")).toBe("ltr");
  });
});
