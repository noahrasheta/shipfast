# Data Center Due Diligence Plugin

This plugin analyzes broker documents for a data center opportunity and produces a scored report with a clear recommendation: Pursue, Proceed with Caution, or Pass. It examines 9 areas — power, connectivity, cooling, land, ownership, environmental, commercials, natural gas, and market comparables — and generates documents you can edit and share. You provide the documents; the plugin does the reading, research, and writing.

---

## What You Need Before Starting

- **Claude Desktop app (Mac)** with a paid plan that includes Cowork
- **A folder on your computer** containing the broker documents for the opportunity (PDFs, Word documents, spreadsheets, presentations, images — any mix works)
- **The plugin file** — a compressed folder with a name ending in `.zip`

That's it. No additional software setup is required.

---

## How to Install

**Step 1: Save the plugin file**

You should have received a file called something like `dc-due-diligence-desktop.zip`. Save it somewhere you can easily find it — your Downloads folder works fine. You do not need to open or unzip it.

**Step 2: Open Claude Desktop and switch to Cowork**

Open the Claude app on your Mac. Look for "Cowork" near the top of the window and click it to switch to Cowork mode.

**Step 3: Open the plugin panel**

On the left side of the Cowork window, look for a "+" or similar button for adding tools. Click it, then look for an option labeled "Plugins" or "Add Plugin."

**Step 4: Upload the plugin file**

Look for an option to upload your own plugin. Drag the `.zip` file into the window that appears, then click the button to confirm the upload.

The plugin will install in a few seconds. You should see "Due Diligence" appear in your list of available tools.

**Step 5: Verify the install**

If installation succeeded, you can type `/due-diligence` in the Cowork message box and the plugin should appear as a suggestion. If it does not appear, see the troubleshooting section below.

---

## How to Run an Analysis

**Step 1: Connect your documents folder**

Before starting, you need to point Claude at the folder containing the broker documents. Look for an option like "Work in a folder" or "Add folder" in the Cowork interface, and choose the folder on your computer that contains the documents for the opportunity.

**Step 2: Start the analysis**

In the Cowork message box, type `/due-diligence` and press Enter. The plugin will take over from there.

**Step 3: Wait for results**

The plugin will scan your documents, sort them by topic, and dispatch specialized analysts for each of the 9 areas — all working at the same time. For a typical document collection (20 to 50 files), expect the analysis to take 20 to 40 minutes. You will see progress updates in the Cowork window as each area completes.

You do not need to stay at your computer while it runs. When all 9 areas are finished, the plugin will run a synthesis step to identify cross-domain risks, calculate an overall score, and prepare the final documents. The full run (including synthesis) typically completes within 45 minutes.

**Step 4: Review the verdict**

When the analysis is complete, you will see a summary in the Cowork window showing the overall recommendation (Pursue / Proceed with Caution / Pass) along with key highlights. The detailed documents will be in your documents folder.

---

## What the Output Looks Like

When the analysis finishes, you will find several documents in your documents folder:

- **Executive Summary** — A scored report covering all 9 areas with an overall recommendation and confidence level. Includes individual scores for each area and the reasoning behind the recommendation.

- **Client Summary** — A version of the findings written for sharing with deal stakeholders. Uses plain language without internal scoring or technical analysis notes.

- **Risk Assessment** — A focused report on issues that span multiple areas — for example, a power situation that also affects the financial projections, or an environmental concern that interacts with the ownership picture.

- **9 Domain Reports** — One detailed report for each area analyzed: Power, Connectivity, Water and Cooling, Land and Zoning, Ownership, Environmental, Commercials, Natural Gas, and Market Comparables. Each report covers what the documents say, what current market data shows, and any gaps or concerns found.

If your Mac has the Word document generator available, all reports will also be saved as `.docx` files in an `output` folder inside your documents folder — ready to open in Word and edit. If the Word document generator is not available, the reports will be saved as text files that you can open with any text editor or copy into Word manually.

---

## If Something Goes Wrong

**"The analysis stopped partway through"**

This can happen if your internet connection drops or the app is interrupted. Just type `/due-diligence` and press Enter again. The plugin remembers which areas it already finished and will pick up where it left off, skipping any completed work. You do not need to start over.

**"Some areas are missing from the final report"**

If certain topic areas show as missing or unavailable after the analysis finishes, it usually means the documents did not contain enough information for that area, or the analyst for that area ran into a problem. The final report will note which areas could not be fully evaluated, and those areas will be scored conservatively. You can type `/due-diligence` again to retry just the missing areas — completed areas will be skipped automatically.

**"I don't see the /due-diligence option"**

Make sure the plugin was uploaded successfully. Look in your Cowork plugin list for "Due Diligence." If it's not listed, try uploading the `.zip` file again following the install steps above.

**"I don't see any Word documents"**

Word document generation requires an additional tool that may not be set up on your computer. The analysis results are still available as text files in your documents folder — you can open them with any text editor or copy the content into Word manually. The text files contain the same information as the Word documents.

**"The analysis is taking a very long time"**

Large document collections (50 or more files) can take 30 to 45 minutes. The plugin analyzes all 9 areas at the same time, and each area needs time to read the documents and research current market data. If you have more than 30 files, you will see a note at the start of the run with an estimated completion time. As long as you see progress updates appearing in the Cowork window, the analysis is working normally.

**"The recommendation seems wrong for one area"**

If a domain is scored lower than you expect (for example, "Power" is scored Low but you know the power situation is good), it may mean the analyst for that area did not complete successfully and the score defaulted to a conservative value. Look at the individual domain reports to check. If a report for that area is missing or very short, type `/due-diligence` again to retry it.

---

## Tips for Best Results

- **Put all documents in one folder.** The plugin reads everything in the folder you connect — no need to sort files by category beforehand.
- **More documents is better.** The analysts are looking for specific information in each area. If a topic has no documents, the analyst will rely entirely on web research, which may be less specific to your opportunity.
- **Images and scanned documents work.** The plugin can read image files and scanned PDFs directly.
- **You can run it more than once.** If you receive additional documents after the first run, add them to the folder and run `/due-diligence` again. Already-completed areas will be skipped, and only the areas affected by the new documents need to be re-analyzed.
