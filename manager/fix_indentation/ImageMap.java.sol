// This example is from the book _Java in a Nutshell_ by David Flanagan.
// Written by David Flanagan.  Copyright (c) 1996 O'Reilly & Associates.
// You may study, use, modify, and distribute this example for any purpose.
// This example is provided WITHOUT WARRANTY either expressed or implied.

import java.applet.*;
import java.awt.*;
import java.net.*;
import java.util.*;

public class Imagemap extends Applet {
    protected Image image;      // image to display.
    protected Vector rects;     // list of rectangles in it.
    
    public void init() {
        // load the image to be displayed.
        image = this.getImage(this.getDocumentBase(), this.getParameter("image"));
        // lookup a list of rectangular areas and the URLs they map to.
        rects = new Vector();
        ImagemapRectangle r;
        int i = 0;
        while((r = getRectangleParameter("rect" + i)) != null) {
            rects.addElement(r);
            i++;
        }
    }
    
    // Called when the applet is being unloaded from the system.
    // We use it here to "flush" the image. This may result in memory 
    // and other resources being freed quicker than they otherwise would.
    public void destroy() {
        image.flush();
    }
    
    // Display the image.
    public void paint(Graphics g) {
        g.drawImage(image, 0, 0, this);
    }
    
    // We override this method so that it doesn't clear the background
    // before calling paint().  Makes for less flickering in some situations.
    public void update(Graphics g) {
        paint(g);
    }
    
    // find the rectangle we're inside
    private ImagemapRectangle findrect(int x, int y) {
        int i;
        ImagemapRectangle r = null;
        for(i = 0; i < rects.size(); i++)  {
            r = (ImagemapRectangle) rects.elementAt(i);
            if (r.inside(x, y)) break;
        }
        if (i < rects.size()) return r;
        else return null;
    }
    
    private ImagemapRectangle lastrect;
    
    // On button down, highlight the rectangle, and display a message
    public boolean mouseDown(Event e, int x, int y) {
        ImagemapRectangle r = findrect(x, y);
        if (r == null) return false;
        Graphics g = this.getGraphics();
        g.setXORMode(Color.red);
        g.drawRect(r.x, r.y, r.width, r.height);
        lastrect = r;
        this.showStatus("To: " + r.url);
        return true;
    }
    
    // On button up, unhighlight the rectangle. 
    // If still inside the rectangle go to the URL
    public boolean mouseUp(Event e, int x, int y) {
        if (lastrect != null) {
            Graphics g = this.getGraphics();
            g.setXORMode(Color.red);
            g.drawRect(lastrect.x, lastrect.y, lastrect.width, lastrect.height);
            this.showStatus("");
            ImagemapRectangle r = findrect(x,y);
            if ((r != null) && (r == lastrect))
                this.getAppletContext().showDocument(r.url);
            lastrect = null;
        }
        return true;
    }    

    // Parse a comma-separated list of rectangle coordinates and a URL.
    protected ImagemapRectangle getRectangleParameter(String name) {
        int x, y, w, h;
        URL url;
        String value = this.getParameter(name);
        if (value == null) return null;
        
        try {
            StringTokenizer st = new StringTokenizer(value, ",");
            x = Integer.parseInt(st.nextToken());
            y = Integer.parseInt(st.nextToken());
            w = Integer.parseInt(st.nextToken());
            h = Integer.parseInt(st.nextToken());
            url = new URL(this.getDocumentBase(), st.nextToken());
        } 
        catch (NoSuchElementException e) { return null; }
        catch (NumberFormatException e) { return null; }
        catch (MalformedURLException e) { return null; }
        
        return new ImagemapRectangle(x, y, w, h, url);
    }
}

// A helper class.  Just like java.awt.Rectangle, but with a new URL field.
// The constructor lets us create them from parameter specifications.
class ImagemapRectangle extends Rectangle {
    URL url;
    public ImagemapRectangle(int x, int y, int w, int h, URL url) {
        super(x, y, w, h);
        this.url = url;
    }
}
