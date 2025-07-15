import React, { useState } from "react";
import { Toaster, toast } from "sonner";
import Text from "../atom/Text";

const UploadArea = ({setSessionId}) => {
  const [file, setFile] = useState(null);
  const inputRef = React.useRef(null);

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    setFile(uploadedFile);
  };

  const removeFile = () => {
    setFile(null);
    if(inputRef.current) {
      inputRef.current.value = null;
    }
  };

  // backed logic for uploading the file
  const handleSubmit = async () => {
    if (!file) return;

    try {
      const formData = new FormData();
      formData.append("file", file);

      // enter backedn endpoint to receive the file
      const response = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        toast.error("File upload failed!, please try again.");
        removeFile();
        return;
      } else if (response.status === 200) {
        const data = await response.json();
        console.log(data.session_id);
        setSessionId(data.session_id);
        toast.success("File uploaded successfully!");
        // removeFile();
      }
    } catch (error) {
      toast.error(error.message);
    }
  };

  return (
    <>
      <div className="flex flex-col items-center justify-center p-10 border-2 border-dashed rounded-lg border-gray-400 w-[80%] min-md:w-[70%] mx-auto gap-4">
        <div>
          <Text
            variant="heading"
            className="text-center"
          >
            Upload your <span className="text-green-600">Java</span> file here
          </Text>
        </div>

        <label className="cursor-pointer">
          <input
            type="file"
            onChange={handleFileChange}
            className="hidden"
            accept=".java"
            ref={inputRef}
          />
          <div className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-900/90 transition">
            <Text variant="span">Upload File</Text>
          </div>
        </label>

        {file && (
          <div className="flex flex-col w-full text-center gap-2 pb-0">
            <Text
              variant="span"
              className="text-gray-400"
            >
              {file.name}
            </Text>
            <button
              onClick={() => {
                toast.error("File removed successfully!");
                removeFile();
              }}
              className="text-red-500 text-sm hover:underline cursor-pointer"
            >
              <Text variant="span">Remove File</Text>
            </button>
          </div>
        )}

        <button
          onClick={() => {
            handleSubmit();
          }}
          disabled={!file}
          className={`px-4 py-2 rounded-lg text-white transition ${
            file
              ? "bg-green-700 hover:bg-green-800 cursor-pointer"
              : "bg-gray-400 cursor-not-allowed"
          }`}
        >
          <Text variant="span">Submit</Text>
        </button>
      </div>
      <Toaster
        position="top-center"
        richColors
        closeButton
        className="pb-0"
      />
    </>
  );
};

export default UploadArea;
