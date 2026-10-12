/** Vérifie le tri, les filtres et l'accès clavier au rapport HTML. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { chromium } = require(process.argv[2] || "playwright");

async function main() {
  // Le navigateur sans interface utilise uniquement des données synthétiques.
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    let html = fs.readFileSync(path.join(__dirname, "../assets/metadata_report.html"), "utf8");
    const rows = [
      ["KEY2", "Alpha", "DOI", "", "10.2/a", "proposition", "Motif B", "https://example.org/b"],
      ["KEY10", "Beta", "language", "", "fr", "manquant", "Motif A", "https://example.org/a"],
      ["KEY1", "Gamma", "volume", "", "2", "proposition", "Motif C", "https://example.org/c"],
    ];
    const escape = value => value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll('"', "&quot;");
    const rendered = rows.map(row => "<tr>" + row.map((cell, index) =>
      "<td>" + (index === 7 ? '<a href="' + escape(cell) + '">Source</a>' : escape(cell)) + "</td>"
    ).join("") + "</tr>").join("");
    const replacements = { rows: rendered, missing: "{}", article_count: "3", other_count: "0", application_summary: "Données synthétiques." };
    html = html.replace(/\{\{(\w+)\}\}/g, (_, key) => replacements[key]);
    await page.setContent(html);
    assert.equal(await page.locator("thead button").count(), 8);
    for (let column = 0; column < 8; column++) {
      const header = page.locator("thead th").nth(column);
      await header.locator("button").click();
      assert.equal(await header.getAttribute("aria-sort"), "ascending");
      const values = await page.locator("tbody tr").evaluateAll((elements, index) =>
        elements.map(row => index === 7 ? row.cells[index].querySelector("a").getAttribute("href") : row.cells[index].textContent), column);
      const collator = new Intl.Collator("fr", { numeric: true, sensitivity: "base" });
      assert.deepEqual(values, [...values].sort(collator.compare));
      await header.locator("button").click();
      assert.equal(await header.getAttribute("aria-sort"), "descending");
      const reversed = await page.locator("tbody tr").evaluateAll((elements, index) =>
        elements.map(row => index === 7 ? row.cells[index].querySelector("a").getAttribute("href") : row.cells[index].textContent), column);
      assert.deepEqual(reversed, [...values].sort((a, b) => collator.compare(b, a)));
    }
    await page.locator("#search").fill("Beta");
    assert.equal(await page.locator("tbody tr:visible").count(), 1);
    await page.locator("#status").selectOption({ label: "proposition" });
    assert.equal(await page.locator("tbody tr:visible").count(), 0);
    await page.locator("#search").fill("");
    assert.equal(await page.locator("tbody tr:visible").count(), 2);
    await page.locator("thead button").first().focus();
    await page.keyboard.press("Enter");
    assert.equal(await page.locator("tbody tr:visible").count(), 2);
    assert.equal(await page.locator("tbody a").first().getAttribute("href") !== null, true);
    assert.deepEqual(errors, []);
    console.log("Metadata report: all eight sorts, filters and keyboard activation passed.");
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
