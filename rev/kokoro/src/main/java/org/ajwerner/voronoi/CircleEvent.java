package org.ajwerner.voronoi;

// import edu.princeton.cs.introcs.StdDraw;

/**
 * Created by ajwerner on 12/28/13.
 */
public class CircleEvent extends Event {
    public final Arc arc;
    public final Point vert;

    public CircleEvent(Arc a, Point p, Point vert) {
        super(p);
        this.arc = a;
        this.vert = vert;
    }

    // public void draw() {
    //     this.p.draw(StdDraw.GREEN);
    //     StdDraw.circle(vert.x, vert.y, (vert.y - p.y));
    // }
}
