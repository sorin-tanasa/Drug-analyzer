FROM python:3.9
ADD main.py .
ADD compounds.csv .
RUN pip install pandas requests openpyxl
CMD ["python", "main.py"]
