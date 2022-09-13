

################################
### Format files
.PHONY: fmt
fmt:
	prettier --write .

.PHONY: test/fmt
test/fmt:
	prettier --check .