/**
 * API Gateway - Ollama + PhoWhisper Integration
 * QLTB -> Audio -> PhoWhisper (transcribe) -> Ollama (process) -> Response
 */

const express = require('express');
const multer = require('multer');
const axios = require('axios');
const cors = require('cors');

const app = express();
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 500 * 1024 * 1024 } // 500MB
});

// Middleware
app.use(cors());
app.use(express.json({ limit: '500mb' }));

// Config
const PHOWHISPER_URL = "http://localhost:8000";
const OLLAMA_URL = "http://localhost:11434";
const PORT = process.env.PORT || 3000;

/**
 * Health check
 */
app.get("/health", (req, res) => {
  res.json({ status: "ok", services: ["ollama", "phowhisper"] });
});

/**
 * Speech to Text only
 * POST /transcribe
 * Body: audio file
 */
app.post("/transcribe", upload.single("audio"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "No audio file provided" });
    }

    const audioB64 = req.file.buffer.toString('base64');

    console.log(`[PhoWhisper] Transcribing ${req.file.originalname}...`);
    console.log(`[PhoWhisper] Audio size: ${req.file.size} bytes`);

    const response = await axios.post(
      `${PHOWHISPER_URL}/api/transcribe`,
      {
        audio: audioB64,
        model: "vinai/PhoWhisper-small"
      },
      { timeout: 180000 }
    );

    const text = response.data.text;
    console.log(`[PhoWhisper] Result: ${text}`);

    res.json({
      text: text,
      model: "vinai/PhoWhisper-small",
      source: "phowhisper"
    });

  } catch (error) {
    console.error("[PhoWhisper Error]", error.message);
    res.status(500).json({
      error: "Transcription failed",
      details: error.message
    });
  }
});

/**
 * Speech to Text + Ollama Processing
 * POST /process
 * Body: audio file + ollama_model + prompt (optional)
 */
app.post("/process", upload.single("audio"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "No audio file provided" });
    }

    const ollamaModel = req.body.model || "llama2";
    const promptTemplate = req.body.prompt || "Tóm tắt: {text}";

    // Step 1: Transcribe with PhoWhisper
    console.log(`[Step 1] Transcribing audio...`);
    const audioB64 = req.file.buffer.toString('base64');

    const transcribeRes = await axios.post(
      `${PHOWHISPER_URL}/api/transcribe`,
      {
        audio: audioB64,
        model: "vinai/PhoWhisper-small"
      },
      { timeout: 180000 }
    );

    const transcribedText = transcribeRes.data.text;
    console.log(`[Step 1] Transcribed: ${transcribedText}`);

    // Step 2: Process with Ollama
    console.log(`[Step 2] Processing with Ollama (${ollamaModel})...`);

    const prompt = promptTemplate.replace("{text}", transcribedText);

    const ollamaRes = await axios.post(
      `${OLLAMA_URL}/api/generate`,
      {
        model: ollamaModel,
        prompt: prompt,
        stream: false
      },
      { timeout: 180000 }
    );

    const ollamaResponse = ollamaRes.data.response;
    console.log(`[Step 2] Ollama response: ${ollamaResponse}`);

    res.json({
      transcription: transcribedText,
      ollama_model: ollamaModel,
      ollama_response: ollamaResponse,
      prompt_used: prompt
    });

  } catch (error) {
    console.error("[Processing Error]", error.message);
    res.status(500).json({
      error: "Processing failed",
      details: error.message,
      step: error.config?.url?.includes("phowhisper") ? "transcription" : "ollama"
    });
  }
});

/**
 * Ollama only (text processing)
 * POST /ollama
 * Body: { "prompt": "...", "model": "llama2" }
 */
app.post("/ollama", express.json(), async (req, res) => {
  try {
    const { prompt, model = "llama2" } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: "No prompt provided" });
    }

    console.log(`[Ollama] Generating with ${model}...`);

    const response = await axios.post(
      `${OLLAMA_URL}/api/generate`,
      {
        model: model,
        prompt: prompt,
        stream: false
      },
      { timeout: 180000 }
    );

    res.json({
      prompt: prompt,
      model: model,
      response: response.data.response
    });

  } catch (error) {
    console.error("[Ollama Error]", error.message);
    res.status(500).json({
      error: "Ollama generation failed",
      details: error.message
    });
  }
});

/**
 * List available models
 * GET /models
 */
app.get("/models", async (req, res) => {
  try {
    const phoRes = await axios.get(`${PHOWHISPER_URL}/api/tags`, { timeout: 5000 });
    const ollamaRes = await axios.get(`${OLLAMA_URL}/api/tags`, { timeout: 5000 });

    res.json({
      phowhisper: phoRes.data.models || [],
      ollama: ollamaRes.data.models || []
    });
  } catch (error) {
    res.status(500).json({
      error: "Failed to fetch models",
      details: error.message
    });
  }
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: "Internal server error" });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 API Gateway running on port ${PORT}`);
  console.log(`   PhoWhisper: ${PHOWHISPER_URL}`);
  console.log(`   Ollama: ${OLLAMA_URL}`);
  console.log(`\n   POST /transcribe - Audio to text`);
  console.log(`   POST /process - Audio to text + Ollama`);
  console.log(`   POST /ollama - Text to Ollama`);
  console.log(`   GET /models - List all models`);
});
