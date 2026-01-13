import { useState } from 'react'
import * as XLSX from 'xlsx'
import './App.css'

function App() {
  const [poNumber, setPoNumber] = useState('')
  const [lineItems, setLineItems] = useState([])
  const [selectedIndices, setSelectedIndices] = useState(new Set())
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [fileName, setFileName] = useState('')
  const [hasProcessed, setHasProcessed] = useState(false)

  const handleFileChange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type
    const validTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
    if (!validTypes.includes(file.type) && !file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      setMessage({ type: 'error', text: 'Please upload an Excel file (.xlsx, .xls).' })
      return
    }

    setFileName(file.name)
    setMessage({ type: '', text: '' })
    setHasProcessed(false)

    try {
      const data = await file.arrayBuffer()
      const workbook = XLSX.read(data, { cellDates: true })
      const worksheet = workbook.Sheets[workbook.SheetNames[0]]
      const rawData = XLSX.utils.sheet_to_json(worksheet, { defval: '' })

      // Ensure we have some data
      if (rawData.length === 0) {
        setMessage({ type: 'error', text: 'The uploaded Excel file is empty.' })
        setLineItems([])
        return
      }

      // Format Date objects to YYYY-MM-DD strings and initialize Status
      const itemsWithStatus = rawData.map(item => {
        const newItem = { ...item, Status: '' };
        // Check for Date objects and convert them
        Object.keys(newItem).forEach(key => {
          if (newItem[key] instanceof Date) {
            // Adjust for timezone offset if necessary, or just use simple ISO date part
            // Using toISOString() uses UTC. Excel dates are usually "local" to the user's intent.
            // A safer way for pure dates often acts on local time.
            const d = newItem[key];
            // Simple YYYY-MM-DD format manually to avoid timezone shifts
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            newItem[key] = `${year}-${month}-${day}`;
          }
        });
        return newItem;
      });

      setLineItems(itemsWithStatus)

      // Select all by default or none? Let's select all by default for convenience
      const allIndices = new Set(itemsWithStatus.map((_, i) => i))
      setSelectedIndices(allIndices)

    } catch (error) {
      console.error('Error parsing Excel:', error)
      setMessage({ type: 'error', text: 'Failed to parse Excel file.' })
    }
  }

  const handleLineItemChange = (index, field, value) => {
    const updatedItems = [...lineItems]
    updatedItems[index] = { ...updatedItems[index], [field]: value }
    setLineItems(updatedItems)
  }

  const toggleSelectAll = (e) => {
    if (e.target.checked) {
      const allIndices = new Set(lineItems.map((_, i) => i))
      setSelectedIndices(allIndices)
    } else {
      setSelectedIndices(new Set())
    }
  }

  const toggleSelectRow = (index) => {
    const newSelected = new Set(selectedIndices)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedIndices(newSelected)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!poNumber.trim()) {
      setMessage({ type: 'error', text: 'Please enter a PO Number.' })
      return
    }

    if (selectedIndices.size === 0) {
      setMessage({ type: 'error', text: 'Please select at least one line item to submit.' })
      return
    }

    setIsSubmitting(true)
    setMessage({ type: 'info', text: 'Processing...' })

    try {
      const selectedLines = lineItems.filter((_, index) => selectedIndices.has(index))

      const mappedLines = selectedLines.map(row => {
        // Construct Schedule
        const schedule = {
          ScheduleNumber: 1,
          ProductType: row['Product Type'] || "Goods",
          Quantity: row['Quantity'],
          ShipToOrganization: row['Organization'],
          DestinationType: row['Destination Type'],
          //DestinationTypeCode: "EXPENSE", // Keeping hardcoded as per previous logic or should it be mapped? User example showed EXPENSE code.
          InvoiceMatchOption: row['Invoice Match Option'],
          InvoiceMatchOptionCode: "P", // Keeping hardcoded for now unless mapped
          MatchApprovalLevel: row['Match Approval Level'],
          ReceiptRequiredFlag: false,
          InspectionRequiredFlag: true,
          RequestedDeliveryDate: row['Requested Delivery Date'],

          // Nested Distribution
          distributions: [{
            DistributionNumber: 1,
            Quantity: row['Quantity'],
            POChargeAccount: row['Charge account'],
            DeliverToLocation: row['Deliver To Location'] || row['DeliverToLocation'],
            Requester: row['Requester'],
            // Map Project DFF if project fields are present
            projectDFF: (row['Project ID'] || row['_PROJECT_ID'] || row['Project Number']) ? [{
              _PROJECT_ID: row['Project ID'] || row['_PROJECT_ID'] || row['Project Number'],
              _EXPENDITURE_ITEM_DATE: row['Expenditure Item Date'] || row['_EXPENDITURE_ITEM_DATE'],
              _EXPENDITURE_TYPE_ID: row['Expenditure Type ID'] || row['_EXPENDITURE_TYPE_ID'] || row['Expenditure Type Name'] || row['Expenditure Name'],
              _ORGANIZATION_ID: row['Expenditure Organization ID'] || row['_ORGANIZATION_ID'] || row['Organization Name'] || row['Expenditure Organization'] || row['OrganizationName'],
              _TASK_ID: row['Task ID'] || row['_TASK_ID'],
              _CONTRACT_ID: row['Contract ID'] || row['_CONTRACT_ID']
            }] : []
          }]
        };

        return {
          LineNumber: row['LineNumber'],
          LineType: row['LineType'] || "Goods",
          Description: row['Description'],
          Category: row['Category'],
          //CategoryCode: row['Category Code'] || row['CategoryCode'],
          //UOM: row['UOM'],
          UOMCode: row['UOM'] || row['UOMCode'],
          Quantity: row['Quantity'],
          Price: row['Price'],
          Item: row['Item'],
          NegotiatedFlag: row['NegotiatedFlag'],
          schedules: [schedule]
        };
      });

      const payload = {
        poNumber: poNumber,
        lines: mappedLines
      }

      const backendUrl = `https://172.16.10.130:8000/process-lines`
      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      const data = await response.json()



      if (!response.ok && !data.errors) {
        throw new Error(data.detail || 'Submission failed')
      }

      let msgType = 'success';
      let msgText = data.message || `Successfully processed ${selectedLines.length} line items for PO ${poNumber}`

      // --- Update Statuses ---
      const newItems = [...lineItems];

      // 1. Mark all selected lines as Success initially (if overall success)
      if (response.ok) {
        // Mark all originally selected lines as Success. 
        // If any have errors, they will be overwritten in the next step.
        selectedIndices.forEach(index => {
          newItems[index] = { ...newItems[index], Status: 'Success' };
        });
      }

      // 2. Parse errors and update specific failures
      if (data.errors && data.errors.length > 0) {
        msgType = 'warning';
        const errorDetails = data.errors.join('\n');
        msgText += `\n\nErrors:\n${errorDetails}`;

        data.errors.forEach(errStr => {
          // Expected format: "Line {LineNumberValue}: {message}"
          const match = errStr.match(/Line ([^:]+):/);
          if (match) {
            const errorLineValue = match[1].trim();

            // Find the item(s) with this LineNumber in our list
            // Iterate through ALL items to be safe, or just selected ones. 
            // Since we know the LineNumber is unique per PO usually, findIndex is fine.
            const foundIndex = newItems.findIndex(item => String(item['LineNumber']) === String(errorLineValue));

            if (foundIndex !== -1) {
              newItems[foundIndex] = { ...newItems[foundIndex], Status: `Error: ${errStr}` };
            }
          }
        });
      }

      setLineItems(newItems);
      setHasProcessed(true);

      setMessage({
        type: msgType,
        text: msgText
      })
    } catch (error) {
      console.error('Submission error:', error)
      setMessage({ type: 'error', text: error.message || 'An error occurred during submission.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDownload = () => {
    if (lineItems.length === 0) return;
    const worksheet = XLSX.utils.json_to_sheet(lineItems);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "PO_Lines");
    const fname = poNumber ? `PO_Lines_${poNumber}.xlsx` : "PO_Lines_Status.xlsx";
    XLSX.writeFile(workbook, fname);
  };

  // Get headers from the first item if exists, ensure Status is first
  const headers = lineItems.length > 0 ? Object.keys(lineItems[0]).filter(k => k !== 'Status') : []


  return (
    <div className="app-container fade-in">
      <div className="glass-card" style={{ maxWidth: lineItems.length > 0 ? '90%' : '500px', transition: 'max-width 0.3s' }}>
        <h1>PO Line Import</h1>
        <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: 'var(--spacing-lg)' }}>
          Upload Excel and process line items
        </p>

        <form onSubmit={handleSubmit} className="po-form">
          <div className="form-group">
            <label htmlFor="po-number">Purchase Order Number</label>
            <input
              id="po-number"
              type="text"
              value={poNumber}
              onChange={(e) => setPoNumber(e.target.value)}
              placeholder="Enter PO Number"
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="excel-upload">Excel Line Items</label>
            <input
              id="excel-upload"
              type="file"
              accept=".xlsx, .xls"
              onChange={handleFileChange}
              disabled={isSubmitting}
            />
            {fileName && <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>Selected: {fileName}</span>}
          </div>

          {message.text && (
            <div className={`message message-${message.type}`} style={{ whiteSpace: 'pre-wrap', textAlign: 'left' }}>
              {message.text}
            </div>
          )}


          {lineItems.length > 0 && (
            <>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th className="checkbox-cell">
                        <input
                          type="checkbox"
                          checked={lineItems.length > 0 && selectedIndices.size === lineItems.length}
                          onChange={toggleSelectAll}
                        />
                      </th>
                      <th style={{ minWidth: '80px' }}>Status</th>
                      {headers.map(header => (
                        <th key={header}>{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {lineItems.map((item, index) => (
                      <tr key={index} style={{ opacity: selectedIndices.has(index) ? 1 : 0.5 }}>
                        <td className="checkbox-cell">
                          <input
                            type="checkbox"
                            checked={selectedIndices.has(index)}
                            onChange={() => toggleSelectRow(index)}
                          />
                        </td>
                        <td style={{
                          color: item.Status === 'Success' ? 'green' : (item.Status ? 'red' : 'inherit'),
                          fontWeight: item.Status ? 'bold' : 'normal',
                          fontSize: '0.9em'
                        }} title={item.Status}>
                          {item.Status === 'Success' ? 'Has Success' : (item.Status ? 'Error' : '')}
                        </td>
                        {headers.map(header => (
                          <td key={`${index}-${header}`}>
                            <input
                              type="text"
                              value={item[header]}
                              placeholder={header.toLowerCase().includes('date') ? 'YYYY-MM-DD' : ''}
                              onChange={(e) => handleLineItemChange(index, header, e.target.value)}
                            />
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="actions-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className="selection-info">{selectedIndices.size} item(s) selected</span>
                <button type="button" onClick={handleDownload} className="download-button" disabled={!hasProcessed} style={{ opacity: hasProcessed ? 1 : 0.5, cursor: hasProcessed ? 'pointer' : 'not-allowed' }}>
                  Download Excel Results
                </button>
              </div>
            </>
          )}



          <button
            type="submit"
            disabled={isSubmitting || lineItems.length === 0}
            className="submit-button"
          >
            {isSubmitting ? 'Processing...' : 'Submit Selected Lines'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default App
