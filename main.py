from src.retriever.setup_vectorstore import setup_vectorstore
from src.llm.analyzer import analyze_code
from langchain_community.chat_models import ChatOllama
from langchain.tools.retriever import create_retriever_tool
from src.pipeline.antipattern_flow import build_pipeline
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings

# Use pre-seeded ChromaDB
persist_dir = "vector_store"
embedding = OllamaEmbeddings(model="nomic-embed-text")
vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding)

# Build retriever
retriever = vectordb.as_retriever()
retriever_tool = create_retriever_tool(
    retriever,
    name="retrieve_Java_antipatterns",
    description="Search for Java anti-patterns in the codebase"
)

# Load LLM
llm = ChatOllama(model="granite3.3:8b")

# Build pipeline
pipeline = build_pipeline(retriever_tool, analyze_code, llm)

# Sample input
legacy_code = """public class ApplicationManager {
    private List<String> users = new ArrayList<>();
    private List<String> logs = new ArrayList<>();
    public void addUser(String user) {
        users.add(user);
        logs.add("User added: " + user);
    }
    public void removeUser(String user) {
        users.remove(user);
        logs.add("User removed: " + user);
    }
    public void logEvent(String event) {
        logs.add(event);
    }
    public void printReport() {
        System.out.println("=== Users ===");
        for (String user : users) System.out.println(user);
        System.out.println("=== Logs ===");
        for (String log : logs) System.out.println(log);
    }
    public void backupData() {
        System.out.println("Backing up users and logs...");
    }
}"""

initial_state = {"code": legacy_code, "context": None, "answer": None}
final_state = pipeline.invoke(initial_state)
