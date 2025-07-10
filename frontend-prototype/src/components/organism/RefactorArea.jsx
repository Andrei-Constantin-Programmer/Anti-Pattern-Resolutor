import React from "react";
import Text from "../atom/Text";
import { toast } from "sonner";
import { useState } from "react";

import { LineSpinner } from "ldrs/react";
import "ldrs/react/LineSpinner.css";

const StrategyArea = ({ sessionId }) => {
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading] = useState(null);

  const fetchStrategy = async () => {
    if (!sessionId) {
      toast.error("No session ID available. Please upload a file first");
      return;
    }
    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/refactor/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      const data = await response.json();

      if (response.ok) {
        setStrategy(data.refactored_code);
        toast.success("Refactored Code loaded!");
      } else {
        toast.warning(
          "Maybe you forgot to do the analysis and strategy before trying to get the refactored code?"
        );
      }
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col w-full p-5 border-2 border-white h-full max-w-[730px]">
      <Text
        variant="heading"
        className="w-full text-center"
      >
        Refactor Agent Code
      </Text>
      <div className="flex-1 w-full justify-center mt-4">
        {!strategy && !loading && (
          <Text variant="body">Click the button to get the refactored code</Text>
        )}
        {loading && (
            <div className="flex flex-row justify-start gap-2">
            <Text variant="body">
            Loading refactored code
          </Text>
          <LineSpinner
              size="20"
              stroke="4"
              speed="1"
              color="white"
            />
        </div>
        )}
        {strategy && <Text variant="body">{strategy}</Text>}
      </div>

      <button
        onClick={fetchStrategy}
        className="mt-4 mx-auto px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 transition"
      >
        <Text variant="span">Refactor Code</Text>
      </button>
    </div>
  );
};

export default StrategyArea;
