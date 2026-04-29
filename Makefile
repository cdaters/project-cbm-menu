BUNDLE_VERSION ?= $(shell cat VERSION 2>/dev/null || echo 1.0.0)

.PHONY: bundle clean

bundle:
	./packaging/build-menu-bundle.sh $(BUNDLE_VERSION)

clean:
	rm -rf dist
