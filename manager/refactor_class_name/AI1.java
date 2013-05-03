public class AI1 {

    private AI AI;
    private AI2 AI2;
    private AI3 AI3;

    public void setAI(AI AI) {
        this.AI = AI;
    }

    public void setAI2(AI2 AI2) {
        this.AI2 = AI2;
    }

    public void setAI3(AI3 AI3) {
        this.AI3 = AI3;
    }

    public static void main(String args) {
        AI AI = new AI();

        AI.setAI(new AI());
        AI.setAI1(new AI1());
        AI.setAI2(new AI2());
    }
}
