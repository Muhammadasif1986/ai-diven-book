# Data Model: Audit K-12 AI Book

## Overview
This document describes the data structures and entities involved in auditing the K-12 AI book.

## Entity: Book Content
- **Name**: BookContent
- **Fields**:
  - id: string (unique identifier for the book)
  - title: string (title of the book)
  - wordCount: number (total word count)
  - content: string (raw content of the book)
  - filePath: string (path to the MDX file)
  - lastModified: Date (timestamp of last modification)

## Entity: Academic Source
- **Name**: AcademicSource
- **Fields**:
  - id: string (DOI or unique identifier)
  - title: string (title of the source)
  - authors: string[] (authors of the paper)
  - publicationYear: number (year of publication)
  - journal: string (name of the journal)
  - isPeerReviewed: boolean (whether it's peer-reviewed)
  - isK12Relevant: boolean (whether it's relevant to K-12 education)
  - citationText: string (the citation as it appears in the book)
  - citationFormat: string (APA format verification)
  - doi: string (digital object identifier)

## Entity: Citation Reference
- **Name**: CitationReference
- **Fields**:
  - id: string (unique identifier)
  - sourceId: string (reference to AcademicSource)
  - contentLocation: string (where in the book content this citation appears)
  - citationText: string (the in-text citation)
  - isVerified: boolean (whether the citation has been verified)

## Entity: Audit Result
- **Name**: AuditResult
- **Fields**:
  - id: string (unique identifier)
  - bookId: string (reference to BookContent)
  - auditType: string (type of audit: "word-count", "citations", "readability", "plagiarism", etc.)
  - status: string ("pass", "fail", "warning")
  - details: object (specific details about the audit result)
  - timestamp: Date (when the audit was performed)
  - severity: string ("critical", "major", "minor")

## Entity: AI Application
- **Name**: AIApplication
- **Fields**:
  - id: string (unique identifier)
  - name: string (name of the AI application)
  - description: string (description of the application)
  - evidence: string[] (citations supporting the effectiveness)
  - k12Relevance: string (grade level and subject area)
  - outcomes: string (measurable outcomes)
  - sourceId: string (reference to AcademicSource providing evidence)

## Entity: ROI Metric
- **Name**: ROIMetric
- **Fields**:
  - id: string (unique identifier)
  - description: string (what is being measured)
  - value: number (quantitative value)
  - unit: string (unit of measurement)
  - source: string (where this metric comes from)
  - bookSection: string (which section of the book contains this)