#!/bin/bash

# Define your output zip file
OUTPUT_ZIP="Práctica01_DoblesComillas.zip"

# Hardcode your list of files here
# Wrap filenames in quotes if they contain spaces
FILES_TO_ZIP=(
    "README_DoblesComillas.pdf"
    "Docs/BitácoraContreras.pdf"
    "Docs/BitácoraCornejo.pdf"
    "Docs/BitácoraHipolito.pdf"
    "Docs/BitácoraLedesma.pdf"
    "Docs/PreguntasDoblesComillas.pdf"
)

# Remove the old zip file if it already exists
if [ -f "$OUTPUT_ZIP" ]; then
    rm "$OUTPUT_ZIP"
fi

echo "Creating $OUTPUT_ZIP..."

# Loop through the hardcoded array
for filename in "${FILES_TO_ZIP[@]}"; do
    # Check if the file actually exists in the directory
    if [ -f "$filename" ]; then
        # Add the file to the zip quietly (-q)
        zip -q "$OUTPUT_ZIP" "$filename"
        echo "Added: $filename"
    else
        echo "Skipped: '$filename' (File not found)"
    fi
done

echo "Done!"
