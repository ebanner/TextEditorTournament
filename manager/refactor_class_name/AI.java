public class AI {

    private AI1 AI1;
    private AI2 AI2;
    private AI3 AI3;

    public void setAI1(AI1 AI1) {
        this.AI1 = AI1;
    }

    public void setAI2(AI2 AI2) {
        this.AI2 = AI2;
    }

    public void setAI3(AI3 AI3) {
        this.AI3 = AI3;
    }

    public static void main(String args) {
        AI AI = new AI();

        AI.setAI1(new AI1());
        AI.setAI2(new AI2());
        AI.setAI3(new AI3());
    }
}
