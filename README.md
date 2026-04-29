# Attendance Report Transformer

Pipeline-based project to transform attendance PDF reports with classification, parsing, validation, and PDF generation.

## Project Structure

```
attendance_report/
├── models/              ← Domain objects (AttendanceRow, AttendanceReport)
├── ocr/                 ← PDF text extraction
├── classifier/          ← Report type detection (TYPE_A / TYPE_B / TYPE_C)
├── parser/              ← Parsing into domain objects (Template Method pattern)
├── validation/          ← Transformation & validation (Strategy + Decorator pattern)
├── generator/           ← PDF output generation
└── tests/               ← Unit and integration tests
```

## How it works

1. **OCR** (`ocr/`) - Extracts raw text from PDF
2. **Classifier** (`classifier/`) - Determines TYPE_A / TYPE_B / TYPE_C based on keywords
3. **Parser** (`parser/`) - Converts text to domain objects (Template Method)
4. **Validation** (`validation/`) - Applies transformations and validates (Strategy + Decorator)
5. **Generator** (`generator/`) - Produces output PDF with original structure

## Run

```bash
python main.py data/input/a_r_9.pdf -o data/output
```

Strict quality mode (optional):

```bash
python main.py data/input/a_r_9.pdf -o data/output --strict-quality
```

Set log level (optional):

```bash
python main.py data/input/a_r_9.pdf -o data/output --log-level DEBUG
```

## Tests

```bash
pytest attendance_report/tests/ -v
```

## Docker

Build image:

```bash
docker build -t attendance-report .
```

Run with mounted samples folder (same style as evaluator):

```bash
docker run --rm -v $(pwd)/samples:/data attendance-report /data/sample.pdf -o /data/
```

Windows PowerShell example:

```powershell
docker run --rm -v "${PWD}\data\input:/data" attendance-report /data/a_r_9.pdf -o /data/
```

If you want the output file to be written back to a local folder you can mount the whole data directory instead:

```powershell
docker run --rm -v "${PWD}\data:/data" attendance-report /data/input/a_r_9.pdf -o /data/output/
```
