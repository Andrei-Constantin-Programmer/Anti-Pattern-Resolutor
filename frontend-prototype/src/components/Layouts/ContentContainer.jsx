const ContentContainer = ({ children }) => {
    return (
        <main className="flex flex-col flex-1 px-6 w-full md:px-10 py-4 md:py-8 rounded-[40px] gap-[40px]">
            {children}
        </main>
    );
};

export default ContentContainer;