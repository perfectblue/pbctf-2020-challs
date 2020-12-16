package org.ajwerner.voronoi;

/**
 * Created by ajwerner on 12/29/13.
 */
public class ArcQuery extends ArcKey {
    private final Point p;
    public ArcQuery(Point p) {
        this.p = p;
    }

    protected Point getLeft() {
        return p;
    }

    protected Point getRight() {
        return p;
    }
}
