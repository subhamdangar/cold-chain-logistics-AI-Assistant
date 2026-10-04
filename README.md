# AI-Powered Cold-Chain Logistics Intelligence and Decision Support System

An AI-powered cold-chain logistics intelligence and decision-support system that enables logistics teams to interact with fleet and shipment telemetry through natural-language queries.

The system combines structured operational data from SQL Server, external corridor conditions, and a Retrieval-Augmented Generation (RAG) knowledge base containing cold-chain Standard Operating Procedures (SOPs). An AI agent coordinates these sources to identify operational risks, analyze cold-chain conditions, and provide evidence-based, SOP-supported recommendations.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Project Objectives](#project-objectives)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [How the System Works](#how-the-system-works)
- [Data Sources](#data-sources)
- [Database Architecture](#database-architecture)
- [Database Security Model](#database-security-model)
- [Audit Logging](#audit-logging)
- [AI Agent Architecture](#ai-agent-architecture)
- [Tool Architecture](#tool-architecture)
- [RAG Pipeline](#rag-pipeline)
- [LLM Configuration](#llm-configuration)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Local Installation](#local-installation)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [SOP Ingestion](#sop-ingestion)
- [Running the Application](#running-the-application)
- [Example Queries](#example-queries)
- [Security Design](#security-design)
- [Operational Response Design](#operational-response-design)
- [Audit and Traceability](#audit-and-traceability)
- [Testing the Database Layer](#testing-the-database-layer)
- [Troubleshooting](#troubleshooting)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)
- [Project Outcomes](#project-outcomes)
- [License](#license)

---

# Project Overview

Cold-chain logistics requires continuous monitoring of temperature-sensitive cargo, vehicle conditions, route risks, delays, congestion, and operational procedures.

Traditional logistics analysis often requires users to:

1. Query operational databases manually.
2. Inspect dashboards.
3. Check external route or weather information separately.
4. Search operational SOP documents manually.
5. Combine the information before making a decision.

This project integrates these activities into a single natural-language interface.

A logistics user can ask a question such as:

> Find high-risk shipments near Los Angeles, check the current corridor conditions, and determine what action is supported by the SOP.

The system decomposes the request and uses specialized tools to retrieve the required information.

The resulting response is based on:

- SQL Server telemetry
- External corridor conditions
- Retrieved SOP information

The system is designed to avoid unsupported assumptions and distinguish between measured data, external conditions, retrieved procedures, and conclusions.

---

# Problem Statement

Cold-chain logistics operations generate large amounts of structured and unstructured information.

Structured information may include:

- Vehicle location
- Cargo temperature
- Cargo condition
- Delay probability
- Port congestion
- Route risk
- Telemetry timestamps

Unstructured information may include:

- Cold-chain SOPs
- Compliance procedures
- Incident-handling instructions
- Operational escalation procedures

The challenge is that these sources are normally accessed independently.

A logistics analyst may need to perform several steps:

```text
Operational Database
        +
External Conditions
        +
SOP Documents
        ↓
Manual Analysis
        ↓
Operational Decision
```

This project aims to simplify that workflow:

```text
Natural-Language Question
        ↓
AI Agent
        ↓
SQL + External Data + SOP Retrieval
        ↓
Evidence Aggregation
        ↓
Operational Decision Support
```

---

# Project Objectives

The primary objectives of the project are:

1. Provide a natural-language interface for logistics data analysis.
2. Enable users to query fleet telemetry without writing SQL manually.
3. Provide controlled access to operational database information.
4. Retrieve external corridor conditions when required.
5. Retrieve relevant cold-chain SOP information using semantic search.
6. Combine structured and unstructured information for operational analysis.
7. Generate recommendations based on available evidence.
8. Prevent unsupported claims and hallucinated operational causes.
9. Maintain an audit trail of agent activity.
10. Provide a modular architecture that can be extended with additional tools and data sources.

---

# Key Features

## Natural-Language Data Access

Users can ask questions about operational telemetry without manually writing SQL queries.

Example:

```text
Which vehicles have the highest delay probability?
```

The agent translates the request into an appropriate database operation.

---

## Semantic Database Layer

The AI agent does not directly interact with the raw legacy database table.

Instead, a controlled semantic view exposes business-readable column names.

```text
Raw Database
      ↓
Semantic View
      ↓
AI Agent
```

This reduces the dependency of the AI agent on legacy column names and database structure.

---

## External Corridor Conditions

The system can retrieve external conditions for a specified geographic location.

This allows operational telemetry to be combined with environmental or corridor-level information.

---

## RAG-Based SOP Retrieval

Cold-chain SOP documents are converted into embeddings and stored in Pinecone.

When a user asks a compliance-related question, the system performs semantic retrieval and uses the relevant SOP information as evidence.

---

## Role-Based Database Access

The AI agent uses a restricted database account.

The agent is given access to the semantic view rather than unrestricted access to the underlying raw table.

---

## Audit Logging

Agent tool execution is recorded in:

```text
FDE_VIEWS.AgentAuditLog
```

This provides traceability for:

- Session
- Agent node
- Tool executed
- Tool input/output content
- Execution timestamp

---

## Streamlit Interface

The project provides an interactive Streamlit interface for:

- Natural-language queries
- Agent responses
- Tool execution visibility
- Operational analysis
- Security and audit log inspection

---

# System Architecture

```text
                         ┌────────────────────────┐
                         │       User Query       │
                         └────────────┬───────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  Streamlit Interface   │
                         └────────────┬───────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │    LangGraph Agent     │
                         │       Reasoner         │
                         └────────────┬───────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                │                     │                     │
                ▼                     ▼                     ▼
      ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
      │ SQL Telemetry    │  │ Corridor          │  │ SOP Retrieval    │
      │ Tool             │  │ Conditions Tool   │  │ Tool             │
      └────────┬─────────┘  └──────────────────┘  └────────┬─────────┘
               │                                            │
               ▼                                            ▼
      ┌──────────────────┐                         ┌──────────────────┐
      │ Dockerized       │                         │ Pinecone         │
      │ SQL Server       │                         │ Vector Index     │
      └────────┬─────────┘                         └──────────────────┘
               │
               ▼
      ┌──────────────────┐
      │ FDE_VIEWS        │
      │ VW_ACTIVE_FLEET  │
      └──────────────────┘

                         ┌────────────────────────┐
                         │   Agent Audit Trail   │
                         │ FDE_VIEWS.AgentAuditLog│
                         └────────────────────────┘
```

---

# How the System Works

A typical user request passes through the following stages.

## Step 1 — User Query

The user submits a natural-language request through the Streamlit interface.

Example:

```text
Find high-risk shipments near Los Angeles and check the SOP requirements.
```

---

## Step 2 — Agent Reasoning

The LangGraph-based agent analyzes the request and determines which tools are required.

The available tools include:

```text
query_telemetry_db
fetch_corridor_conditions
search_compliance_sop
```

---

## Step 3 — Telemetry Retrieval

The SQL tool queries the semantic SQL Server view.

The agent receives structured operational data such as:

- Timestamp
- Latitude
- Longitude
- Current temperature
- Cargo condition
- Risk classification
- Delay probability
- Port congestion
- Route risk

---

## Step 4 — External Conditions

If required, the corridor conditions tool retrieves environmental or route-related information based on the relevant geographic coordinates.

---

## Step 5 — SOP Retrieval

If the question involves compliance or operational action, the SOP retrieval tool searches the Pinecone knowledge base.

Relevant SOP information is returned to the agent.

---

## Step 6 — Evidence Aggregation

The agent combines the retrieved information.

Conceptually:

```text
Telemetry
    +
Corridor Conditions
    +
SOP
    ↓
Evidence-Based Analysis
```

---

## Step 7 — Final Response

The agent generates a structured operational response containing the relevant findings and actions supported by the available evidence.

---

# Data Sources

The system currently works with three primary information sources.

## 1. SQL Server Telemetry

The local SQL Server contains the logistics telemetry dataset.

Raw table:

```text
dbo.TBL_SC_FLEET_HIST_RAW
```

The current development database contains approximately:

```text
32,065 records
```

The raw table contains legacy-style field names.

A semantic view is used to expose cleaner business-oriented names.

---

## 2. External Corridor Conditions

The corridor conditions tool provides external information for geographic locations.

The agent can use this information alongside SQL telemetry when analyzing route-level operational risk.

---

## 3. Cold-Chain SOP Knowledge Base

The project uses a RAG-based knowledge base for cold-chain procedures.

The SOP documents are:

```text
Document
   ↓
Text Extraction
   ↓
Chunking
   ↓
Embedding
   ↓
Pinecone
   ↓
Semantic Retrieval
```

This allows the system to retrieve relevant procedural information rather than relying exclusively on the LLM's pretrained knowledge.

---

# Database Architecture

The project uses Microsoft SQL Server running locally in Docker.

The primary database is:

```text
SupplyChainDB
```

The database contains the following objects.

```text
SupplyChainDB
│
├── dbo
│   └── TBL_SC_FLEET_HIST_RAW
│
└── FDE_VIEWS
    ├── VW_ACTIVE_FLEET
    └── AgentAuditLog
```

---

# Raw Telemetry Table

The raw operational data is stored in:

```text
dbo.TBL_SC_FLEET_HIST_RAW
```

This table contains the original logistics telemetry data.

The AI agent does not directly query this table.

---

# Semantic View

The project creates:

```text
FDE_VIEWS.VW_ACTIVE_FLEET
```

The view translates legacy database fields into readable business-oriented fields.

Example mapping:

| Raw Field | Semantic Field |
|---|---|
| `TS_UTC` | `Timestamp` |
| `V_LAT` | `Latitude` |
| `V_LON` | `Longitude` |
| `IOT_TEMP_VAL_C` | `Current_Temperature_C` |
| `CGO_COND_CD` | `Cargo_Condition_Code` |
| `RISK_CLS_TXT` | `Risk_Classification` |
| `DELAY_PROB_DEC` | `Delay_Probability` |
| `PRT_CNG_LVL` | `Port_Congestion_Level` |
| `RT_RSK_IDX` | `Route_Risk_Index` |

This creates a controlled abstraction layer between the AI agent and the legacy database.

---

# Database Security Model

The project implements a least-privilege database access model.

The AI agent uses:

```text
AI_AGENT_RO
```

rather than the administrative:

```text
sa
```

account.

The intended access model is:

```text
                     AI_AGENT_RO
                         │
             ┌───────────┴────────────┐
             │                        │
             ▼                        ▼
      SELECT Permission       INSERT Permission
             │                        │
             ▼                        ▼
 VW_ACTIVE_FLEET             AgentAuditLog
```

The raw table remains protected:

```text
AI_AGENT_RO
     │
     └── Direct SELECT on
         dbo.TBL_SC_FLEET_HIST_RAW
         → Restricted
```

This prevents the AI agent from directly modifying or querying the underlying raw operational table.

---

# Audit Logging

The system maintains an audit trail in:

```text
FDE_VIEWS.AgentAuditLog
```

The table contains:

| Column | Description |
|---|---|
| `LogID` | Unique audit record ID |
| `Timestamp` | Time of execution |
| `SessionID` | Agent session identifier |
| `NodeExecuted` | LangGraph node involved |
| `ToolName` | Tool executed |
| `Content` | Recorded tool content |

Example:

```text
LogID: 1
NodeExecuted: reasoner
ToolName: query_telemetry_db
```

Other examples include:

```text
reasoner → fetch_corridor_conditions
reasoner → search_compliance_sop
tools → query_telemetry_db
reasoner_final → LLM Text Synthesis
```

This provides an execution trail for agent operations.

---

# AI Agent Architecture

The agent is implemented using LangGraph.

The core graph consists of:

```text
START
  │
  ▼
reasoner
  │
  ├──── tool required ────► tools
  │                           │
  │                           ▼
  │                        reasoner
  │
  └──── final response ───► END
```

The agent maintains message state and uses tool calls to retrieve external information.

---

# Agent Tools

The project currently uses three major tools.

## `query_telemetry_db`

Purpose:

```text
Query operational fleet and shipment telemetry.
```

Source:

```text
SQL Server
```

Primary data source:

```text
FDE_VIEWS.VW_ACTIVE_FLEET
```

Example question:

```text
Which vehicles have the highest delay probability?
```

---

## `fetch_corridor_conditions`

Purpose:

```text
Retrieve external conditions for a geographic location.
```

Input:

```text
latitude
longitude
```

Example:

```text
What are the current corridor conditions near 33.8, -118.1?
```

---

## `search_compliance_sop`

Purpose:

```text
Retrieve relevant cold-chain SOP information.
```

Source:

```text
Pinecone
```

Example:

```text
What does the SOP require when cargo temperature exceeds the permitted range?
```

---

# RAG Pipeline

The SOP component follows a Retrieval-Augmented Generation architecture.

```text
                  SOP Documents
                       │
                       ▼
                Text Extraction
                       │
                       ▼
                    Chunking
                       │
                       ▼
                  Embeddings
                       │
                       ▼
                   Pinecone
                       │
                       │
User Question ─────────┘
       │
       ▼
Semantic Search
       │
       ▼
Relevant SOP Chunks
       │
       ▼
Agent Context
       │
       ▼
Final Response
```

The purpose of this architecture is to ground compliance-related responses in the organization's SOP documentation.

---

# LLM Configuration

The application supports configurable LLM providers.

The current development configuration uses Groq with a Qwen-based model.

The configuration is controlled through:

```env
Agent_llm=GROQ
```

The architecture can be extended to support other providers.

The LLM is responsible for:

- Understanding the user request
- Selecting tools
- Interpreting tool results
- Combining evidence
- Generating the final response

The LLM is not treated as the source of truth for operational telemetry or SOP requirements.

---

# Operational Reasoning Principles

The system is designed around several important rules.

## Telemetry Is the Source of Operational Measurements

Measured values should come from the SQL telemetry database.

For example:

```text
Current_Temperature_C
Delay_Probability
Route_Risk_Index
```

should not be invented by the language model.

---

## SOP Is the Source of Compliance Requirements

Compliance-related thresholds and operational procedures should be based on retrieved SOP information.

---

## Missing Information Should Not Be Invented

If the available data does not establish a cause, the system should explicitly state that the cause cannot be determined from the available information.

For example:

```text
Cause cannot be determined from the available data.
```

rather than inventing:

```text
The refrigeration unit failed.
```

---

## Temperature Does Not Automatically Mean Spoilage

A temperature anomaly should not automatically be interpreted as cargo spoilage.

The system should distinguish between:

```text
Temperature measurement
        ↓
Threshold comparison
        ↓
Compliance status
        ↓
Operational interpretation
```

---

## Environmental Temperature vs Cargo Temperature

The system distinguishes:

```text
Cargo Temperature
```

from:

```text
Ambient / Weather Temperature
```

These values should not be treated as interchangeable.

---

# Operational Response Design

The intended response format is structured around three sections.

## 1. Executive Summary

Provides a concise summary of the operational condition.

Example:

```text
### Executive Summary

Several shipments show elevated operational risk based on
temperature, delay probability, and route conditions.
```

---

## 2. Telemetry and Environment Analysis

Relevant evidence can be presented in a structured format.

Example:

| Location | Current Temp | Cargo Risk | Weather / Congestion |
|---|---:|---|---|
| 33.8, -118.1 | 4.6°C | Elevated | High congestion |

The response should distinguish measured telemetry from external conditions.

---

## 3. Required Action Plan

Actions should be derived from the retrieved SOP.

Example:

```text
1. Identify affected shipment.
2. Compare measured temperature with the applicable SOP threshold.
3. Follow the documented cold-chain incident procedure.
```

The system should not invent responsibilities or escalation levels that are not supported by the SOP.

---

# Example Queries

## Basic Fleet Queries

```text
Show me the latest fleet telemetry.
```

```text
Which vehicles have the highest delay probability?
```

```text
Show the current temperature and risk classification of active shipments.
```

```text
Which vehicles have the highest route risk?
```

---

## Temperature Queries

```text
Which shipments currently have temperature anomalies?
```

```text
Show vehicles where the cargo temperature is outside the acceptable range.
```

```text
Which shipments have both elevated temperature and high delay probability?
```

---

## Geographic Queries

```text
Show me shipments near latitude 33.8 and longitude -118.1.
```

```text
Find high-risk shipments near Los Angeles.
```

```text
Are there any temperature anomalies near 33.8, -118.1?
```

---

## Corridor Queries

```text
What are the current corridor conditions near 33.8, -118.1?
```

```text
Are external conditions likely to affect shipments near this location?
```

---

## SOP Queries

```text
What is the SOP temperature requirement for fresh perishables?
```

```text
What does the SOP require when cargo temperature exceeds the allowed threshold?
```

```text
What are the documented escalation requirements for a cold-chain incident?
```

---

## End-to-End Queries

These queries exercise multiple components of the system.

```text
Find high-risk shipments near Los Angeles, check the current corridor conditions, and determine what action is supported by the SOP.
```

```text
Identify shipments with temperature anomalies, check their surrounding corridor conditions, and explain whether the SOP requires any action.
```

```text
Find shipments with high delay probability and elevated cargo temperature. Check the relevant corridor conditions and provide an SOP-supported action plan.
```

---

# Technology Stack

| Layer | Technology |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| Agent Framework | LangGraph |
| LLM Provider | Groq |
| LLM Model Family | Qwen |
| Relational Database | Microsoft SQL Server |
| Database Environment | Docker |
| Vector Database | Pinecone |
| Retrieval | RAG / Semantic Search |
| Database Driver | ODBC Driver 18 |
| Database Interface | SQLAlchemy / pyodbc |
| Configuration | python-dotenv |
| Package Management | uv / pip |
| Version Control | Git / GitHub |

---

# Project Structure

```text
FDE-Project/
│
├── .github/
│
├── .streamlit/
│
├── data/
│
├── docs/
│
├── scripts/
│   ├── audit_log.sql
│   ├── ingest_legacy_data.py
│   ├── ingest_sop_pinecone.py
│   └── setup_security_and_view.sql
│
├── src/
│   ├── prompts/
│   │
│   ├── agent_tools.py
│   ├── orchestrator.py
│   └── ui.py
│
├── .env
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── README.md
├── requirements.txt
└── uv.lock
```

---

# Important Files

## `src/ui.py`

The Streamlit application.

Responsibilities include:

- User interface
- Session management
- Agent interaction
- Displaying tool activity
- Displaying operational responses
- Security and audit-log interface

---

## `src/orchestrator.py`

Defines the LangGraph agent.

Responsibilities include:

- Agent state
- LLM configuration
- Tool binding
- Reasoning node
- Tool node
- Graph construction
- Checkpointing

---

## `src/agent_tools.py`

Contains the specialized tools used by the agent.

Major tools include:

```text
query_telemetry_db
fetch_corridor_conditions
search_compliance_sop
```

---

## `scripts/setup_security_and_view.sql`

Creates the semantic database layer and database security configuration.

---

## `scripts/audit_log.sql`

Creates the agent audit table and grants the required insert permission.

---

## `scripts/ingest_legacy_data.py`

Used for loading the logistics dataset into SQL Server.

---

## `scripts/ingest_sop_pinecone.py`

Used for indexing SOP documents into Pinecone.

---

# Prerequisites

Before running the project locally, install:

- Python 3.10 or later
- Docker Desktop
- Microsoft SQL Server 2022
- ODBC Driver 18 for SQL Server
- Git
- Pinecone account
- Groq API key

---

# Local Installation

## 1. Clone the Repository

```bash
git clone <repository-url>
cd FDE-Project
```

---

## 2. Create Virtual Environment

Using Python:

```bash
python -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

---

## 3. Install Dependencies

Using pip:

```bash
pip install -r requirements.txt
```

Or using uv:

```bash
uv sync
```

---

# Dockerized SQL Server Setup

The project uses SQL Server running inside Docker.

Verify the container:

```bash
docker ps
```

The SQL Server container should expose:

```text
localhost:1433
```

Example:

```text
0.0.0.0:1433->1433/tcp
```

The database used by the application is:

```text
SupplyChainDB
```

---

# Environment Configuration

Create:

```text
.env
```

in the project root.

Example configuration:

```env
# ==========================================
# SQL Server
# ==========================================

SQL_SERVER_HOST=localhost
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=SupplyChainDB

# ==========================================
# AI Agent Database Account
# ==========================================

SQL_AGENT_USER=AI_AGENT_RO
SQL_AGENT_PASSWORD=your_agent_password

# ==========================================
# Administrative Database Account
# ==========================================

SQL_ADMIN_USER=sa
SQL_ADMIN_PASSWORD=your_sa_password

# ==========================================
# LLM
# ==========================================

Agent_llm=GROQ
GROQ_API_KEY=your_groq_api_key

# ==========================================
# Pinecone
# ==========================================

PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=your_pinecone_index
```

Do not commit this file.

---

# Database Setup

After starting SQL Server, connect to the database:

```text
SupplyChainDB
```

Verify the raw data:

```sql
SELECT COUNT(*)
FROM dbo.TBL_SC_FLEET_HIST_RAW;
GO
```

Expected development dataset size:

```text
32065
```

---

# Create Semantic View

Run:

```text
scripts/setup_security_and_view.sql
```

The script creates:

```text
FDE_VIEWS.VW_ACTIVE_FLEET
```

Verify:

```sql
SELECT TOP 10 *
FROM FDE_VIEWS.VW_ACTIVE_FLEET;
GO
```

---

# Create Audit Log

Run:

```text
scripts/audit_log.sql
```

This creates:

```text
FDE_VIEWS.AgentAuditLog
```

Verify:

```sql
SELECT *
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'FDE_VIEWS'
  AND TABLE_NAME = 'AgentAuditLog';
GO
```

Verify audit records:

```sql
SELECT TOP 10 *
FROM FDE_VIEWS.AgentAuditLog
ORDER BY Timestamp DESC;
GO
```

---

# Database Validation

The final database structure should look like:

```text
SupplyChainDB
│
├── dbo
│   └── TBL_SC_FLEET_HIST_RAW
│
└── FDE_VIEWS
    ├── VW_ACTIVE_FLEET
    └── AgentAuditLog
```

---

# Verify AI Agent Permissions

The AI agent should have:

```text
SELECT
    FDE_VIEWS.VW_ACTIVE_FLEET
```

and:

```text
INSERT
    FDE_VIEWS.AgentAuditLog
```

The AI agent should not have unrestricted access to:

```text
dbo.TBL_SC_FLEET_HIST_RAW
```

This provides a controlled database boundary for AI-generated queries.

---

# SOP Ingestion

Before using SOP-based queries, index the SOP documents.

Run:

```bash
python scripts/ingest_sop_pinecone.py
```

The process is conceptually:

```text
SOP Document
     ↓
Document Loading
     ↓
Text Processing
     ↓
Chunking
     ↓
Embedding Model
     ↓
Pinecone Index
```

Once ingestion is complete, the agent can use:

```text
search_compliance_sop
```

to retrieve relevant procedural information.

---

# Running the Application

From the project root:

```bash
streamlit run src/ui.py
```

The application will start on the local Streamlit server.

Typically:

```text
http://localhost:8501
```

---

# Application Modes

The interface provides operational and audit functionality.

## Dispatch / Operational Mode

Used for:

- Natural-language fleet queries
- Risk analysis
- Temperature analysis
- Corridor analysis
- SOP-supported operational decisions

---

## Security & Audit Mode

Used for:

- Administrative authentication
- Audit-log inspection
- Reviewing agent tool activity
- Examining recorded agent sessions

Administrative credentials should be kept separate from the AI agent credentials.

---

# Security Considerations

Security is an important part of the system architecture because the application allows an LLM to interact with operational data.

## Least Privilege

The AI agent does not require administrative database access.

Instead:

```text
AI Agent
    ↓
AI_AGENT_RO
    ↓
Semantic View
```

---

## Semantic Access Layer

The agent interacts with:

```text
FDE_VIEWS.VW_ACTIVE_FLEET
```

rather than directly accessing the raw operational table.

This provides an additional layer between generated SQL and the underlying data.

---

## Administrative Access

The `sa` account should only be used for administrative tasks such as:

- Database setup
- Security configuration
- Audit inspection
- Maintenance

It should not be used as the normal AI-agent database account.

---

## Secrets

Never commit:

```text
.env
```

to Git.

The following should remain private:

- SQL Server passwords
- Groq API keys
- Pinecone API keys
- Administrative credentials

---

# Audit and Traceability

A major objective of the project is to make agent activity traceable.

For each tool execution, the system can record:

```text
SessionID
NodeExecuted
ToolName
Content
Timestamp
```

Example:

```text
SessionID:
a74deb31-1750-45ba-8a0f-f2fe635fb026

NodeExecuted:
reasoner

ToolName:
query_telemetry_db
```

This allows developers or administrators to inspect what tools were executed during an agent session.

---

# Example Audit Flow

For a complex query, the audit trail may contain events such as:

```text
reasoner
    ↓
query_telemetry_db

reasoner
    ↓
fetch_corridor_conditions

reasoner
    ↓
search_compliance_sop

tools
    ↓
query_telemetry_db

reasoner_final
    ↓
LLM Text Synthesis
```

This provides visibility into the agent workflow rather than treating the final LLM response as an opaque result.

---

# Testing the Database Layer

## Check SQL Server

```bash
docker ps
```

---

## Check Port

```bash
nc -vz localhost 1433
```

Expected:

```text
Connection to localhost port 1433 succeeded
```

---

## Check Database

```sql
SELECT name
FROM sys.databases;
GO
```

Expected to include:

```text
SupplyChainDB
```

---

## Check Raw Data

```sql
USE SupplyChainDB;
GO

SELECT COUNT(*)
FROM dbo.TBL_SC_FLEET_HIST_RAW;
GO
```

Expected:

```text
32065
```

---

## Check Semantic View

```sql
SELECT TOP 5 *
FROM FDE_VIEWS.VW_ACTIVE_FLEET;
GO
```

---

## Check Audit Table

```sql
SELECT TOP 5 *
FROM FDE_VIEWS.AgentAuditLog
ORDER BY Timestamp DESC;
GO
```

---

# Troubleshooting

## SQL Server Connection Timeout

Error:

```text
HYT00
Login timeout expired
```

Check:

```bash
docker ps
```

and:

```bash
nc -vz localhost 1433
```

Make sure the application uses:

```env
SQL_SERVER_HOST=localhost
SQL_SERVER_PORT=1433
```

---

## Login Failed for `sa`

Error:

```text
Login failed for user 'sa'. (18456)
```

This indicates an authentication problem.

Verify that:

- The Docker SQL Server container is running.
- The `sa` username is correct.
- The configured password is correct.
- The application is loading the expected `.env`.
- The Streamlit application was restarted after changing `.env`.

Test the Docker SQL Server directly:

```bash
docker exec -it legacy-mssql /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -C
```

---

## Database Does Not Exist

Error:

```text
Cannot open database "SupplyChainDB" requested by the login.
```

Verify:

```sql
SELECT name
FROM sys.databases;
GO
```

Make sure the application is configured for:

```env
SQL_SERVER_DATABASE=SupplyChainDB
```

---

## Audit Table Not Found

Error:

```text
Invalid object name 'FDE_VIEWS.AgentAuditLog'
```

Verify:

```sql
SELECT *
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'FDE_VIEWS'
  AND TABLE_NAME = 'AgentAuditLog';
GO
```

If the table does not exist, run:

```text
scripts/audit_log.sql
```

---

## Audit Insert Permission Error

If the AI agent cannot insert audit records, verify:

```sql
SELECT
    USER_NAME(grantee_principal_id) AS UserName,
    permission_name,
    state_desc
FROM sys.database_permissions
WHERE major_id = OBJECT_ID('FDE_VIEWS.AgentAuditLog');
GO
```

The expected permission is:

```text
AI_AGENT_RO
INSERT
GRANT
```

---

## Pinecone Retrieval Problems

If SOP retrieval does not return relevant information:

1. Verify the Pinecone API key.
2. Verify the configured index name.
3. Run the SOP ingestion script again.
4. Confirm that the index contains vectors.
5. Check that the embedding model used for querying matches the indexed vectors.

---

## Groq API Problems

If the LLM fails to respond:

Check:

```env
Agent_llm=GROQ
GROQ_API_KEY=your_key
```

Make sure the API key is valid and that the configured model is available through the selected provider.

---

# Current Database Architecture

The local development database currently follows this structure:

```text
Docker
  │
  ▼
SQL Server 2022
  │
  ▼
SupplyChainDB
  │
  ├── dbo.TBL_SC_FLEET_HIST_RAW
  │
  └── FDE_VIEWS
        │
        ├── VW_ACTIVE_FLEET
        │
        └── AgentAuditLog
```

---

# Current AI Architecture

```text
Streamlit
    │
    ▼
LangGraph
    │
    ▼
Reasoner
    │
    ├───────────────┐
    │               │
    ▼               ▼
SQL Tool        External Tool
    │               │
    ▼               ▼
SQL Server     Corridor Data
    │
    │
    └───────────────┐
                    ▼
              SOP Retrieval
                    │
                    ▼
                 Pinecone
                    │
                    ▼
             Evidence Context
                    │
                    ▼
             Final LLM Response
```

---

# Design Principles

## 1. Controlled Data Access

The AI agent should interact with a controlled semantic layer rather than directly accessing unrestricted database tables.

---

## 2. Evidence-Based Analysis

The system should distinguish between:

```text
Measured Data
External Conditions
Retrieved SOP
Agent Interpretation
```

---

## 3. No Unsupported Claims

If the available information does not establish a cause, the agent should not invent one.

For example:

```text
Cause cannot be determined from the available data.
```

is preferable to an unsupported equipment-failure claim.

---

## 4. SOP-Grounded Actions

Operational recommendations should be based on retrieved SOP information whenever the question concerns compliance or incident handling.

---

## 5. Traceability

Agent operations should be recorded so that tool execution can be reviewed later.

---

# Current Limitations

The current implementation is primarily intended for local development, testing, and demonstration.

The system currently depends on:

- Availability of the SQL Server database
- Quality of fleet telemetry
- Availability of external corridor information
- Quality of SOP documents
- Pinecone availability
- LLM provider availability

The system should not be considered a fully autonomous logistics control system.

It is a decision-support system intended to assist users by combining multiple information sources.

---

# Future Improvements

Potential future improvements include:

## Advanced Geographic Filtering

Implement true radius-based geographic queries instead of simple latitude/longitude bounding boxes.

Example:

```text
Find all shipments within 25 km of Los Angeles.
```

---

## Advanced Anomaly Detection

Introduce dedicated anomaly detection models for:

- Temperature excursions
- Sudden route-risk changes
- Delay anomalies
- Abnormal telemetry patterns

---

## Historical Trend Analysis

Allow questions such as:

```text
How has the temperature of this shipment changed over the last 24 hours?
```

---

## Automated Incident Prioritization

Introduce automated prioritization based on:

- Temperature severity
- Delay probability
- Route risk
- Cargo condition
- SOP requirements

---

## Enhanced Monitoring

Add:

- Operational dashboards
- Alerting
- Historical charts
- Incident tracking
- Performance monitoring

---

## Production Security

For production deployment:

- Use a dedicated secret-management system.
- Rotate credentials regularly.
- Use TLS for database connections.
- Restrict database network access.
- Avoid exposing SQL Server directly to the public internet.
- Use separate development and production credentials.
- Implement application-level authentication and authorization.
- Add comprehensive monitoring and logging.

---

# Project Outcomes

The project demonstrates how structured logistics data, external information, and operational documentation can be integrated into a single AI-assisted decision-support system.

The resulting architecture provides:

```text
Natural-Language Interaction
            +
Structured SQL Analytics
            +
External Operational Context
            +
RAG-Based SOP Retrieval
            +
Controlled Database Access
            +
Audit Logging
            ↓
AI-Powered Cold-Chain Decision Support
```

The project therefore goes beyond a simple chatbot by combining:

- Database querying
- Retrieval-Augmented Generation
- Agent orchestration
- External API integration
- Database security
- Auditability
- Operational decision support

---

# Example End-to-End Scenario

A logistics manager asks:

```text
Find high-risk shipments near Los Angeles, check the current corridor
conditions, and tell me what action is supported by the SOP.
```

The system processes the request as follows:

```text
1. User submits query
          ↓
2. Agent identifies required information
          ↓
3. SQL telemetry tool retrieves relevant fleet records
          ↓
4. Corridor tool retrieves external conditions
          ↓
5. SOP tool retrieves relevant compliance procedures
          ↓
6. Agent combines the evidence
          ↓
7. Agent evaluates the operational situation
          ↓
8. Agent generates an SOP-supported response
          ↓
9. Tool activity is recorded in AgentAuditLog
```

This provides the user with a single operational response without requiring manual navigation across multiple systems.

---

# Repository Safety

The following files should not be committed:

```text
.env
.venv/
venv/
__pycache__/
*.log
local database files
local vector database files
private credentials
API keys
```

The `.gitignore` file should be configured accordingly.

Before pushing the repository, verify:

```bash
git status
```

and ensure that no credentials or secret files are staged.

---

# Development Status

The project currently supports:

- Local Dockerized SQL Server
- Fleet telemetry ingestion
- Semantic SQL view
- Restricted AI database access
- Audit logging
- Pinecone SOP retrieval
- Natural-language agent interaction
- External corridor-condition retrieval
- Streamlit interface
- Configurable LLM provider

The system is currently being developed and tested as a cold-chain logistics AI decision-support application.

---

# License

This project is developed for academic, research, and demonstration purposes.