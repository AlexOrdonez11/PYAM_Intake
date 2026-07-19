const frontendBaseUrl = process.env.FRONTEND_BASE_URL || "http://127.0.0.1:5178";
const apiBaseUrl = process.env.PYAM_API_BASE_URL || "http://127.0.0.1:5177";

const routes = ["/login", "/start", "/intake", "/submissions", "/submissions/example-submission-id", "/templates", "/staff"];

async function checkUrl(url, predicate, label) {
  const response = await fetch(url);
  const text = await response.text();
  if (!response.ok || !predicate(text, response)) {
    throw new Error(`${label} failed (${response.status}) at ${url}`);
  }
  return { url, status: response.status };
}

const results = [];

for (const route of routes) {
  results.push(
    await checkUrl(
      `${frontendBaseUrl}${route}`,
      (text) => text.includes("<div id=\"root\"></div>") || text.includes("/assets/"),
      `Frontend route ${route}`
    )
  );
}

results.push(
  await checkUrl(
    `${apiBaseUrl}/api/health`,
    (text) => {
      try {
        return JSON.parse(text).ok === true;
      } catch {
        return false;
      }
    },
    "API health"
  )
);

console.log(JSON.stringify({ ok: true, checked: results }, null, 2));
