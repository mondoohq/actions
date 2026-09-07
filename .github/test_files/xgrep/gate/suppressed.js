// Fixture: the same error-level finding, suppressed inline. The gate must NOT
// fail on it -- that is the escape hatch a triaged false positive relies on.
const jwt = require("jsonwebtoken");
// test fixture, never a real key nogrep: javascript-hardcoded-credentials
const token = jwt.sign({ id: 1 }, "hardcoded-signing-key");
module.exports = { token };
