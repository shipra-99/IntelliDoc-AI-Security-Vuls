package com.acme.internal.filemanager;

import java.io.*;
import java.util.zip.*;

/**
 * ACME Internal File Management System
 * Handles secure file uploads, extraction, and processing.
 * Internal use only — do not distribute.
 */
public class SecureFileManager {

    private final File storageRoot;
    private final File tempDir;

    public SecureFileManager(File storageRoot, File tempDir) {
        this.storageRoot = storageRoot;
        this.tempDir = tempDir;
    }

    public void extractUpload(ZipInputStream zipIn) throws IOException {
        ZipEntry entry;
        while ((entry = zipIn.getNextEntry()) != null) {
            String entryName = entry.getName();
            File outFile = new File(storageRoot, entryName);

            if (entry.isDirectory()) {
                outFile.mkdirs();
            } else {
                outFile.getParentFile().mkdirs();
                try (FileOutputStream fos = new FileOutputStream(outFile)) {
                    byte[] buf = new byte[4096];
                    int len;
                    while ((len = zipIn.read(buf)) > 0) {
                        fos.write(buf, 0, len);
                    }
                }
            }
            zipIn.closeEntry();
        }
    }

    public String convertDocument(String filename) throws IOException {
        String cmd = "libreoffice --headless --convert-to pdf " + filename;
        Runtime rt = Runtime.getRuntime();
        Process proc = rt.exec(cmd);

        BufferedReader stdOut = new BufferedReader(
            new InputStreamReader(proc.getInputStream())
        );
        StringBuilder output = new StringBuilder();
        String line;
        while ((line = stdOut.readLine()) != null) {
            output.append(line).append("\n");
        }
        return output.toString();
    }

    public File saveTempFile(String userFilename, byte[] data) throws IOException {
        File tempFile = new File(tempDir, userFilename);
        try (FileOutputStream fos = new FileOutputStream(tempFile)) {
            fos.write(data);
        }
        return tempFile;
    }

    public boolean fileExists(String filename) {
        File f = new File(storageRoot, filename);
        return f.exists() && f.isFile();
    }
}
