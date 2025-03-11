# Unit Tests  
pytest -v tests/test_award_detection.py  

# Integration Testing  
python -m pytest tests/integration/test_full_pipeline.py  

# Load Testing (100 concurrent requests)  
locust -f tests/load_test.py  
