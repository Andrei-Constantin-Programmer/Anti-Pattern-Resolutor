import React from "react";
import Text from "../atom/Text";
import { toast } from "sonner";
import { useState } from "react";

import { LineSpinner } from "ldrs/react";
import "ldrs/react/LineSpinner.css";

const AnalysisArea = ({ sessionId }) => {
  const [analysis, setAnalysis] = useState({
    status: 'IDLE',
    antipatterns: []
  });
  const [loading, setLoading] = useState(false);

  const fetchAnalysis = async () => {
    if (!sessionId) {
      toast.error("No session ID available. Please upload a file first.");
      return;
    }

    setLoading(true);
    await toast.promise(
    new Promise(async (resolve, reject) => {
      try {
        const response = await fetch("http://127.0.0.1:8000/analyze/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId }),
        });

        const data = await response.json();

        if (response.ok) {
          try {
            const analysisString = data.antipattern_analysis;
            const parsedObject = JSON.parse(analysisString);

            setAnalysis(parsedObject);
            resolve({ name: "Analysis" });
          } catch (error) {
            console.error("Failed to parse analysis data:", error);
            reject("Could not read the analysis data from the server.");
          }
        } else {
          reject(data.detail || "Failed to load analysis");
        }
      } catch (error) {
        reject(error.message);
      }
    }),
    {
      loading: "Running analysis...",
      success: (data) => `${data.name} completed successfully!`,
      error: (message) => `${message}`,
    }
  );
  setLoading(false);
  };

  return (
    <div className="flex flex-col w-full p-5 border-2 border-white h-full rounded-xl">
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
        {!loading && analysis.status === 'IDLE' && (
          <p>Click the button to fetch analysis</p>
        )}

        {!loading && analysis.status === 'NO_ISSUES_FOUND' && (
          <p>No significant anti-patterns were detected!</p>
        )}

        {!loading && analysis.status === 'ISSUES_FOUND' && (
          <div className="flex flex-col gap-4">
            <Text variant="subheading" className="text-white">The issues detected are:</Text>
            {analysis.antipatterns.map((issue, index) => (
              <div key={index} className="w-full">
                <Text variant="subheading">{index+1}. {issue.name}</Text>
                <Text variant="span" className="text-gray-400"><span className="text-white underline underline-offset-4">Issue location:</span> {issue.location}</Text>
                <Text variant="body" >{issue.description}</Text>
              </div>
            ))}
          </div>
        )}
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
