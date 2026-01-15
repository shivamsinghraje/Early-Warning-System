package com.ews.util;

import com.ews.dto.CleanRequest;
import com.opencsv.CSVReader;
import com.opencsv.CSVWriter;
import java.io.*;
import java.util.*;

public class CSVUtils {

    public static boolean validateColumns(File csvFile, CleanRequest request) {
        try (CSVReader reader = new CSVReader(new FileReader(csvFile))) {
            String[] headers = reader.readNext();
            if (headers == null) return false;

            Set<String> headerSet = new HashSet<>(Arrays.asList(headers));

            // Check required columns
            if (!headerSet.contains(request.getDatetimeCol())) return false;
            if (!headerSet.contains(request.getTargetCol())) return false;

            for (String gndCol : request.getGndCols()) {
                if (!headerSet.contains(gndCol)) return false;
            }

            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public static Map<String, Object> getCSVInfo(File csvFile) {
        Map<String, Object> info = new HashMap<>();
        try (CSVReader reader = new CSVReader(new FileReader(csvFile))) {
            String[] headers = reader.readNext();
            info.put("columns", Arrays.asList(headers));

            int rowCount = 0;
            while (reader.readNext() != null) {
                rowCount++;
            }
            info.put("rowCount", rowCount);

        } catch (Exception e) {
            info.put("error", e.getMessage());
        }
        return info;
    }
}