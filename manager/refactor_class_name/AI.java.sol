public class newAI {

    private AIone AIone;
    private AItwo AItwo;
    private AIthree AIthree;

    public void setAIone(AIone AIone) {
        this.AIone = AIone;
    }

    public void setAItwo(AItwo AItwo) {
        this.AItwo = AItwo;
    }

    public void setAIthree(AIthree AIthree) {
        this.AIthree = AIthree;
    }

    public static void main(String args) {
        AI AI = new AI();

        AI.setAIone(new AIone());
        AI.setAItwo(new AItwo());
        AI.setAIthree(new AIthree());
    }
}
