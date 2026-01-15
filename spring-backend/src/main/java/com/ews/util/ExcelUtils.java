package com.ews.util;

import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.springframework.web.multipart.MultipartFile;
import java.io.*;
import java.util.*;

public class ExcelUtils {

    public static File convertToCSV(MultipartFile excelFile, String outputPath) throws IOException {
        Workbook workbook = null;
        FileWriter csvWriter = null;

        try {
            // Determine Excel type
            String filename = excelFile.getOriginalFilename();
            InputStream inputStream = excelFile.getInputStream();

            if (filename.endsWith(".xlsx")) {
                workbook = new XSSFWorkbook(inputStream);
            } else if (filename.endsWith(".xls")) {
                workbook = new HSSFWorkbook(inputStream);
            } else {
                throw new IllegalArgumentException("Invalid Excel file format");
            }

            // Get first sheet
            Sheet sheet = workbook.getSheetAt(0);
            csvWriter = new FileWriter(outputPath);

            // Convert to CSV
            for (Row row : sheet) {
                List<String> cellValues = new ArrayList<>();

                for (Cell cell : row) {
                    cellValues.add(getCellValueAsString(cell));
                }

                csvWriter.write(String.join(",", cellValues) + "\n");
            }

            csvWriter.flush();
            return new File(outputPath);

        } finally {
            if (workbook != null) workbook.close();
            if (csvWriter != null) csvWriter.close();
        }
    }

    private static String getCellValueAsString(Cell cell) {
        if (cell == null) return "";

        switch (cell.getCellType()) {
            case STRING:
                return cell.getStringCellValue();
            case NUMERIC:
                if (DateUtil.isCellDateFormatted(cell)) {
                    return cell.getDateCellValue().toString();
                }
                return String.valueOf(cell.getNumericCellValue());
            case BOOLEAN:
                return String.valueOf(cell.getBooleanCellValue());
            case FORMULA:
                return cell.getCellFormula();
            default:
                return "";
        }
    }
}