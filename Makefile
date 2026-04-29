BUNDLE_VERSION ?= $(shell cat VERSION 2>/dev/null || echo 1.0.0)
PUBLIC_VERSION ?= $(shell cat PUBLIC_VERSION 2>/dev/null || echo 1.0.0)

.PHONY: bundle public-docs release-kit clean

bundle:
	./packaging/build-menu-bundle.sh $(BUNDLE_VERSION)

public-docs:
	./packaging/build-public-docs.sh $(PUBLIC_VERSION)

release-kit: bundle public-docs

clean:
	rm -rf dist
