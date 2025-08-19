from agents.antipattern_scanner import AntipatternScanner
from agents.code_generator import CodeGenerator
from agents.strategist_agent import StrategistAgent
#from utils.watsonx_client import WatsonXClient
from utils import OllamaModelClient

model = OllamaModelClient()

code = """

        public class GodClass {

    public static int count = 0;
    public static String status = "OK";
    public static String globalConnection;

    public static void main(String[] args) {
        GodClass god = new GodClass();
        god.doEverything();
    }

    public void doEverything() {
        try {
            System.out.println("Starting process...");
            count = 5;

            for (int i = 0; i < 100; i++) {
                if (i % 5 == 0) {
                    processThing(i, "Task" + i);
                } else {
                    System.out.println("Skipping task " + i);
                }
            }

            // Copy-paste logic
            if (count > 50) {
                status = "TOO MUCH";
                System.out.println("Status: " + status);
            } else {
                status = "ALL GOOD";
                System.out.println("Status: " + status);
            }

            if (count > 50) {
                status = "TOO MUCH";
                System.out.println("Status: " + status);
            } else {
                status = "ALL GOOD";
                System.out.println("Status: " + status);
            }

            connectToDB();
            System.out.println("Process finished with status: " + status);

        } catch (Exception e) {
            // do nothing
        }
    }

    public void processThing(int val, String name) {
        System.out.println("Processing " + name + " with value " + val);
        if (name.length() > 3) {
            System.out.println(name.substring(0, 3).toUpperCase());
        }

        if (val == 42) {
            System.out.println("The Answer.");
        }

        // Unused variable
        String temp = "I exist for no reason";
    }

    public void connectToDB() {
        globalConnection = "jdbc:mysql://localhost:3306/baddb?user=admin&password=admin";
        System.out.println("Connected to DB using " + globalConnection);
    }
}



        """

antipattern_scanner = AntipatternScanner(model)
antiPatterns = antipattern_scanner.analyze(code)

strategist = StrategistAgent(model)
strategy = strategist.suggest_refactorings(code, antiPatterns)

coder = CodeGenerator(model)
code = coder.generate_refactored_code(code, strategy)

print(code)
