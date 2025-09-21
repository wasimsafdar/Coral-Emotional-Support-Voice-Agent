# Coral Emotional Support Voice Agent (STT-LLM-TTS Pipeline)

## [Coral Emotional Support Voice Agent ](https://github.com/wasimsafdar/Coral-Emotional-Support-Voice-Agent)

This is a real-time voice interface agent that uses an STT-LLM-TTS pipeline, enabling natural conversations with AI systems. This AI agent talks with a user and analyzes the user's voice. If the user is feeling sad or depressed, it directs them to an emotional support AI agent.

## Responsibility
The emotional support AI agent then helps the user by suggesting various exercises and sharing jokes to lighten the mood. It leverages LiveKit for streaming, Deepgram for speech-to-text, OpenAI for language processing, and Cartesia for text-to-speech synthesis.

## Details
- **Framework**: LiveKit Agents
- **Tools used**: LiveKit, Deepgram STT, OpenAI LLM, Cartesia TTS, Silero VAD
- **AI model**: GPT-4o-mini with Nova-3 STT and Sonic-2 TTS
- **Date added**:Sep 2025

## Use the Agent

### 1. Clone & Install Dependencies

<details>

```bash
# In a new terminal clone the repository in any folder:
git clone https://github.com/wasimsafdar/Coral-Emotional-Support-Voice-Agent

# Install uv:
pip install uv

# Install dependencies from pyproject.toml using uv:
uv sync

# Copy the client sse.py from utils to mcp package (Linux/ Mac)
cp -r utils/sse.py .venv/lib/python3.13/site-packages/mcp/client/sse.py

# OR Copy this for Windows
cp -r utils\sse.py .venv\Lib\site-packages\mcp\client\sse.py
```

</details>

### 2. Configure Environment Variables

<details>

Get the API Keys:
[LiveKit](https://cloud.livekit.io/) |
[OpenAI](https://platform.openai.com/api-keys) |
[Deepgram](https://deepgram.com/) |
[Cartesia](https://play.cartesia.ai/keys)

```bash
# Create .env file in project root
cp -r .env.example .env
```

Required environment variables:
* `LIVEKIT_URL` - Your LiveKit server URL
* `LIVEKIT_API_KEY` - LiveKit API key
* `LIVEKIT_API_SECRET` - LiveKit API secret
* `OPENAI_API_KEY` - OpenAI API key for GPT-4o-mini
* `DEEPGRAM_API_KEY` - Deepgram API key for Nova-3 STT
* `CARTESIA_API_KEY` - Cartesia API key for Sonic-2 TTS

</details>

### 3. Download Turn Detector Files

<details>

```bash
uv run python main.py download-files
```

</details>

### 4. Run Agent

<details>

```bash
# Run in terminal (console) mode:
uv run python main.py console
```

</details>

### 5. Example

<details>

```bash
# Input:
Speak your query naturally into the microphone.

# Output:
The system will:
- Capture your voice input using Deepgram STT
- Process your request with OpenAI LLM
- Respond using natural voice synthesis via Cartesia TTS
```

</details>

## Pipeline Components

1. **STT (Speech-to-Text):** Deepgram Nova-3 with multilingual support
2. **LLM (Language Model):** OpenAI GPT-4o-mini for intelligent responses  
3. **TTS (Text-to-Speech):** Cartesia Sonic-2 for natural voice synthesis
4. **VAD (Voice Activity Detection):** Silero for accurate speech detection
5. **Turn Detection:** Multilingual model for conversation flow

## Creator Details
- **Name**: Wasim Safdar
