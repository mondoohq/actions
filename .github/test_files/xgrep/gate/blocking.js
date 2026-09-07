// Fixture: one error-level finding, not suppressed. The gate must fail on it.
const jwt = require("jsonwebtoken");
const token = jwt.sign({ id: 1 }, "hardcoded-signing-key");
module.exports = { token };
