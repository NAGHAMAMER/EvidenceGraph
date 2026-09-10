# EvidenceGraph Frontend

Interactive multilingual web interface for the EvidenceGraph scientific research agent.

Users can ask a scientific question in any language and receive an evidence-based answer containing scientific papers, web sources, evidence claims, and research limitations.

## Features

* Accepts scientific questions in multiple languages.
* Returns the final answer in the user’s language.
* Automatically supports RTL and LTR text directions.
* Displays scientific papers from OpenAlex and Crossref.
* Displays general web sources retrieved using Tavily.
* Shows semantic relevance scores.
* Links evidence claims to source identifiers such as `P1` and `W1`.
* Distinguishes supporting, contradicting, mixed, and uncertain evidence.
* Provides expandable paper abstracts and web source content.
* Provides direct links to original scientific and web sources.
* Displays an animated research workflow while processing.
* Includes responsive layouts for desktop and mobile screens.
* Uses interactive transitions and animations.
* Handles validation, connection, gateway, and timeout errors.
* Supports reduced-motion accessibility preferences.

## Technology Stack

```text
React 19
Vite 8
Material UI
Framer Motion
Vitest
React Testing Library
jsdom
```

## Requirements

* Node.js 24 or another compatible modern version.
* npm.
* EvidenceGraph Backend running locally on port `8000`.

## Installation

Open a terminal inside the frontend directory:

```powershell
cd frontend
npm install
```

## Environment Configuration

The frontend uses this Backend address by default:

```text
http://localhost:8000/api/v1
```

The address can be configured using:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Create a local `.env` file only when a different Backend address is required.

## Development

Start the development server:

```powershell
npm run dev
```

Open the interface at:

```text
http://localhost:5173
```

## Production Build

Create an optimized production build:

```powershell
npm run build
```

Production files are generated inside:

```text
dist/
```

Preview the production build:

```powershell
npm run preview
```

## Available Scripts

```text
npm run dev         Start the Vite development server
npm run build       Create the production build
npm run preview     Preview the production build
npm run lint        Check frontend code quality
npm test            Run all frontend tests once
npm run test:watch  Run tests in watch mode
```

## Main Project Structure

```text
frontend/
├── public/
│   └── evidence-network.png
├── src/
│   ├── components/
│   │   ├── EvidenceList.jsx
│   │   ├── HeroVisual.jsx
│   │   ├── PaperList.jsx
│   │   ├── ResearchForm.jsx
│   │   ├── ResearchForm.test.jsx
│   │   ├── ResearchProgress.jsx
│   │   ├── ResearchResults.jsx
│   │   └── WebSourceList.jsx
│   ├── services/
│   │   ├── researchApi.js
│   │   └── researchApi.test.js
│   ├── test/
│   │   └── setup.js
│   ├── utils/
│   │   ├── language.js
│   │   └── language.test.js
│   ├── App.jsx
│   ├── index.css
│   ├── main.jsx
│   └── theme.js
├── .env.example
├── index.html
├── package.json
├── vite.config.js
└── vitest.config.js
```

## Research Workflow

```text
User question
    ↓
ResearchForm
    ↓
researchApi
    ↓
FastAPI Research Agent
    ↓
LangGraph workflow
    ↓
Gemini + OpenAlex + Crossref + Tavily
    ↓
ResearchAgentResponse
    ↓
Answer + Evidence + Papers + Web Sources
```

## API Integration

The frontend sends a request to:

```text
POST /api/v1/research
```

Example request:

```json
{
  "question": "What does current research say about semantic search?",
  "limit": 5
}
```

The response contains:

* Original question.
* Detected language and language code.
* Optimized English research query.
* Synthesized answer.
* Evidence claims.
* Research limitations.
* Scientific papers.
* Web sources.
* Partial service errors.

## Result Sections

The result interface contains four tabs:

### Answer

Displays the synthesized answer, detected language, optimized English query, limitations, and partial errors.

### Evidence

Displays short evidence claims generated from the retrieved sources.

Each claim includes:

```text
claim
stance
source_ids
```

Possible evidence stances:

```text
supports
contradicts
mixed
uncertain
```

### Papers

Displays scientific paper metadata, authors, publication information, DOI, citation count, open-access state, semantic score, abstract, and original link.

### Web

Displays the web source title, domain, relevance score, content preview, and original URL.

## Source Traceability

Scientific papers use identifiers such as:

```text
P1
P2
P3
```

Web sources use identifiers such as:

```text
W1
W2
W3
```

Selecting a source identifier from an evidence claim opens the correct result tab and scrolls to the linked source.

## Multilingual Support

The final answer is displayed using the language and direction of the original question.

Arabic, Persian, Hebrew, Urdu, and other RTL languages are displayed from right to left.

Scientific papers and web sources remain in their original languages to preserve source accuracy and traceability.

## Error Handling

The frontend handles:

```text
422  Invalid research request
502  Research agent execution failure
504  External research service timeout
```

The browser-side request timeout is `135` seconds, slightly longer than the Backend LLM timeout of `120` seconds.

## Animations and Accessibility

Framer Motion is used for:

* Page entrance transitions.
* Research form animation.
* Research workflow animation.
* Result card entrance.
* Card hover interactions.
* Hero image movement.
* Result section lazy loading.

Animations are reduced automatically when the user enables the operating system’s reduced-motion preference.

## Tests

Run the frontend tests:

```powershell
npm test
```

Current result:

```text
3 test files passed
10 tests passed
```

The tests cover:

* Arabic RTL detection.
* English LTR detection.
* Regional language codes.
* Successful Research API responses.
* Backend timeout messages.
* Connection failures.
* Form submission.
* Question trimming.
* Arabic example selection.
* Loading-state behavior.

## Code Quality

Run the linter:

```powershell
npm run lint
```

Expected result:

```text
0 warnings
0 errors
```

## Running the Complete Application

From the project root, start the Backend:

```powershell
docker compose up -d api
```

Then start the Frontend:

```powershell
cd frontend
npm run dev
```

Application URLs:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
Swagger:  http://localhost:8000/docs
```

## Repository

[EvidenceGraph on GitHub](https://github.com/NAGHAMAMER/EvidenceGraph)
