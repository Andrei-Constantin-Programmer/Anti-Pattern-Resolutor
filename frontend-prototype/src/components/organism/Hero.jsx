import React from "react";
import Text from "../atom/Text";

const Hero = () => {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg  w-full mx-auto space-y-4">
      <Text variant="heading">Some text content here</Text>
      <Text variant="body">something explaining about the project maybe</Text>
    </div>
  );
};

export default Hero;
