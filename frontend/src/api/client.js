import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "";

/**
 * Upload a sales file and email address to the backend.
 * @param {File}   file  - The CSV or XLSX file
 * @param {string} email - Recipient email address
 * @returns {Promise<{message: string, recipient: string, rows_analyzed: number}>}
 */
export async function uploadSalesFile(file, email) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("email", email);

  const response = await axios.post(`${BASE_URL}/api/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

  return response.data;
}
