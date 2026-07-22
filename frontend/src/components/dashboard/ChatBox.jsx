import { useState } from "react";
import axios from "axios";
import toast from "react-hot-toast";
import {
  Sparkles,
  Loader2,
  Download,
  CheckCircle,
} from "lucide-react";

import Progress from "./Progress";
import useWebSocket from "../../hooks/useWebSocket";

const API = "http://127.0.0.1:8000";

export default function ChatBox() {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const sessionId = "demo";

  const progress = useWebSocket(sessionId);

  const generateProject = async () => {
    if (!prompt.trim()) {
      toast.error("Please enter a project description.");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const { data } = await axios.post(`${API}/chat`, {
        session_id: sessionId,
        message: prompt,
      });

      setResult(data);

      toast.success("Project Generated Successfully 🚀");
    } catch (error) {
      console.error(error);

      toast.error("Failed to generate project.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">

      {/* Hero */}

      <div className="rounded-2xl bg-gradient-to-r from-cyan-600 to-blue-700 p-10 shadow-xl">

        <h1 className="text-5xl font-bold mb-4">
          🚀 AutoDev AI
        </h1>

        <p className="text-xl text-cyan-100">
          Autonomous AI Software Engineer
        </p>

      </div>

      {/* Prompt */}

      <div className="bg-gray-800 rounded-2xl p-8 shadow-lg">

        <h2 className="text-2xl font-bold flex items-center gap-3 mb-6">

          <Sparkles />

          Build Anything

        </h2>

        <textarea
          rows={8}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Example:

Build a MERN Ecommerce Website with Authentication, Admin Panel, Stripe Payments and Docker deployment."
          className="w-full rounded-xl bg-gray-900 border border-gray-700 p-5 resize-none outline-none text-lg"
        />

        <button
          onClick={generateProject}
          disabled={loading}
          className="mt-6 bg-cyan-500 hover:bg-cyan-600 transition px-8 py-4 rounded-xl font-bold flex items-center gap-3"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles />
              Generate Project
            </>
          )}
        </button>

      </div>

      {/* Progress */}

      <Progress progress={progress} />

      {/* Result */}

      {result && (
        <div className="bg-gray-800 rounded-2xl p-8 shadow-xl space-y-6">

          <h2 className="text-3xl font-bold flex items-center gap-3">

            <CheckCircle className="text-green-400" />

            Project Generated Successfully

          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">

            <div className="bg-gray-900 rounded-xl p-5">

              <p className="text-cyan-400 font-semibold mb-2">

                Project

              </p>

              <p>{result.plan.title}</p>

            </div>

            <div className="bg-gray-900 rounded-xl p-5">

              <p className="text-cyan-400 font-semibold mb-2">

                Validation

              </p>

              <p>{result.validation.score}/100</p>

            </div>

            <div className="bg-gray-900 rounded-xl p-5">

              <p className="text-cyan-400 font-semibold mb-2">

                Tests

              </p>

              <p>

                {result.tests.success
                  ? "✅ Passed"
                  : "❌ Failed"}

              </p>

            </div>

            <div className="bg-gray-900 rounded-xl p-5">

              <p className="text-cyan-400 font-semibold mb-2">

                Files Generated

              </p>

              <p>{result.project.file_count}</p>

            </div>

          </div>

          {/* Download */}

          <a
            href={`${API}${result.project.download_url}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-3 bg-green-600 hover:bg-green-700 px-8 py-4 rounded-xl font-bold transition"
          >
            <Download />

            Download ZIP

          </a>

        </div>
      )}

    </div>
  );
}