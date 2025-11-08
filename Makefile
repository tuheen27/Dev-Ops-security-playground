.PHONY: build push run test clean help docker

# Version
VERSION ?= latest
IMAGE_NAME ?= security-playground
REGISTRY ?= sysdiglabs

help:
	@echo "Security Playground Makefile"
	@echo "Usage:"
	@echo "  make build        - Build Docker image"
	@echo "  make push         - Push Docker image to registry"
	@echo "  make run          - Run Docker container locally"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean up containers and images"
	@echo "  make docker       - Build and push (CI/CD)"

build:
	@echo "Building $(IMAGE_NAME):$(VERSION)..."
	docker build -t $(IMAGE_NAME):$(VERSION) .
	docker build -t $(IMAGE_NAME):latest .
	@echo "Build complete!"

push:
	@echo "Pushing $(REGISTRY)/$(IMAGE_NAME):$(VERSION)..."
	docker tag $(IMAGE_NAME):$(VERSION) $(REGISTRY)/$(IMAGE_NAME):$(VERSION)
	docker tag $(IMAGE_NAME):latest $(REGISTRY)/$(IMAGE_NAME):latest
	docker push $(REGISTRY)/$(IMAGE_NAME):$(VERSION)
	docker push $(REGISTRY)/$(IMAGE_NAME):latest
	@echo "Push complete!"

run:
	@echo "Running $(IMAGE_NAME):$(VERSION)..."
	docker run --rm -p 8080:8080 $(IMAGE_NAME):$(VERSION)

test:
	@echo "Testing endpoints..."
	@sleep 2
	@curl -s http://localhost:8080/health || echo "Health check failed"
	@curl -s http://localhost:8080/etc/hostname | head -c 50 || echo "File read failed"
	@echo "\nTests complete!"

clean:
	@echo "Cleaning up..."
	docker rm -f $$(docker ps -aq --filter ancestor=$(IMAGE_NAME)) 2>/dev/null || true
	docker rmi -f $(IMAGE_NAME):latest $(IMAGE_NAME):$(VERSION) 2>/dev/null || true
	@echo "Cleanup complete!"

docker: build push
