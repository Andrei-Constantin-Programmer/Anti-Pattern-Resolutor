const PageContainer = ({ children}) => {
    return (
        <main className="flex-1 flex flex-col w-full h-full items-center max-w-[1560px] mx-auto">
            {children}
        </main>
    );
};

export default PageContainer;