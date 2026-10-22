import { useEffect, useMemo, useState } from "react";

type SourceRun = {
  id: number;
  source: string;
  started_at: string;
  finished_at: string | null;
  status: string;
  items_seen: number;
  error_type: string | null;
};

type LifecycleState = {
  id: number;
  source: string;
  source_id: string;
  canonical_key: string;
  state: string;
  transition: string;
  recorded_at: string;
};

type IdentityDecision = {
  id: number;
  left_key: string;
  right_key: string;
  score: number;
  threshold: number;
  matched: boolean;
  evidence: Array<{ kind: string; value: string; weight: number }>;
};

type LoadState = "loading" | "ready" | "error";

type Health = { status: string };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

const isHealth = (value: unknown): value is Health =>
  isRecord(value) && typeof value.status === "string";

const isSourceRuns = (value: unknown): value is SourceRun[] =>
  Array.isArray(value) && value.every((run) =>
    isRecord(run) &&
    typeof run.id === "number" &&
    typeof run.source === "string" &&
    typeof run.status === "string" &&
    typeof run.items_seen === "number" &&
    (run.finished_at === null || typeof run.finished_at === "string")
  );

const isIdentities = (value: unknown): value is IdentityDecision[] =>
  Array.isArray(value) && value.every((decision) =>
    isRecord(decision) &&
    typeof decision.id === "number" &&
    typeof decision.left_key === "string" &&
    typeof decision.right_key === "string" &&
    typeof decision.score === "number" &&
    typeof decision.threshold === "number" &&
    typeof decision.matched === "boolean" &&
    Array.isArray(decision.evidence) &&
    decision.evidence.every((item: unknown) =>
      isRecord(item) &&
      typeof item.kind === "string" &&
      typeof item.value === "string" &&
      typeof item.weight === "number"
    )
  );

const isLifecycle = (value: unknown): value is LifecycleState[] =>
  Array.isArray(value) && value.every((item) =>
    isRecord(item) &&
    typeof item.id === "number" &&
    typeof item.canonical_key === "string" &&
    typeof item.source === "string" &&
    typeof item.state === "string" &&
    typeof item.transition === "string"
  );

async function readApi<T>(path: string, valid: (value: unknown) => value is T): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) throw new Error("HTTP response unavailable");
  const payload: unknown = await response.json();
  if (!valid(payload)) throw new Error("Invalid API response shape");
  return payload;
}

const time = (value: string | null) => {
  if (!value) return "—";
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(value));
};

function App() {
  const [health, setHealth] = useState("checking");
  const [runs, setRuns] = useState<SourceRun[] | null>(null);
  const [identities, setIdentities] = useState<IdentityDecision[] | null>(null);
  const [lifecycle, setLifecycle] = useState<LifecycleState[] | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [unavailable, setUnavailable] = useState<string[]>([]);

  useEffect(() => {
    let active = true;

    void Promise.allSettled([
      readApi("/api/health", isHealth),
      readApi("/api/ops/source-runs?limit=12", isSourceRuns),
      readApi("/api/identity/decisions?limit=8", isIdentities),
      readApi("/api/lifecycle?limit=12", isLifecycle),
    ]).then(([healthResult, runsResult, identitiesResult, lifecycleResult]) => {
      if (!active) return;
      setHealth(healthResult.status === "fulfilled" ? healthResult.value.status : "unreachable");
      setRuns(runsResult.status === "fulfilled" ? runsResult.value : null);
      setIdentities(identitiesResult.status === "fulfilled" ? identitiesResult.value : null);
      setLifecycle(lifecycleResult.status === "fulfilled" ? lifecycleResult.value : null);
      setUnavailable([
        ...(healthResult.status === "rejected" ? ["API health"] : []),
        ...(runsResult.status === "rejected" ? ["Source runs"] : []),
        ...(identitiesResult.status === "rejected" ? ["Identity decisions"] : []),
        ...(lifecycleResult.status === "rejected" ? ["Lifecycle"] : []),
      ]);
      const hasRecords = [runsResult, identitiesResult, lifecycleResult]
        .some((result) => result.status === "fulfilled");
      setLoadState(hasRecords ? "ready" : "error");
    });

    return () => {
      active = false;
    };
  }, []);

  const failedRuns = useMemo(
    () => runs === null ? null : runs.filter((run) => run.status === "failed").length,
    [runs],
  );
  const matchedIdentities = useMemo(
    () => identities === null ? null : identities.filter((decision) => decision.matched).length,
    [identities],
  );
  const disappearedIdentities = useMemo(
    () => lifecycle === null ? null : lifecycle.filter((item) => item.state === "disappeared").length,
    [lifecycle],
  );

  return (
    <main className="shell">
      <header className="masthead">
        <div>
          <p className="eyebrow">SYSTEM STATE / LIVE EVIDENCE</p>
          <h1>Multi-Source State &amp; Reconciliation</h1>
          <p className="lede">
            Acquisition, identity, provenance, history, and operations on one
            inspectable surface.
          </p>
        </div>
        <div className={"health " + (health === "ok" ? "health-ok" : "health-warn")}>
          <span className="pulse" />
          API {health}
        </div>
      </header>

      {unavailable.length > 0 && (
        <p className="empty" role="status">
          Unavailable: {unavailable.join(", ")}. Missing evidence is not zero.
        </p>
      )}

      <section className="stats" aria-label="Platform summary">
        <article className="stat">
          <span>Runtime</span>
          <strong>{loadState === "ready" ? "Connected" : loadState}</strong>
          <small>FastAPI via Nginx</small>
        </article>
        <article className="stat">
          <span>Recent source runs</span>
          <strong>{runs === null ? "—" : runs.length}</strong>
          <small>Persisted operational evidence</small>
        </article>
        <article className="stat">
          <span>Recent failures</span>
          <strong>{failedRuns === null ? "—" : failedRuns}</strong>
          <small>Explicit, queryable failure state</small>
        </article>
        <article className="stat">
          <span>Identity matches</span>
          <strong>{matchedIdentities === null ? "—" : matchedIdentities}</strong>
          <small>Evidence-backed cross-system links</small>
        </article>
        <article className="stat">
          <span>Disappeared identities</span>
          <strong>{disappearedIdentities === null ? "—" : disappearedIdentities}</strong>
          <small>Durable lifecycle state</small>
        </article>
      </section>

      <section className="grid">
        <article className="panel panel-wide">
          <div className="panel-heading">
            <div>
              <p className="kicker">OPERATIONS</p>
              <h2>Source runs</h2>
            </div>
            <span className="mono">latest 12</span>
          </div>

          <div className="table" role="table">
            <div className="table-row table-head" role="row">
              <span>Source</span>
              <span>Status</span>
              <span>Items</span>
              <span>Finished</span>
            </div>
            {runs === null ? (
              <div className="empty">Source runs unavailable.</div>
            ) : runs.length === 0 ? (
              <div className="empty">No source-run evidence yet.</div>
            ) : (
              runs.map((run) => (
                <div className="table-row" role="row" key={run.id}>
                  <span className="source-name">{run.source}</span>
                  <span>
                    <b className={"status status-" + run.status}>{run.status}</b>
                  </span>
                  <span className="mono">{run.items_seen}</span>
                  <span className="mono subtle">{time(run.finished_at)}</span>
                </div>
              ))
            )}
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="kicker">IDENTITY</p>
              <h2>Cross-system decisions</h2>
            </div>
          </div>

          <div className="identity-list">
            {identities === null ? (
              <div className="empty">Identity decisions unavailable.</div>
            ) : identities.length === 0 ? (
              <div className="empty">No persisted identity decisions yet.</div>
            ) : (
              identities.map((decision) => (
                <div className="identity-card" key={decision.id}>
                  <div className="identity-top">
                    <span className={decision.matched ? "match" : "review"}>
                      {decision.matched ? "MATCHED" : "UNRESOLVED"}
                    </span>
                    <span className="mono">
                      {decision.score}/{decision.threshold}
                    </span>
                  </div>
                  <strong>{decision.left_key}</strong>
                  <span className="relation">↕ evidence relation ↕</span>
                  <strong>{decision.right_key}</strong>
                  <div className="evidence">
                    {decision.evidence.map((item) => (
                      <span key={item.kind + item.value}>
                        {item.kind} +{item.weight}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </article>
        <article className="panel panel-wide">
          <div className="panel-heading">
            <div>
              <p className="kicker">STATE LIFECYCLE</p>
              <h2>Current identity state</h2>
            </div>
            <span className="mono">latest per source identity</span>
          </div>

          <div className="table" role="table">
            <div className="table-row table-head" role="row">
              <span>Identity</span>
              <span>Source</span>
              <span>State</span>
              <span>Transition</span>
            </div>
            {lifecycle === null ? (
              <div className="empty">Lifecycle unavailable.</div>
            ) : lifecycle.length === 0 ? (
              <div className="empty">No lifecycle evidence yet.</div>
            ) : (
              lifecycle.map((item) => (
                <div className="table-row" role="row" key={item.id}>
                  <span className="source-name">{item.canonical_key}</span>
                  <span className="mono">{item.source}</span>
                  <span>
                    <b className={"status status-" + item.state}>{item.state}</b>
                  </span>
                  <span className="mono subtle">{item.transition}</span>
                </div>
              ))
            )}
          </div>
        </article>
      </section>

      <section className="flow" aria-label="Platform flow">
        {[
          ["01", "Acquire", "API · HTML · external systems"],
          ["02", "Canonicalize", "typed observations + provenance"],
          ["03", "Compare", "change + conflict classification"],
          ["04", "Reconcile", "evidence before selection"],
          ["05", "Operate", "Celery · metrics · history"],
        ].map(([index, title, detail]) => (
          <div className="flow-step" key={index}>
            <span className="mono">{index}</span>
            <strong>{title}</strong>
            <small>{detail}</small>
          </div>
        ))}
      </section>
    </main>
  );
}

export default App;
