const statusElement = document.getElementById("status");
const resultSection = document.getElementById("result-section");
const summarySection = document.getElementById("summary-section");
const transcriptionOutput = document.getElementById("transcription-output");
const summaryOutput = document.getElementById("summary-output");
const submitButton = document.getElementById("submit-button");
const spinnerTemplate = document.getElementById("spinner-template");

const defaultConfig = {
  component1_base_url: "http://localhost:8000",
  poll_interval_seconds: 3,
};

async function loadConfig() {
  try {
    const response = await fetch("/config.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error("Failed to load config");
    }
    const data = await response.json();
    return {
      component1_base_url: data.component1_base_url || defaultConfig.component1_base_url,
      poll_interval_seconds: data.poll_interval_seconds || defaultConfig.poll_interval_seconds,
    };
  } catch (error) {
    console.warn("Falling back to default config", error);
    return defaultConfig;
  }
}

const configPromise = loadConfig();

document.getElementById("upload-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  clearOutput();
  setBusy(true);

  const fileInput = document.getElementById("audio-input");
  const file = fileInput.files?.[0];
  if (!file) {
    setStatus("Please select an audio file to upload.");
    setBusy(false);
    return;
  }

  const config = await configPromise;

  try {
    setStatus("Uploading audio and creating transcription job...");
    const jobId = await uploadAudio(file, config.component1_base_url);
    setStatus(`Job ${jobId} queued. Waiting for transcription...`);
    const job = await pollForTranscription(jobId, config);

    transcriptionOutput.textContent = job.transcript;
    resultSection.classList.remove("hidden");

    setStatus("Generating summary...");
    const summary = await requestSummary(job.transcript);
    summaryOutput.textContent = summary.summary;
    summarySection.classList.remove("hidden");
    setStatus("All done!");
  } catch (error) {
    console.error(error);
    setStatus(`Something went wrong: ${error.message}`);
  } finally {
    setBusy(false);
  }
});

function setBusy(isBusy) {
  submitButton.disabled = isBusy;
  if (isBusy) {
    const spinner = spinnerTemplate.content.firstElementChild.cloneNode(true);
    statusElement.innerHTML = "";
    statusElement.appendChild(spinner);
  }
}

function setStatus(message) {
  statusElement.textContent = message;
}

function clearOutput() {
  resultSection.classList.add("hidden");
  summarySection.classList.add("hidden");
  transcriptionOutput.textContent = "";
  summaryOutput.textContent = "";
}

async function uploadAudio(file, baseUrl) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${baseUrl}/transcriptions`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await safeJson(response);
    throw new Error(error?.detail || `Upload failed with status ${response.status}`);
  }

  const data = await response.json();
  return data.job_id;
}

async function pollForTranscription(jobId, config) {
  const intervalMs = Math.max(config.poll_interval_seconds * 1000, 1000);
  while (true) {
    await sleep(intervalMs);
    const response = await fetch(`${config.component1_base_url}/transcriptions/${jobId}`, {
      cache: "no-store",
    });

    if (!response.ok) {
      const error = await safeJson(response);
      throw new Error(error?.detail || `Failed to fetch job status (${response.status})`);
    }

    const job = await response.json();
    if (job.status === "completed") {
      return job;
    }

    if (job.status === "failed") {
      throw new Error(job.error_message || "Transcription failed.");
    }

    setStatus(`Current status: ${job.status}. Still waiting...`);
  }
}

async function requestSummary(transcript) {
  const response = await fetch(`/summaries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcript }),
  });

  if (!response.ok) {
    const error = await safeJson(response);
    throw new Error(error?.detail || `Summary request failed (${response.status})`);
  }

  return response.json();
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function safeJson(response) {
  try {
    return await response.json();
  } catch (error) {
    return null;
  }
}
