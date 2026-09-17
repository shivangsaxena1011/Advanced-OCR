# Table Extraction & Reconstruction

## Algorithm

1. **Row Binning**: Groups OCR tokens sharing horizontal alignment within a 14px center-Y tolerance window.
2. **Tabular Clustering**: Identifies contiguous sequences of rows containing multiple column tokens with vertical spacing < 65px.
3. **Cell Boundary Assignment**: Derives column spans and row headers.
4. **Export Formats**: Directly exports structured tables to CSV, Markdown (`| Col 1 | Col 2 |`), and JSON.
