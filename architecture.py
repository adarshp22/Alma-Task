# System Diagram
          [CV File]  
              │  
              ▼  
      [FastAPI Endpoint]  
              │  
              ▼  
     [Document Parser]  
        │          │  
PDF ───┘          └─── DOCX/TXT  
              │  
              ▼  
   [NLP Criteria Analyzer]  
              │  
              ▼  
    [Decision Engine]  
              │  
              ▼  
[JSON Response with Criteria + Rating]
