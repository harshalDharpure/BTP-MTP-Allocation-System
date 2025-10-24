# BTP/MTP Allocation System

A web-based application for automated allocation of Bachelor's Thesis Project (BTP) and Master's Thesis Project (MTP) assignments based on student preferences and CGPA.

## 🚀 Features

- **Automated Allocation**: Implements mod-n algorithm with CGPA-based sorting
- **Web Interface**: User-friendly Streamlit-based web application
- **File Upload/Download**: Easy CSV file processing and result downloads
- **Comprehensive Logging**: Detailed logging with error handling
- **Docker Support**: Containerized deployment with Docker Compose
- **Preference Statistics**: Detailed analysis of faculty preferences

## 📋 Requirements

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)

## 🛠️ Installation

### Local Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd btp-mtp-allocation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run streamlit_app.py
```

### Docker Installation

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

2. Access the application at: http://localhost:8501

## 📊 Input Format

The input CSV file should contain the following columns:

- **Roll**: Student roll number
- **Name**: Student name  
- **Email**: Student email
- **CGPA**: Student's CGPA
- **Faculty columns**: Preference rankings (1-18) for each faculty

### Example Faculty Codes
ABM, AE, AM, AR, CA, JC, JM, MA, RH, RM, RM2, RS, SK, SKD, SKM, SM, SS, ST

## 🔧 Algorithm

The allocation process follows these steps:

1. **Sort by CGPA**: Students are sorted by CGPA in descending order
2. **Mod N Allocation**: Each faculty gets exactly one student per cycle
3. **Preference Matching**: Students are allocated based on their preference rankings
4. **Fair Distribution**: Ensures balanced distribution across all faculties

## 📁 Output Files

### Allocation Results (`allocation_results_*.csv`)
Contains student information and their allocated faculty:
- Roll, Name, Email, CGPA, Allocated

### Preference Statistics (`preference_stats_*.csv`)
Shows how many students ranked each faculty at each preference level:
- Faculty name and count for each preference rank (1-18)

## 🐳 Docker Commands

```bash
# Build and start the application
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f

# Rebuild without cache
docker-compose build --no-cache
```

## 📝 Usage

1. **Upload File**: Use the web interface to upload your student preference CSV file
2. **Process**: Click "Process Allocation" to run the algorithm
3. **View Results**: Review the allocation results and statistics
4. **Download**: Download both allocation results and preference statistics

## 🔍 Logging

The application generates detailed logs in:
- `allocation.log`: Allocation engine logs
- `streamlit_app.log`: Streamlit application logs

## 🧪 Testing

Test the application with the provided sample data:

```bash
# Test locally
python allocation_engine.py

# Test with Docker
docker-compose up --build
```

## 📋 Project Structure

```
├── allocation_engine.py      # Core allocation logic
├── streamlit_app.py         # Web application interface
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Docker ignore file
├── README.md              # This file
└── logs/                  # Log files directory
```

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `docker-compose.yml` or stop other services
2. **File upload errors**: Ensure CSV format matches the expected structure
3. **Memory issues**: Increase Docker memory allocation if processing large files

### Logs

Check the log files for detailed error information:
```bash
# View allocation logs
tail -f allocation.log

# View Streamlit logs  
tail -f streamlit_app.log

# View Docker logs
docker-compose logs -f
```

## 📄 License

This project is developed for educational purposes as part of Algorithm Course Assignment 2.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions, please check the logs first and create an issue in the repository.
