# TRP 1 - AI-Content Generation Challenge

## Character-First Screening for Forward Deployed Engineers

**Time Limit:** 3 Hours (Time-Boxed)  
**Difficulty:** Intermediate  
**Focus:** Codebase Exploration, Technical Comprehension, Content Generation

---

## Overview

This challenge measures your ability to **explore, understand, and operate** an existing AI content generation codebase. In the 2026 Forward Deployed Engineer (FDE) role, you will rarely build systems from scratch—instead, you will inherit complex codebases, decipher their architecture, and deploy them to solve real-world problems.

**The question we are answering:** Can you explore an unfamiliar codebase, understand its capabilities, configure it correctly, and generate meaningful outputs despite incomplete documentation?

---

## What We're Measuring

| Trait | Definition | How We Measure It |
|-------|------------|-------------------|
| **Curiosity** | Exploratory drive; seeking to understand "why" not just "how" | Evidence of exploring multiple providers, presets, and pipelines beyond minimum requirements |
| **Technical Comprehension** | Ability to understand complex systems and map instructions to execution | Successful environment setup, correct API configuration, and functional content generation |
| **Motivation & Persistence** | Persistence through errors, API failures, and ambiguous instructions | Documented troubleshooting steps, workarounds discovered, and completion despite obstacles |

---

## The Challenge

### Part 1: Environment Setup & API Configuration (30 min)

You are given access to the `ai-content` package—a multi-provider AI content generation framework.

**Your tasks:**

1. **Clone and Install the Package**
   ```bash
   cd ai-content
   uv sync  # or pip install -e .
   ```

2. **Obtain API Keys** (Choose at least ONE provider)
   
   | Provider | Purpose | How to Get |
   |----------|---------|------------|
   | **Google Gemini** | Music (Lyria), Video (Veo), Image (Imagen) | [Google AI Studio](https://aistudio.google.com/) → Get API Key |
   | **AIMLAPI** | Music with Vocals (MiniMax) | [AIMLAPI.com](https://aimlapi.com/) → Sign up → API Keys |

3. **Configure Your Environment**
   
   Create a `.env` file in the project root:
   ```env
   # Google Gemini API (for Lyria music, Veo video, Imagen images)
   GEMINI_API_KEY=your_google_api_key_here
   
   # AIMLAPI (for MiniMax music with vocals)
   AIMLAPI_KEY=your_aimlapi_key_here
   ```

4. **Verify Installation**
   ```bash
   uv run ai-content --help
   uv run ai-content list-providers
   uv run ai-content list-presets
   ```

> **Note:** You do NOT need KlingAI credentials. Gemini and/or AIMLAPI are sufficient.

---

### Part 2: Codebase Exploration (45 min)

Before generating content, you must **understand** the system you're working with.

**Explore and document:**

1. **Package Structure**
   - What are the main modules in `src/ai_content/`?
   - How are providers organized?
   - What is the purpose of the `pipelines/` directory?

2. **Provider Capabilities**
   - What music providers are available? What are their differences?
   - What video providers are available? Which supports image-to-video?
   - Which provider supports vocals/lyrics?

3. **Preset System**
   - List all available music presets with their BPM and mood
   - List all available video presets with their aspect ratios
   - How would you add a new preset?

4. **CLI Commands**
   - What commands are available?
   - What options does the `music` command accept?
   - What options does the `video` command accept?

**Exploration Artifacts to Create:**
- `exploration/ARCHITECTURE.md` - Your understanding of the codebase structure
- `exploration/PROVIDERS.md` - Summary of provider capabilities
- `exploration/PRESETS.md` - Catalog of available presets

---

### Part 3: Content Generation (60 min)

Now, put your understanding to work by generating actual content.

**Required Generations:**

1. **Generate Music (Instrumental)**
   ```bash
   # Using a preset
   uv run ai-content music --style jazz --provider lyria --duration 30
   
   # Or with custom prompt
   uv run ai-content music --prompt "Your creative prompt here" --provider lyria
   ```

2. **Generate Music with Vocals** (if you have AIMLAPI key)
   - Create a lyrics file (`.txt`)
   - Use MiniMax provider with lyrics:
   ```bash
   uv run ai-content music --prompt "Your style prompt" --provider minimax --lyrics path/to/lyrics.txt
   ```

3. **Generate Video**
   ```bash
   uv run ai-content video --style nature --provider veo --duration 5
   ```

4. **Combine into a Music Video** (Bonus)
   - Use FFmpeg to merge your audio and video:
   ```bash
   ffmpeg -i video.mp4 -i music.wav -c:v copy -c:a aac -shortest output.mp4
   ```

**Generation Artifacts:**
- At least 2 generated audio files (different styles/providers)
- At least 1 generated video file
- (Bonus) 1 combined music video

---

### Part 4: YouTube Upload & Submission (45 min)

**Upload Requirements:**
1. Upload your best generated content to YouTube (unlisted is fine)
2. Title format: `[TRP1] Your Name - Content Description`
3. Description should include:
   - Prompt used for generation
   - Provider and preset used
   - Any creative decisions made

**Submission Package:**

Create a submission report (`SUBMISSION.md`) containing:

1. **Environment Setup Documentation**
   - Which APIs did you configure?
   - Any issues encountered during setup?
   - How did you resolve them?

2. **Codebase Understanding**
   - Architecture diagram or description
   - Key insights about the provider system
   - How the pipeline orchestration works

3. **Generation Log**
   - Commands executed
   - Prompts used and why
   - Results achieved (screenshots, file sizes, durations)

4. **Challenges & Solutions**
   - What didn't work on first try?
   - How did you troubleshoot?
   - What workarounds did you discover?

5. **Insights & Learnings**
   - What surprised you about the codebase?
   - What would you improve?
   - How does this compare to other AI tools you've used?

6. **Links**
   - YouTube video link(s)
   - GitHub repo with your exploration artifacts

---

## Grading Rubric Overview

| Category | Points | Focus |
|----------|--------|-------|
| Environment Setup & Configuration | 15 | Successful API setup, working installation |
| Codebase Exploration & Documentation | 25 | Depth of understanding, quality of exploration artifacts |
| Content Generation | 25 | Successfully generated audio/video, creative use of presets |
| Troubleshooting & Persistence | 20 | Documented challenges, workarounds found |
| Curiosity & Extra Effort | 15 | Exploration beyond requirements, insights gained |
| **Total** | **100** | |

---

## Tips for Success

1. **Read the Source Code** - The best documentation is often in the code itself. Look at `src/ai_content/providers/` to understand how each provider works.

2. **Check the Examples** - The `examples/` directory contains working code for common use cases.

3. **Use the Presets** - Start with presets before crafting custom prompts. They're optimized for good results.

4. **Document Everything** - Your troubleshooting journey is as valuable as your final output. We want to see how you think.

5. **Ask Unblocking Questions** - If you're stuck for more than 15 minutes, describe your problem clearly and ask for help.

---

## Available Commands Reference

```bash
# List available options
uv run ai-content list-providers
uv run ai-content list-presets

# Music generation
uv run ai-content music --style <preset> --provider <lyria|minimax>
uv run ai-content music --prompt "..." --provider lyria --bpm 120 --duration 30
uv run ai-content music --prompt "..." --provider minimax --lyrics path/to/file.txt

# Video generation
uv run ai-content video --style <preset> --provider veo
uv run ai-content video --prompt "..." --provider veo --aspect 16:9 --duration 5
```

---

## Submission Checklist

- [ ] `.env` file configured (do NOT commit this!)
- [ ] `exploration/ARCHITECTURE.md` - Codebase understanding
- [ ] `exploration/PROVIDERS.md` - Provider comparison
- [ ] `exploration/PRESETS.md` - Preset catalog
- [ ] At least 2 generated audio files
- [ ] At least 1 generated video file
- [ ] `SUBMISSION.md` - Complete report
- [ ] YouTube link(s) in submission
- [ ] GitHub repo link with all artifacts

---

**Good luck! Remember: We're measuring your exploration, comprehension, and persistence—not just the final output.**
