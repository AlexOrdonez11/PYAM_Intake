const fs = require("node:fs");
const path = require("node:path");

const publicDir = path.join(__dirname, "..", "public");
const apiBaseUrl = process.env.PYAM_API_BASE_URL || "";

fs.writeFileSync(
  path.join(publicDir, "config.js"),
  `window.PYAM_API_BASE_URL = ${JSON.stringify(apiBaseUrl)};\n`,
  "utf8"
);
