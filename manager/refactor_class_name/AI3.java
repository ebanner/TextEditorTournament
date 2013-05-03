public class AI3 {

    private AI AI;
    private AI1 AI1;
    private AI2 AI2;

    public void setAI(AI AI) {
        this.AI = AI;
    }

    public void setAI1(AI1 AI1) {
        this.AI1 = AI1;
    }

    public void setAI2(AI2 AI2) {
        this.AI2 = AI2;
    }

    public static void main(String args) {
        AI3 AI3 = new AI3();

        AI3.setAI(new AI());
        AI3.setAI1(new AI1());
        AI3.setAI2(new AI2());
    }
}
