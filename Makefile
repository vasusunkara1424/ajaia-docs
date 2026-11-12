.PHONY: install backend frontend test build serve

install:            ## Install backend and frontend dependencies
	cd backend && python -m pip install -r requirements-dev.txt
	cd frontend && npm install

backend:            ## Run the API with auto-reload on :8000
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:           ## Run the Vite dev server on :5173 (proxies /api to :8000)
	cd frontend && npm run dev

test:               ## Run backend tests
	cd backend && python -m pytest

build:              ## Type-check and build the frontend into frontend/dist
	cd frontend && npm run build

serve: build        ## Production-style: one server on :8000 serving API + UI
	cd backend && ENVIRONMENT=production uvicorn app.main:app --port 8000
