import { useEffect, useState } from "react";

export default function StatusBar() {
  const [status, setStatus] = useState<"checking" | "connected" | "error">("checking");
  const [expanded, setExpanded] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const checkConnection = async () => {
    setStatus("checking");
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      if (data.status === "ok") {
        setStatus("connected");
        setErrorMessage(null);
      } else {
        setStatus("error");
        setErrorMessage(data.message || "Connection failed");
      }
    } catch (e) {
      setStatus("error");
      setErrorMessage((e as Error).message);
    }
  };

  useEffect(() => {
    void checkConnection();
  }, []);

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 text-white text-sm z-50">
      <div
        className="flex items-center justify-between px-4 py-2 cursor-pointer hover:bg-gray-800"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          {status === "checking" && (
            <>
              <span className="inline-block w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></span>
              <span>Checking database...</span>
            </>
          )}
          {status === "connected" && (
            <>
              <span className="inline-block w-2 h-2 bg-green-400 rounded-full"></span>
              <span>Database connected</span>
            </>
          )}
          {status === "error" && (
            <>
              <span className="inline-block w-2 h-2 bg-red-400 rounded-full"></span>
              <span>Database error</span>
            </>
          )}
        </div>
        <span className="text-gray-400">{expanded ? "▼" : "▲"}</span>
      </div>

      {expanded && (
        <div className="px-4 py-3 border-t border-gray-700 bg-gray-800">
          {status === "error" && errorMessage && (
            <p className="text-red-300 mb-2">Error: {errorMessage}</p>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              void checkConnection();
            }}
            className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm mr-2"
          >
            Retry Connection
          </button>
          <span className="text-gray-400 text-xs">
            Click to {expanded ? "collapse" : "expand"}
          </span>
        </div>
      )}
    </div>
  );
}
