import React from "react";
import clsx from "clsx";

const Text = ({ children, className, variant = "body" }) => {
  const Component =
    variant === "title"
      ? "h1"
      : variant === "heading"
      ? "h3"
      : variant === "nav"
      ? "span"
      : variant === "card_heading"
      ? "h4"
      : variant === "body"
      ? "p"
      : "span";

  const baseStyle = clsx(
    variant === "title" && " text-[28px] sm:text-[32px] font-black",
    variant === "heading" && "sm:text-[24px] text-[18px] font-black",
    variant === "body" && "text-[14px] sm:text-[16px]",
    variant === "span" && "sm:text-[16px] text-[14px]",
    variant === "nav" &&
      "text-[10px] sm:text-[14px] font-normal ",
    className
  );

  return <Component className={baseStyle}>{children}</Component>;
};

export default Text;
