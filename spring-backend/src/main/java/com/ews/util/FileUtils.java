package com.ews.util;

import org.springframework.web.multipart.MultipartFile;
import java.io.File;
import java.io.IOException;
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;

public class FileUtils {

    public static File saveFile(MultipartFile multipartFile, String path) throws IOException {
        File file = new File(path);
        file.getParentFile().mkdirs();
        multipartFile.transferTo(file);
        return file;
    }

    public static void deleteDirectory(Path path) throws IOException {
        if (Files.exists(path)) {
            Files.walkFileTree(path, new SimpleFileVisitor<Path>() {
                @Override
                public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) throws IOException {
                    Files.delete(file);
                    return FileVisitResult.CONTINUE;
                }

                @Override
                public FileVisitResult postVisitDirectory(Path dir, IOException exc) throws IOException {
                    Files.delete(dir);
                    return FileVisitResult.CONTINUE;
                }
            });
        }
    }

    public static boolean isValidFileType(String filename) {
        String lowerCase = filename.toLowerCase();
        return lowerCase.endsWith(".csv") ||
                lowerCase.endsWith(".xlsx") ||
                lowerCase.endsWith(".xls");
    }
}