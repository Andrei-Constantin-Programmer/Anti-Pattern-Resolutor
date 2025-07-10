import "./index.css";
import PageContainer from "./components/Layouts/PageContainer.jsx";
import Hero from "./components/organism/Hero.jsx";
import UploadArea from "./components/organism/UploadArea.jsx";
import StrategyArea from "./components/organism/StrategyArea.jsx";
import AnalysisArea from "./components/organism/AnalysisArea.jsx";
import ContentContainer from "./components/Layouts/ContentContainer.jsx";
import RefactorArea from "./components/organism/RefactorArea.jsx";
import TitleArea from "./components/organism/TitleArea.jsx";
import Text from "./components/atom/Text.jsx"
import { useState } from "react";

function App() {
  const [sessionId, setSessionId] = useState(null);
  return (
    <div className="flex flex-col min-h-screen text-white">
      <TitleArea />
      <PageContainer>
        <ContentContainer>
          <Hero />

          <UploadArea setSessionId={setSessionId} />

          <div
            className={
              "flex flex-col min-sm:flex-row gap-5 items-start justify-center min-h-[150px]"
            }
          >
            <AnalysisArea sessionId={sessionId}/>
            <StrategyArea sessionId={sessionId}/>
          </div>
          
          <div className="w-full flex items-center justify-center">
          <RefactorArea sessionId={sessionId}/>
          </div>

        </ContentContainer>
      </PageContainer>
        <div className="w-full bottom-0 left-0 right-0 text-center bg-gray-800 text-white py-4">
          <Text variant="nav"> &copy; All Rights Reserved</Text>
        </div>
    </div>
  );
}

export default App;
