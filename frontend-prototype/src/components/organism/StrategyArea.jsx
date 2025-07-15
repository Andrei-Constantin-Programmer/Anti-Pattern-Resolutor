import Text from "../atom/Text";
import { toast } from "sonner";
import { useState } from "react";

import { LineSpinner } from "ldrs/react";
import "ldrs/react/LineSpinner.css";

const StrategyArea = ({ sessionId }) => {
  const [strategy, setStrategy] = useState({
    status: 'IDLE',
    refactorings: []
  });
  const [loading, setLoading] = useState(null);

  const fetchStrategy = async () => {
    if (!sessionId) {
      toast.error("No session ID available. Please upload a file first");
      return;
    }
    setLoading(true);

    await toast.promise(
    new Promise(async (resolve, reject) => {
      try {
        const response = await fetch("http://127.0.0.1:8000/strategy/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId }),
        });

        const data = await response.json();

        if (response.ok) {
          try {
            const strategy = data.refactoring_strategy;
            const parsedObject = JSON.parse(strategy);
            setStrategy(parsedObject);
            resolve({ name: "Strategy" });
          } catch (error) {
            reject("Could not read the strategy data from the server.");
          }
        } else {
          reject("Maybe you forgot to do the analysis before trying to get the strategy?");
        }
      } catch (error) {
        reject(error.message);
      }
    }),
    {
      loading: "Running strategy agent...",
      success: (data) => `${data.name} loaded successfully!`,
      error: (message) => message,
    }
  );

  setLoading(false);
  };

  return (
    <div className="flex flex-col w-full p-5 border-2 border-white h-full  rounded-xl">
      <Text
        variant="heading"
        className="w-full text-center"
      >
        Refactoring Strategy Agent
      </Text>
      <div className="flex-1 w-full justify-center mt-4">
        {!strategy && !loading && (
          <Text variant="body">Click the button to fetch strategies</Text>
        )}
        {loading && (
          <div className="flex flex-row justify-start gap-2">
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

        {!loading && strategy.status === 'IDLE' && (
          <Text variant="body">Click the button to get refactoring strategies</Text>
        )}

        {!loading && strategy.status === 'NO_REFACTORING_NEEDED' && (
          <Text variant="body">No significant changes are requied</Text>
        )}

        {!loading && strategy.status === 'REFACTORING_SUGGESTED' && (
          <div className="flex flex-col gap-4">
            <Text variant="subheading" className="text-white">The refactoring strategies are:</Text>
            {strategy.refactorings.map((issue, index) => (
              <div key={index} className="w-full">
                <Text variant="subheading">{index + 1}. {issue.issueName}</Text>

                <div className="flex flex-col gap-2">
                  <div className="flex flex-col gap-0">
                  <Text className="underline underline-offset-4">Issue suggestion:</Text>
                  <Text variant="body">
                    {issue.suggestion}
                  </Text>
                </div>

                <div className="flex flex-col gap-0">
                  <Text className="text-white underline underline-offset-4">Justification:</Text>
                  <Text variant="body" >
                    {issue.justification}
                  </Text>
                </div>
                </div>

              </div>
            ))}
          </div>
        )}

        {/* {strategy && <Text variant="body">{strategy}</Text>} */}
      </div>

      <button
        onClick={fetchStrategy}
        className="mt-4 mx-auto px-4 py-2 bg-green-700 text-white rounded-lg hover:bg-green-800 transition"
      >
        <Text variant="span">Get Strategy</Text>
      </button>
    </div>
  );
};

export default StrategyArea;
