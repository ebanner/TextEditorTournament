public class AI2 {

    private AI AI;
    private AI1 AI1;
    private AI3 AI3;

    public void setAI(AI AI) {
        this.AI = AI;
    }

    public void setAI1(AI1 AI1) {
        this.AI1 = AI1;
    }

    public void setAI3(AI3 AI3) {
        this.AI3 = AI3;
    }

    public static void main(String args) {
        AI2 AI2 = new AI2();

        AI2.setAI(new AI());
        AI2.setAI1(new AI1());
        AI2.setAI3(new AI3());
    }
}
