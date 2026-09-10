const RTL_LANGUAGE_CODES = new Set([
  "ar",
  "fa",
  "he",
  "ur",
  "ps",
  "sd",
  "ug",
  "yi",
  "dv",
  "ku",
]);

const RTL_CHARACTERS =
  /[\u0590-\u08ff\ufb1d-\ufdff\ufe70-\ufefc]/;

export function getTextDirection(
  languageCode = "",
  text = "",
) {
  const primaryCode = languageCode
    .trim()
    .toLowerCase()
    .split("-")[0];

  if (RTL_LANGUAGE_CODES.has(primaryCode)) {
    return "rtl";
  }

  return RTL_CHARACTERS.test(text) ? "rtl" : "ltr";
}