/**
 * =========================================================================
 * Sai Seva FMSC - Coordinator Google Sheet Auto-Sync Script
 * Coordinator: Manjunatha Arasaiah (Saibaba Group Phoenix SSSGC)
 * =========================================================================
 * 
 * HOW TO SET THIS UP (Takes 2 minutes):
 * 1. Open Google Sheets (https://sheets.new)
 * 2. Rename sheet to: "Sai Center - FMSC Volunteer Roster"
 * 3. In menu, click: Extensions > Apps Script
 * 4. Delete any code in the editor, paste this entire script, and click the Save icon.
 * 5. Click the blue "Deploy" button (top right) > "New deployment"
 * 6. Click the gear icon next to "Select type" > choose "Web app"
 * 7. Set Description: "Sai FMSC Webhook"
 * 8. Set "Execute as": "Me"
 * 9. Set "Who has access": "Anyone"  <-- CRITICAL so portal submissions work
 * 10. Click "Deploy", review/grant Google permissions.
 * 11. Copy the "Web app URL" (ends with /exec) and paste it into your portal Admin tab!
 * =========================================================================
 */

function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({
      status: "active",
      message: "Om Sri Sai Ram! Sai FMSC Coordinator Webhook is active and healthy.",
      timestamp: new Date().toISOString()
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  // Wait up to 10 seconds for other submissions to avoid race conditions
  lock.tryLock(10000);
  
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getActiveSheet();
    
    // Parse JSON payload or URL parameters
    var data = {};
    if (e && e.postData && e.postData.contents) {
      try {
        data = JSON.parse(e.postData.contents);
      } catch (parseErr) {
        data = e.parameter || {};
      }
    } else if (e && e.parameter) {
      data = e.parameter;
    }
    
    // Ensure header row exists
    if (sheet.getLastRow() === 0) {
      var headers = [
        "Logged Timestamp",
        "Seva Date",
        "Seva Time",
        "Volunteer / Family Name",
        "WhatsApp / Phone",
        "Email",
        "Adults",
        "Kids (5+)",
        "Kids Ages",
        "Total Count",
        "Carpool / Transport",
        "FMSC.org Registered?",
        "Notes for Coordinator"
      ];
      sheet.appendRow(headers);
      
      // Style Header
      var headerRange = sheet.getRange(1, 1, 1, headers.length);
      headerRange.setFontWeight("bold");
      headerRange.setBackground("#0f172a"); // Dark slate
      headerRange.setFontColor("#f59e0b"); // Sai Gold / Amber
      sheet.setFrozenRows(1);
      
      // Auto-adjust column widths
      for (var c = 1; c <= headers.length; c++) {
        sheet.setColumnWidth(c, 150);
      }
      sheet.setColumnWidth(4, 200); // Name
      sheet.setColumnWidth(13, 250); // Notes
    }
    
    var adults = parseInt(data.adults_count || 1, 10);
    var kids = parseInt(data.kids_count || 0, 10);
    var totalCount = adults + kids;
    
    // Format timestamp in Arizona Phoenix MST time
    var timestamp = Utilities.formatDate(new Date(), "America/Phoenix", "yyyy-MM-dd hh:mm:ss a");
    
    var row = [
      timestamp,
      data.session_date || data.date_formatted || data.date || "Upcoming Seva",
      data.session_time || data.time || "2:30 PM - 4:00 PM",
      data.name || "Anonymous Devotee",
      data.phone || "",
      data.email || "",
      adults,
      kids,
      data.kids_ages || "",
      totalCount,
      data.carpool || "Driving Independently",
      data.registered_on_fmsc ? "Yes (FMSC Reserved)" : "Pending FMSC Reservation",
      data.notes || ""
    ];
    
    sheet.appendRow(row);
    
    // Format the newly appended row
    var lastRow = sheet.getLastRow();
    sheet.getRange(lastRow, 1, 1, row.length).setVerticalAlignment("middle");
    
    return ContentService
      .createTextOutput(JSON.stringify({
        status: "success",
        message: "Volunteer details logged successfully to Google Sheet",
        row: lastRow
      }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({
        status: "error",
        message: error.toString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
