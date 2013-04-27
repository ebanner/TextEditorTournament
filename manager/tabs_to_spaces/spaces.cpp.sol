#include <iostream>

class MyClass {

  private:
	int x;
	int y;
	
  public:
	MyClass();
	
	int getX();
	int getY();
	
	void setX(int x);
	void setY(int y);

};

// Initializes x and y both to 0.
MyClass::MyClass () {
	this->x = 0;
	this->y = 0;
}

// This code has absolutely no purpose in life other than to be here for the
//	sake of being here.
//	<- see this space? Yeah, that should become a TAB, too.
int MyClass::getX() {
	int retval = 0;
	for(int i=0; i<10; i++) {
		retval += i * this->x;
	}
	return retval;
}

// More comments where you should be careful and convert the indents to TABS.
//	Remember, it's a tricky spot.
int MyClass::getY() {
	int retval = 100;
	for(int i=0; i<10; i++) {
		retval += i + this->y;
	}
	return retval;
}

// Set MyClass's x to the given x value.
void MyClass::setX(int x) {
	this->x = x;
}

// Set MyClass's y to the given y value. This is tricky stuff. Mind blowing
//	in fact. And you guessed it, another artificially long comment here.
void MyClass::setY(int y) {
	this->y = y;
}

	
int main(int arc, char ** argv) {
	MyClass c;
	c.setX(10);
	c.setY(5);
	std::cout << c.getX() << ", "
		<< c.getY() << std::endl;
	return 0;
}
