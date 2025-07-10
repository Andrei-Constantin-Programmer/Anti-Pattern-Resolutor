import React from "react";
import Text from "../atom/Text";
import { toast } from "sonner";
import { useState } from "react";

import { LineSpinner } from "ldrs/react";
import "ldrs/react/LineSpinner.css";

const AnalysisArea = ({ sessionId }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchAnalysis = async () => {
    if (!sessionId) {
      toast.error("No session ID available. Please upload a file first.");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/analyze/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });

      const data = await response.json();

      if (response.ok) {
        setAnalysis(data.antipattern_analysis);
        toast.success("Analysis loaded!");
      } else {
        toast.error(data.detail || "Failed to load analysis");
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col w-full p-5 border-2 border-white h-full">
      <Text
        variant="heading"
        className="w-full text-center"
      >
        Analysis Agent Response
      </Text>
      <div className="flex-1 w-full justify-center mt-4">
        {!analysis && !loading && (
          <Text variant="body">Click the button to fetch analysis</Text>
        )}
        {loading && (
          <div className="flex flex-row justify-start  gap-2">
            <Text variant="body">
            Loading analysis
          </Text>
          <LineSpinner
              size="20"
              stroke="4"
              speed="1"
              color="white"
            />
        </div>
        )}
        {analysis && <Text variant="body">{analysis}</Text>}
      </div>

      <button
        onClick={fetchAnalysis}
        className="mt-4 mx-auto px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 transition"
      >
        <Text variant="span">Get Analysis</Text>
      </button>
    </div>
  );
};

export default AnalysisArea;
