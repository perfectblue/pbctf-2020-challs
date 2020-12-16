package org.ajwerner.voronoi;

// import edu.princeton.cs.introcs.StdDraw;
// import edu.princeton.cs.introcs.StdStats;
// import edu.princeton.cs.introcs.Stopwatch;

import java.util.*;
import java.util.Map.Entry;

/**
 * Created by ajwerner on 12/23/13.
 */
public class Voronoi {
    public static final double MIN_DRAW_DIM = -5;
    public static final double MAX_DRAW_DIM = 5;
    // Ghetto but just for drawing stuff
    private static final double MAX_DIM = 10;
    private static final double MIN_DIM = -10;
    private double sweepLoc;
    public final List<Point> sites;
    public final List<VoronoiEdge> edgeList;
    public HashSet<BreakPoint> breakPoints;
    private TreeMap<ArcKey, CircleEvent> arcs;
    private TreeSet<Event> events;

    public double getSweepLoc() {
        return sweepLoc;
    }

    // public static void main(String[] args) {
    //     if (args.length > 0) {
    //         int N = Integer.parseInt(args[0]);
    //         ArrayList<Point> sites = new ArrayList<>();
    //         Random rnd = new Random();
    //         for (int i = 0; i < N; i++) {
    //             sites.add(new Point(rnd.nextDouble(), rnd.nextDouble()));
    //         }
    //         // StdDraw.setCanvasSize(1024, 1024);
    //         // StdDraw.setScale(-.1, 1.1);
    //         Voronoi v = new Voronoi(sites);
    //         // v.show();
    //     }
    //     else {
    //         int numTrials = 5;
    //         System.out.println("         N:   \ttime (s)");
    //         int[] Ns = {50000, 100000, 200000, 400000, 800000, 1600000, 3200000};
    //         for (int n : Ns) {
    //             double res[] = new double[numTrials];
    //             for (int i = 0; i < numTrials; i++) {
    //                 res[i] = randomTrial(n);
    //             }
    //             // System.out.printf("%10d:\t%-5.6f +/- %f \n", n, StdStats.mean(res), StdStats.stddev(res)/Math.sqrt(numTrials));
    //         }
    //     }
    // }

    // private static double randomTrial(int N) {
    //     Random rnd = new Random();
    //     ArrayList<Point> sites = new ArrayList<>();
    //     // Stopwatch s = new Stopwatch();
    //     double stop, start;
    //     sites.clear();
    //     for (int i = 0; i < N; i++) {
    //         sites.add(new Point(rnd.nextDouble(), rnd.nextDouble()));
    //     }
    //     // start = s.elapsedTime();
    //     Voronoi v = new Voronoi(sites);
    //     // stop = s.elapsedTime();
    //
    //     // return stop-start;
    //     return 0.d;
    // }

    public Voronoi(List<Point> sites) {
        // initialize data structures;
        this.sites = sites;
        edgeList = new ArrayList<>(sites.size());
        events = new TreeSet<>();
        breakPoints = new HashSet<>();
        arcs = new TreeMap<>();

        for (Point site : sites) {
            if ((site.x > MAX_DIM || site.x < MIN_DIM) || (site.y > MAX_DIM || site.y < MIN_DIM))
                throw new RuntimeException(String.format(
                    "Invalid site in input, sites must be between %f and %f", MIN_DIM, MAX_DIM ));
            events.add(new Event(site));
        }
        sweepLoc = MAX_DIM;
        do {
            Event cur = events.pollFirst();
            sweepLoc = cur.p.y;
            // if (animate) this.draw();
            if (cur.getClass() == Event.class) {
                handleSiteEvent(cur);
            }
            else {
                CircleEvent ce = (CircleEvent) cur;
                handleCircleEvent(ce);
            }
        } while ((events.size() > 0));

        this.sweepLoc = MIN_DIM; // hack to draw negative infinite points
        for (BreakPoint bp : breakPoints) {
            bp.finish();
        }
    }

    private void handleSiteEvent(Event cur) {
        // Deal with first point case
        if (arcs.size() == 0) {
            arcs.put(new Arc(cur.p, this), null);
            return;
        }

        // Find the arc above the site
        Map.Entry<ArcKey, CircleEvent> arcEntryAbove = arcs.floorEntry(new ArcQuery(cur.p));
        Arc arcAbove = (Arc) arcEntryAbove.getKey();

        // Deal with the degenerate case where the first two points are at the same y value
        if (arcs.size() == 0 && arcAbove.site.y == cur.p.y) {
            VoronoiEdge newEdge = new VoronoiEdge(arcAbove.site, cur.p);
            newEdge.p1 = new Point((cur.p.x + arcAbove.site.x)/2, Double.POSITIVE_INFINITY);
            BreakPoint newBreak = new BreakPoint(arcAbove.site, cur.p, newEdge, false, this);
            breakPoints.add(newBreak);
            this.edgeList.add(newEdge);
            Arc arcLeft = new Arc(null, newBreak, this);
            Arc arcRight = new Arc(newBreak, null, this);
            arcs.remove(arcAbove);
            arcs.put(arcLeft, null);
            arcs.put(arcRight, null);
            return;
        }

        // Remove the circle event associated with this arc if there is one
        CircleEvent falseCE = arcEntryAbove.getValue();
        if (falseCE != null) {
            events.remove(falseCE);
        }

        BreakPoint breakL = arcAbove.left;
        BreakPoint breakR = arcAbove.right;
        VoronoiEdge newEdge = new VoronoiEdge(arcAbove.site, cur.p);
        this.edgeList.add(newEdge);
        BreakPoint newBreakL = new BreakPoint(arcAbove.site, cur.p, newEdge, true, this);
        BreakPoint newBreakR = new BreakPoint(cur.p, arcAbove.site, newEdge, false, this);
        breakPoints.add(newBreakL);
        breakPoints.add(newBreakR);

        Arc arcLeft = new Arc(breakL, newBreakL, this);
        Arc center = new Arc(newBreakL, newBreakR, this);
        Arc arcRight = new Arc(newBreakR, breakR, this);

        arcs.remove(arcAbove);
        arcs.put(arcLeft, null);
        arcs.put(center, null);
        arcs.put(arcRight, null);

        checkForCircleEvent(arcLeft);
        checkForCircleEvent(arcRight);
    }

    private void handleCircleEvent(CircleEvent ce) {
        arcs.remove(ce.arc);
        ce.arc.left.finish(ce.vert);
        ce.arc.right.finish(ce.vert);
        breakPoints.remove(ce.arc.left);
        breakPoints.remove(ce.arc.right);

        Entry<ArcKey, CircleEvent> entryRight = arcs.higherEntry(ce.arc);
        Entry<ArcKey, CircleEvent> entryLeft = arcs.lowerEntry(ce.arc);
        Arc arcRight = null;
        Arc arcLeft = null;

        Point ceArcLeft = ce.arc.getLeft();
        boolean cocircularJunction = ce.arc.getRight().equals(ceArcLeft);

        if (entryRight != null) {
            arcRight = (Arc) entryRight.getKey();
            while (cocircularJunction && arcRight.getRight().equals(ceArcLeft)) {
                arcs.remove(arcRight);
                arcRight.left.finish(ce.vert);
                arcRight.right.finish(ce.vert);
                breakPoints.remove(arcRight.left);
                breakPoints.remove(arcRight.right);

                CircleEvent falseCe = entryRight.getValue();
                if (falseCe != null) {
                    events.remove(falseCe);
                }

                entryRight = arcs.higherEntry(arcRight);
                arcRight = (Arc) entryRight.getKey();
            }

            CircleEvent falseCe = entryRight.getValue();
            if (falseCe != null) {
                events.remove(falseCe);
                arcs.put(arcRight, null);
            }
        }
        if (entryLeft != null) {
            arcLeft = (Arc) entryLeft.getKey();
            while (cocircularJunction && arcLeft.getLeft().equals(ceArcLeft)) {
                arcs.remove(arcLeft);
                arcLeft.left.finish(ce.vert);
                arcLeft.right.finish(ce.vert);
                breakPoints.remove(arcLeft.left);
                breakPoints.remove(arcLeft.right);

                CircleEvent falseCe = entryLeft.getValue();
                if (falseCe != null) {
                    events.remove(falseCe);
                }

                entryLeft = arcs.lowerEntry(arcLeft);
                arcLeft = (Arc) entryLeft.getKey();
            }

            CircleEvent falseCe = entryLeft.getValue();
            if (falseCe != null) {
                events.remove(falseCe);
                arcs.put(arcLeft, null);
            }
        }

        VoronoiEdge e = new VoronoiEdge(arcLeft.right.s1, arcRight.left.s2);
        edgeList.add(e);

        // Here we're trying to figure out if the org.ajwerner.voronoi.Voronoi vertex
        // we've found is the left
        // or right point of the new edge.
        // If the edges being traces out by these two arcs take a right turn then we
        // know
        // that the vertex is going to be above the current point
        boolean turnsLeft = Point.ccw(arcLeft.right.edgeBegin, ce.p, arcRight.left.edgeBegin) == 1;
        // So if it turns left, we know the next vertex will be below this vertex
        // so if it's below and the slow is negative then this vertex is the left point
        boolean isLeftPoint = (turnsLeft) ? (e.m < 0) : (e.m > 0);
        if (isLeftPoint) {
            e.p1 = ce.vert;
        } else {
            e.p2 = ce.vert;
        }

        BreakPoint newBP = new BreakPoint(arcLeft.right.s1, arcRight.left.s2, e, !isLeftPoint, this);
        breakPoints.add(newBP);

        arcRight.left = newBP;
        arcLeft.right = newBP;

        checkForCircleEvent(arcLeft);
        checkForCircleEvent(arcRight);
    }

    private void checkForCircleEvent(Arc a) {
        Point circleCenter = a.checkCircle();
        if (circleCenter != null) {
            double radius = a.site.distanceTo(circleCenter);
            Point circleEventPoint = new Point(circleCenter.x, circleCenter.y - radius);
            CircleEvent ce = new CircleEvent(a, circleEventPoint, circleCenter);
            arcs.put(a, ce);
            events.add(ce);
        }
    }

    // private void show() {
    //     StdDraw.clear();
    //     for (Point p : sites) {
    //         p.draw(StdDraw.RED);
    //     }
    //     for (VoronoiEdge e : edgeList) {
    //         if (e.p1 != null && e.p2 != null) {
    //             double topY = (e.p1.y == Double.POSITIVE_INFINITY) ? MAX_DIM : e.p1.y; // HACK to draw from infinity
    //             StdDraw.line(e.p1.x, topY, e.p2.x, e.p2.y);
    //         }
    //     }
    //     StdDraw.show();
    // }
    //
    // private void draw() {
    //     StdDraw.clear();
    //     for (Point p : sites) {
    //         p.draw(StdDraw.RED);
    //     }
    //     for (BreakPoint bp : breakPoints) {
    //         bp.draw();
    //     }
    //     for (ArcKey a : arcs.keySet()) {
    //         ((Arc) a).draw();
    //     }
    //     for (VoronoiEdge e : edgeList) {
    //         if (e.p1 != null && e.p2 != null) {
    //             double topY = (e.p1.y == Double.POSITIVE_INFINITY) ? MAX_DIM : e.p1.y; // HACK to draw from infinity
    //             StdDraw.line(e.p1.x, topY, e.p2.x, e.p2.y);
    //         }
    //     }
    //     StdDraw.line(MIN_DIM, sweepLoc, MAX_DIM, sweepLoc);
    //     StdDraw.show(1);
    // }
}

