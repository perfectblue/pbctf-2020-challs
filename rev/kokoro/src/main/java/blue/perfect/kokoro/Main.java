/*
 * Copyright LWJGL. All rights reserved.
 * License terms: https://www.lwjgl.org/license
 */
package blue.perfect.kokoro;

import org.ajwerner.voronoi.Point;
import org.ajwerner.voronoi.Voronoi;
import org.ajwerner.voronoi.VoronoiEdge;
import org.lwjgl.glfw.*;
import org.lwjgl.opengl.*;
import org.lwjgl.system.*;

import java.io.*;
import java.nio.*;
import java.security.SecureRandom;
import java.util.*;

import static java.lang.Math.*;
import static org.lwjgl.BufferUtils.createByteBuffer;
import static org.lwjgl.glfw.Callbacks.*;
import static org.lwjgl.glfw.GLFW.*;
import static org.lwjgl.opengl.GL11.*;
import static org.lwjgl.opengl.GL12.*;
import static org.lwjgl.stb.STBImage.*;
import static org.lwjgl.stb.STBImageResize.*;
import static org.lwjgl.system.MemoryStack.*;
import static org.lwjgl.system.MemoryUtil.*;

import org.lwjgl.*;

import java.nio.channels.*;
import java.nio.file.*;

public final class Main {

    private ByteBuffer image;

    private int w;
    private int h;
    private int comp;

    private long window;
    private int ww;
    private int wh;

    private boolean ctrlDown;

    private int scale;

    private Callback debugProc;

    public static ByteBuffer ioResourceToByteBuffer(String resource, int bufferSize) throws IOException {
        ByteBuffer buffer;

        Path path = Paths.get(resource);
        if (Files.isReadable(path)) {
            try (SeekableByteChannel fc = Files.newByteChannel(path)) {
                buffer = createByteBuffer((int)fc.size() + 1);
                while (fc.read(buffer) != -1) {
                    ;
                }
            }
        } else {
            try (
                InputStream source = Main.class.getClassLoader().getResourceAsStream(resource);
                ReadableByteChannel rbc = Channels.newChannel(source)
            ) {
                buffer = createByteBuffer(bufferSize);

                while (true) {
                    int bytes = rbc.read(buffer);
                    if (bytes == -1) {
                        break;
                    }
                    if (buffer.remaining() == 0) {
                        buffer = resizeBuffer(buffer, buffer.capacity() * 3 / 2); // 50%
                    }
                }
            }
        }

        buffer.flip();
        return buffer;
    }

    private static ByteBuffer resizeBuffer(ByteBuffer buffer, int newCapacity) {
        ByteBuffer newBuffer = BufferUtils.createByteBuffer(newCapacity);
        buffer.flip();
        newBuffer.put(buffer);
        return newBuffer;
    }

    private VoronoiPolygon getPolygonUnder(Point p) {
        double bestD = Double.POSITIVE_INFINITY;
        VoronoiPolygon best = null;
        for (VoronoiPolygon shard : shards.values()) {
            double d = shard.getTranslatedSite().distanceTo(p);
            if (d <= bestD) {
                bestD = d;
                best = shard;
            }
        }
        return best;
    }

    Voronoi v;
    LinkedHashMap<Point, VoronoiPolygon> shards;
    long rng;
    private String flag;

    private void setupGame(int difficulty, long seed) {
        rng = seed;

        shards = new LinkedHashMap<>();
        List<Point> sites = new ArrayList<>();
        for (int i = 0; i < difficulty; i++) {
            rng ^= rng << 13;
            rng &= 0xffffffffL;
            rng ^= rng >>> 17;
            rng &= 0xffffffffL;
            rng ^= rng << 5;
            rng &= 0xffffffffL;
            double x = rng / (double)0xffffffffL;
            rng ^= rng << 13;
            rng &= 0xffffffffL;
            rng ^= rng >>> 17;
            rng &= 0xffffffffL;
            rng ^= rng << 5;
            rng &= 0xffffffffL;
            double y = rng / (double)0xffffffffL;
            // System.out.println("" + x + " " + y);
            Point site = new Point(x, y);
            sites.add(site);
            VoronoiPolygon shard = new VoronoiPolygon(site);
            shards.put(site, shard);
        }
        v = new Voronoi(sites);
        for (VoronoiEdge e : v.edgeList) {
            if (e.p1 != null && e.p2 != null) {
                shards.get(e.site1).points.add(e.p1);
                shards.get(e.site1).points.add(e.p2);
                shards.get(e.site2).points.add(e.p1);
                shards.get(e.site2).points.add(e.p2);
            }
        }
        shards.values().forEach(VoronoiPolygon::sortPoints);

        // now scramble it.
        for (VoronoiPolygon shard : shards.values()) {
            // dump all the pieces at the center
            shard.translate(0.5-shard.site.x, 0.5-shard.site.y);
            // random rotation
            rng ^= rng << 13;
            rng &= 0xffffffffL;
            rng ^= rng >>> 17;
            rng &= 0xffffffffL;
            rng ^= rng << 5;
            rng &= 0xffffffffL;
            shard.rotation = (rng % 36) * 10.f;

            // random color ;)
            rng ^= rng << 13;
            rng &= 0xffffffffL;
            rng ^= rng >>> 17;
            rng &= 0xffffffffL;
            rng ^= rng << 5;
            rng &= 0xffffffffL;
            long rgb = rng;
            shard.color[0] = (byte)((rgb >> 0) & 0xff);
            shard.color[1] = (byte)((rgb >> 8) & 0xff);
            shard.color[2] = (byte)((rgb >> 16) & 0xff);
            // System.out.println(Arrays.toString(shard.color));
        }
    }

    // private long next() {
    //     rng ^= rng << 13;
    //     rng &= 0xffffffffL;
    //     rng ^= rng >>> 17;
    //     rng &= 0xffffffffL;
    //     rng ^= rng << 5;
    //     rng &= 0xffffffffL;
    //     return rng;
    // }
    //
    // private double nextDouble() {
    //     return next() / (double)0xffffffffL;
    // }

    private Main(String imagePath, int difficulty) {
        flag = new ReadFlag().readFlag();

        long seed = new SecureRandom().nextLong();
        // System.out.println(seed);
        setupGame(difficulty, seed);

        ByteBuffer imageBuffer;
        try {
            imageBuffer = ioResourceToByteBuffer(imagePath, 8 * 1024);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        try (MemoryStack stack = stackPush()) {
            IntBuffer w = stack.mallocInt(1);
            IntBuffer h = stack.mallocInt(1);
            IntBuffer comp = stack.mallocInt(1);

            // Use info to read image metadata without decoding the entire image.
            // We don't need this for this demo, just testing the API.
            if (!stbi_info_from_memory(imageBuffer, w, h, comp)) {
                throw new RuntimeException("Failed to read image information: " + stbi_failure_reason());
            } else {
                System.out.println("Texture OK");
            }

            System.out.println("Image width: " + w.get(0));
            System.out.println("Image height: " + h.get(0));
            System.out.println("Image components: " + comp.get(0));
            System.out.println("Image HDR: " + stbi_is_hdr_from_memory(imageBuffer));

            // Decode the image
            image = stbi_load_from_memory(imageBuffer, w, h, comp, 0);
            if (image == null) {
                throw new RuntimeException("Failed to load image: " + stbi_failure_reason());
            }

            this.w = w.get(0);
            this.h = h.get(0);
            this.comp = comp.get(0);
        }
    }

    public static void main(String[] args) {
        String imagePath = args[0];
        int difficulty = Integer.parseInt(args[1]);
        new Main(imagePath, difficulty).run();
    }

    private void run() {
        try {
            init();

            loop();
        } finally {
            try {
                destroy();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    private void windowSizeChanged(long window, int width, int height) {
        this.ww = width;
        this.wh = height;

        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        glOrtho(0.0, width, height, 0.0, -1.0, 1.0);
        glMatrixMode(GL_MODELVIEW);
    }

    private static void framebufferSizeChanged(long window, int width, int height) {
        glViewport(0, 0, width, height);
    }

    double mouseX, mouseY;
    VoronoiPolygon selectedPolygon = null;

    private void checkSolved() {
        for (VoronoiPolygon shard : shards.values()) {
            if (!shard.isSolved())
                return;
        }
        // System.out.println("Win?");
        win();
    }

    private void win() {
        System.out.println("Congratulations. Here is your flag");
        System.out.println(flag);
        glfwSetWindowShouldClose(window, true);
    }

    private void init() {
        scale = 0;

        GLFWErrorCallback.createPrint().set();
        if (!glfwInit()) {
            throw new IllegalStateException("Unable to initialize GLFW");
        }

        glfwDefaultWindowHints();
        glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);
        glfwWindowHint(GLFW_RESIZABLE, GLFW_TRUE);
        // glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 2);
        // glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);

        // GLFWVidMode vidmode = Objects.requireNonNull(glfwGetVideoMode(glfwGetPrimaryMonitor()));

        // ww = max(800, min(w, vidmode.width() - 160));
        // wh = max(600, min(h, vidmode.height() - 120));
		ww = 800;
		wh = 800;

        this.window = glfwCreateWindow(ww, wh, "Kokoro", NULL, NULL);
        if (window == NULL) {
            throw new RuntimeException("Failed to create the GLFW window");
        }

        glfwSetWindowSize(this.window, ww, wh);

        // Center window
        // glfwSetWindowPos(
        //         window,
        //         (vidmode.width() - ww) / 2,
        //         (vidmode.height() - wh) / 2
        // );

        glfwSetWindowRefreshCallback(window, window -> render());
        glfwSetWindowSizeCallback(window, this::windowSizeChanged);
        glfwSetFramebufferSizeCallback(window, Main::framebufferSizeChanged);

        glfwSetKeyCallback(window, (window, key, scancode, action, mods) -> {
            ctrlDown = (mods & GLFW_MOD_CONTROL) != 0;
            if (action == GLFW_RELEASE) {
                return;
            }

            switch (key) {
            case GLFW_KEY_ESCAPE:
                glfwSetWindowShouldClose(window, true);
                break;
            case GLFW_KEY_KP_ADD:
            case GLFW_KEY_EQUAL:
                // setScale(scale + 1);
                break;
            case GLFW_KEY_KP_SUBTRACT:
            case GLFW_KEY_MINUS:
                // setScale(scale - 1);
                break;
            case GLFW_KEY_0:
            case GLFW_KEY_KP_0:
                if (ctrlDown) {
                    // setScale(0);
                }
                break;
            }
        });
        glfwSetMouseButtonCallback(window, (window, button, action, mods) -> {
            // DoubleBuffer posX = BufferUtils.createDoubleBuffer(1);
            // DoubleBuffer posY = BufferUtils.createDoubleBuffer(1);
            // glfwGetCursorPos(window, posX, posY);
            // System.out.println("" + button + " " + action + " " + mouseX + " " + mouseY);
            if (button == 0) {
                if (action == GLFW_PRESS) {
                    selectedPolygon = getPolygonUnder(new Point(mouseX, mouseY));
                    shards.remove(selectedPolygon.site);
                    shards.put(selectedPolygon.site, selectedPolygon);
                    // selectedPolygon.rotation += 2.f;
                } else if (action == GLFW_RELEASE) {
                    selectedPolygon = null;
                    checkSolved();
                }
            }
            // GLFW_PRESS GLFW_RELEASE
        });
        glfwSetCursorPosCallback(window, (window, x, y) -> {
            double newX = x/w;
            double newY = y/h;
            if (selectedPolygon != null) {
                double dx = newX - mouseX;
                double dy = newY - mouseY;
                selectedPolygon.translate(dx, dy);
            }
            mouseX = newX;
            mouseY = newY;
        });

        glfwSetScrollCallback(window, (window, xoffset, yoffset) -> {
            if (selectedPolygon != null) {
                selectedPolygon.rotate((float)yoffset*10.f);
                checkSolved();
            }
        });

        // Create context
        glfwMakeContextCurrent(window);
        GL.createCapabilities();
        debugProc = GLUtil.setupDebugMessageCallback();

        glfwSwapInterval(1);
        glfwShowWindow(window);

        // glfwInvoke(window, this::windowSizeChanged, Main::framebufferSizeChanged);
    }

    private void setScale(int scale) {
        this.scale = max(-9, scale);
    }

    private void premultiplyAlpha() {
        int stride = w * 4;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                int i = y * stride + x * 4;

                float alpha = (image.get(i + 3) & 0xFF) / 255.0f;
                image.put(i + 0, (byte) round(((image.get(i + 0) & 0xFF) * alpha)));
                image.put(i + 1, (byte) round(((image.get(i + 1) & 0xFF) * alpha)));
                image.put(i + 2, (byte) round(((image.get(i + 2) & 0xFF) * alpha)));
            }
        }
    }

    private int createTexture() {
        int texID = glGenTextures();

        glBindTexture(GL_TEXTURE_2D, texID);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

        int format;
        if (comp == 3) {
            if ((w & 3) != 0) {
                glPixelStorei(GL_UNPACK_ALIGNMENT, 2 - (w & 1));
            }
            format = GL_RGB;
        } else {
            premultiplyAlpha();

            glEnable(GL_BLEND);
            glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA);

            format = GL_RGBA;
        }

        glTexImage2D(GL_TEXTURE_2D, 0, format, w, h, 0, format, GL_UNSIGNED_BYTE, image);

        ByteBuffer input_pixels = image;
        int input_w = w;
        int input_h = h;
        int mipmapLevel = 0;
        while (1 < input_w || 1 < input_h) {
            int output_w = Math.max(1, input_w >> 1);
            int output_h = Math.max(1, input_h >> 1);

            ByteBuffer output_pixels = memAlloc(output_w * output_h * comp);
            stbir_resize_uint8_generic(
                    input_pixels, input_w, input_h, input_w * comp,
                    output_pixels, output_w, output_h, output_w * comp,
                    comp, comp == 4 ? 3 : STBIR_ALPHA_CHANNEL_NONE, STBIR_FLAG_ALPHA_PREMULTIPLIED,
                    STBIR_EDGE_CLAMP,
                    STBIR_FILTER_MITCHELL,
                    STBIR_COLORSPACE_SRGB
            );

            if (mipmapLevel == 0) {
                stbi_image_free(image);
            } else {
                memFree(input_pixels);
            }

            glTexImage2D(GL_TEXTURE_2D, ++mipmapLevel, format, output_w, output_h, 0, format, GL_UNSIGNED_BYTE, output_pixels);

            input_pixels = output_pixels;
            input_w = output_w;
            input_h = output_h;
        }
        if (mipmapLevel == 0) {
            stbi_image_free(image);
        } else {
            memFree(input_pixels);
        }

        return texID;
    }

    private void loop() {
        int texID = createTexture();

		windowSizeChanged(this.window, ww, wh); // fix the fucking viewport

        glClearColor(0.1f,0.1f,0.1f,0.f);

        glPointSize(3.f); // set the point size to 3px

        while (!glfwWindowShouldClose(window)) {
            glfwPollEvents();
            render();
        }

        glDeleteTextures(texID);
    }

    private void render() {
        glClear(GL_COLOR_BUFFER_BIT);

        float scaleFactor = 1.0f + scale * 0.1f;

        glPushMatrix();

        // scale at center of image
        // glTranslatef(ww * 0.5f, wh * 0.5f, 0.0f);
        // glScalef(scaleFactor, scaleFactor, 1f);
        // glTranslatef(-ww * 0.5f, -wh * 0.5f, 0.0f);

        glScalef(w, h, 1f); // move to image coordinate space (0.0 to 1.0 on x and y -> w,h)



        for (VoronoiPolygon shard : shards.values()) {
            glPushMatrix();

            glTranslated(shard.offX, shard.offY, 0.d);

            Point site = shard.site;
            glTranslated(site.x, site.y, 0.d);
            glRotatef(shard.rotation, 0.f, 0.f, 1.f);
            glTranslated(-site.x, -site.y, 0.d);

            // float[] rgb = shard.color;
            // glColor3f(rgb[0], rgb[1], rgb[2]);
            // glBegin(GL_LINES);
            // {
            //     for (VoronoiEdge e : shard.edges) {
            //         glVertex2d(e.p1.x, e.p1.y);
            //         glVertex2d(e.p2.x, e.p2.y);
            //     }
            // }
            // glEnd();
            // float i = 1.f;

            glColor4f(1.f,1.f,1.f,1.f);
            glEnable(GL_TEXTURE_2D);

            glBegin(GL_TRIANGLE_FAN);
            {
                glTexCoord2d(site.x, site.y);
                glVertex2d(site.x, site.y);
                for (Point p : shard.points) {
                    glTexCoord2d(p.x, p.y);
                    // glColor3f(rgb[0]*i, rgb[1]*i, rgb[2]*i);
                    glVertex2d(p.x, p.y);
                    // i -= 0.1f;
                }
                // loop back around to the first one to complete the polygon
                Point p = shard.points.get(0);
                // glColor3f(rgb[0]*i, rgb[1]*i, rgb[2]*i);
                glTexCoord2d(p.x, p.y);
                glVertex2d(p.x, p.y);

                // glTexCoord2f(0.0f, 0.0f);
                // glVertex2f(0.0f, 0.0f);
                //
                // glTexCoord2f(1.0f, 0.0f);
                // glVertex2f(1.0f, 0.0f);
                //
                // glTexCoord2f(1.0f, 1.0f);
                // glVertex2f(1.0f, 1.0f);
                //
                // glTexCoord2f(0.0f, 1.0f);
                // glVertex2f(0.0f, 1.0f);
            }
            glEnd();

            glDisable(GL_TEXTURE_2D);

            glColor3f(1.f,0.f,0.f);
            glBegin(GL_LINE_STRIP);
            {
                for (Point p : shard.points) {
                    glVertex2d(p.x, p.y);
                }
                // loop back around to the first one to complete the polygon
                Point p = shard.points.get(0);
                glVertex2d(p.x, p.y);
            }
            glEnd();

            glPopMatrix();
        }

        glPushAttrib(GL_CURRENT_BIT); //GL_POINT_BIT

        // hax
        glColor3f(0.f, 1.f, 0.f);
        glBegin(GL_LINES);
        {
            for (VoronoiEdge e : v.edgeList) {
                if (e.p1 != null && e.p2 != null) {
                    if (shards.get(e.site1).isRotated() && shards.get(e.site2).isRotated()) {
                        glVertex2d(e.p1.x, e.p1.y);
                        glVertex2d(e.p2.x, e.p2.y);
                    }
                }
            }
        }
        glEnd();

        glBegin(GL_POINTS);
        {
            // hax
            // for (Point site : v.sites) {
            //     if (shards.get(site).isRotated()) {
            //         glVertex2d(site.x, site.y);
            //     }
            // }

            // Because it's a linkedhashmap, the topmost shard will always be on top
            // This makes the challenge much easier to solve
            for (VoronoiPolygon shard : shards.values()) {
                byte[] rgb = shard.color;
                glColor3ub(rgb[0],rgb[1],rgb[2]);
                Point p = shard.getTranslatedSite();
                glVertex2d(p.x, p.y);
            }

            // glColor3f(1.f,1.f,1.f);
            // glVertex2d(mouseX, mouseY);
        }
        glEnd();
        glPopAttrib();

        glPopMatrix();

        glfwSwapBuffers(window);
    }

    private void destroy() {
        if (debugProc != null) {
            debugProc.free();
        }

        glfwFreeCallbacks(window);
        glfwDestroyWindow(window);
        glfwTerminate();
        Objects.requireNonNull(glfwSetErrorCallback(null)).free();
    }

}