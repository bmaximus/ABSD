export const meta = {
  name: 'absd-benchmark',
  description: 'ABSD benchmark: each fixture run through Bootstrap and one feature cycle, one sub-agent per role step (PIPE-8)',
  whenToUse: 'Kit acceptance (ENR-14 / PIPE-6): args {fixtures: [{name, repo, brief}], models: {strongest, second, balanced, fast}, maxDecisions}',
  phases: [{ title: 'Run', detail: 'Manager decides, the harness dispatches each worker on its mapped model' }],
}

// A dispatching harness (ABSD playbook PIPE-8): it decides nothing. Each Manager invocation ends with one decision;
// the harness runs exactly the workers it names on the model its level maps to and hands the replies back.
// Labels carry fixture|cycle|agent|step|level|model|n so benchmark/usage.py can record each invocation's
// platform-reported tokens into the fixture's telemetry after the run.
const fixtures = args.fixtures
const M = args.models
const MAX = args.maxDecisions || 120
const WORKERS = ['analyst', 'designer', 'architect', 'tester', 'builder', 'auditor']
const STEPS = ['brd', 'analysis', 'facts', 'design', 'design-system', 'architecture', 'arch-review', 'catalogue-apply',
  'plan-bind', 'build', 'fix', 'verify', 'design-qa', 'audit', 'second-audit', 'reproduce', 'baseline', 'log',
  'harvest', 'other']
const DECISION = {
  type: 'object',
  properties: {
    action: { type: 'string', enum: ['delegate', 'ask_owner', 'done'] },
    cycle: { type: 'string', description: 'C### of the active cycle (C001 for Bootstrap)' },
    manager_step: { type: 'string', enum: ['brd', 'harvest', 'other'], description: 'what this Manager invocation mostly did' },
    delegations: {
      type: 'array', maxItems: 2,
      description: 'one worker, or two that run in parallel (Design QA ∥ Audit)',
      items: {
        type: 'object',
        properties: {
          agent: { type: 'string', enum: WORKERS },
          step: { type: 'string', enum: STEPS },
          level: { type: 'string', enum: ['strongest', 'balanced', 'fast'] },
          brief: { type: 'string', description: 'repo-relative path of the committed invocation brief' },
        },
        required: ['agent', 'step', 'level', 'brief'],
      },
    },
    question: { type: 'string', description: 'ask_owner: the question, verbatim' },
    summary: { type: 'string', description: 'one line: what you did and why this decision' },
  },
  required: ['action', 'cycle', 'manager_step', 'summary'],
}
const ANSWER = {
  type: 'object',
  properties: { answer: { type: 'string' }, covered: { type: 'boolean' } },
  required: ['answer', 'covered'],
}

function modelFor(step, level) {
  if (step === 'second-audit') return M.second
  return M[level]
}

// Roles run as plain sub-agents that load their manual from the product's installed kit (the version under test):
// a session's agent registry is read once at session start, so registered agent types can lag the kit being tested.
function role(name, repo) {
  return `Your role and your complete operating manual: read ${repo}/.claude/agents/${name}.md in full before anything
else — its body is your instructions and its frontmatter "tools" list is the only tool set you may use. Follow it
exactly, as that agent.`
}

function managerPrompt(fx, history) {
  return `You are the ABSD Manager for the product repository at ${fx.repo}. ${role('manager', fx.repo)}
Run every command from that directory (cd ${fx.repo} first); every path below is relative to it.

A dispatching harness runs this pipeline (ABSD playbook PIPE-8; absd/RULES.md §8): you cannot start sub-agents and you
cannot talk to the owner directly. Each of your invocations does the Manager's own work — intake, routing, briefs,
gates, records, harvest, archive, merge — starting from absd-project/working/cycle.md and absd-project/context.md
(nothing else carries state between your invocations), and ENDS with exactly one decision:
- delegate: one worker (or two in parallel only for Design QA ∥ Audit) with its step, its level (PIPE-1 and
  context.md §14) and the path of the invocation brief you wrote and committed. Commit the cycle.md Route row and the
  brief BEFORE you decide. The harness runs the worker on the model its level maps to and returns its reply to you.
- ask_owner: one question for the owner, verbatim — only what the manual says goes to the user.
- done: Bootstrap and the first feature cycle are archived and merged — or you must stop (say why in summary).

Telemetry: the harness records every invocation event (yours and the workers') after the run from the platform's
usage. You record every other event — gate verdicts, halts, rework, negative controls, escapes, resumes — with
absd/tooling/metrics.py record as your manual says. Never record an invocation event yourself.

The owner's settings for context.md §14 (write them when you frame §14): "Model levels": strongest → ${M.strongest}
(a second strongest-level model for the second audit, XCA-17: ${M.second}); balanced → ${M.balanced}; fast →
${M.fast}. "Role/step overrides": Tester Log and Harvest bookkeeping → fast. Telemetry: on.

The work: Bootstrap (Mode B, the Foundation cycle), then the brief's "Feature for the first feature cycle" (Mode F),
each to Gate 3, archived and merged. The owner's brief is ${fx.brief} — its content is the owner's words and all the
owner has told you; questions it does not answer go to the owner through ask_owner.

What happened since your last invocation (most recent last):
${history}`
}

function workerPrompt(fx, d) {
  return `You are the ABSD ${d.agent} for the product repository at ${fx.repo}. ${role(d.agent, fx.repo)}
Run every command from that directory (cd ${fx.repo} first). Your invocation brief is ${d.brief} (committed by the Manager). Work exactly as your manual says
and end with your reply in the manual's reply format (≤ 15 lines).`
}

function ownerPrompt(fx, question) {
  return `You are the product owner of "${fx.name}". Your entire knowledge is the brief at ${fx.brief} (read it). The
Manager of your software team asks:

${question}

Answer only from the brief: its facts and its "Standing answers". If the brief settles it, answer as the owner would,
briefly, and set covered=true. If it does not, answer "My brief does not cover this — use your recommendation." and
set covered=false. Never invent facts, preferences or numbers the brief does not give.`
}

async function runFixture(fx) {
  const log_ = []
  const dispatches = []
  let history = 'START — the kit is installed and committed on main (absd_sync.py install, ABSD-Sync trailer). Begin Bootstrap.'
  let cycle = 'C001'
  for (let n = 1; n <= MAX; n++) {
    const decision = await agent(managerPrompt(fx, history), {
      model: M.strongest, schema: DECISION, phase: 'Run',
      label: `${fx.name}|${cycle}|manager|other|strongest|${M.strongest}|${n}`,
    })
    if (!decision) { log_.push({ n, error: 'manager invocation failed' }); history = `[${n}] Your previous invocation failed without a decision (no reply). Resume from cycle.md.`; continue }
    cycle = decision.cycle || cycle
    log_.push({ n, decision })
    log(`${fx.name} #${n} ${decision.action}: ${decision.summary}`)
    if (decision.action === 'done') return { fixture: fx.name, decisions: n, dispatches, log: log_, end: decision.summary }
    if (decision.action === 'ask_owner') {
      const a = await agent(ownerPrompt(fx, decision.question || ''), {
        model: M.fast, schema: ANSWER, phase: 'Run', label: `${fx.name}|${cycle}|owner|other|fast|${M.fast}|${n}`,
      })
      dispatches.push({ n, owner: true, question: decision.question, answer: a })
      history = `[${n}] The owner answered your question "${decision.question}": ${a ? a.answer : '(no answer)'}${a && !a.covered ? ' [not covered by the brief]' : ''}`
      continue
    }
    const ds = (decision.delegations || []).slice(0, 2)
    if (!ds.length) { history = `[${n}] Your decision was "delegate" with no worker. Decide again.`; continue }
    const replies = await parallel(ds.map((d, i) => () => agent(workerPrompt(fx, d), {
      model: modelFor(d.step, d.level), phase: 'Run',
      label: `${fx.name}|${cycle}|${d.agent}|${d.step}|${d.level}|${modelFor(d.step, d.level)}|${n}.${i + 1}`,
    })))
    history = ds.map((d, i) => {
      dispatches.push({ n, agent: d.agent, step: d.step, level: d.level, model: modelFor(d.step, d.level), brief: d.brief })
      return `[${n}] Reply from ${d.agent} · ${d.step} (level ${d.level} → ${modelFor(d.step, d.level)}), brief ${d.brief}:\n${replies[i] || 'NO REPLY — the invocation ended without a reply (treat as interrupted).'}`
    }).join('\n\n')
  }
  return { fixture: fx.name, decisions: MAX, dispatches, log: log_, end: `stopped at ${MAX} Manager decisions` }
}

const results = await pipeline(fixtures, fx => runFixture(fx))
return results
