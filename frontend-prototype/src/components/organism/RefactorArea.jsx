import Text from "../atom/Text";
import { toast } from "sonner";
import { useState } from "react";

import { LineSpinner } from "ldrs/react";
import "ldrs/react/LineSpinner.css";
import { useRef } from "react";
import { FaRegCopy } from "react-icons/fa";

const StrategyArea = ({ sessionId }) => {
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading] = useState(null);

  const codeRef = useRef(null);

  const fetchStrategy = async () => {
    if (!sessionId) {
      toast.error("No session ID available. Please upload a file first");
      return;
    }
    setLoading(true);
    // try {
    //   const response = await fetch("http://127.0.0.1:8000/refactor/", {
    //     method: "POST",
    //     headers: { "Content-Type": "application/json" },
    //     body: JSON.stringify({ session_id: sessionId }),
    //   });
    //   const data = await response.json();

    //   if (response.ok) {
    //     setStrategy(data.refactored_code);
    //     toast.success("Refactored Code loaded!");
    //   } else {
    //     toast.warning(
    //       "Maybe you forgot to do the analysis and strategy before trying to get the refactored code?"
    //     );
    //   }
    // } catch (error) {
    //   toast.error(error.message);
    // } 
    toast.promise(
      new Promise(async (resolve, reject) => {
        try {
          const response = await fetch("http://127.0.0.1:8000/refactor/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId }),
          });
          const data = await response.json();

          if (response.ok) {
            try {
              setStrategy(data.refactored_code);
              resolve({ name: "Refactor Code" });
            } catch (error) {
              reject("Could not read the refactored code from the server.");
            }

          }
          else {
            reject("Could not read the refactored code from the server.");
          }
        } catch (error) {
          reject(error.message);
        }
      }),
      {
        loading: "Generating refactored code...",
        success: (data) => `${data.name} loaded successfully!`,
        error: (message) => message,
      }
    )

    setLoading(false);
  };

  const handleCopy = () => {
    if (codeRef.current) {
      navigator.clipboard.writeText(codeRef.current.innerText)
        .then(() => {
          toast.success("Copied to clipboard!");
        })
        .catch((err) => {
          toast.error("Failed to copy!", err);
        });
    }
  };

  return (
    <div className="flex flex-col w-full md:w-fit p-5 border-2 border-white h-full md:min-w-[70vh]  rounded-xl">
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
        {strategy && <Text variant="body">
          <div className="flex flex-col gap-2">
            <div className="w-full flex items-center justify-end">
              <button onClick={handleCopy} className="px-4 py-2 border-1 text-white rounded-lg cursor-pointer hover:bg-white/10 transition flex flex-row items-center justify-center gap-1"><FaRegCopy />Copy</button>
            </div>
            <pre className="text-green-300 p-4 rounded overflow-auto text-sm">
              <code ref={codeRef}>{strategy}</code>
            </pre>

          </div>

        </Text>}
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
