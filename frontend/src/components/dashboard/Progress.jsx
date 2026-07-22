import {
  CheckCircle,
  Loader2,
  Circle,
} from "lucide-react";

const STEPS = [
  {
    key: "planning",
    title: "Planning",
    percent: 10,
  },
  {
    key: "coding",
    title: "Generating Code",
    percent: 30,
  },
  {
    key: "building",
    title: "Building Project",
    percent: 50,
  },
  {
    key: "executing",
    title: "Executing",
    percent: 65,
  },
  {
    key: "testing",
    title: "Running Tests",
    percent: 80,
  },
  {
    key: "review",
    title: "AI Review",
    percent: 90,
  },
  {
    key: "completed",
    title: "Completed",
    percent: 100,
  },
];

export default function Progress({ progress }) {
  const current =
    progress?.progress || 0;

  return (
    <div className="bg-gray-800 rounded-2xl p-8 shadow-xl">

      <h2 className="text-2xl font-bold mb-8">
        🚀 Live Pipeline
      </h2>

      <div className="space-y-6">

        {STEPS.map((step) => {

          const completed =
            current > step.percent;

          const active =
            current === step.percent;

          return (
            <div key={step.key}>

              <div className="flex justify-between items-center mb-2">

                <div className="flex items-center gap-3">

                  {completed ? (
                    <CheckCircle
                      className="text-green-400"
                      size={22}
                    />
                  ) : active ? (
                    <Loader2
                      className="animate-spin text-cyan-400"
                      size={22}
                    />
                  ) : (
                    <Circle
                      size={20}
                      className="text-gray-500"
                    />
                  )}

                  <span className="font-semibold">
                    {step.title}
                  </span>

                </div>

                <span className="text-cyan-400">

                  {step.percent}%

                </span>

              </div>

              <div className="w-full h-3 bg-gray-700 rounded-full">

                <div
                  className="h-3 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 transition-all duration-700"
                  style={{
                    width:
                      current >= step.percent
                        ? "100%"
                        : current > step.percent - 15
                        ? `${((current - (step.percent - 15)) / 15) * 100}%`
                        : "0%",
                  }}
                />

              </div>

            </div>
          );
        })}

      </div>

      <div className="mt-8 text-gray-400">

        {progress?.message || "Waiting..."}

      </div>

    </div>
  );
}