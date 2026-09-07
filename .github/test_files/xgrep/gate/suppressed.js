// Fixture: the same error-level finding as blocking.js, suppressed inline. The
// gate must not fail on it -- that is the escape hatch a triaged false positive
// relies on.
//
// A bare `nogrep` rather than a rule-specific one, on purpose: the action installs
// xgrep `latest`, so the set of rules that fire on any given line grows over time.
// Naming one rule here made this fixture report two findings the day a second rule
// started matching, one of them unsuppressed, and the test failed for a reason that
// had nothing to do with what it was checking.
const jwt = require("jsonwebtoken");
// test fixture, never a real key nogrep
const token = jwt.sign({ id: 1 }, "hardcoded-signing-key");
module.exports = { token };
