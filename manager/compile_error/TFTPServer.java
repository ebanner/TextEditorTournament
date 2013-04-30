// TFTPServer implements the server side of RFC 1350.  Octet mode only.
// This server is multi-threaded.
//
// Usage: java TFTPServer [-p port] [-r retries]

import java.io.*;
import java.net.*;
import java.nio.channels.DatagramChannel;


public class TFTPServer extends Thread
{
  // maximum DATA segment size (in bytes)
  static final int DATASEGSZ = 512;

  // TFTP opcode values
  static final int RRQ   = 1;
  static final int WRQ   = 2;
  static final int DATA  = 3;
  static final int ACK   = 4;
  static final int ERROR = 5;

  // defaults for global parameters
  static final int DEFAULT_RETRIES =    2;
  static final int DEFAULT_PORT    = 3069;

  // global parameters specified at runtime
  static int retries;

  // thread variables
  DatagramSocket threadSocket;
  DatagramPacket threadPacket;
  byte[] buf;

  // Constucts a TFTP server thread for one client/initial packet
  // param: serverPacket the initial packet
    public TFTPServer(DatagramPacket serverPacket){
	threadPacket = serverPacket; // assign server packet to thread variable
	this.buf = new byte[DATASEGSZ+4]; // all TFTP packets are 516 or less
	
	// Attempt to construct a datagram socket and bind it to any
	// available port on the local host machine.  This will be used for
	// this thread/client.
	try{
	    DatagramSocket threadSocket = new DatagramSocket();
	}catch (SocketException se){
	    System.err.println(se);
	}
	// Get the initial packet's data in the thread buffer.
	buf = threadPacket.getData();
    }
    
    // Handles packets with the RRQ opcode.
    void handleRRQ(){
	System.err.println("\n\nREAD REQUEST INITIALIZED...\n");
	// Get filename from packet.
	String filename = "";
	for (int i = 2; (int)buf[i] != 0; i++){
	    filename += (char)buf[i];
	} 

	System.err.println(filename + " requested.");

	// Get mode from the packet
	// (after the opcode, filename, and null byte).
	String mode = "";
	for (int i = filename.length() + 2 + 1; (int)buf[i] != 0; i++){
	    mode += (char)buf[i];
	}
	mode = mode.toLowerCase();
	
	System.err.println(mode + " mode");

	// Report unsupported modes; only octet is supported.
	if (!mode.equals("octet")){
	    sendError(0,"Unsupported mode: " + mode);
	    return;
	}

	// Try to set up reading from file filename
	BufferedInputStream in = null;
	try{
	    in = new BufferedInputStream(new FileInputStream(filename));
	}
	catch (FileNotFoundException e){
	    System.err.println("Failure in handleRRQ - 1");
	    sendError(1,""); // Send "File not found" to client.
	}

	// send DATA packets and recieve acknowledgement packets
	int block = 0; // this thread's block counter
	int n = 0; // blocks read counter
	boolean leave = false;
	while (true){
	    // Try read n byte (up to DATASEGSZ bytes) of input into the
	    // packet buffer, add the opcode and block headers, and send the
	    // packet to the client.
	    block++;
	    System.err.println("BLOCK #" + block);

	    try {
		n = in.read(buf, 4, DATASEGSZ);
	    }
	    catch (IOException e){
		System.err.println(e);
		System.err.println("Failure in handleRRQ - 2");
		System.exit(3);
	    }
	    if (n < 0){ // indicates end of file{
		n = 0;   // send an empty DATA field
	    }
	    int retry = 0;
	    while(retry < 2) {
		buf[0] = (byte)(0x00);       // opcode byte
		buf[1] = (byte)(0x03);       // opcode byte
		buf[2] = (byte)(block >> 8); // block byte
		buf[3] = (byte)(block);    // block byte
		threadPacket.setLength(n+4); // adjust the packet length
		sendPacket(threadPacket);    // send the packet
		
		System.err.println("BLOCK UPDATED: " +  block);
		// stop sending packets when we reach the end of the input
		if (n < DATASEGSZ){
		    leave = true;
		    break;
		}
		
		// Try to listen for an acknowledgement packet.
		try{
		    threadSocket.receive(threadPacket);
		    byte[] items = threadPacket.getData();
		    String stuff = "";
		    for(int i=0; i<items.length; i++)
		    stuff += "" + (char)items[i];
		    System.err.println("<<GOT>>:\n" + stuff +
				       "\n<<END OF RECIEVED PACKET>>");
		}catch (IOException e){
		    System.err.println(e);
		    System.err.println("Failure in handleRRQ - 3");
		    System.exit(3);
		}
		
		
		// Get the block number of the packet.
		int clientBlock = ((0xFF & buf[2]) << 8) | (0xFF & buf[3]);
		
		System.err.println("CLIENT BLOCK NUMBER IS: " + clientBlock);
		
		// If the block number in the packet does not match the block
		// number the server thread expects to receive, resend the last
		// DATA packet.  It is unlikely that this will happen often on a
		// local area network, so this should be fine.
		if (clientBlock != block){
		    System.err.println("RECEIVED BAD BLOCK NUMBER");
		    retry++;
		} else
		    break;
	    }
	    System.err.println("READ COMPLETE.");    
	    if(leave)
		break;
	}
	
    }

  // Handles packets with the WRQ opcode.
    void handleWRQ(){

	System.err.println("\n\nWRITE INITIALIZED\n");
	// Get filename from packet.
	String filename = "";
	for (int i = 2; (int)buf[i] != 0; i++){
	    filename += (char)buf[i];
	} 
    
	// Get mode from the packet
	// (after the opcode, filename, and null byte).
	String mode = "";
	for (int i = filename.length() + 2 + 1; (int)buf[i] != 0; i++){
	    mode += (char)buf[i];
	}
	mode = mode.toLowerCase();
	
	// Report unsupported modes; only octet is supported.
	if (!mode.equals("octet")) {
	    sendError(0,"Unsupported mode: " + mode);
	    return;
	}
	
	// Try to set up writing to file filename
	BufferedOutputStream out = null;
	try{
	    out = new BufferedOutputStream(new FileOutputStream(filename));
	}catch (FileNotFoundException fnfe){
	    System.err.println("Failure in handleWRQ() - 1");
	    sendError(1,""); // Send "File not found" to client.
	}

	/*
	sendACK(0);

	int timeouts = 0;
	int lastBlock = 0;
	boolean initialized = false;

	try {
	    threadSocket.setSoTimeout(500);
	} catch (SocketException se) {
	    System.err.println("Socket error.");
	    System.exit(7);
	}
	try {
	    // while loop to continue listening 
	       //for packets until a non-full is sent
	    while (true) {
		int n = threadPacket.getLength();
		//couldn't find a better way

		System.out.println(n);
		System.out.println(DATASEGSZ + 4);
		if (n < 2) {
		    System.err.println("datagram format error");
		    return;
		}
		// grab the block number and write some info
		int block = ((0xFF & buf[2]) << 8) | (0xFF & buf[3]);

		if(initialized && lastBlock!= block)
		    return;

		if (!initialized) {
		    initialized = true;
		    lastBlock = block;
		}

		System.out.println("block=" + block);
		n -= 2; // number of data bytes
		out.write(buf, 2, n); 
		//check for end condition of a non-full byte[]
		if (n < DATASEGSZ) {
		    System.out.println("end conditional found.");
		    out.close();
		    sendACK(block);
		    break;
		}
		//handle timeouts
		while (timeouts <= retries) 
		    try {
			sendACK(block);
			System.out.println("SENT ACK");
			threadSocket.receive(threadPacket);
			System.out.println("Got new packet.");
			break;
		    } catch (Exception e) {
			sendACK(block);
			timeouts++;
		    }
	    }
	} catch (Exception e) {
	    System.err.println(e);
	    System.out.println("End of RRQ error");
	}*/




	// Receive DATA packets and send acknowledgement packets.
	int block = 0; // this thread's block counter

	int count = 1;

	boolean expected = false;

	System.err.println("Initiating byte collection LOOP sequence.\n");

	while (true){
	    System.err.println("On packet #" + count++);
	    // Try to send an acknowledgement with block number block.  If it
	    // fails, notify the client and return control to the server.
	   if (!sendACK(block)){
		sendError(0,"Connection timed out.");
		System.err.println("AWK failure in handleWRQ() - 2");
		return;
	   }
	   

	    // Try to wait for a packet.
	   DatagramPacket newPacket = null;
	   try{
	       byte[] bytes = new byte[516];
	       newPacket = new DatagramPacket(bytes, bytes.length);
	       DatagramSocket newSocket = new DatagramSocket();
	       
	       //threadSocket.setSoTimeout(500);

	       newSocket.setSoTimeout(500);
	       System.err.println("Waiting on packet...");
	       newSocket.receive(newPacket);
	       byte[] items = newPacket.getData();

	       //threadSocket.receive(threadPacket);

	       block++; //increment BLOCK # after it was received
	       //byte[] items = threadPacket.getData();
	       String stuff = "";
	       for(int i=0; i<items.length; i++)
		   stuff += "" + (char)items[i];
		System.err.println("<<GOT>>:\n" + stuff +
				   "\n<<END OF RECIEVED PACKET>>");
	   }
	   catch (IOException e){
	       System.err.println(e);
	       System.err.println("Failure in handleWRQ() - 3");
		try{
		    out.close();
		    System.err.println("File saved.");
		}catch(Exception ex){
		    System.err.println("File closing fail.");
		}
	    	System.exit(3);
	   }

	   buf = newPacket.getData();
	    
	    // Check the packet.
	    System.err.println("Checking recieved packet...");
	    // Get the packet length.
	    int n = threadPacket.getLength();
	    System.err.println("Packet is " + n + " bytes in size.");
	    
	    // If the packet is too small, tell the client and return control
	    // to the server.
	    if (n < 2){
		sendError(4,""); // Send "Illegal TFTP operation."
		System.err.println("Sent ILLEGAL TFTP OPERATION Error.");
		return;
	    }
	    
	    // Get the block number of the packet.
	    int clientBlock = ((0xFF & buf[0]) << 8) | (0xFF & buf[1]);
	    System.err.println("Client sent me a block #" + clientBlock);
	    
	    if(!expected){ //first block recieved, adjusted to server
		System.err.println
		    ("Client and Server BLOCK numbers are now set to match,");
		expected = true;
		block = clientBlock;
	    }

	    System.err.println("Server block ID is now #" + block);

	    // If the block number in the packet does not match the block
	    // number the server thread expects to receive, resend the last
	    // acknowlegement.  It is unlikely that this will happen often on
	    // a local area network, so this should be fine.
	    if (clientBlock != block){
	    	block--; // to resend previous ACK
	    	System.err.println("Blocks mismatched... resending LAST AWK.");
	    }else{
		// Write n-2 DATA bytes.
		n -= 4; // number of bytes to write (subtracting opcode length)
		System.err.println("All went good - we have " + n
				   + "bytes of a file (should be ~512).");
		try{
		    String contents = "";
		    for(int i=4; i<n; i++){
			contents += buf[i];
		    }
		    //out.write(contents);
		    out.write(buf, 4, n); // Write n bytes from packet buffer.
		    System.err.println("Wrote bytes to file... ");
		}catch (IOException e){
		    System.err.println(e);
		    System.err.println
			("Failure in handleWRQ() FILE WRITE ERROR - 3");
		    //System.exit(3);
		    return;
		}
		    
		// If the last packet was the last packet that will be sent, try
		// to close the output, and then return control to the server.
		if (n < DATASEGSZ){
		    System.err.println
			("n is NOT 512 bytes... finishing thread.");
		    sendACK(block);
		    try{
			out.close();
			System.err.println("File done.");
		    }catch (IOException e){
			System.err.println(e);
			System.err.println
			    ("Failure in handleWRQ() FILE CLOSE ERROR - 4");
			//System.exit(3);
			return;
		    }
		    System.err.println("WRITE COMPLETE\n\n");
		    return;
		}
	    }
	}
    }
    
    // send 4-byte ACK packet with block # block
    // returns false on failure to send
    boolean sendACK(int block) {
	byte[] buff = new byte[4];
	buff[0] = (byte)(ACK >> 8);
	buff[1] = (byte)(ACK);
	buff[2] = (byte)(block >> 8);
	buff[3] = (byte)(block);
	//threadPacket.setLength(4);
	//threadPacket.setData(buf, 0, 4);
	DatagramPacket p = null;
	try{
	    p = new DatagramPacket(buff, 0, 4);
	    p.setAddress(threadPacket.getAddress());
	    p.setPort(threadPacket.getPort());
	}catch(Exception e){
	    System.err.println("Couldn't make new packet.");
	    return false;
	}
	for(int i=0; i<buff.length; i++)
	    System.err.print((char)buf[i]);
	System.err.println(" ... Sending ACK - " + block);
	return sendPacket(p);
    }
    
    // send a packet through the threadSocket,
    // handling timeouts and RETRIES retries;
    // returns false on failure to send
    boolean sendPacket(DatagramPacket packet) {
	int timeouts = 0;
	try{
	    threadSocket = new DatagramSocket();
	    threadSocket.setSoTimeout(500)
	}catch(SocketException ste){
	    System.err.println(ste);
	    System.err.println("Failure in sendPacket() - 1");
	    return false;
	}catch(Exception e){
	    System.err.println(e);
	    System.err.println("Failure in sendPacket() - 2");
	    return false;
	}
		// try to send the packet through the socket
		try{
		    threadSocket.send(packet);
		    byte[] items = packet.getData();
		    String stuff = "";
		    for(int i=0; i<items.length; i++)
			stuff += "" + (char)items[i];
		    System.err.println("<<SENDING>>:\n" + stuff +
				       "\n<<END OF PACKET>>");
		} catch (IOException e){
		    System.err.println("Failure in sendPacket() - 3");
		    System.err.println(e);
		    System.exit(3);
		}

	if (timeouts > retries)
	    return false;

	return true;
    }

  void sendError(int errorCode, String errorMsg)
  {
    // error codes and messages, see page 9 of the RFC
    switch (errorCode)
    {
      case 0:  errorMsg = errorMsg;                            break;
      case 1:  errorMsg = "File not found.";                   break;
      case 2:  errorMsg = "Access violation";                  break;
      case 3:  errorMsg = "Disk full or allocation exceeded."; break;
      case 4:  errorMsg = "Illegal TFTP operation.";           break;
      case 5:  errorMsg = "Unknown transfer ID.";              break;
      case 6:  errorMsg = "File already exists.";              break;
      case 7:  errorMsg = "No such user.";                     break;
      default: errorMsg = "Invalid error code.";               break;
    }

    // 2 byte error opcode
    buf[0] = (byte)0x00; buf[1] = (byte)0x05;
    // 2 byte ErrorCode
    buf[2] = (byte)0x00; buf[3] = (byte)errorCode;
    // errorMsg
    byte[] errorBytes = errorMsg.getBytes();
    for (int i = 4; i < errorMsg.length(); i++)
    {
      buf[i] = errorBytes[i];
    }
    // null byte to signal the packet's end
    buf[errorMsg.length()] = (byte)0x00;
    // send it!
    threadPacket.setLength(buf.length); // adjust the packet size
    sendPacket(threadPacket); // pass it to sendPacket()
  }

    public void run(){
	// find out what opcode we're dealing with
	int opcode = ((0xFF & buf[0] << 8) | (0xFF & buf[1]));
	// decide what to do with the packet's data
	if(opcode == RRQ)
	    handleRRQ();
	else if (opcode == WRQ)
	    handleWRQ();
	else
	    sendError(4,""); // illegal TFTP operation
  }

  // exit codes:
  // 1: invalid input
  // 2: connection issue
  // 3: I/O error
  public static void main(String [] args)
  {
    int port = DEFAULT_PORT;
    retries = DEFAULT_RETRIES;

    DatagramSocket serverSocket = null;
    try
    {
      // Construct a datagram socket and bind it to port port.  Notice,
      // this is the server's socket, not the socket of the threads
      // created by the server.
      serverSocket = new DatagramSocket(port);
      // Set the maximum size of the packet that can be received on this
      // socket to 1MB.
      // Note: It is implementation specific if a packet larger than
      // this can be received (API).
      serverSocket.setReceiveBufferSize(1024);
    }
    catch (SocketException se)
    {
      System.err.println(se);
      System.exit(2)
    }

    // the server actions
    while (true)
    {
      // construct a datagram packet
      DatagramPacket serverPacket = new DatagramPacket(new byte[1024], 1024);
      // listen for a packet
      try
      {
        serverSocket.receive(serverPacket)
      }
      catch (IOException e)
      {
        System.err.println(e);
        System.exit(3);
      }
      // spawn a thread for the packet/client
      new TFTPServer(serverPacket).run();
    }
  }
}
