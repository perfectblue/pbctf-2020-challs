package blue.perfect.kokoro;

import org.ajwerner.voronoi.Point;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;

public class VoronoiPolygon {
    public final Point site;
    public final List<Point> points;
    public final byte color[];
    public float rotation;
    public double offX, offY;

    public VoronoiPolygon(Point site) {
        this.site = site;
        this.color = new byte[3];
        points = new ArrayList<>();
        rotation = 0.f;
    }

    public void sortPoints() {
        //unique
        HashSet<Point> pts = new HashSet<>(points);
        points.clear();
        points.addAll(pts);
        //sort by angle
        points.sort(Comparator.comparingDouble(e -> Math.atan2(e.y - site.y, e.x - site.x)));
    }

    public void translate(double dx, double dy) {
        this.offX += dx;
        this.offY += dy;
    }

    public void rotate(float dr) {
        this.rotation += dr;
        while (this.rotation >= 360f) {
            this.rotation -= 360.f;
        }
        while (this.rotation < 0.f) {
            this.rotation += 360.f;
        }
    }

    public Point getTranslatedSite() {
        return site.translate(offX, offY);
    }

    public boolean isRotated() {
        return Math.abs(rotation) <= 1.f;
    }

    public boolean isSolved() {
        // 1% margin of error on x and y
        // System.out.println(" " + offX + " " + offY + " " + rotation);
        return Math.abs(offX) <= 0.01 && Math.abs(offY) <= 0.01 && isRotated();
    }
}
