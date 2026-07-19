const fs = require("node:fs");
const path = require("node:path");

const publicDir = path.join(__dirname, "..", "public");
const apiBaseUrl = process.env.PYAM_API_BASE_URL || "";
const appMode = process.env.PYAM_APP_MODE || "unified";

fs.writeFileSync(
  path.join(publicDir, "config.js"),
  `window.PYAM_API_BASE_URL = ${JSON.stringify(apiBaseUrl)};\nwindow.PYAM_APP_MODE = ${JSON.stringify(appMode)};\n`,
  "utf8"
);
