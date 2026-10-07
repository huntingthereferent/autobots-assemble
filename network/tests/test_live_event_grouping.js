// Run: node --test network/tests/test_live_event_grouping.js
const {test} = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.dataset = {}; this.listeners = {}; }
  append(...children) { this.children.push(...children); }
  appendChild(child) { this.append(child); }
  addEventListener(kind, handler) { this.listeners[kind] = handler; }
  replaceChildren(...children) { this.children = children; }
}
const elements = new Map();
const document = {
  createElement: tag => new Element(tag),
  createTextNode: text => Object.assign(new Element("text"), {textContent: text}),
  querySelector: key => {
    if (!elements.has(key)) elements.set(key, new Element("div"));
    return elements.get(key);
  }
};
const preferences = new Map();
const localStorage = {
  getItem: key => preferences.get(key) || null,
  setItem: (key, value) => preferences.set(key, value)
};
const context = vm.createContext({document, URL, console, localStorage});
const app = fs.readFileSync(path.join(__dirname, "../../runtime/http/app.js"), "utf8");
vm.runInContext(app.slice(0, app.indexOf('$("#ohayo").addEventListener')), context);
const group = items => context.groupLiveItems(items);
const title = "City council approves new river bridge construction plan";
function row(source, overrides = {}) {
  return {id: source + ":1", source_id: source, source_name: source,
    title, url: "https://example.org/" + source,
    published_at: "2026-10-06T12:00:00Z", snippet: source + " separate claim",
    roles: ["news"], medium: "article", ...overrides};
}
function walk(el) { return [el, ...el.children.flatMap(walk)]; }

test("four providers share coverage without altering or discarding witnesses", () => {
  const rows = ["BBC", "Reuters", "Reddit", "Hacker News"].map(x => row(x));
  const before = JSON.stringify(rows);
  const groups = group(rows);
  assert.equal(groups.length, 1);
  assert.equal(groups[0].items.length, 4);
  groups[0].items.forEach((item, i) => assert.equal(item, rows[i]));
  assert.equal(JSON.stringify(rows), before);
});

test("shared URL ignores fragment but preserves meaningful query parameters", () => {
  const a = row("BBC", {url: "https://example.org/story?id=1#top"});
  const b = row("HN", {title: "Different claim", url: "https://example.org/story?id=1#comments"});
  assert.equal(group([a, b]).length, 1);
  assert.equal(group([a, {...b, url: "https://example.org/story?id=2"}]).length, 2);
});

test("invalid URLs and homepages do not group differing titles", () => {
  for (const url of ["", "invalid", "javascript:alert(1)", "https://example.org/"]) {
    assert.equal(group([row("a", {url}), row("b", {url, title: "Different"})]).length, 2);
  }
});

test("headline matching tolerates case and whitespace only", () => {
  assert.equal(group([row("a"), row("b", {title: title.toUpperCase().replace(/ /g, "  ")})]).length, 1);
  assert.equal(group([row("a"), row("b", {title: title.replace("approves", "rejects")})]).length, 2);
});

test("short, truncated, missing and paraphrased headlines stay separate", () => {
  for (const headline of ["", "Breaking news", title + "…"]) {
    assert.equal(group([row("a", {title: headline}), row("b", {title: headline})]).length, 2);
  }
  assert.equal(group([row("a"), row("b", {title: "New bridge approved by the city council today"})]).length, 2);
});

test("headline grouping requires valid dates and a bounded whole-group span", () => {
  for (const published_at of ["", "invalid", "2026-10-08T12:00:00Z"]) {
    assert.equal(group([row("a"), row("b", {published_at})]).length, 2);
  }
  assert.equal(group([row("a"), row("b", {published_at: "2026-10-07T12:00:00Z"})]).length, 1);
  assert.equal(group([
    row("a"), row("b", {published_at: "2026-10-07T08:00:00Z"}),
    row("c", {published_at: "2026-10-08T04:00:00Z"})
  ]).length, 2);
});

test("URL/headline bridges cannot transitively merge unrelated witnesses", () => {
  const a = row("a", {url: "https://example.org/story"});
  const b = row("b", {url: a.url, title: title + " update"});
  const c = row("c", {title: b.title});
  assert.equal(group([a, b, c]).length, 2);
});

test("singletons and groups follow first encounter order without dropping repeated IDs", () => {
  const rows = [row("a"), row("x", {title: "Unrelated"}), row("b"), row("a")];
  const groups = group(rows);
  assert.equal(groups.length, 2);
  assert.equal(groups[0].items.length, 3);
  assert.equal(groups[1].items[0], rows[1]);
});

test("rendered group exposes all source names, claims and native click targets", () => {
  const rows = ["BBC", "Reuters", "Reddit", "Hacker News"].map(x => row(x));
  const card = context.liveEventCard(group(rows)[0]);
  const nodes = walk(card);
  assert.equal(card.children.length, 5);
  assert.match(card.children[0].textContent, /matching headline within 24h/);
  const clicks = [];
  context.openLiveItem = item => clicks.push(item);
  for (const row of rows) {
    assert.ok(nodes.some(x => x.textContent === row.source_name));
    assert.ok(nodes.some(x => x.textContent === row.snippet));
  }
  nodes.filter(x => x.className === "live-title-link").forEach(x => x.listeners.click());
  assert.deepEqual(clicks, rows);
});

test("filters operate on witnesses before grouping and refresh replaces ephemeral groups", () => {
  const rows = [row("BBC"), row("Reuters", {medium: "video"}),
    row("Reddit", {roles: ["social", "community"]}), row("HN", {roles: ["community"]})];
  context.rows = rows;
  vm.runInContext('liveFeedState = {items: rows, sources: []}; liveFeedFilter = "video"; renderLiveFeed();', context);
  assert.equal(elements.get("#live-feed").children.length, 1);
  assert.equal(elements.get("#live-feed").children[0].dataset.source, "Reuters");
  vm.runInContext('liveFeedFilter = "balanced"; renderLiveFeed();', context);
  assert.equal(elements.get("#live-feed").children[0].children.length, 5);
  vm.runInContext('liveFeedState = {items: [], sources: []}; renderLiveFeed();', context);
  assert.equal(elements.get("#live-feed").children.length, 0);
  assert.equal(elements.get("#empty-live-feed").hidden, false);
});

test("tickers cover every source and overlapping layers without mutating witnesses", () => {
  const rows = [row("BBC"), row("Reuters", {medium: "video"}), row("Reddit", {roles: ["social", "community"]})];
  const snapshot = {items: rows, sources: [{id: "offline", name: "Offline", ok: false}], fetched_at: "2026-10-07T12:00:00Z"};
  const before = JSON.stringify(snapshot);
  const layers = context.tickerLayers(snapshot);
  assert.equal(layers.filter(x => x.id.startsWith("source:")).length, 4);
  assert.equal(layers.filter(x => x.domain && !x.parentId).length, 9);
  assert.equal(layers.find(x => x.id === "role:news").items.length, 2);
  assert.equal(layers.find(x => x.id === "role:video").items[0], rows[1]);
  assert.equal(layers.find(x => x.id === "source:BBC").items[0], rows[0]);
  assert.equal(layers.find(x => x.id === "all").items, rows);
  assert.equal(JSON.stringify(snapshot), before);
});

test("ticker summary uses date order, preserves unknown dates and distinguishes failure from zero", () => {
  const rows = [row("a", {published_at: "bad"}), row("b", {published_at: "2026-10-06T10:00:00Z"}), row("c")];
  const snapshot = {fetched_at: "2026-10-07T12:00:00Z"};
  const summary = context.tickerSummary({items: rows}, snapshot);
  assert.equal(summary.latest, rows[2]);
  assert.equal(summary.undated, 1);
  assert.equal(summary.fetchedAt, snapshot.fetched_at);
  assert.match(summary.status, /3 witnesses/);
  assert.equal(context.tickerSummary({items: [], source: {ok: false}}, snapshot).status, "Unavailable");
  assert.equal(context.tickerSummary({items: [], source: {ok: true}}, snapshot).status, "No sampled items");
});

test("ticker expansion exposes all witnesses and retains open state on refresh", () => {
  context.rows = [row("BBC"), row("Reuters")];
  vm.runInContext('hiddenTickers.clear(); liveFeedState = {items: rows, sources: []}; renderTickers();', context);
  const all = elements.get("#feed-tickers").children[0];
  assert.equal(walk(all).filter(x => x.className === "live-title-link").length, 2);
  all.open = true;
  vm.runInContext('renderTickers();', context);
  assert.equal(elements.get("#feed-tickers").children[0].open, true);
});

test("ticker choices persist only display identifiers and hide all includes future providers", () => {
  vm.runInContext('hiddenTickers = new Set(["*"]); saveTickerChoices(); renderTickers();', context);
  assert.equal(elements.get("#feed-tickers").hidden, true);
  assert.deepEqual([...context.readHiddenTickers()], ["*"]);
  assert.equal([...preferences.values()][0], '["*"]');
  context.rows = [row("new-provider")];
  vm.runInContext('liveFeedState = {items: rows, sources: []}; renderTickers();', context);
  assert.equal(elements.get("#feed-tickers").children.length, 0);
  const firstChoice = elements.get("#ticker-choices").children[0].children[0];
  firstChoice.checked = true;
  firstChoice.listeners.change();
  assert.equal(elements.get("#feed-tickers").children.length, 1);
  assert.equal(elements.get("#feed-tickers").children[0].dataset.ticker, "all");
});

test("broken preferences fall back to all tickers and filtering does not alter total layer sample", () => {
  preferences.set("continuityHiddenTickersV1", "broken");
  assert.equal(context.readHiddenTickers().size, 0);
  context.rows = [row("BBC"), row("Reuters", {medium: "video"})];
  vm.runInContext('hiddenTickers.clear(); liveFeedState = {items: rows, sources: []}; liveFeedFilter = "video"; renderLiveFeed();', context);
  const all = elements.get("#feed-tickers").children[0];
  assert.match(all.children[0].children[1].textContent, /2 witnesses/);
  assert.equal(elements.get("#live-feed").children.length, 1);
});

test("broad categories exist without pretending generic news or provider names are domain evidence", () => {
  const rows = [row("BBC", {title: "Sports stocks factory learning research world household"}),
    row("sports-provider")];
  const layers = context.domainTickerLayers(rows);
  assert.deepEqual(Array.from(layers.filter(x => !x.parentId), x => x.id),
    ["world", "industry", "markets", "sports", "work", "learning", "research", "household", "culture"].map(x => "domain:" + x));
  assert.ok(layers.every(layer => layer.items.length === 0));
  assert.equal(context.tickerSummary(layers[0], {}).status, "No connected witnesses");
});

test("one explicit witness can cross sports, markets and world without inflating parent counts", () => {
  const witness = row("report", {topics: ["sports:results", "sports:teams", "markets:stocks", "world:countries:usa:missouri"]});
  const layers = context.domainTickerLayers([witness]);
  for (const id of ["domain:sports", "domain:sports:results", "domain:markets",
    "domain:world", "domain:world:countries", "domain:world:countries:usa",
    "domain:world:countries:usa:missouri"]) {
    const layer = layers.find(x => x.id === id);
    assert.equal(layer.items.length, 1);
    assert.equal(layer.items[0], witness);
  }
  assert.equal(layers.find(x => x.id === "domain:world:countries:usa:missouri").parentId, "domain:world:countries:usa");
});

test("source nests preserve independent claims and unknown source status", () => {
  const rows = [row("BBC", {topics: ["industry:production"]}),
    row("Reuters", {topics: ["industry:production"], snippet: "Conflicting source claim"})];
  const snapshot = {items: rows, sources: [{id: "BBC", name: "BBC", ok: true}]};
  const layer = context.domainTickerLayers(rows).find(x => x.id === "domain:industry");
  const branches = context.tickerSourceBranches(layer, snapshot);
  assert.equal(branches.length, 2);
  assert.equal(branches[0].items[0], rows[0]);
  assert.equal(branches[1].source, undefined);
  const card = context.tickerCard(layer, snapshot, new Set());
  assert.equal(walk(card).filter(x => x.className === "live-title-link").length, 2);
  assert.ok(walk(card).some(x => x.textContent === rows[1].snippet));
});

test("hiding a parent can promote a chosen child and nested expansion survives refresh", () => {
  context.rows = [row("BBC", {topics: ["sports:results"]})];
  vm.runInContext('hiddenTickers = new Set(tickerLayers({items:rows}).map(x=>x.id)); hiddenTickers.delete("domain:sports:results"); liveFeedState={items:rows,sources:[]}; renderTickers();', context);
  assert.equal(elements.get("#feed-tickers").children.length, 1);
  assert.equal(elements.get("#feed-tickers").children[0].dataset.ticker, "domain:sports:results");
  const root = elements.get("#feed-tickers").children[0];
  const sources = walk(root).find(x => x.className === "ticker-source-nest");
  root.open = sources.open = true;
  vm.runInContext('renderTickers();', context);
  assert.equal(elements.get("#feed-tickers").children[0].open, true);
  assert.equal(walk(elements.get("#feed-tickers")).find(x => x.className === "ticker-source-nest").open, true);
});

test("100 reports conserve witnesses across domain and nested source projections", () => {
  const rows = Array.from({length:100}, (_,i)=>row("source"+i%4,
    {id:String(i), topics:["research:experiments", "research:findings", "work:projects"]}));
  const before = JSON.stringify(rows);
  const layers = context.domainTickerLayers(rows);
  for (const id of ["domain:research", "domain:work"]) {
    const layer = layers.find(x => x.id === id);
    assert.equal(layer.items.length, 100);
    const nested = context.tickerSourceBranches(layer, {}).flatMap(x => x.items);
    assert.equal(nested.length, 100);
    assert.deepEqual(new Set(nested), new Set(rows));
  }
  assert.equal(JSON.stringify(rows), before);
});

test("configured unavailable sources remain nested in their empty domain", () => {
  const snapshot = {items: [], sources: [{id:"sec", name:"SEC", topics:["markets"], ok:false, error:"Timeout"}]};
  const layer = context.tickerLayers(snapshot).find(x => x.id === "domain:markets");
  assert.equal(context.tickerSummary(layer, snapshot).status, "Sources unavailable");
  const branches = context.tickerSourceBranches(layer, snapshot);
  assert.equal(branches.length, 1);
  assert.equal(branches[0].source, snapshot.sources[0]);
  const card = context.tickerCard(layer, snapshot, new Set());
  assert.ok(walk(card).some(x => x.textContent === "SEC"));
  assert.ok(walk(card).some(x => x.textContent === "Timeout"));
  snapshot.sources[0].ok = true;
  assert.equal(context.tickerSummary(layer, snapshot).status, "No sampled items");
});

test("publisher-feed scope remains visible on the native witness card", () => {
  const card = context.liveFeedCard(row("BBC", {topics:["learning"],
    topic_basis:{kind:"publisher_feed_scope", feed_url:"https://example.org/education.xml"}}));
  assert.ok(walk(card).some(x => (x.textContent || "").includes("Coverage: learning · publisher feed scope")));
});


test("country branches survive unavailable publishers and conserve overlapping witnesses", () => {
  const sources = [{id: "ca_labour", name: "Statistics Canada", ok: false,
    topics: ["work", "world:countries:canada"]}];
  const empty = context.domainTickerLayers([], sources);
  const country = empty.find(x => x.id === "domain:world:countries:canada");
  assert.ok(country);
  assert.equal(context.tickerSummary(country, {}).status, "Sources unavailable");
  assert.equal(context.tickerSourceBranches(country, {sources}).length, 1);
  const witness = row("ca_labour", {topics: sources[0].topics, country: "Canada",
    country_basis: "publisher_jurisdiction", language: "en", topic_basis: {kind:"publisher_feed_scope"}});
  const layers = context.domainTickerLayers([witness], sources);
  for (const id of ["domain:work", "domain:world", "domain:world:countries:canada"]) {
    assert.equal(layers.find(x => x.id === id).items[0], witness);
  }
  assert.ok(walk(context.liveFeedCard(witness)).some(x => (x.textContent || "").includes("Source jurisdiction: Canada")));
});
