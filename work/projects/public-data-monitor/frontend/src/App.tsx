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
  const [runs, setRuns] = useState<SourceRun[]>([]);
  const [identities, setIdentities] = useState<IdentityDecision[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("loading");

  useEffect(() => {
    let active = true;

    Promise.all([
      fetch("/api/health").then((response) => response.json()),
      fetch("/api/ops/source-runs?limit=12").then((response) => response.json()),
      fetch("/api/identity/decisions?limit=8").then((response) => response.json()),
    ])
      .then(([healthPayload, runPayload, identityPayload]) => {
        if (!active) return;
        setHealth(healthPayload.status ?? "unknown");
        setRuns(runPayload);
        setIdentities(identityPayload);
        setLoadState("ready");
      })
      .catch(() => {
        if (!active) return;
        setHealth("unreachable");
        setLoadState("error");
      });

    return () => {
      active = false;
    };
  }, []);

  const failedRuns = useMemo(
    () => runs.filter((run) => run.status === "failed").length,
    [runs],
  );
  const matchedIdentities = useMemo(
    () => identities.filter((decision) => decision.matched).length,
    [identities],
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

      <section className="stats" aria-label="Platform summary">
        <article className="stat">
          <span>Runtime</span>
          <strong>{loadState === "ready" ? "Connected" : loadState}</strong>
          <small>FastAPI via Nginx</small>
        </article>
        <article className="stat">
          <span>Recent source runs</span>
          <strong>{runs.length}</strong>
          <small>Persisted operational evidence</small>
        </article>
        <article className="stat">
          <span>Recent failures</span>
          <strong>{failedRuns}</strong>
          <small>Explicit, queryable failure state</small>
        </article>
        <article className="stat">
          <span>Identity matches</span>
          <strong>{matchedIdentities}</strong>
          <small>Evidence-backed cross-system links</small>
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
            {runs.length === 0 ? (
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
            {identities.length === 0 ? (
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
