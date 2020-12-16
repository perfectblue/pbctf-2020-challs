package blue.perfect.kokoro;

import java.io.*;

public class ReadFlag {
    public String readFlag() {
        try {
            return new BufferedReader(new FileReader(new File("flag.txt"))).readLine();
        } catch(Exception e) {
            System.err.println("Failed to read flag");
            e.printStackTrace();
            while (true) {
                System.exit(1);
            }
        }
    }
}
