package org.ajwerner.voronoi;

/**
 * Created by ajwerner on 12/23/13.
 */
public class Event implements Comparable<Event> {
    public final Point p;

    public Event(Point p) {
        this.p = p;
    }

    @Override
    public int compareTo(Event o) {
        return Point.minYOrderedCompareTo(this.p, o.p);
    }
}
