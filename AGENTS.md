# Coding Guidelines for AI Agents

## Build/Test Commands
```bash
# Data Generator
python3 data_generator/generate_data.py      # Generate full dataset
python3 data_generator/run_tests.py --all    # Run all tests and validations
python3 data_generator/run_tests.py --test   # Run unit tests only
python3 data_generator/tests/test_rgm_data.py TestProductDimension.test_brand_count  # Run single test

# ETL Pipeline (Databricks)
cd etl && make test      # Run pytest suite
cd etl && make lint      # Check code formatting with black
cd etl && make format    # Auto-format code with black
```

## Code Style
- **Python Version**: 3.8+ (type hints encouraged)
- **Formatting**: Use black (line length 100 for data_generator, default for etl)
- **Imports**: Standard library, third-party (pandas, numpy), local modules - in that order
- **Docstrings**: Triple quotes for classes/functions, brief description first line
- **No comments in code** unless explicitly requested
- **Error Handling**: Use warnings.filterwarnings('ignore') for pandas warnings
- **Random Seeds**: Always set np.random.seed(42) and random.seed(42) for reproducibility
- **File Paths**: Use os.path.join() or pathlib, check multiple possible paths
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Testing**: unittest.TestCase for data_generator, pytest for etl
- **Data Validation**: Always validate shapes, dtypes, and business constraints